"""
Rule-based diagnosis suggestion model
Generates clinical suggestions based on patient data with safety checks

Enhanced with evidence-based medicine for PhD-level academic rigor.
Includes citations, clinical guidelines, and GRADE evidence levels.
"""
import logging
from typing import List, Tuple, Optional, Dict, Any
from schemas import (
    VitalReading,
    LabResult,
    Suggestion,
    DiagnosisSuggestionRequest
)

# Import medical evidence database
try:
    from medical_evidence import (
        get_evidence,
        get_evidence_dict,
        find_evidence_for_suggestion,
        EVIDENCE_DATABASE
    )
    EVIDENCE_AVAILABLE = True
except ImportError:
    EVIDENCE_AVAILABLE = False

logger = logging.getLogger(__name__)


def add_evidence_to_suggestion(suggestion: Suggestion, evidence_key: str) -> Suggestion:
    """
    Enhance a suggestion with medical evidence from the evidence database.
    This adds PhD-level academic rigor to AI explanations.
    """
    if not EVIDENCE_AVAILABLE:
        return suggestion
    
    evidence = get_evidence(evidence_key)
    if not evidence:
        return suggestion
    
    # Add evidence fields to suggestion
    suggestion.evidence_level = evidence.evidence_level.value
    suggestion.recommendation_strength = evidence.recommendation_strength.value
    suggestion.mechanism = evidence.mechanism
    suggestion.clinical_pearl = evidence.clinical_pearl
    suggestion.limitations = evidence.limitations
    suggestion.guidelines = [g.to_dict() for g in evidence.guidelines]
    suggestion.citations = [c.to_dict() for c in evidence.citations]
    
    # Enhance explanation with evidence summary
    enhanced_explanation = suggestion.explanation
    enhanced_explanation += f"\n\n**Evidence Level:** {evidence.evidence_level.value} (GRADE)"
    enhanced_explanation += f"\n**Recommendation Strength:** {evidence.recommendation_strength.value}"
    if evidence.guidelines:
        enhanced_explanation += f"\n**Guidelines:** {evidence.guidelines[0].organization} ({evidence.guidelines[0].year})"
    if evidence.citations:
        enhanced_explanation += f"\n**Key Citation:** {evidence.citations[0].authors} ({evidence.citations[0].year})"
    suggestion.explanation = enhanced_explanation
    
    return suggestion

# Prescriptive words/phrases to avoid
PRESCRIPTIVE_PATTERNS = [
    "you should",
    "you must",
    "you need to",
    "you have to",
    "prescribe",
    "give",
    "administer",
    "order",
    "start",
    "begin",
    "initiate",
]


def check_prescriptive_language(text: str) -> bool:
    """Check if text contains prescriptive language"""
    text_lower = text.lower()
    return any(pattern in text_lower for pattern in PRESCRIPTIVE_PATTERNS)


def sanitize_suggestion_text(text: str) -> str:
    """Remove prescriptive language from suggestion text"""
    # Replace prescriptive patterns with non-prescriptive alternatives
    replacements = {
        "you should": "consider",
        "you must": "may want to",
        "you need to": "consider",
        "you have to": "may want to",
        "prescribe": "consider",
        "give": "consider",
        "administer": "consider",
        "order": "consider",
        "start": "consider",
        "begin": "consider",
        "initiate": "consider",
    }
    
    text_lower = text.lower()
    for pattern, replacement in replacements.items():
        if pattern in text_lower:
            # Simple replacement - in production, use more sophisticated NLP
            text = text.replace(pattern, replacement)
            text = text.replace(pattern.capitalize(), replacement.capitalize())
    
    return text


