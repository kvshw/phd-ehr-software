"""
Diagnosis Helper Service
Provides rule-based clinical suggestions with explanations
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
from schemas import DiagnosisSuggestionRequest, DiagnosisSuggestionResponse
from suggestion_model import generate_suggestions as generate_rule_suggestions
from hybrid_model import generate_hybrid_suggestions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model version
MODEL_VERSION = "1.0.0"

app = FastAPI(
    title="Diagnosis Helper Service",
    description="Service for generating rule-based clinical diagnosis suggestions with explanations",
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
        "service": "diagnosis-helper-model",
        "status": "running",
        "version": MODEL_VERSION,
        "model_version": MODEL_VERSION
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": MODEL_VERSION}


@app.post("/suggest", response_model=DiagnosisSuggestionResponse)
async def suggest_diagnosis(request: DiagnosisSuggestionRequest):
    """
    Generate diagnosis suggestions based on patient data.
    
    Accepts patient data including vitals, labs, and diagnoses, and returns:
    - List of suggestions with:
      - Suggestion text (non-prescriptive)
      - Confidence score (0.0-1.0)
      - Source (e.g., 'rules', 'vital_risk', 'lab_analysis')
      - Human-readable explanation
    
    All suggestions are non-prescriptive and include clear explanations.
    Safety checks prevent prescriptive language.
    """
    try:
        logger.info(
            f"Received diagnosis suggestion request for patient {request.patient_id} "
            f"with {len(request.vitals)} vitals, {len(request.labs)} labs, "
            f"{len(request.diagnoses)} diagnoses"
        )
        
        # Validate input
        if not request.vitals and not request.labs and not request.diagnoses:
            logger.warning(f"No patient data provided for patient {request.patient_id}")
            return DiagnosisSuggestionResponse(
                version=MODEL_VERSION,
                suggestions=[]
            )
        
        # Generate suggestions using hybrid model (rules + AI if enabled)
        use_ai = os.getenv("USE_AI_MODEL", "true").lower() == "true"
        suggestions = generate_hybrid_suggestions(request, use_ai=use_ai)
        
        response = DiagnosisSuggestionResponse(
            version=MODEL_VERSION,
            suggestions=suggestions
        )
        
        logger.info(
            f"Generated {len(suggestions)} suggestions for patient {request.patient_id}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing diagnosis suggestion request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing diagnosis suggestions: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
