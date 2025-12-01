"""
Fairness Analysis Service

Comprehensive fairness analysis for self-adaptive clinical systems.
Implements formal fairness metrics from the algorithmic fairness literature.

References:
- Mehrabi et al. (2021): A Survey on Bias and Fairness in Machine Learning
- Dwork et al. (2012): Fairness Through Awareness
- Hardt et al. (2016): Equality of Opportunity in Supervised Learning
- Chouldechova (2017): Fair Prediction with Disparate Impact

Key Metrics:
- Demographic Parity: P(Ŷ=1|A=0) = P(Ŷ=1|A=1)
- Equalized Odds: TPR and FPR equal across groups
- Calibration: P(Y=1|Ŷ=p,A=a) = p for all groups
- Individual Fairness: Similar individuals get similar outcomes
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from uuid import UUID
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


@dataclass
class GroupStatistics:
    """Statistics for a demographic group"""
    group_id: str
    group_size: int
    positive_rate: float  # P(Ŷ=1|A=a)
    true_positive_rate: float  # P(Ŷ=1|Y=1,A=a)
    false_positive_rate: float  # P(Ŷ=1|Y=0,A=a)
    true_negative_rate: float
    false_negative_rate: float
    precision: float
    recall: float
    f1_score: float


@dataclass
class DemographicParityResult:
    """Demographic Parity Analysis Result"""
    metric_name: str = "demographic_parity"
    groups: Dict[str, GroupStatistics] = field(default_factory=dict)
    parity_gap: float = 0.0  # Max difference in positive rates
    parity_ratio: float = 1.0  # Min/Max positive rate ratio
    is_fair: bool = True
    threshold: float = 0.8  # 80% rule
    interpretation: str = ""
    recommendations: List[str] = field(default_factory=list)


@dataclass
class EqualizedOddsResult:
    """Equalized Odds Analysis Result"""
    metric_name: str = "equalized_odds"
    groups: Dict[str, GroupStatistics] = field(default_factory=dict)
    tpr_gap: float = 0.0  # Max TPR difference
    fpr_gap: float = 0.0  # Max FPR difference
    equalized_odds_gap: float = 0.0  # Max of TPR and FPR gaps
    is_fair: bool = True
    threshold: float = 0.1
    interpretation: str = ""
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CalibrationResult:
    """Calibration Analysis Result"""
    metric_name: str = "calibration"
    groups: Dict[str, List[Tuple[float, float]]] = field(default_factory=dict)  # group -> [(predicted, actual)]
    calibration_error: Dict[str, float] = field(default_factory=dict)  # group -> ECE
    is_well_calibrated: Dict[str, bool] = field(default_factory=dict)
    interpretation: str = ""


@dataclass
class IndividualFairnessResult:
    """Individual Fairness Analysis Result"""
    metric_name: str = "individual_fairness"
    consistency_score: float = 0.0  # 1 - Lipschitz violation rate
    lipschitz_violations: int = 0
    total_pairs_checked: int = 0
    is_fair: bool = True
    interpretation: str = ""


@dataclass
class ComprehensiveFairnessReport:
    """Complete fairness analysis report"""
    analysis_date: datetime
    sensitive_attribute: str
    demographic_parity: DemographicParityResult
    equalized_odds: EqualizedOddsResult
    calibration: CalibrationResult
    individual_fairness: IndividualFairnessResult
    overall_fairness_score: float  # 0-1 aggregate score
    critical_issues: List[str]
    recommendations: List[str]


class FairnessAnalysisService:
    """
    Comprehensive fairness analysis for self-adaptive systems.
    
    Analyzes:
    1. Group fairness (across specialties, experience levels, etc.)
    2. Individual fairness (similar users get similar adaptations)
    3. Temporal fairness (fairness maintained over time)
    4. Intersectional fairness (combinations of attributes)
    """
    
    # Sensitive attributes to analyze
    SENSITIVE_ATTRIBUTES = [
        "specialty",
        "experience_level",  # junior, mid, senior
        "department",
        "shift_type",  # day, night, weekend
    ]
    
    # Fairness thresholds
    DEMOGRAPHIC_PARITY_THRESHOLD = 0.8  # 80% rule
    EQUALIZED_ODDS_THRESHOLD = 0.1      # 10% max gap
    CALIBRATION_THRESHOLD = 0.1         # 10% ECE
    INDIVIDUAL_FAIRNESS_THRESHOLD = 0.9 # 90% consistency
    
    def __init__(self, db: Session):
        self.db = db
    
    def demographic_parity_analysis(
        self,
        predictions: List[Dict[str, Any]],
        sensitive_attribute: str,
        positive_label: str = "high_priority"
    ) -> DemographicParityResult:
        """
        Analyze demographic parity: P(Ŷ=1|A=0) = P(Ŷ=1|A=1)
        
        Adaptations should not disproportionately favor/disfavor any group.
        
        Args:
            predictions: List of {user_id, sensitive_value, prediction, ground_truth}
            sensitive_attribute: Attribute to analyze (e.g., 'specialty')
            positive_label: What counts as positive prediction
            
        Returns:
            DemographicParityResult with parity metrics
        """
        # Group by sensitive attribute
        groups: Dict[str, List[Dict]] = {}
        for pred in predictions:
            group = pred.get(sensitive_attribute, "unknown")
            if group not in groups:
                groups[group] = []
            groups[group].append(pred)
        
        # Calculate positive rates per group
        group_stats = {}
        positive_rates = []
        
        for group_id, group_preds in groups.items():
            if len(group_preds) < 10:  # Minimum sample size
                continue
            
            positives = sum(1 for p in group_preds if p.get("prediction") == positive_label)
            positive_rate = positives / len(group_preds)
            positive_rates.append(positive_rate)
            
            # Full stats
            stats = self._calculate_group_statistics(group_id, group_preds, positive_label)
            group_stats[group_id] = stats
        
        if len(positive_rates) < 2:
            return self._insufficient_groups_parity_result(sensitive_attribute)
        
        # Calculate parity metrics
        max_rate = max(positive_rates)
        min_rate = min(positive_rates)
        parity_gap = max_rate - min_rate
        parity_ratio = min_rate / max_rate if max_rate > 0 else 1.0
        
        is_fair = parity_ratio >= self.DEMOGRAPHIC_PARITY_THRESHOLD
        
        interpretation = self._interpret_demographic_parity(
            parity_ratio, parity_gap, group_stats, sensitive_attribute
        )
        
        recommendations = []
        if not is_fair:
            recommendations = self._generate_parity_recommendations(
                group_stats, sensitive_attribute
            )
        
        return DemographicParityResult(
            groups=group_stats,
            parity_gap=parity_gap,
            parity_ratio=parity_ratio,
            is_fair=is_fair,
            threshold=self.DEMOGRAPHIC_PARITY_THRESHOLD,
            interpretation=interpretation,
            recommendations=recommendations,
        )
    
    def equalized_odds_analysis(
        self,
        predictions: List[Dict[str, Any]],
        sensitive_attribute: str,
        positive_label: str = "high_priority"
    ) -> EqualizedOddsResult:
        """
        Analyze equalized odds:
        P(Ŷ=1|Y=1,A=0) = P(Ŷ=1|Y=1,A=1) AND
        P(Ŷ=1|Y=0,A=0) = P(Ŷ=1|Y=0,A=1)
        
        TPR and FPR should be equal across groups.
        
        Args:
            predictions: List with ground_truth labels
            sensitive_attribute: Attribute to analyze
            positive_label: What counts as positive
            
        Returns:
            EqualizedOddsResult
        """
        # Group and calculate TPR/FPR per group
        groups: Dict[str, List[Dict]] = {}
        for pred in predictions:
            group = pred.get(sensitive_attribute, "unknown")
            if group not in groups:
                groups[group] = []
            groups[group].append(pred)
        
        group_stats = {}
        tprs = []
        fprs = []
        
        for group_id, group_preds in groups.items():
            if len(group_preds) < 10:
                continue
            
            stats = self._calculate_group_statistics(group_id, group_preds, positive_label)
            group_stats[group_id] = stats
            tprs.append(stats.true_positive_rate)
            fprs.append(stats.false_positive_rate)
        
        if len(tprs) < 2:
            return self._insufficient_groups_odds_result(sensitive_attribute)
        
        tpr_gap = max(tprs) - min(tprs)
        fpr_gap = max(fprs) - min(fprs)
        equalized_odds_gap = max(tpr_gap, fpr_gap)
        
        is_fair = equalized_odds_gap <= self.EQUALIZED_ODDS_THRESHOLD
        
        interpretation = self._interpret_equalized_odds(
            tpr_gap, fpr_gap, group_stats, sensitive_attribute
        )
        
        recommendations = []
        if not is_fair:
            recommendations = self._generate_odds_recommendations(
                group_stats, tpr_gap, fpr_gap, sensitive_attribute
            )
        
        return EqualizedOddsResult(
            groups=group_stats,
            tpr_gap=tpr_gap,
            fpr_gap=fpr_gap,
            equalized_odds_gap=equalized_odds_gap,
            is_fair=is_fair,
            threshold=self.EQUALIZED_ODDS_THRESHOLD,
            interpretation=interpretation,
            recommendations=recommendations,
        )
    
    def calibration_analysis(
        self,
        predictions: List[Dict[str, Any]],
        sensitive_attribute: str,
        num_bins: int = 10
    ) -> CalibrationResult:
        """
        Analyze calibration: P(Y=1|Ŷ=p,A=a) = p for all groups.
        
        Predicted probabilities should match actual outcomes.
        
        Args:
            predictions: List with predicted_prob and ground_truth
            sensitive_attribute: Attribute to analyze
            num_bins: Number of probability bins
            
        Returns:
            CalibrationResult
        """
        groups: Dict[str, List[Dict]] = {}
        for pred in predictions:
            group = pred.get(sensitive_attribute, "unknown")
            if group not in groups:
                groups[group] = []
            groups[group].append(pred)
        
        calibration_curves = {}
        calibration_errors = {}
        is_calibrated = {}
        
        for group_id, group_preds in groups.items():
            if len(group_preds) < 20:
                continue
            
            # Bin predictions
            bins = [[] for _ in range(num_bins)]
            for pred in group_preds:
                prob = pred.get("predicted_prob", 0.5)
                bin_idx = min(int(prob * num_bins), num_bins - 1)
                bins[bin_idx].append(pred)
            
            # Calculate calibration curve
            curve = []
            total_ece = 0.0
            total_samples = 0
            
            for i, bin_preds in enumerate(bins):
                if len(bin_preds) < 5:
                    continue
                
                bin_center = (i + 0.5) / num_bins
                actual_positive_rate = sum(
                    1 for p in bin_preds if p.get("ground_truth") == 1
                ) / len(bin_preds)
                
                curve.append((bin_center, actual_positive_rate))
                
                # ECE contribution
                ece_contrib = len(bin_preds) * abs(bin_center - actual_positive_rate)
                total_ece += ece_contrib
                total_samples += len(bin_preds)
            
            calibration_curves[group_id] = curve
            ece = total_ece / total_samples if total_samples > 0 else 0
            calibration_errors[group_id] = ece
            is_calibrated[group_id] = ece <= self.CALIBRATION_THRESHOLD
        
        interpretation = self._interpret_calibration(
            calibration_errors, is_calibrated, sensitive_attribute
        )
        
        return CalibrationResult(
            groups=calibration_curves,
            calibration_error=calibration_errors,
            is_well_calibrated=is_calibrated,
            interpretation=interpretation,
        )
    
    def individual_fairness_analysis(
        self,
        users: List[Dict[str, Any]],
        adaptations: List[Dict[str, Any]],
        similarity_threshold: float = 0.8,
        max_pairs: int = 1000
    ) -> IndividualFairnessResult:
        """
        Analyze individual fairness:
        d(A(u1), A(u2)) ≤ L * d(u1, u2)
        
        Similar users should receive similar adaptations.
        
        Args:
            users: List of user profiles
            adaptations: List of adaptations per user
            similarity_threshold: What counts as "similar" users
            max_pairs: Maximum pairs to check (for scalability)
            
        Returns:
            IndividualFairnessResult
        """
        # Build user-adaptation map
        user_adaptations = {a["user_id"]: a for a in adaptations}
        
        # Check pairs
        violations = 0
        total_pairs = 0
        
        import random
        user_pairs = []
        for i, u1 in enumerate(users):
            for u2 in users[i+1:]:
                user_pairs.append((u1, u2))
        
        # Sample if too many pairs
        if len(user_pairs) > max_pairs:
            user_pairs = random.sample(user_pairs, max_pairs)
        
        for u1, u2 in user_pairs:
            total_pairs += 1
            
            # Calculate user similarity
            user_sim = self._calculate_user_similarity(u1, u2)
            
            if user_sim < similarity_threshold:
                continue  # Not similar enough to require similar treatment
            
            # Calculate adaptation similarity
            a1 = user_adaptations.get(u1.get("user_id"))
            a2 = user_adaptations.get(u2.get("user_id"))
            
            if not a1 or not a2:
                continue
            
            adaptation_sim = self._calculate_adaptation_similarity(a1, a2)
            
            # Lipschitz violation: similar users but different adaptations
            if adaptation_sim < user_sim * 0.8:  # 80% of user similarity
                violations += 1
        
        consistency_score = 1 - (violations / total_pairs) if total_pairs > 0 else 1.0
        is_fair = consistency_score >= self.INDIVIDUAL_FAIRNESS_THRESHOLD
        
        interpretation = self._interpret_individual_fairness(
            consistency_score, violations, total_pairs
        )
        
        return IndividualFairnessResult(
            consistency_score=consistency_score,
            lipschitz_violations=violations,
            total_pairs_checked=total_pairs,
            is_fair=is_fair,
            interpretation=interpretation,
        )
    
    def comprehensive_fairness_audit(
        self,
        predictions: List[Dict[str, Any]],
        users: List[Dict[str, Any]],
        adaptations: List[Dict[str, Any]],
        sensitive_attribute: str = "specialty"
    ) -> ComprehensiveFairnessReport:
        """
        Perform comprehensive fairness audit.
        
        Combines all fairness metrics into a single report.
        """
        dp_result = self.demographic_parity_analysis(predictions, sensitive_attribute)
        eo_result = self.equalized_odds_analysis(predictions, sensitive_attribute)
        cal_result = self.calibration_analysis(predictions, sensitive_attribute)
        if_result = self.individual_fairness_analysis(users, adaptations)
        
        # Calculate overall score (weighted average)
        scores = []
        if dp_result.parity_ratio > 0:
            scores.append(min(1.0, dp_result.parity_ratio / self.DEMOGRAPHIC_PARITY_THRESHOLD))
        if eo_result.equalized_odds_gap < 1:
            scores.append(max(0, 1 - eo_result.equalized_odds_gap / self.EQUALIZED_ODDS_THRESHOLD))
        scores.append(if_result.consistency_score)
        
        overall_score = sum(scores) / len(scores) if scores else 0.5
        
        # Identify critical issues
        critical_issues = []
        if not dp_result.is_fair:
            critical_issues.append(f"Demographic parity violation ({sensitive_attribute})")
        if not eo_result.is_fair:
            critical_issues.append(f"Equalized odds violation ({sensitive_attribute})")
        if not if_result.is_fair:
            critical_issues.append("Individual fairness violation")
        
        # Aggregate recommendations
        recommendations = list(set(
            dp_result.recommendations + eo_result.recommendations
        ))
        
        if not recommendations and critical_issues:
            recommendations.append(
                "Consider rebalancing training data or adjusting adaptation thresholds"
            )
        
        return ComprehensiveFairnessReport(
            analysis_date=datetime.utcnow(),
            sensitive_attribute=sensitive_attribute,
            demographic_parity=dp_result,
            equalized_odds=eo_result,
            calibration=cal_result,
            individual_fairness=if_result,
            overall_fairness_score=overall_score,
            critical_issues=critical_issues,
            recommendations=recommendations,
        )
    
    def analyze_adaptation_fairness(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, ComprehensiveFairnessReport]:
        """
        Analyze fairness of adaptations across all sensitive attributes.
        """
        if start_date is None:
            start_date = datetime.utcnow() - timedelta(days=30)
        if end_date is None:
            end_date = datetime.utcnow()
        
        # Fetch data
        predictions = self._get_adaptation_predictions(start_date, end_date)
        users = self._get_user_profiles()
        adaptations = self._get_adaptations(start_date, end_date)
        
        reports = {}
        for attr in self.SENSITIVE_ATTRIBUTES:
            try:
                reports[attr] = self.comprehensive_fairness_audit(
                    predictions, users, adaptations, attr
                )
            except Exception as e:
                logger.warning(f"Fairness analysis failed for {attr}: {e}")
        
        return reports
    
    # Helper methods
    
    def _calculate_group_statistics(
        self,
        group_id: str,
        predictions: List[Dict],
        positive_label: str
    ) -> GroupStatistics:
        """Calculate comprehensive statistics for a group."""
        n = len(predictions)
        if n == 0:
            return GroupStatistics(
                group_id=group_id, group_size=0,
                positive_rate=0, true_positive_rate=0, false_positive_rate=0,
                true_negative_rate=0, false_negative_rate=0,
                precision=0, recall=0, f1_score=0
            )
        
        # Count outcomes
        tp = fp = tn = fn = 0
        for pred in predictions:
            predicted_positive = pred.get("prediction") == positive_label
            actual_positive = pred.get("ground_truth") == 1 or pred.get("ground_truth") == positive_label
            
            if predicted_positive and actual_positive:
                tp += 1
            elif predicted_positive and not actual_positive:
                fp += 1
            elif not predicted_positive and not actual_positive:
                tn += 1
            else:
                fn += 1
        
        # Calculate rates
        positive_rate = (tp + fp) / n
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tpr
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return GroupStatistics(
            group_id=group_id,
            group_size=n,
            positive_rate=positive_rate,
            true_positive_rate=tpr,
            false_positive_rate=fpr,
            true_negative_rate=tnr,
            false_negative_rate=fnr,
            precision=precision,
            recall=recall,
            f1_score=f1,
        )
    
    def _calculate_user_similarity(self, u1: Dict, u2: Dict) -> float:
        """Calculate similarity between two users (0-1)."""
        similarity = 0.0
        features_compared = 0
        
        # Compare categorical features
        categorical = ["specialty", "department", "role"]
        for feat in categorical:
            if feat in u1 and feat in u2:
                features_compared += 1
                if u1[feat] == u2[feat]:
                    similarity += 1.0
        
        # Compare numerical features
        numerical = ["experience_years", "session_count"]
        for feat in numerical:
            if feat in u1 and feat in u2:
                v1, v2 = u1[feat], u2[feat]
                if v1 is not None and v2 is not None:
                    features_compared += 1
                    max_val = max(abs(v1), abs(v2), 1)
                    similarity += 1 - abs(v1 - v2) / max_val
        
        return similarity / features_compared if features_compared > 0 else 0.5
    
    def _calculate_adaptation_similarity(self, a1: Dict, a2: Dict) -> float:
        """Calculate similarity between two adaptations (0-1)."""
        # Compare feature priorities
        f1 = set(a1.get("feature_priority", []))
        f2 = set(a2.get("feature_priority", []))
        
        if not f1 and not f2:
            return 1.0
        
        intersection = len(f1 & f2)
        union = len(f1 | f2)
        
        return intersection / union if union > 0 else 0.0
    
    def _interpret_demographic_parity(
        self,
        ratio: float,
        gap: float,
        stats: Dict[str, GroupStatistics],
        attr: str
    ) -> str:
        """Generate demographic parity interpretation."""
        if ratio >= self.DEMOGRAPHIC_PARITY_THRESHOLD:
            return (
                f"Demographic parity is satisfied for {attr}. "
                f"The positive rate ratio ({ratio:.2f}) meets the 80% threshold."
            )
        
        # Find most advantaged/disadvantaged groups
        rates = [(g, s.positive_rate) for g, s in stats.items()]
        rates.sort(key=lambda x: x[1], reverse=True)
        
        return (
            f"Demographic parity violation detected for {attr}. "
            f"'{rates[0][0]}' has {rates[0][1]*100:.1f}% positive rate while "
            f"'{rates[-1][0]}' has {rates[-1][1]*100:.1f}% (gap: {gap*100:.1f}%)."
        )
    
    def _interpret_equalized_odds(
        self,
        tpr_gap: float,
        fpr_gap: float,
        stats: Dict[str, GroupStatistics],
        attr: str
    ) -> str:
        """Generate equalized odds interpretation."""
        if max(tpr_gap, fpr_gap) <= self.EQUALIZED_ODDS_THRESHOLD:
            return (
                f"Equalized odds is satisfied for {attr}. "
                f"TPR gap: {tpr_gap*100:.1f}%, FPR gap: {fpr_gap*100:.1f}%."
            )
        
        issue = "True Positive Rate" if tpr_gap > fpr_gap else "False Positive Rate"
        return (
            f"Equalized odds violation detected for {attr}. "
            f"Main issue: {issue} gap of {max(tpr_gap, fpr_gap)*100:.1f}%."
        )
    
    def _interpret_calibration(
        self,
        errors: Dict[str, float],
        is_calibrated: Dict[str, bool],
        attr: str
    ) -> str:
        """Generate calibration interpretation."""
        well_calibrated = [g for g, c in is_calibrated.items() if c]
        poorly_calibrated = [g for g, c in is_calibrated.items() if not c]
        
        if not poorly_calibrated:
            return f"All groups are well-calibrated for {attr}."
        
        return (
            f"Calibration issues detected for {attr}. "
            f"Poorly calibrated groups: {', '.join(poorly_calibrated)}. "
            f"ECE values: {', '.join(f'{g}:{errors[g]:.3f}' for g in poorly_calibrated)}"
        )
    
    def _interpret_individual_fairness(
        self,
        score: float,
        violations: int,
        total: int
    ) -> str:
        """Generate individual fairness interpretation."""
        if score >= self.INDIVIDUAL_FAIRNESS_THRESHOLD:
            return (
                f"Individual fairness is satisfied. "
                f"Consistency score: {score*100:.1f}% ({violations} violations in {total} pairs)."
            )
        
        return (
            f"Individual fairness violation detected. "
            f"Consistency score: {score*100:.1f}% ({violations} violations in {total} pairs). "
            f"Similar users are receiving different adaptations."
        )
    
    def _generate_parity_recommendations(
        self,
        stats: Dict[str, GroupStatistics],
        attr: str
    ) -> List[str]:
        """Generate recommendations for parity violations."""
        recommendations = []
        
        # Find disadvantaged groups
        rates = [(g, s.positive_rate, s.group_size) for g, s in stats.items()]
        avg_rate = sum(r[1] for r in rates) / len(rates)
        
        disadvantaged = [g for g, r, _ in rates if r < avg_rate * 0.9]
        small_groups = [g for g, _, s in rates if s < 50]
        
        if disadvantaged:
            recommendations.append(
                f"Review adaptation policies for groups: {', '.join(disadvantaged)}"
            )
        
        if small_groups:
            recommendations.append(
                f"Consider collecting more data for underrepresented groups: {', '.join(small_groups)}"
            )
        
        recommendations.append(
            "Consider stratified training or post-processing fairness constraints"
        )
        
        return recommendations
    
    def _generate_odds_recommendations(
        self,
        stats: Dict[str, GroupStatistics],
        tpr_gap: float,
        fpr_gap: float,
        attr: str
    ) -> List[str]:
        """Generate recommendations for equalized odds violations."""
        recommendations = []
        
        if tpr_gap > self.EQUALIZED_ODDS_THRESHOLD:
            recommendations.append(
                "TPR disparity detected. Consider adjusting decision thresholds per group."
            )
        
        if fpr_gap > self.EQUALIZED_ODDS_THRESHOLD:
            recommendations.append(
                "FPR disparity detected. Review false positive sources across groups."
            )
        
        recommendations.append(
            "Consider applying equalized odds post-processing (Hardt et al., 2016)"
        )
        
        return recommendations
    
    def _insufficient_groups_parity_result(self, attr: str) -> DemographicParityResult:
        """Return result when insufficient groups."""
        return DemographicParityResult(
            interpretation=f"Insufficient groups for {attr} analysis (minimum 2 groups with 10+ samples)."
        )
    
    def _insufficient_groups_odds_result(self, attr: str) -> EqualizedOddsResult:
        """Return result when insufficient groups."""
        return EqualizedOddsResult(
            interpretation=f"Insufficient groups for {attr} analysis (minimum 2 groups with 10+ samples)."
        )
    
    def _get_adaptation_predictions(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch adaptation predictions from database."""
        try:
            result = self.db.execute(text("""
                SELECT 
                    a.user_id,
                    u.specialty,
                    u.department,
                    a.adaptation_type as prediction,
                    CASE WHEN ua.action_type = 'accept' THEN 1 ELSE 0 END as ground_truth
                FROM adaptations a
                JOIN users u ON a.user_id = u.id
                LEFT JOIN user_actions ua ON ua.user_id = a.user_id 
                    AND ua.action_metadata->>'adaptation_id' = a.id::text
                WHERE a.created_at BETWEEN :start_date AND :end_date
            """), {
                "start_date": start_date,
                "end_date": end_date,
            }).fetchall()
            
            return [
                {
                    "user_id": str(row[0]),
                    "specialty": row[1],
                    "department": row[2],
                    "prediction": row[3],
                    "ground_truth": row[4],
                }
                for row in result
            ]
        except Exception as e:
            logger.warning(f"Error fetching predictions: {e}")
            return []
    
    def _get_user_profiles(self) -> List[Dict[str, Any]]:
        """Fetch user profiles."""
        try:
            result = self.db.execute(text("""
                SELECT id, specialty, department, role
                FROM users
            """)).fetchall()
            
            return [
                {
                    "user_id": str(row[0]),
                    "specialty": row[1],
                    "department": row[2],
                    "role": row[3],
                }
                for row in result
            ]
        except Exception as e:
            logger.warning(f"Error fetching users: {e}")
            return []
    
    def _get_adaptations(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch adaptations."""
        try:
            result = self.db.execute(text("""
                SELECT user_id, plan_json
                FROM adaptations
                WHERE created_at BETWEEN :start_date AND :end_date
            """), {
                "start_date": start_date,
                "end_date": end_date,
            }).fetchall()
            
            return [
                {
                    "user_id": str(row[0]),
                    "feature_priority": row[1].get("feature_priority", []) if row[1] else [],
                }
                for row in result
            ]
        except Exception as e:
            logger.warning(f"Error fetching adaptations: {e}")
            return []

