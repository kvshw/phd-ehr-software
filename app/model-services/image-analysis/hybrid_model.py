"""
Hybrid Model: Combines Rule-Based and CNN Model for Image Analysis
"""
import logging
import os
from typing import Tuple, Optional
from image_model import analyze_image as analyze_rule_image
from cnn_model import analyze_image_cnn

logger = logging.getLogger(__name__)

# Configuration
USE_CNN_MODEL = os.getenv("USE_CNN_MODEL", "true").lower() == "true"


def analyze_hybrid_image(
    image_id: str,
    image_type: str,
    image_data: Optional[bytes] = None,
    use_cnn: bool = None
) -> Tuple[float, str, Optional[str], str]:
    """
    Analyze image using hybrid approach: rules + CNN model
    
    Args:
        image_id: Image ID
        image_type: Type of image
        image_data: Image bytes (optional)
        use_cnn: Override CNN usage (None = use config)
        
    Returns:
        Tuple of (abnormality_score, classification, heatmap_url, explanation)
    """
    if use_cnn is None:
        use_cnn = USE_CNN_MODEL
    
    # Step 1: Rule-based analysis (always)
    logger.info("Performing rule-based image analysis...")
    rule_result = analyze_rule_image(image_id, image_type, image_data)
    
    # Step 2: CNN analysis (if enabled and image data available)
    cnn_result = None
    if use_cnn and image_data and image_type.lower() in ["chest_xray", "x-ray", "xray", "chest x-ray"]:
        try:
            logger.info("Performing CNN image analysis...")
            cnn_result = analyze_image_cnn(image_data, image_type)
            if cnn_result:
                logger.info(f"CNN detected: {cnn_result[1]} with {cnn_result[0]:.1%} confidence")
        except Exception as e:
            logger.warning(f"CNN analysis failed, using rules only: {str(e)}")
    
    # Step 3: Combine results
    if cnn_result:
        # Use CNN result if confidence is high, otherwise combine
        cnn_score, cnn_class, _, cnn_explanation = cnn_result
        rule_score, rule_class, _, rule_explanation = rule_result
        
        if cnn_score > 0.7:
            # High confidence CNN result - use it
            return (
                cnn_score,
                cnn_class,
                None,
                f"Hybrid analysis: CNN model detected {cnn_class} ({cnn_score:.1%} confidence). Rule-based: {rule_class} ({rule_score:.1%})."
            )
        else:
            # Combine both
            combined_score = (cnn_score * 0.6) + (rule_score * 0.4)
            combined_class = cnn_class if cnn_score > rule_score else rule_class
            
            return (
                combined_score,
                combined_class,
                None,
                f"Hybrid analysis: Combined CNN ({cnn_class}, {cnn_score:.1%}) and rule-based ({rule_class}, {rule_score:.1%}) assessments."
            )
    else:
        # Use rule-based only
        return rule_result

