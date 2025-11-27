"""
Vital Risk Model Service
Analyzes vital signs trends and produces risk assessments
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
from schemas import VitalRiskRequest, VitalRiskResponse
from risk_model import assess_vital_risk as assess_rule_risk
from hybrid_model import assess_hybrid_risk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Model version
MODEL_VERSION = "1.0.0"

app = FastAPI(
    title="Vital Risk Model Service",
    description="Service for analyzing vital signs trends and predicting patient risk",
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
        "service": "vital-risk-model",
        "status": "running",
        "version": MODEL_VERSION,
        "model_version": MODEL_VERSION
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "version": MODEL_VERSION}


@app.post("/predict", response_model=VitalRiskResponse)
async def predict_risk(request: VitalRiskRequest):
    """
    Predict patient risk based on vital signs trends.
    
    Accepts the most recent 12-hour vital trends and returns:
    - Risk level (routine, needs_attention, high_concern)
    - Risk score (0.0-1.0)
    - Top contributing features
    - Human-readable explanation
    """
    try:
        logger.info(f"Received risk prediction request for patient {request.patient_id} with {len(request.vitals)} vital readings")
        
        if not request.vitals or len(request.vitals) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one vital reading is required"
            )
        
        # Assess risk using hybrid model (rules + ML if enabled)
        import os
        use_ml = os.getenv("USE_ML_MODEL", "true").lower() == "true"
        risk_result = assess_hybrid_risk(
            request.vitals,
            patient_age=None,  # Not in request, but can be extracted if needed
            patient_sex=None,
            use_ml=use_ml
        )
        
        # Extract values from hybrid result (maintains backward compatibility)
        risk_level = risk_result.get("risk_level", "routine")
        # Map hybrid risk levels to expected format
        if risk_level == "high":
            risk_level = "high_concern"
        elif risk_level == "medium":
            risk_level = "needs_attention"
        elif risk_level == "low":
            risk_level = "routine"
        
        risk_score = risk_result.get("score", 0.0)
        explanation = risk_result.get("explanation", "")
        top_features = risk_result.get("top_features", [])
        
        response = VitalRiskResponse(
            version=MODEL_VERSION,
            risk_level=risk_level,
            score=round(risk_score, 2),
            top_features=top_features,
            explanation=explanation
        )
        
        logger.info(f"Risk prediction completed: {risk_level} (score: {risk_score:.2f}) for patient {request.patient_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing risk prediction request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing risk prediction: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

