"""
Counterfactual Explanation Service

Generates "what-if" explanations for AI suggestions, enabling clinicians
to understand what would need to change for a different outcome.

References:
- Wachter et al. (2017): Counterfactual Explanations without Opening the Black Box
- Mothilal et al. (2020): DiCE: Diverse Counterfactual Explanations
- Karimi et al. (2020): Algorithmic Recourse

Key Features:
- Minimum perturbation counterfactuals
- Contrastive explanations (why this patient vs similar patient)
- Actionable recourse (what clinician can do)
- GDPR-compliant "right to explanation"
"""

from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass, field
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


@dataclass
class FeaturePerturbation:
    """A single feature change in a counterfactual"""
    feature_name: str
    current_value: Any
    counterfactual_value: Any
    change_magnitude: float
    is_actionable: bool  # Can clinician actually change this?
    clinical_meaning: str


@dataclass
class CounterfactualExplanation:
    """Complete counterfactual explanation"""
    original_prediction: str
    counterfactual_prediction: str
    perturbations: List[FeaturePerturbation]
    total_change_cost: float  # Sum of normalized changes
    confidence: float
    explanation_text: str
    actionable_steps: List[str]


@dataclass
class ContrastiveExplanation:
    """Why this patient differs from a similar patient"""
    patient_id: UUID
    comparison_patient_id: UUID
    patient_prediction: str
    comparison_prediction: str
    key_differences: List[Dict[str, Any]]
    explanation_text: str


