"""
Rule-based risk assessment model for vital signs
"""
from typing import List, Tuple
from schemas import VitalReading
import logging

logger = logging.getLogger(__name__)

# Normal ranges for vital signs
NORMAL_RANGES = {
    'hr': (60, 100),  # Heart rate (bpm)
    'bp_sys': (90, 140),  # Systolic BP (mmHg)
    'bp_dia': (60, 90),  # Diastolic BP (mmHg)
    'spo2': (95, 100),  # Oxygen saturation (%)
    'rr': (12, 20),  # Respiratory rate (breaths/min)
    'temp': (36.1, 37.2),  # Temperature (Celsius)
    'pain': (0, 3),  # Pain scale (0-10, but 0-3 is normal)
}

# Critical thresholds
CRITICAL_THRESHOLDS = {
    'hr': (40, 130),  # Critical HR range
    'bp_sys': (70, 180),  # Critical BP range
    'spo2': (90, 100),  # Critical SpO2 range
    'rr': (8, 30),  # Critical RR range
    'temp': (35.0, 38.5),  # Critical temp range
}


def assess_vital_risk(vitals: List[VitalReading]) -> Tuple[str, float, List[str], str]:
    """
    Assess risk based on vital signs trends.
    
    Returns:
        Tuple of (risk_level, score, top_features, explanation)
    """
    if not vitals or len(vitals) == 0:
        return "routine", 0.0, [], "No vital signs data available"
    
    # Sort by timestamp (most recent first)
    sorted_vitals = sorted(vitals, key=lambda v: v.timestamp, reverse=True)
    latest = sorted_vitals[0]
    
    risk_factors = []
    risk_score = 0.0
    
    # Analyze each vital sign
    # Heart Rate
    if latest.hr is not None:
        if latest.hr < CRITICAL_THRESHOLDS['hr'][0] or latest.hr > CRITICAL_THRESHOLDS['hr'][1]:
            risk_factors.append("heart_rate_critical")
            risk_score += 0.4
        elif latest.hr < NORMAL_RANGES['hr'][0] or latest.hr > NORMAL_RANGES['hr'][1]:
            risk_factors.append("heart_rate_abnormal")
            risk_score += 0.2
        
        # Check for trends (if we have multiple readings)
        if len(sorted_vitals) >= 2:
            prev_hr = sorted_vitals[1].hr
            if prev_hr is not None:
                hr_change = latest.hr - prev_hr
                if hr_change > 20:
                    risk_factors.append("heart_rate_increasing")
                    risk_score += 0.15
                elif hr_change < -20:
                    risk_factors.append("heart_rate_decreasing")
                    risk_score += 0.15
    
    # Blood Pressure
    if latest.bp_sys is not None:
        if latest.bp_sys < CRITICAL_THRESHOLDS['bp_sys'][0]:
            risk_factors.append("bp_low")
            risk_score += 0.3
        elif latest.bp_sys > CRITICAL_THRESHOLDS['bp_sys'][1]:
            risk_factors.append("bp_high")
            risk_score += 0.25
        elif latest.bp_sys < NORMAL_RANGES['bp_sys'][0] or latest.bp_sys > NORMAL_RANGES['bp_sys'][1]:
            risk_factors.append("bp_abnormal")
            risk_score += 0.15
        
        # Check for trends
        if len(sorted_vitals) >= 2:
            prev_bp = sorted_vitals[1].bp_sys
            if prev_bp is not None:
                bp_change = latest.bp_sys - prev_bp
                if bp_change < -20:
                    risk_factors.append("bp_falling")
                    risk_score += 0.2
                elif bp_change > 20:
                    risk_factors.append("bp_rising")
                    risk_score += 0.15
    
    # Oxygen Saturation
    if latest.spo2 is not None:
        if latest.spo2 < CRITICAL_THRESHOLDS['spo2'][0]:
            risk_factors.append("spo2_low")
            risk_score += 0.35
        elif latest.spo2 < NORMAL_RANGES['spo2'][0]:
            risk_factors.append("spo2_abnormal")
            risk_score += 0.2
    
    # Respiratory Rate
    if latest.rr is not None:
        if latest.rr < CRITICAL_THRESHOLDS['rr'][0] or latest.rr > CRITICAL_THRESHOLDS['rr'][1]:
            risk_factors.append("respiratory_rate_critical")
            risk_score += 0.3
        elif latest.rr < NORMAL_RANGES['rr'][0] or latest.rr > NORMAL_RANGES['rr'][1]:
            risk_factors.append("respiratory_rate_abnormal")
            risk_score += 0.15
    
    # Temperature
    if latest.temp is not None:
        if latest.temp < CRITICAL_THRESHOLDS['temp'][0] or latest.temp > CRITICAL_THRESHOLDS['temp'][1]:
            risk_factors.append("temperature_critical")
            risk_score += 0.25
        elif latest.temp < NORMAL_RANGES['temp'][0] or latest.temp > NORMAL_RANGES['temp'][1]:
            risk_factors.append("temperature_abnormal")
            risk_score += 0.15
    
    # Pain
    if latest.pain is not None and latest.pain > NORMAL_RANGES['pain'][1]:
        risk_factors.append("high_pain")
        risk_score += 0.1
    
    # Cap risk score at 1.0
    risk_score = min(risk_score, 1.0)
    
    # Determine risk level
    if risk_score >= 0.7:
        risk_level = "high_concern"
    elif risk_score >= 0.4:
        risk_level = "needs_attention"
    else:
        risk_level = "routine"
    
    # Generate explanation
    explanation_parts = []
    if "heart_rate_critical" in risk_factors:
        explanation_parts.append(f"Critical heart rate ({latest.hr} bpm)")
    if "bp_low" in risk_factors:
        explanation_parts.append(f"Low blood pressure ({latest.bp_sys}/{latest.bp_dia} mmHg)")
    if "bp_high" in risk_factors:
        explanation_parts.append(f"High blood pressure ({latest.bp_sys}/{latest.bp_dia} mmHg)")
    if "spo2_low" in risk_factors:
        explanation_parts.append(f"Low oxygen saturation ({latest.spo2}%)")
    if "heart_rate_increasing" in risk_factors:
        explanation_parts.append("Rising heart rate")
    if "bp_falling" in risk_factors:
        explanation_parts.append("Falling blood pressure")
    
    if explanation_parts:
        explanation = " → ".join(explanation_parts) + " → " + risk_level.replace("_", " ").title() + " risk."
    else:
        explanation = "All vital signs within normal ranges. Routine monitoring recommended."
    
    # Get top 3 features
    top_features = risk_factors[:3] if len(risk_factors) > 0 else []
    
    logger.info(f"Risk assessment: {risk_level} (score: {risk_score:.2f}), features: {top_features}")
    
    return risk_level, risk_score, top_features, explanation

