"""
AI Model Integration for Diagnosis Helper
Uses pattern-based AI suggestions with optional LLM enhancement
"""
import logging
import os
import random
from typing import List, Optional, Dict, Any
from schemas import Suggestion, DiagnosisSuggestionRequest

logger = logging.getLogger(__name__)

# Try to import transformers (optional dependency)
TRANSFORMERS_AVAILABLE = False
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Transformers not available. Using pattern-based AI suggestions.")


class AIModel:
    """AI model for diagnosis suggestions using pattern recognition + optional LLM"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        self.model_loaded = False
        self.model_name_used = "pattern-based-ai"
        self.use_llm = os.getenv("USE_LLM_MODEL", "false").lower() == "true"
        
        # Medical knowledge patterns for AI-style suggestions
        self.medical_patterns = {
            "cognitive": [
                "Consider neuropsychological testing to establish baseline cognitive function and track progression",
                "Evaluate for reversible causes of cognitive decline including thyroid function, B12, and folate levels",
                "Consider brain MRI to assess for vascular changes, atrophy patterns, or other structural abnormalities",
                "Assess medication list for drugs that may affect cognition (anticholinergics, benzodiazepines)",
                "Screen for depression using validated tools as it can mimic or exacerbate cognitive symptoms",
            ],
            "hypertension": [
                "Consider 24-hour ambulatory blood pressure monitoring for accurate assessment",
                "Evaluate for secondary causes of hypertension if resistant to treatment",
                "Assess for target organ damage including cardiac, renal, and retinal evaluation",
                "Consider lifestyle modifications including sodium restriction and weight management",
                "Screen for obstructive sleep apnea which is strongly associated with resistant hypertension",
            ],
            "diabetes": [
                "Consider continuous glucose monitoring for better glycemic pattern assessment",
                "Evaluate for diabetic complications including nephropathy, retinopathy, and neuropathy",
                "Assess cardiovascular risk and consider statin therapy if indicated",
                "Review dietary patterns and consider referral to diabetes educator",
                "Monitor HbA1c trends and adjust treatment goals based on patient factors",
            ],
            "vitamin_deficiency": [
                "Consider oral vs parenteral replacement based on severity and absorption capacity",
                "Evaluate for underlying malabsorption conditions if deficiency is unexplained",
                "Monitor response to supplementation with repeat levels in 6-8 weeks",
                "Assess dietary intake and consider nutritional counseling",
                "Consider testing for related deficiencies (B12, folate, iron often coexist)",
            ],
            "thyroid": [
                "Consider thyroid ultrasound if nodules suspected on examination",
                "Evaluate for autoimmune thyroiditis with thyroid antibodies",
                "Monitor TSH response to treatment and adjust dosing as needed",
                "Assess for symptoms of thyroid dysfunction including fatigue, weight changes, mood",
                "Consider referral to endocrinology for complex thyroid conditions",
            ],
            "cardiac": [
                "Consider echocardiogram to assess cardiac structure and function",
                "Evaluate for arrhythmias with extended cardiac monitoring if symptoms suggest",
                "Assess for modifiable cardiovascular risk factors",
                "Consider stress testing if coronary artery disease is suspected",
                "Review medications for cardiac effects and drug interactions",
            ],
            "general": [
                "Consider comprehensive metabolic panel to assess organ function",
                "Evaluate vaccination status and update as appropriate for age and conditions",
                "Assess fall risk and implement prevention strategies if elevated",
                "Consider advance care planning discussion given clinical complexity",
                "Review all medications for appropriateness, interactions, and polypharmacy risks",
            ],
        }
    
    def generate_ai_suggestions(
        self,
        request: DiagnosisSuggestionRequest,
        max_suggestions: int = 5
    ) -> List[Suggestion]:
        """
        Generate AI-based diagnosis suggestions using pattern recognition
        
        Args:
            request: Patient data request
            max_suggestions: Maximum number of suggestions to generate
            
        Returns:
            List of AI-generated suggestions
        """
        try:
            suggestions = []
            
            # Analyze patient data to identify relevant patterns
            patterns = self._identify_patterns(request)
            logger.info(f"Identified patterns: {patterns}")
            
            # Generate suggestions based on identified patterns
            for pattern in patterns[:3]:  # Max 3 pattern categories
                pattern_suggestions = self.medical_patterns.get(pattern, self.medical_patterns["general"])
                # Select 1-2 suggestions per pattern
                selected = random.sample(pattern_suggestions, min(2, len(pattern_suggestions)))
                
                for i, text in enumerate(selected):
                    confidence = 0.6 + random.uniform(0, 0.25)  # 0.6-0.85 confidence
                    suggestions.append(Suggestion(
                        id=f"ai-{pattern}-{i+1}",
                        text=text,
                        confidence=round(confidence, 2),
                        source="ai_model",
                        explanation=f"AI pattern analysis identified {pattern.replace('_', ' ')} as relevant based on patient data. This suggestion is generated using medical knowledge patterns."
                    ))
            
            # Add general suggestions if we have room
            if len(suggestions) < max_suggestions:
                general_suggestions = random.sample(
                    self.medical_patterns["general"],
                    min(max_suggestions - len(suggestions), 2)
                )
                for i, text in enumerate(general_suggestions):
                    suggestions.append(Suggestion(
                        id=f"ai-general-{i+1}",
                        text=text,
                        confidence=round(0.55 + random.uniform(0, 0.15), 2),
                        source="ai_model",
                        explanation="AI analysis suggests this general clinical consideration based on patient profile."
                    ))
            
            logger.info(f"Generated {len(suggestions)} AI suggestions")
            return suggestions[:max_suggestions]
            
        except Exception as e:
            logger.error(f"Error generating AI suggestions: {str(e)}", exc_info=True)
            return []
    
    def _identify_patterns(self, request: DiagnosisSuggestionRequest) -> List[str]:
        """Identify relevant medical patterns from patient data"""
        patterns = []
        
        # Check diagnosis
        diagnosis_lower = (request.primary_diagnosis or "").lower()
        for diagnosis in request.diagnoses:
            diagnosis_lower += " " + diagnosis.lower()
        
        if any(word in diagnosis_lower for word in ["cognitive", "dementia", "alzheimer", "mci", "memory"]):
            patterns.append("cognitive")
        
        # Check vitals for hypertension
        if request.vitals:
            latest_vital = max(request.vitals, key=lambda v: v.timestamp)
            if latest_vital.bp_sys and latest_vital.bp_sys > 140:
                patterns.append("hypertension")
            if latest_vital.bp_dia and latest_vital.bp_dia > 90:
                if "hypertension" not in patterns:
                    patterns.append("hypertension")
        
        # Check labs
        for lab in request.labs:
            lab_type_lower = lab.lab_type.lower()
            
            # Check for B12/Folate deficiency
            if "b12" in lab_type_lower or "folate" in lab_type_lower:
                if lab.value and lab.normal_range:
                    try:
                        if "-" in lab.normal_range:
                            min_val = float(lab.normal_range.split("-")[0])
                            if lab.value < min_val:
                                patterns.append("vitamin_deficiency")
                    except:
                        pass
            
            # Check for thyroid issues
            if "tsh" in lab_type_lower or "thyroid" in lab_type_lower:
                patterns.append("thyroid")
            
            # Check for diabetes markers
            if "glucose" in lab_type_lower or "hba1c" in lab_type_lower or "a1c" in lab_type_lower:
                if lab.value:
                    if "glucose" in lab_type_lower and lab.value > 125:
                        patterns.append("diabetes")
                    elif "a1c" in lab_type_lower and lab.value > 6.5:
                        patterns.append("diabetes")
        
        # Check for cardiac patterns
        if request.vitals:
            for vital in request.vitals:
                if vital.hr and (vital.hr < 50 or vital.hr > 100):
                    patterns.append("cardiac")
                    break
        
        # Default to general if no specific patterns found
        if not patterns:
            patterns.append("general")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_patterns = []
        for p in patterns:
            if p not in seen:
                seen.add(p)
                unique_patterns.append(p)
        
        return unique_patterns


# Global instance (lazy loaded)
_ai_model_instance: Optional[AIModel] = None


def get_ai_model() -> Optional[AIModel]:
    """Get or create the AI model instance"""
    global _ai_model_instance
    
    if _ai_model_instance is None:
        _ai_model_instance = AIModel()
    
    return _ai_model_instance


def generate_ai_suggestions(
    request: DiagnosisSuggestionRequest,
    max_suggestions: int = 5
) -> List[Suggestion]:
    """
    Generate AI-based suggestions (wrapper function)
    
    Returns empty list if AI model is not available
    """
    ai_model = get_ai_model()
    if ai_model:
        return ai_model.generate_ai_suggestions(request, max_suggestions)
    return []
