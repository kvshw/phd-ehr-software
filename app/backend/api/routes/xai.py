"""
XAI (Explainable AI) API Routes
Provides endpoints for generating and retrieving AI explanations
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from core.database import get_db
from core.dependencies import get_current_user
from services.xai_service import XAIService
from schemas.xai import (
    XAIExplanationResponse,
    XAIExplanationRequest,
    QuickXAIResponse
)
from models.suggestion import Suggestion
from sqlalchemy import text

router = APIRouter(prefix="/xai", tags=["Explainable AI"])


@router.get("/explain/{suggestion_id}", response_model=XAIExplanationResponse)
async def get_suggestion_explanation(
    suggestion_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a comprehensive XAI explanation for an AI suggestion.
    
    Returns SHAP-style feature importance, LIME-style local explanations,
    counterfactual analysis, and decision path reasoning.
    """
    # Get the suggestion
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # Generate XAI explanation
    xai_service = XAIService(db)
    explanation = xai_service.generate_explanation(
        suggestion_id=suggestion_id,
        patient_id=suggestion.patient_id,
        suggestion_type=suggestion.type,
        suggestion_text=suggestion.text,
        confidence=suggestion.confidence or 0.5
    )
    
    return explanation


@router.get("/quick/{suggestion_id}", response_model=QuickXAIResponse)
async def get_quick_explanation(
    suggestion_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a quick, summarized XAI explanation for inline display.
    
    Returns top 3 features, key insight, and brief rationale.
    """
    # Get the suggestion
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # Generate full explanation
    xai_service = XAIService(db)
    explanation = xai_service.generate_explanation(
        suggestion_id=suggestion_id,
        patient_id=suggestion.patient_id,
        suggestion_type=suggestion.type,
        suggestion_text=suggestion.text,
        confidence=suggestion.confidence or 0.5
    )
    
    # Extract quick summary
    top_features = [
        {
            "feature": f["feature"],
            "value": f["value"],
            "unit": f["unit"],
            "importance": f["importance"],
            "direction": f["direction"]
        }
        for f in explanation["feature_importance"][:3]
    ]
    
    # Generate key insight
    if top_features:
        top_feature = top_features[0]
        key_insight = f"Primary driver: {top_feature['feature']} ({top_feature['value']} {top_feature['unit']})"
    else:
        key_insight = "Multiple clinical factors contributed to this recommendation"
    
    # Confidence explanation
    confidence = suggestion.confidence or 0.5
    if confidence >= 0.8:
        confidence_explanation = f"High confidence ({confidence*100:.0f}%): Strong clinical indicators support this recommendation"
    elif confidence >= 0.6:
        confidence_explanation = f"Moderate confidence ({confidence*100:.0f}%): Multiple factors align with this suggestion"
    else:
        confidence_explanation = f"Lower confidence ({confidence*100:.0f}%): Consider additional clinical context"
    
    # Action rationale
    action_rationale = explanation.get("summary", "")[:200]
    if len(explanation.get("summary", "")) > 200:
        action_rationale += "..."
    
    return QuickXAIResponse(
        suggestion_id=str(suggestion_id),
        top_features=top_features,
        key_insight=key_insight,
        confidence_explanation=confidence_explanation,
        action_rationale=action_rationale
    )


@router.post("/explain", response_model=XAIExplanationResponse)
async def generate_explanation(
    request: XAIExplanationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generate an XAI explanation with custom options.
    
    Allows specifying which explanation components to include.
    """
    # Get the suggestion
    suggestion = db.query(Suggestion).filter(Suggestion.id == request.suggestion_id).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # Verify patient_id matches
    if suggestion.patient_id != request.patient_id:
        raise HTTPException(status_code=400, detail="Patient ID mismatch")
    
    # Generate XAI explanation
    xai_service = XAIService(db)
    explanation = xai_service.generate_explanation(
        suggestion_id=request.suggestion_id,
        patient_id=request.patient_id,
        suggestion_type=suggestion.type,
        suggestion_text=suggestion.text,
        confidence=suggestion.confidence or 0.5
    )
    
    # Filter based on request options
    if not request.include_counterfactual:
        explanation["counterfactual"] = {
            "scenario": "Not requested",
            "changes_needed": [],
            "minimum_changes": 0,
            "feasibility": "N/A",
            "clinical_note": "Counterfactual analysis was not requested"
        }
    
    if not request.include_contrastive:
        explanation["contrastive"] = {
            "question": "Not requested",
            "alternatives_considered": [],
            "distinguishing_factors": []
        }
    
    if not request.include_decision_path:
        explanation["decision_path"] = []
    
    return explanation


@router.get("/feature-importance/{patient_id}")
async def get_patient_feature_importance(
    patient_id: UUID,
    suggestion_type: Optional[str] = Query(None, description="Filter by suggestion type"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get aggregated feature importance across all suggestions for a patient.
    
    Useful for understanding which patient factors are most influential
    in AI recommendations.
    """
    xai_service = XAIService(db)
    
    # Get patient features
    patient_features = xai_service._get_patient_features(patient_id)
    
    # Calculate importance
    feature_importance = xai_service._calculate_feature_importance(
        patient_features=patient_features,
        suggestion_type=suggestion_type or "general",
        confidence=0.7  # Use average confidence
    )
    
    return {
        "patient_id": str(patient_id),
        "generated_at": datetime.utcnow().isoformat(),
        "feature_importance": feature_importance,
        "patient_summary": {
            "age": patient_features.get("demographics", {}).get("age"),
            "risk_factors": patient_features.get("risk_factors", []),
            "vitals_available": bool(patient_features.get("vitals")),
            "labs_available": bool(patient_features.get("labs"))
        }
    }


@router.get("/decision-factors/{suggestion_id}")
async def get_decision_factors(
    suggestion_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get the key decision factors for a specific suggestion.
    
    Returns a simplified view of what drove the AI's recommendation.
    """
    # Get the suggestion
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # Generate explanation
    xai_service = XAIService(db)
    explanation = xai_service.generate_explanation(
        suggestion_id=suggestion_id,
        patient_id=suggestion.patient_id,
        suggestion_type=suggestion.type,
        suggestion_text=suggestion.text,
        confidence=suggestion.confidence or 0.5
    )
    
    # Extract key decision factors
    factors = []
    for feature in explanation["feature_importance"][:5]:
        if feature["importance"] > 0.05:
            factors.append({
                "factor": feature["feature"],
                "value": f"{feature['value']} {feature['unit']}".strip(),
                "impact": "High" if feature["importance"] > 0.2 else "Moderate" if feature["importance"] > 0.1 else "Low",
                "direction": feature["direction"],
                "explanation": feature["explanation"]
            })
    
    return {
        "suggestion_id": str(suggestion_id),
        "suggestion_text": suggestion.text,
        "confidence": suggestion.confidence,
        "decision_factors": factors,
        "total_factors_analyzed": len(explanation["feature_importance"]),
        "key_insight": explanation.get("summary", "")[:300]
    }


@router.get("/comparison/{suggestion_id}")
async def get_suggestion_comparison(
    suggestion_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a comparison view showing why this suggestion vs alternatives.
    
    Useful for understanding the AI's decision-making process.
    """
    # Get the suggestion
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    # Generate explanation
    xai_service = XAIService(db)
    explanation = xai_service.generate_explanation(
        suggestion_id=suggestion_id,
        patient_id=suggestion.patient_id,
        suggestion_type=suggestion.type,
        suggestion_text=suggestion.text,
        confidence=suggestion.confidence or 0.5
    )
    
    return {
        "suggestion_id": str(suggestion_id),
        "current_suggestion": {
            "text": suggestion.text,
            "confidence": suggestion.confidence,
            "source": suggestion.source
        },
        "contrastive_analysis": explanation["contrastive"],
        "counterfactual_analysis": explanation["counterfactual"],
        "why_this_suggestion": explanation.get("summary", "")
    }

