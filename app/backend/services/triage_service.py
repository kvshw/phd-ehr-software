"""
Triage Service for AI-powered patient categorization and routing.

This service provides:
- AI-based specialty recommendations based on symptoms
- Priority assessment
- Triage queue management
- Nurse override support
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID
import logging
import re

logger = logging.getLogger(__name__)


class TriageService:
    """
    AI-powered triage service for categorizing patients and routing to specialists.
    
    The AI suggestions are based on symptom analysis and should always be
    reviewed and approved by nursing staff before final routing.
    """
    
    # Symptom-to-specialty mapping with confidence weights
    SYMPTOM_SPECIALTY_MAP = {
        # Cardiology
        "chest_pain": {"cardiology": 0.9, "emergency": 0.7, "internal": 0.3},
        "palpitations": {"cardiology": 0.85, "internal": 0.4, "psychiatry": 0.2},
        "shortness_of_breath": {"cardiology": 0.6, "internal": 0.5, "emergency": 0.4},
        "dyspnea": {"cardiology": 0.7, "internal": 0.5, "emergency": 0.4},
        "edema": {"cardiology": 0.6, "internal": 0.5},
        "syncope": {"cardiology": 0.7, "neurology": 0.5, "emergency": 0.4},
        
        # Neurology
        "headache": {"neurology": 0.7, "internal": 0.3, "emergency": 0.2},
        "migraine": {"neurology": 0.85, "internal": 0.2},
        "seizure": {"neurology": 0.9, "emergency": 0.6},
        "dizziness": {"neurology": 0.6, "internal": 0.4, "cardiology": 0.3},
        "numbness": {"neurology": 0.75, "internal": 0.3},
        "vision_changes": {"neurology": 0.6, "ophthalmology": 0.5},
        "weakness": {"neurology": 0.6, "internal": 0.4},
        "confusion": {"neurology": 0.7, "psychiatry": 0.4, "emergency": 0.3},
        
        # Orthopedics
        "fracture": {"orthopedics": 0.95, "emergency": 0.5},
        "joint_pain": {"orthopedics": 0.8, "internal": 0.3},
        "back_pain": {"orthopedics": 0.7, "neurology": 0.3, "internal": 0.2},
        "arm_pain": {"orthopedics": 0.7, "emergency": 0.3},
        "leg_pain": {"orthopedics": 0.7, "emergency": 0.3},
        "swelling": {"orthopedics": 0.5, "internal": 0.4},
        "limited_mobility": {"orthopedics": 0.75, "neurology": 0.3},
        
        # Pediatrics
        "fever_child": {"pediatrics": 0.9, "emergency": 0.3},
        "ear_pain": {"pediatrics": 0.7, "internal": 0.3},
        "rash_child": {"pediatrics": 0.8, "dermatology": 0.4},
        "cough_child": {"pediatrics": 0.75, "internal": 0.3},
        "irritability": {"pediatrics": 0.6, "neurology": 0.2},
        
        # Psychiatry
        "anxiety": {"psychiatry": 0.85, "internal": 0.2},
        "depression": {"psychiatry": 0.9, "internal": 0.1},
        "panic_attacks": {"psychiatry": 0.8, "cardiology": 0.2},
        "insomnia": {"psychiatry": 0.6, "neurology": 0.3, "internal": 0.2},
        "mood_changes": {"psychiatry": 0.8},
        "hallucinations": {"psychiatry": 0.9, "neurology": 0.4},
        
        # Emergency
        "trauma": {"emergency": 0.95, "orthopedics": 0.3},
        "severe_bleeding": {"emergency": 0.95, "surgery": 0.4},
        "unconscious": {"emergency": 0.95, "neurology": 0.4},
        "difficulty_breathing": {"emergency": 0.8, "cardiology": 0.5, "internal": 0.3},
        "high_fever": {"emergency": 0.6, "internal": 0.5},
        
        # Internal Medicine
        "fatigue": {"internal": 0.6, "psychiatry": 0.3, "cardiology": 0.2},
        "weight_loss": {"internal": 0.7, "oncology": 0.4},
        "nausea": {"internal": 0.6, "emergency": 0.3},
        "abdominal_pain": {"internal": 0.7, "surgery": 0.4, "emergency": 0.3},
        "diabetes_symptoms": {"internal": 0.9},
        
        # Dermatology
        "rash": {"dermatology": 0.85, "internal": 0.3},
        "skin_lesion": {"dermatology": 0.8, "oncology": 0.2},
        "itching": {"dermatology": 0.7, "internal": 0.2},
        
        # Oncology
        "lump": {"oncology": 0.6, "surgery": 0.4, "internal": 0.3},
        "unexplained_weight_loss": {"oncology": 0.6, "internal": 0.5},
        "night_sweats": {"oncology": 0.5, "internal": 0.4},
    }
    
    # Priority keywords
    CRITICAL_KEYWORDS = ["unconscious", "severe_bleeding", "not_breathing", "cardiac_arrest"]
    URGENT_KEYWORDS = ["chest_pain", "seizure", "trauma", "difficulty_breathing", "high_fever"]
    
    @classmethod
    def analyze_symptoms(cls, symptoms: List[str], chief_complaint: str = "") -> Dict[str, Any]:
        """
        Analyze symptoms and provide specialty recommendation with confidence score.
        
        Args:
            symptoms: List of symptom keywords
            chief_complaint: Free-text chief complaint
            
        Returns:
            Dict with recommended_specialty, confidence, all_scores, and explanation
        """
        specialty_scores: Dict[str, float] = {}
        matched_symptoms = []
        
        # Analyze provided symptoms
        for symptom in symptoms:
            symptom_lower = symptom.lower().strip()
            if symptom_lower in cls.SYMPTOM_SPECIALTY_MAP:
                matched_symptoms.append(symptom_lower)
                for specialty, weight in cls.SYMPTOM_SPECIALTY_MAP[symptom_lower].items():
                    specialty_scores[specialty] = specialty_scores.get(specialty, 0) + weight
        
        # Also extract symptoms from chief complaint
        if chief_complaint:
            complaint_lower = chief_complaint.lower()
            for symptom in cls.SYMPTOM_SPECIALTY_MAP.keys():
                # Check if symptom appears in complaint
                if symptom.replace("_", " ") in complaint_lower or symptom in complaint_lower:
                    if symptom not in matched_symptoms:
                        matched_symptoms.append(symptom)
                        for specialty, weight in cls.SYMPTOM_SPECIALTY_MAP[symptom].items():
                            # Slightly lower weight for extracted symptoms
                            specialty_scores[specialty] = specialty_scores.get(specialty, 0) + (weight * 0.8)
        
        if not specialty_scores:
            # Default to general/internal medicine
            return {
                "recommended_specialty": "general",
                "confidence": 0.5,
                "all_scores": {"general": 0.5},
                "matched_symptoms": [],
                "explanation": "No specific symptoms matched. Recommending general practice for initial assessment.",
            }
        
        # Normalize scores
        max_score = max(specialty_scores.values())
        normalized_scores = {k: v / max_score for k, v in specialty_scores.items()}
        
        # Get top recommendation
        top_specialty = max(specialty_scores, key=specialty_scores.get)
        confidence = min(normalized_scores[top_specialty], 0.95)  # Cap at 95%
        
        # Build explanation
        explanation = f"Based on symptoms: {', '.join(matched_symptoms)}. "
        if confidence > 0.8:
            explanation += f"Strong indication for {top_specialty}."
        elif confidence > 0.6:
            explanation += f"Moderate indication for {top_specialty}."
        else:
            explanation += f"Weak indication - consider additional assessment."
        
        return {
            "recommended_specialty": top_specialty,
            "confidence": round(confidence, 2),
            "all_scores": {k: round(v, 2) for k, v in sorted(normalized_scores.items(), key=lambda x: -x[1])[:5]},
            "matched_symptoms": matched_symptoms,
            "explanation": explanation,
        }
    
    @classmethod
    def assess_priority(cls, symptoms: List[str], vitals: Optional[Dict[str, Any]] = None) -> str:
        """
        Assess patient priority based on symptoms and vitals.
        
        Returns:
            Priority level: 'critical', 'urgent', 'standard', or 'non_urgent'
        """
        symptoms_lower = [s.lower() for s in symptoms]
        
        # Check for critical symptoms
        for symptom in symptoms_lower:
            if symptom in cls.CRITICAL_KEYWORDS:
                return "critical"
        
        # Check vitals for critical values
        if vitals:
            hr = vitals.get("hr")
            spo2 = vitals.get("spo2")
            temp = vitals.get("temp")
            
            # Critical vitals
            if spo2 and spo2 < 90:
                return "critical"
            if hr and (hr > 150 or hr < 40):
                return "critical"
            
            # Urgent vitals
            if spo2 and spo2 < 94:
                return "urgent"
            if hr and (hr > 120 or hr < 50):
                return "urgent"
            if temp and temp > 39.5:
                return "urgent"
        
        # Check for urgent symptoms
        for symptom in symptoms_lower:
            if symptom in cls.URGENT_KEYWORDS:
                return "urgent"
        
        # Default assessment
        if len(symptoms) >= 3:
            return "standard"
        
        return "non_urgent"
    
    @classmethod
    def get_triage_recommendation(
        cls,
        symptoms: List[str],
        chief_complaint: str = "",
        vitals: Optional[Dict[str, Any]] = None,
        patient_age: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get complete triage recommendation including specialty and priority.
        
        Args:
            symptoms: List of symptom keywords
            chief_complaint: Free-text chief complaint
            vitals: Optional vital signs dict
            patient_age: Optional patient age for pediatric routing
            
        Returns:
            Complete triage recommendation with specialty, priority, and explanations
        """
        # Adjust for pediatric patients
        if patient_age and patient_age < 18:
            # Add pediatric context
            if "fever" in [s.lower() for s in symptoms]:
                symptoms.append("fever_child")
            if "rash" in [s.lower() for s in symptoms]:
                symptoms.append("rash_child")
            if "cough" in [s.lower() for s in symptoms]:
                symptoms.append("cough_child")
        
        # Get specialty recommendation
        specialty_analysis = cls.analyze_symptoms(symptoms, chief_complaint)
        
        # For very young children, boost pediatrics if not already top
        if patient_age and patient_age < 12:
            if specialty_analysis["recommended_specialty"] != "pediatrics":
                # Check if it's a genuine pediatric case
                if specialty_analysis["confidence"] < 0.8:
                    specialty_analysis["recommended_specialty"] = "pediatrics"
                    specialty_analysis["explanation"] += " Adjusted for pediatric patient."
        
        # Get priority assessment
        priority = cls.assess_priority(symptoms, vitals)
        
        return {
            "specialty": specialty_analysis["recommended_specialty"],
            "specialty_confidence": specialty_analysis["confidence"],
            "alternative_specialties": specialty_analysis["all_scores"],
            "priority": priority,
            "matched_symptoms": specialty_analysis["matched_symptoms"],
            "explanation": specialty_analysis["explanation"],
            "ai_disclaimer": "This is an AI-assisted recommendation. Final triage decision should be made by qualified healthcare staff.",
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @classmethod
    def log_triage_decision(
        cls,
        patient_id: str,
        ai_recommendation: Dict[str, Any],
        final_specialty: str,
        nurse_override: bool,
        nurse_id: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Log a triage decision for audit and ML improvement.
        
        This logs whether the nurse accepted the AI suggestion or overrode it,
        which can be used to improve the AI model over time.
        """
        decision = {
            "patient_id": patient_id,
            "ai_recommended_specialty": ai_recommendation.get("specialty"),
            "ai_confidence": ai_recommendation.get("specialty_confidence"),
            "final_specialty": final_specialty,
            "nurse_override": nurse_override,
            "override_type": None,
            "nurse_id": nurse_id,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if nurse_override:
            decision["override_type"] = "specialty_change" if final_specialty != ai_recommendation.get("specialty") else "other"
        
        logger.info(f"Triage decision logged: {decision}")
        
        return decision