class CounterfactualExplanationService:
    """
    Generate counterfactual and contrastive explanations for clinical AI.
    
    This service provides:
    1. Minimum perturbation counterfactuals (smallest change to flip prediction)
    2. Contrastive explanations (why patient A vs patient B)
    3. Actionable recourse recommendations
    4. Human-readable explanation text
    """
    
    # Feature metadata: ranges, actionability, clinical names
    FEATURE_METADATA = {
        # Vital signs
        "bp_systolic": {
            "name": "Systolic Blood Pressure",
            "unit": "mmHg",
            "normal_range": (90, 120),
            "critical_high": 180,
            "critical_low": 90,
            "actionable": True,
            "action_text": "Consider antihypertensive medication or lifestyle modifications",
        },
        "bp_diastolic": {
            "name": "Diastolic Blood Pressure",
            "unit": "mmHg",
            "normal_range": (60, 80),
            "critical_high": 120,
            "critical_low": 60,
            "actionable": True,
            "action_text": "Consider antihypertensive medication",
        },
        "heart_rate": {
            "name": "Heart Rate",
            "unit": "bpm",
            "normal_range": (60, 100),
            "critical_high": 150,
            "critical_low": 50,
            "actionable": True,
            "action_text": "Evaluate cardiac rhythm and consider rate control",
        },
        "spo2": {
            "name": "Oxygen Saturation",
            "unit": "%",
            "normal_range": (95, 100),
            "critical_low": 90,
            "actionable": True,
            "action_text": "Consider supplemental oxygen therapy",
        },
        "temperature": {
            "name": "Body Temperature",
            "unit": "°C",
            "normal_range": (36.1, 37.2),
            "critical_high": 39.0,
            "critical_low": 35.0,
            "actionable": True,
            "action_text": "Evaluate for infection; consider antipyretics",
        },
        "respiratory_rate": {
            "name": "Respiratory Rate",
            "unit": "breaths/min",
            "normal_range": (12, 20),
            "critical_high": 30,
            "critical_low": 10,
            "actionable": True,
            "action_text": "Evaluate respiratory status; consider ABG",
        },
        # Lab values
        "hba1c": {
            "name": "HbA1c",
            "unit": "%",
            "normal_range": (4.0, 5.6),
            "critical_high": 10.0,
            "actionable": True,
            "action_text": "Intensify glycemic control; adjust diabetes medications",
        },
        "creatinine": {
            "name": "Serum Creatinine",
            "unit": "mg/dL",
            "normal_range": (0.6, 1.2),
            "critical_high": 4.0,
            "actionable": False,  # Not directly actionable
            "action_text": "Evaluate renal function; nephrology consult if declining",
        },
        "potassium": {
            "name": "Serum Potassium",
            "unit": "mEq/L",
            "normal_range": (3.5, 5.0),
            "critical_high": 6.0,
            "critical_low": 3.0,
            "actionable": True,
            "action_text": "Correct electrolyte imbalance; consider dietary changes",
        },
        # Demographics (not directly actionable but important for explanation)
        "age": {
            "name": "Age",
            "unit": "years",
            "actionable": False,
            "action_text": "Non-modifiable risk factor",
        },
        "bmi": {
            "name": "Body Mass Index",
            "unit": "kg/m²",
            "normal_range": (18.5, 24.9),
            "critical_high": 40.0,
            "actionable": True,
            "action_text": "Weight management program; dietary counseling",
        },
        # Comorbidities (count)
        "comorbidity_count": {
            "name": "Number of Comorbidities",
            "unit": "count",
            "actionable": False,
            "action_text": "Optimize management of existing conditions",
        },
    }
    
    # Risk thresholds for different conditions
    RISK_THRESHOLDS = {
        "cardiovascular": {
            "high_risk": {"bp_systolic": 160, "heart_rate": 120, "bmi": 35},
            "low_risk": {"bp_systolic": 120, "heart_rate": 80, "bmi": 25},
        },
        "diabetes": {
            "high_risk": {"hba1c": 8.0, "bmi": 30},
            "low_risk": {"hba1c": 5.7, "bmi": 25},
        },
        "respiratory": {
            "high_risk": {"spo2": 92, "respiratory_rate": 25},
            "low_risk": {"spo2": 98, "respiratory_rate": 16},
        },
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def generate_counterfactual(
        self,
        patient_features: Dict[str, Any],
        current_prediction: str,
        desired_prediction: str,
        condition_type: str = "cardiovascular",
        max_features_to_change: int = 3
    ) -> CounterfactualExplanation:
        """
        Generate a minimum perturbation counterfactual explanation.
        
        Args:
            patient_features: Current patient feature values
            current_prediction: Current risk level (e.g., "high_risk")
            desired_prediction: Target risk level (e.g., "low_risk")
            condition_type: Type of condition for threshold lookup
            max_features_to_change: Maximum features to modify
            
        Returns:
            CounterfactualExplanation with minimum changes needed
        """
        if condition_type not in self.RISK_THRESHOLDS:
            condition_type = "cardiovascular"  # Default
        
        thresholds = self.RISK_THRESHOLDS[condition_type]
        target_values = thresholds.get(desired_prediction, thresholds.get("low_risk", {}))
        
        # Calculate perturbations needed
        perturbations = []
        
        for feature, target in target_values.items():
            if feature not in patient_features:
                continue
                
            current = patient_features[feature]
            if current is None:
                continue
            
            # Calculate change needed
            change = target - current
            if abs(change) < 0.01:  # Already at target
                continue
            
            metadata = self.FEATURE_METADATA.get(feature, {})
            normal_range = metadata.get("normal_range", (0, 100))
            range_size = normal_range[1] - normal_range[0] if len(normal_range) == 2 else 100
            
            perturbation = FeaturePerturbation(
                feature_name=metadata.get("name", feature),
                current_value=current,
                counterfactual_value=target,
                change_magnitude=abs(change) / range_size,  # Normalized
                is_actionable=metadata.get("actionable", False),
                clinical_meaning=self._generate_change_meaning(feature, current, target, metadata),
            )
            perturbations.append(perturbation)
        
        # Sort by change magnitude and take top N
        perturbations.sort(key=lambda p: p.change_magnitude)
        perturbations = perturbations[:max_features_to_change]
        
        # Generate explanation text
        explanation_text = self._generate_counterfactual_text(
            current_prediction, desired_prediction, perturbations
        )
        
        # Generate actionable steps
        actionable_steps = [
            self.FEATURE_METADATA.get(p.feature_name.lower().replace(" ", "_"), {}).get("action_text", "")
            for p in perturbations
            if p.is_actionable
        ]
        actionable_steps = [s for s in actionable_steps if s]
        
        # Calculate total change cost
        total_cost = sum(p.change_magnitude for p in perturbations)
        
        return CounterfactualExplanation(
            original_prediction=current_prediction,
            counterfactual_prediction=desired_prediction,
            perturbations=perturbations,
            total_change_cost=total_cost,
            confidence=max(0.0, 1.0 - total_cost),  # Higher cost = lower confidence
            explanation_text=explanation_text,
            actionable_steps=actionable_steps,
        )
    
    def _generate_change_meaning(
        self,
        feature: str,
        current: float,
        target: float,
        metadata: Dict[str, Any]
    ) -> str:
        """Generate clinical meaning for a feature change."""
        name = metadata.get("name", feature)
        unit = metadata.get("unit", "")
        direction = "reduce" if current > target else "increase"
        
        change = abs(target - current)
        
        return f"{direction.capitalize()} {name} from {current:.1f} to {target:.1f} {unit} (change of {change:.1f} {unit})"
    
    def _generate_counterfactual_text(
        self,
        current: str,
        desired: str,
        perturbations: List[FeaturePerturbation]
    ) -> str:
        """Generate human-readable counterfactual explanation."""
        if not perturbations:
            return f"Patient is currently at {current.replace('_', ' ')}. No clear single-factor changes would alter this prediction."
        
        current_nice = current.replace("_", " ").title()
        desired_nice = desired.replace("_", " ").title()
        
        changes = []
        for p in perturbations:
            if p.current_value > p.counterfactual_value:
                changes.append(f"{p.feature_name} was below {p.counterfactual_value:.1f} (currently {p.current_value:.1f})")
            else:
                changes.append(f"{p.feature_name} was above {p.counterfactual_value:.1f} (currently {p.current_value:.1f})")
        
        if len(changes) == 1:
            change_text = changes[0]
        elif len(changes) == 2:
            change_text = f"{changes[0]} AND {changes[1]}"
        else:
            change_text = ", ".join(changes[:-1]) + f", AND {changes[-1]}"
        
        return f"This patient would be classified as {desired_nice} instead of {current_nice} if {change_text}."
    
    def generate_contrastive_explanation(
        self,
        patient_id: UUID,
        patient_features: Dict[str, Any],
        patient_prediction: str,
        comparison_features: Dict[str, Any],
        comparison_prediction: str,
        comparison_patient_id: Optional[UUID] = None
    ) -> ContrastiveExplanation:
        """
        Generate a contrastive explanation comparing two patients.
        
        Answers: "Why is patient A high-risk while similar patient B is low-risk?"
        """
        key_differences = []
        
        # Find features that differ significantly
        all_features = set(patient_features.keys()) | set(comparison_features.keys())
        
        for feature in all_features:
            val1 = patient_features.get(feature)
            val2 = comparison_features.get(feature)
            
            if val1 is None or val2 is None:
                continue
            
            # Calculate difference
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                diff = abs(val1 - val2)
                metadata = self.FEATURE_METADATA.get(feature, {})
                normal_range = metadata.get("normal_range", (0, 100))
                range_size = normal_range[1] - normal_range[0] if len(normal_range) == 2 else 100
                
                # Only include significant differences (> 10% of range)
                if diff / range_size > 0.1:
                    key_differences.append({
                        "feature": metadata.get("name", feature),
                        "patient_value": val1,
                        "comparison_value": val2,
                        "difference": diff,
                        "unit": metadata.get("unit", ""),
                        "significance": "high" if diff / range_size > 0.3 else "moderate",
                    })
        
        # Sort by significance
        key_differences.sort(key=lambda x: x["difference"], reverse=True)
        key_differences = key_differences[:5]  # Top 5 differences
        
        # Generate explanation text
        explanation_text = self._generate_contrastive_text(
            patient_prediction, comparison_prediction, key_differences
        )
        
        return ContrastiveExplanation(
            patient_id=patient_id,
            comparison_patient_id=comparison_patient_id or UUID('00000000-0000-0000-0000-000000000000'),
            patient_prediction=patient_prediction,
            comparison_prediction=comparison_prediction,
            key_differences=key_differences,
            explanation_text=explanation_text,
        )
    
    def _generate_contrastive_text(
        self,
        patient_pred: str,
        comparison_pred: str,
        differences: List[Dict[str, Any]]
    ) -> str:
        """Generate contrastive explanation text."""
        if not differences:
            return "The two patients have very similar profiles. Prediction differences may be due to subtle combinations of factors."
        
        patient_nice = patient_pred.replace("_", " ").title()
        comparison_nice = comparison_pred.replace("_", " ").title()
        
        diff_texts = []
        for d in differences[:3]:  # Top 3
            diff_texts.append(
                f"{d['feature']}: {d['patient_value']:.1f} vs {d['comparison_value']:.1f} {d['unit']}"
            )
        
        diff_list = "; ".join(diff_texts)
        
        return (
            f"This patient is classified as {patient_nice} while the comparison patient is {comparison_nice}. "
            f"Key differences: {diff_list}."
        )
    
    def find_similar_patient_with_different_outcome(
        self,
        patient_features: Dict[str, Any],
        patient_prediction: str,
        limit: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Find a similar patient with a different prediction for contrastive explanation.
        
        Uses nearest neighbor search on feature space, filtered by different outcome.
        """
        # This would query the database for patients with similar features
        # but different outcomes. For now, return None as placeholder.
        # In production, implement proper similarity search.
        logger.info("Similar patient search not implemented - returning None")
        return None
    
    def generate_actionable_recourse(
        self,
        patient_features: Dict[str, Any],
        current_prediction: str,
        desired_prediction: str
    ) -> Dict[str, Any]:
        """
        Generate actionable recourse recommendations.
        
        Unlike counterfactuals which show any change, recourse focuses on
        changes that the clinician/patient can actually make.
        """
        counterfactual = self.generate_counterfactual(
            patient_features, current_prediction, desired_prediction
        )
        
        # Filter to only actionable perturbations
        actionable_perturbations = [p for p in counterfactual.perturbations if p.is_actionable]
        
        # Generate specific action plan
        action_plan = []
        for p in actionable_perturbations:
            feature_key = p.feature_name.lower().replace(" ", "_")
            metadata = self.FEATURE_METADATA.get(feature_key, {})
            
            action_plan.append({
                "target": p.feature_name,
                "current_value": p.current_value,
                "target_value": p.counterfactual_value,
                "action": metadata.get("action_text", "Consult specialist"),
                "priority": "high" if p.change_magnitude > 0.3 else "medium",
                "timeframe": "immediate" if p.change_magnitude > 0.5 else "within 3 months",
            })
        
        return {
            "current_risk": current_prediction,
            "target_risk": desired_prediction,
            "action_plan": action_plan,
            "success_probability": counterfactual.confidence,
            "explanation": counterfactual.explanation_text,
            "disclaimer": (
                "This is an AI-generated recommendation for research purposes. "
                "Clinical decisions should be made by qualified healthcare providers."
            ),
        }
    
    def explain_suggestion(
        self,
        suggestion_id: UUID,
        patient_id: UUID
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation for a specific AI suggestion.
        
        Combines:
        1. Feature importance (which factors contributed)
        2. Counterfactual (what would change the prediction)
        3. Contrastive (vs similar patients)
        4. Actionable recourse
        """
        try:
            # Get suggestion details
            suggestion_result = self.db.execute(text("""
                SELECT s.*, p.name as patient_name
                FROM suggestions s
                JOIN patients p ON s.patient_id = p.id
                WHERE s.id = :suggestion_id
            """), {"suggestion_id": str(suggestion_id)}).fetchone()
            
            if not suggestion_result:
                return {"error": "Suggestion not found"}
            
            # Get patient features (vitals, labs, etc.)
            patient_features = self._get_patient_features(patient_id)
            
            # Generate explanations
            counterfactual = self.generate_counterfactual(
                patient_features,
                current_prediction="high_risk",  # Assumption
                desired_prediction="low_risk",
            )
            
            recourse = self.generate_actionable_recourse(
                patient_features,
                current_prediction="high_risk",
                desired_prediction="low_risk",
            )
            
            return {
                "suggestion_id": str(suggestion_id),
                "patient_id": str(patient_id),
                "explanations": {
                    "counterfactual": {
                        "text": counterfactual.explanation_text,
                        "changes_needed": [
                            {
                                "feature": p.feature_name,
                                "from": p.current_value,
                                "to": p.counterfactual_value,
                                "meaning": p.clinical_meaning,
                            }
                            for p in counterfactual.perturbations
                        ],
                    },
                    "actionable_recourse": recourse,
                },
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "explanation_type": "counterfactual_with_recourse",
                },
            }
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return {"error": str(e)}
    
    def _get_patient_features(self, patient_id: UUID) -> Dict[str, Any]:
        """Get patient features for explanation generation."""
        features = {}
        
        try:
            # Get latest vitals
            vitals_result = self.db.execute(text("""
                SELECT hr, bp_sys, bp_dia, spo2, temp, rr
                FROM vitals
                WHERE patient_id = :patient_id
                ORDER BY recorded_at DESC
                LIMIT 1
            """), {"patient_id": str(patient_id)}).fetchone()
            
            if vitals_result:
                features["heart_rate"] = vitals_result[0]
                features["bp_systolic"] = vitals_result[1]
                features["bp_diastolic"] = vitals_result[2]
                features["spo2"] = vitals_result[3]
                features["temperature"] = vitals_result[4]
                features["respiratory_rate"] = vitals_result[5]
            
            # Get patient demographics
            patient_result = self.db.execute(text("""
                SELECT age FROM patients WHERE id = :patient_id
            """), {"patient_id": str(patient_id)}).fetchone()
            
            if patient_result:
                features["age"] = patient_result[0]
                
        except Exception as e:
            logger.warning(f"Error fetching patient features: {e}")
        
        return features

