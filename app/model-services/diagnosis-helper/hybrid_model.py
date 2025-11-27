"""
Hybrid Model: Combines Rule-Based and AI Model Suggestions
Provides best of both worlds: explainable rules + learned patterns
"""
import logging
import os
from typing import List
from schemas import Suggestion, DiagnosisSuggestionRequest
from suggestion_model import generate_suggestions as generate_rule_suggestions
from ai_model import generate_ai_suggestions

logger = logging.getLogger(__name__)

# Configuration: Enable/disable AI and set weights
USE_AI_MODEL = os.getenv("USE_AI_MODEL", "true").lower() == "true"
# Note: Weights no longer used to reduce confidence (was causing suggestions to be filtered out)
# Keeping variables for backwards compatibility but not applying them


def generate_hybrid_suggestions(
    request: DiagnosisSuggestionRequest,
    use_ai: bool = None
) -> List[Suggestion]:
    """
    Generate suggestions using hybrid approach: rules + AI model
    
    Args:
        request: Patient data request
        use_ai: Override AI usage (None = use config)
        
    Returns:
        Combined list of suggestions from rules and AI
    """
    if use_ai is None:
        use_ai = USE_AI_MODEL
    
    all_suggestions = []
    
    # Step 1: Generate rule-based suggestions (always)
    logger.info("Generating rule-based suggestions...")
    rule_suggestions = generate_rule_suggestions(request)
    logger.info(f"Generated {len(rule_suggestions)} rule-based suggestions")
    
    # Tag rule suggestions
    for suggestion in rule_suggestions:
        suggestion.source = "rules"
        all_suggestions.append(suggestion)
    
    # Step 2: Generate AI suggestions (if enabled)
    ai_suggestions = []
    if use_ai:
        try:
            logger.info("Generating AI model suggestions...")
            ai_suggestions = generate_ai_suggestions(request, max_suggestions=5)
            logger.info(f"Generated {len(ai_suggestions)} AI suggestions")
            
            # Tag AI suggestions (no confidence adjustment - keep original confidence)
            for suggestion in ai_suggestions:
                suggestion.source = "ai_model"
                # Don't reduce confidence - it causes suggestions to be filtered out in UI
        except Exception as e:
            logger.warning(f"AI model generation failed, using rules only: {str(e)}")
            ai_suggestions = []  # Ensure empty list on error
    
    # Step 3: Merge and deduplicate suggestions
    merged_suggestions = merge_suggestions(rule_suggestions, ai_suggestions)
    
    # Step 4: Sort by confidence (highest first)
    merged_suggestions.sort(key=lambda s: s.confidence or 0.0, reverse=True)
    
    logger.info(f"Hybrid model generated {len(merged_suggestions)} total suggestions")
    
    return merged_suggestions


def merge_suggestions(
    rule_suggestions: List[Suggestion],
    ai_suggestions: List[Suggestion]
) -> List[Suggestion]:
    """
    Merge rule-based and AI suggestions, removing duplicates
    
    Uses semantic similarity to identify duplicate suggestions
    """
    merged = []
    seen_texts = set()
    
    # Add rule suggestions first (higher priority)
    for suggestion in rule_suggestions:
        text_key = suggestion.text.lower().strip()[:100]  # First 100 chars as key
        if text_key not in seen_texts:
            merged.append(suggestion)
            seen_texts.add(text_key)
    
    # Add AI suggestions (avoid duplicates)
    for suggestion in ai_suggestions:
        text_key = suggestion.text.lower().strip()[:100]
        if text_key not in seen_texts:
            # Check for semantic similarity (simple keyword matching)
            is_duplicate = False
            for existing in merged:
                # Check if they mention similar concepts
                if are_similar_suggestions(suggestion.text, existing.text):
                    is_duplicate = True
                    # If AI suggestion has higher confidence, replace
                    if suggestion.confidence and existing.confidence:
                        if suggestion.confidence > existing.confidence:
                            merged.remove(existing)
                            merged.append(suggestion)
                            seen_texts.add(text_key)
                    break
            
            if not is_duplicate:
                merged.append(suggestion)
                seen_texts.add(text_key)
    
    return merged


def are_similar_suggestions(text1: str, text2: str) -> bool:
    """
    Check if two suggestions are semantically similar
    Simple keyword-based approach (can be improved with embeddings)
    """
    # Extract key medical terms
    medical_keywords = [
        "b12", "folate", "tsh", "hypothyroidism", "hypertension",
        "diabetes", "cognitive", "deficiency", "elevated", "low"
    ]
    
    text1_lower = text1.lower()
    text2_lower = text2.lower()
    
    # Count matching keywords
    matches = sum(1 for keyword in medical_keywords if keyword in text1_lower and keyword in text2_lower)
    
    # If 2+ keywords match, consider them similar
    return matches >= 2