def generate_suggestions(request: DiagnosisSuggestionRequest) -> List[Suggestion]:
    """
    Generate diagnosis suggestions based on patient data.
    
    Uses rule-based logic to identify potential clinical considerations.
    All suggestions are non-prescriptive and include explanations.
    """
    suggestions = []
    suggestion_id_counter = 1
    
    # Get most recent vital signs
    latest_vitals = None
    if request.vitals:
        sorted_vitals = sorted(request.vitals, key=lambda v: v.timestamp, reverse=True)
        latest_vitals = sorted_vitals[0]
    
    # Rule 1: Post-operative infection (fever + elevated WBC or CRP)
    if latest_vitals and latest_vitals.temp and latest_vitals.temp > 38.0:
        # Check for post-operative context or elevated inflammatory markers
        has_inflammatory_marker = False
        for lab in request.labs:
            if lab.lab_type.lower() in ["wbc", "white blood cell", "crp", "c-reactive protein"]:
                if lab.value and lab.value > (get_normal_max(lab.normal_range) if lab.normal_range else 0):
                    has_inflammatory_marker = True
                    break
        
        if has_inflammatory_marker or "post" in (request.primary_diagnosis or "").lower():
            suggestion_text = "Post-operative fever with elevated inflammatory markers may indicate infection."
            if check_prescriptive_language(suggestion_text):
                suggestion_text = sanitize_suggestion_text(suggestion_text)
            
            suggestions.append(Suggestion(
                id=f"dx-postop-infection-{suggestion_id_counter}",
                text=suggestion_text,
                confidence=0.7,
                source="rules",
                explanation=f"Triggered due to fever ({latest_vitals.temp:.1f}°C) and elevated inflammatory markers."
            ))
            suggestion_id_counter += 1
    
    # Rule 2: Sepsis risk (low BP + high HR + elevated WBC)
    if latest_vitals:
        sepsis_indicators = 0
        sepsis_details = []
        
        if latest_vitals.bp_sys and latest_vitals.bp_sys < 90:
            sepsis_indicators += 1
            sepsis_details.append(f"low BP ({latest_vitals.bp_sys} mmHg)")
        
        if latest_vitals.hr and latest_vitals.hr > 100:
            sepsis_indicators += 1
            sepsis_details.append(f"elevated HR ({latest_vitals.hr} bpm)")
        
        for lab in request.labs:
            if lab.lab_type.lower() in ["wbc", "white blood cell"]:
                if lab.value and lab.value > 12.0:  # Elevated WBC
                    sepsis_indicators += 1
                    sepsis_details.append(f"elevated WBC ({lab.value:.1f})")
                    break
        
        if sepsis_indicators >= 2:
            suggestion_text = "Combination of hypotension, tachycardia, and elevated WBC may suggest sepsis risk."
            if check_prescriptive_language(suggestion_text):
                suggestion_text = sanitize_suggestion_text(suggestion_text)
            
            suggestions.append(Suggestion(
                id=f"dx-sepsis-risk-{suggestion_id_counter}",
                text=suggestion_text,
                confidence=0.65,
                source="rules",
                explanation=f"Triggered by: {', '.join(sepsis_details)}."
            ))
            suggestion_id_counter += 1
    
    # Rule 3: Dehydration (elevated creatinine/BUN, low BP, high HR)
    if latest_vitals:
        dehydration_indicators = 0
        dehydration_details = []
        
        if latest_vitals.bp_sys and latest_vitals.bp_sys < 100:
            dehydration_indicators += 1
            dehydration_details.append("low BP")
        
        if latest_vitals.hr and latest_vitals.hr > 90:
            dehydration_indicators += 1
            dehydration_details.append("elevated HR")
        
        for lab in request.labs:
            if lab.lab_type.lower() in ["creatinine", "bun", "urea"]:
                if lab.value and lab.value > (get_normal_max(lab.normal_range) if lab.normal_range else 0):
                    dehydration_indicators += 1
                    dehydration_details.append(f"elevated {lab.lab_type}")
                    break
        
        if dehydration_indicators >= 2:
            suggestion_text = "Signs consistent with possible dehydration: elevated creatinine/BUN with hypotension and tachycardia."
            if check_prescriptive_language(suggestion_text):
                suggestion_text = sanitize_suggestion_text(suggestion_text)
            
            suggestions.append(Suggestion(
                id=f"dx-dehydration-{suggestion_id_counter}",
                text=suggestion_text,
                confidence=0.6,
                source="rules",
                explanation=f"Triggered by: {', '.join(dehydration_details)}."
            ))
            suggestion_id_counter += 1
    
    # Rule 4: Acute kidney injury (elevated creatinine, decreased urine output if available)
    for lab in request.labs:
        if lab.lab_type.lower() == "creatinine":
            if lab.value and lab.value > 1.5:  # Elevated creatinine
                suggestion_text = "Elevated creatinine may indicate acute kidney injury. Consider monitoring renal function."
                if check_prescriptive_language(suggestion_text):
                    suggestion_text = sanitize_suggestion_text(suggestion_text)
                
                suggestions.append(Suggestion(
                    id=f"dx-aki-{suggestion_id_counter}",
                    text=suggestion_text,
                    confidence=0.55,
                    source="rules",
                    explanation=f"Triggered by elevated creatinine ({lab.value:.2f} mg/dL)."
                ))
                suggestion_id_counter += 1
            break
    
    # Rule 5: Anemia (low hemoglobin)
    for lab in request.labs:
        if lab.lab_type.lower() in ["hemoglobin", "hgb", "hb"]:
            if lab.value and lab.value < 12.0:  # Low hemoglobin (general threshold)
                suggestion_text = "Low hemoglobin may indicate anemia. Further evaluation may be warranted."
                if check_prescriptive_language(suggestion_text):
                    suggestion_text = sanitize_suggestion_text(suggestion_text)
                
                suggestions.append(Suggestion(
                    id=f"dx-anemia-{suggestion_id_counter}",
                    text=suggestion_text,
                    confidence=0.6,
                    source="rules",
                    explanation=f"Triggered by low hemoglobin ({lab.value:.1f} g/dL)."
                ))
                suggestion_id_counter += 1
            break
    
    # Rule 6: Hypoxia risk (low SpO2)
    if latest_vitals and latest_vitals.spo2 and latest_vitals.spo2 < 95:
        suggestion_text = "Low oxygen saturation may indicate respiratory compromise. Consider monitoring oxygen levels."
        if check_prescriptive_language(suggestion_text):
            suggestion_text = sanitize_suggestion_text(suggestion_text)
        
        suggestions.append(Suggestion(
            id=f"dx-hypoxia-risk-{suggestion_id_counter}",
            text=suggestion_text,
            confidence=0.7,
            source="rules",
            explanation=f"Triggered by low SpO2 ({latest_vitals.spo2:.1f}%)."
        ))
        suggestion_id_counter += 1
    
    # Rule 7: Diabetes monitoring (elevated glucose or HbA1c)
    for lab in request.labs:
        if lab.lab_type.lower() in ["glucose", "blood glucose", "hba1c", "hemoglobin a1c"]:
            is_elevated = False
            if lab.lab_type.lower() in ["glucose", "blood glucose"]:
                is_elevated = lab.value and lab.value > 140  # Elevated glucose
            elif lab.lab_type.lower() in ["hba1c", "hemoglobin a1c"]:
                is_elevated = lab.value and lab.value > 6.5  # Elevated HbA1c
            
            if is_elevated:
                suggestion_text = "Elevated glucose or HbA1c may indicate diabetes or poor glycemic control."
                if check_prescriptive_language(suggestion_text):
                    suggestion_text = sanitize_suggestion_text(suggestion_text)
                
                suggestions.append(Suggestion(
                    id=f"dx-diabetes-{suggestion_id_counter}",
                    text=suggestion_text,
                    confidence=0.65,
                    source="rules",
                    explanation=f"Triggered by elevated {lab.lab_type} ({lab.value:.1f})."
                ))
                suggestion_id_counter += 1
            break
    
    # Rule 8: B12/Folate Deficiency (brain health - cognitive decline)
    # Evidence: Level A (High) - Multiple RCTs and meta-analyses support B12-cognition link
    for lab in request.labs:
        if lab.lab_type.upper() == "B12":
            if lab.value and lab.value < 200:  # Low B12
                suggestion_text = "Low B12 levels may contribute to cognitive decline. B12 deficiency can cause reversible dementia-like symptoms."
                if check_prescriptive_language(suggestion_text):
                    suggestion_text = sanitize_suggestion_text(suggestion_text)
                
                suggestion = Suggestion(
                    id=f"dx-b12-deficiency-{suggestion_id_counter}",
                    text=suggestion_text,
                    confidence=0.80,  # High confidence - strong evidence
                    source="rules",
                    explanation=f"Triggered by low B12 ({lab.value:.0f} pg/mL, normal: 200-900). B12 deficiency is a reversible cause of cognitive impairment."
                )
                # Add evidence-based enhancement
                suggestion = add_evidence_to_suggestion(suggestion, "b12_cognitive")
                suggestions.append(suggestion)
                suggestion_id_counter += 1
                break
    
    # Rule 8b: Folate deficiency - Evidence Level B (Moderate)
    for lab in request.labs:
        if lab.lab_type.lower() in ["folate", "folic acid"]:
            if lab.value and lab.normal_range and ">" in lab.normal_range:
                # For ">3.0" format, check if value is below threshold
                threshold = float(lab.normal_range.replace(">", "").strip())
                if lab.value < threshold:
                    suggestion_text = "Low folate levels may contribute to cognitive decline and should be addressed."
                    if check_prescriptive_language(suggestion_text):
                        suggestion_text = sanitize_suggestion_text(suggestion_text)
                    
                    suggestion = Suggestion(
                        id=f"dx-folate-deficiency-{suggestion_id_counter}",
                        text=suggestion_text,
                        confidence=0.75,
                        source="rules",
                        explanation=f"Triggered by low folate ({lab.value:.1f} ng/mL, normal: >{threshold}). Folate deficiency can affect cognitive function."
                    )
                    suggestion = add_evidence_to_suggestion(suggestion, "folate_cognitive")
                    suggestions.append(suggestion)
                    suggestion_id_counter += 1
                    break
    
    # Rule 9: Hypothyroidism (elevated TSH - brain health)
    # Evidence: Level A (High) - ATA and AACE guidelines with multiple RCTs
    for lab in request.labs:
        if lab.lab_type.upper() == "TSH":
            if lab.value and lab.normal_range:
                normal_max = get_normal_max(lab.normal_range)
                if normal_max > 0 and lab.value > normal_max:
                    suggestion_text = "Elevated TSH may indicate hypothyroidism, which can cause cognitive symptoms including memory problems and slowed thinking."
                    if check_prescriptive_language(suggestion_text):
                        suggestion_text = sanitize_suggestion_text(suggestion_text)
                    
                    suggestion = Suggestion(
                        id=f"dx-hypothyroidism-{suggestion_id_counter}",
                        text=suggestion_text,
                        confidence=0.80,  # High confidence - strong evidence
                        source="rules",
                        explanation=f"Triggered by elevated TSH ({lab.value:.1f} mIU/L, normal: {lab.normal_range}). Hypothyroidism is a reversible cause of cognitive impairment."
                    )
                    suggestion = add_evidence_to_suggestion(suggestion, "tsh_cognitive")
                    suggestions.append(suggestion)
                    suggestion_id_counter += 1
                    break
    
    # Rule 10: Hypertension (elevated BP - brain health)
    # Evidence: Level A (High) - SPRINT-MIND trial, AHA Scientific Statement
    if latest_vitals and latest_vitals.bp_sys and latest_vitals.bp_sys >= 140:
        suggestion_text = "Elevated blood pressure may contribute to cognitive decline and vascular dementia risk. Blood pressure control is important for brain health."
        if check_prescriptive_language(suggestion_text):
            suggestion_text = sanitize_suggestion_text(suggestion_text)
        
        suggestion = Suggestion(
            id=f"dx-hypertension-{suggestion_id_counter}",
            text=suggestion_text,
            confidence=0.80,  # High confidence - SPRINT-MIND evidence
            source="rules",
            explanation=f"Triggered by elevated systolic BP ({latest_vitals.bp_sys}/{latest_vitals.bp_dia or 'N/A'} mmHg). Hypertension is a risk factor for cognitive decline."
        )
        suggestion = add_evidence_to_suggestion(suggestion, "hypertension_cognitive")
        suggestions.append(suggestion)
        suggestion_id_counter += 1
    
    # Rule 11: Diabetes and Cognitive Decline
    # Evidence: Level A (High) - NEJM study, Nature Reviews, ADA Guidelines
    for lab in request.labs:
        if lab.lab_type.lower() in ["hba1c", "hemoglobin a1c"]:
            if lab.value and lab.value > 6.5:  # Elevated HbA1c
                suggestion_text = "Elevated HbA1c indicates poor diabetes control, which is associated with increased risk of cognitive decline and dementia."
                if check_prescriptive_language(suggestion_text):
                    suggestion_text = sanitize_suggestion_text(suggestion_text)
                
                suggestion = Suggestion(
                    id=f"dx-diabetes-cognitive-{suggestion_id_counter}",
                    text=suggestion_text,
                    confidence=0.80,  # High confidence - strong evidence
                    source="rules",
                    explanation=f"Triggered by elevated HbA1c ({lab.value:.1f}%). Poor glycemic control is linked to cognitive impairment."
                )
                suggestion = add_evidence_to_suggestion(suggestion, "diabetes_cognitive")
                suggestions.append(suggestion)
                suggestion_id_counter += 1
                break
    
    # Rule 12: Medication Cognitive Side Effects
    # Note: This would require medication data, which isn't in the current request schema
    # But we can check for cognitive-related diagnoses
    if request.primary_diagnosis and any(term in request.primary_diagnosis.lower() for term in ["cognitive", "dementia", "alzheimer", "mci", "mild cognitive"]):
        # Check for reversible causes
        has_reversible_cause = False
        reversible_details = []
        
        for lab in request.labs:
            if lab.lab_type.upper() == "B12" and lab.value and lab.value < 200:
                has_reversible_cause = True
                reversible_details.append("B12 deficiency")
            elif lab.lab_type.lower() in ["folate", "folic acid"] and lab.value:
                if lab.normal_range and ">" in lab.normal_range:
                    threshold = float(lab.normal_range.replace(">", "").strip())
                    if lab.value < threshold:
                        has_reversible_cause = True
                        reversible_details.append("Folate deficiency")
            elif lab.lab_type.upper() == "TSH" and lab.value and lab.normal_range:
                normal_max = get_normal_max(lab.normal_range)
                if normal_max > 0 and lab.value > normal_max:
                    has_reversible_cause = True
                    reversible_details.append("Hypothyroidism")
        
        if has_reversible_cause:
            suggestion_text = f"Patient with cognitive impairment has potentially reversible causes identified: {', '.join(reversible_details)}. Addressing these may improve cognitive function."
            if check_prescriptive_language(suggestion_text):
                suggestion_text = sanitize_suggestion_text(suggestion_text)
            
            suggestion = Suggestion(
                id=f"dx-reversible-cognitive-{suggestion_id_counter}",
                text=suggestion_text,
                confidence=0.85,  # Very high - critical for patient care
                source="rules",
                explanation=f"Triggered by cognitive diagnosis with reversible causes: {', '.join(reversible_details)}."
            )
            suggestion = add_evidence_to_suggestion(suggestion, "reversible_cognitive")
            suggestions.append(suggestion)
            suggestion_id_counter += 1
    
    # Safety check: Remove any suggestions that still contain prescriptive language
    safe_suggestions = []
    for suggestion in suggestions:
        if check_prescriptive_language(suggestion.text):
            logger.warning(f"Removed prescriptive suggestion: {suggestion.text}")
            continue
        safe_suggestions.append(suggestion)
    
    logger.info(f"Generated {len(safe_suggestions)} diagnosis suggestions for patient {request.patient_id}")
    
    return safe_suggestions


def get_normal_max(normal_range: Optional[str]) -> float:
    """Extract maximum value from normal range string (e.g., '70-100' -> 100.0)"""
    if not normal_range:
        return 0.0
    
    try:
        # Try to parse range like "70-100" or "70.0-100.0"
        parts = normal_range.replace(" ", "").split("-")
        if len(parts) == 2:
            return float(parts[1])
    except (ValueError, IndexError):
        pass
    
    return 0.0

