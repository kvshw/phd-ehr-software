"""
Image Analysis Model Service
Processes medical images and produces abnormality assessments with heatmaps
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
from schemas import ImageAnalysisRequest, ImageAnalysisResponse
from image_model import analyze_image as analyze_rule_image
from hybrid_model import analyze_hybrid_image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model version
MODEL_VERSION = "1.0.0"

app = FastAPI(
    title="Image Analysis Model Service",
    description="Service for analyzing medical images and producing abnormality assessments",
    version=MODEL_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Service information endpoint"""
    return {
        "service": "image-analysis-model",
        "status": "running",
        "version": MODEL_VERSION,
        "model_version": MODEL_VERSION
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": MODEL_VERSION}


@app.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze(request: ImageAnalysisRequest):
    """
    Analyze a medical image and produce abnormality assessment.
    
    Accepts image ID and type (X-ray/MRI/CT) and returns:
    - Abnormality score (0.0-1.0)
    - Classification (normal/suspicious/abnormal)
    - Heatmap URL (if abnormalities detected)
    - Human-readable explanation
    """
    try:
        logger.info(
            f"Received image analysis request for image {request.image_id} "
            f"(type: {request.image_type})"
        )
        
        # Validate image type
        valid_types = ["X-ray", "MRI", "CT", "x-ray", "mri", "ct"]
        if request.image_type not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Must be one of: {', '.join(valid_types)}"
            )
        
        # In a production system, we would:
        # 1. Fetch the image from object storage using image_id
        # 2. Load and preprocess the image
        # 3. Run through ML model (e.g., CNN)
        # 4. Generate heatmap highlighting areas of interest
        # 5. Return results
        
        # Use hybrid model (rules + CNN if enabled)
        # TODO: Integrate with backend to fetch actual image data when needed
        import os
        use_cnn = os.getenv("USE_CNN_MODEL", "true").lower() == "true"
        abnormality_score, classification, heatmap_url, explanation = analyze_hybrid_image(
            request.image_id,
            request.image_type,
            image_data=None,  # Would be fetched from storage in production
            use_cnn=use_cnn
        )
        
        response = ImageAnalysisResponse(
            version=MODEL_VERSION,
            abnormality_score=round(abnormality_score, 2),
            classification=classification,
            heatmap_url=heatmap_url,
            explanation=explanation
        )
        
        logger.info(
            f"Image analysis completed: {classification} (score: {abnormality_score:.2f}) "
            f"for image {request.image_id}"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image analysis request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image analysis: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
