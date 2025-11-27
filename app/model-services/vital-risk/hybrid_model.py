"""
Hybrid Model: Combines Rule-Based and ML Model for Vital Risk Assessment
"""
import logging
import os
from typing import Dict, Any, Optional
from risk_model import assess_vital_risk as assess_rule_risk
from ml_model import predict_ml_risk

logger = logging.getLogger(__name__)

# Configuration
USE_ML_MODEL = os.getenv("USE_ML_MODEL", "true").lower() == "true"
RULE_WEIGHT = float(os.getenv("VITAL_RULE_WEIGHT", "0.5"))  # 50% weight for rules
ML_WEIGHT = float(os.getenv("VITAL_ML_WEIGHT", "0.5"))  # 50% weight for ML


def assess_hybrid_risk(
    vitals_data: list,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None,
    use_ml: bool = None
) -> Dict[str, Any]:
    """
    Assess vital risk using hybrid approach: rules + ML model
    
    Args:
        vitals_data: List of vital readings
        patient_age: Patient age
        patient_sex: Patient sex
        use_ml: Override ML usage (None = use config)
        
    Returns:
        Combined risk assessment
    """
    if use_ml is None:
        use_ml = USE_ML_MODEL
    
    # Step 1: Rule-based risk (always)
    logger.info("Assessing rule-based risk...")
    rule_result = assess_rule_risk(vitals_data)  # Returns tuple: (risk_level, score, top_features, explanation)
    rule_risk = {
        "risk_level": rule_result[0],
        "score": rule_result[1],
        "top_features": rule_result[2],
        "explanation": rule_result[3]
    }
    logger.info(f"Rule-based risk: {rule_risk.get('risk_level', 'unknown')}")
    
    # Step 2: ML model risk (if enabled)
    ml_risk = None
    if use_ml:
        try:
            logger.info("Assessing ML model risk...")
            ml_risk = predict_ml_risk(vitals_data, patient_age, patient_sex)
            if ml_risk:
                logger.info(f"ML model risk: {ml_risk.get('risk_level', 'unknown')}")
        except Exception as e:
            logger.warning(f"ML model assessment failed, using rules only: {str(e)}")
    
    # Step 3: Combine risks
    if ml_risk:
        # Weighted combination
        rule_score = rule_risk.get('score', 0.0) * RULE_WEIGHT
        ml_score = ml_risk.get('score', 0.0) * ML_WEIGHT
        combined_score = rule_score + ml_score
        
        # Determine combined risk level
        if combined_score >= 0.7:
            risk_level = "high"
        elif combined_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Combine explanations
        explanation = f"Hybrid assessment: Rule-based ({rule_risk.get('risk_level', 'unknown')}, score: {rule_risk.get('score', 0):.2f}) + ML model ({ml_risk.get('risk_level', 'unknown')}, score: {ml_risk.get('score', 0):.2f}) = {risk_level} risk (combined score: {combined_score:.2f})"
        
        return {
            "risk_level": risk_level,
            "score": combined_score,
            "top_features": rule_risk.get("top_features", []),
            "explanation": explanation,
            "source": "hybrid",
            "rule_based": rule_risk,
            "ml_model": ml_risk
        }
    else:
        # Use rule-based only
        rule_risk["source"] = "rules"
        return rule_risk

