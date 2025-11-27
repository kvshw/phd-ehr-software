"""
AI Service Routing endpoints
Routes requests to appropriate AI model services and stores outputs in database
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from core.database import get_db
from core.dependencies import get_current_user, require_role
from services.ai_service import ai_service_client
from services.suggestion_service import SuggestionService
from services.vital_service import VitalService
from services.lab_service import LabService
from services.patient_service import PatientService
from services.user_action_service import UserActionService
from schemas.suggestion import SuggestionCreate, SuggestionResponse, SuggestionListResponse
from schemas.user_action import UserActionCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/vitals-risk")
async def predict_vital_risk(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Predict patient risk based on vital signs trends.
    Routes to vital risk model service and stores result in database.
    """
    try:
        # Get recent vitals (last 12 hours)
        recent_vitals = VitalService.get_recent_vitals(db, patient_id, hours=12)
        
        if not recent_vitals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No vital signs data available for the last 12 hours"
            )
        
        # Convert to format expected by vital risk service
        vitals_data = [
            {
                "timestamp": v.timestamp.isoformat(),
                "hr": v.hr,
                "bp_sys": v.bp_sys,
                "bp_dia": v.bp_dia,
                "spo2": v.spo2,
                "rr": v.rr,
                "temp": v.temp,
                "pain": v.pain,
            }
            for v in recent_vitals
        ]
        
        # Call vital risk service
        risk_response = await ai_service_client.predict_vital_risk(
            str(patient_id),
            vitals_data
        )
        
        if not risk_response:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vital risk service is unavailable"
            )
        
        # Store suggestion in database
        suggestion = SuggestionService.create_suggestion(
            db,
            SuggestionCreate(
                patient_id=patient_id,
                type="vital_risk",
                text=f"Vital risk assessment: {risk_response.get('risk_level', 'unknown')} risk (score: {risk_response.get('score', 0):.2f})",
                source="vital_risk_model",
                explanation=risk_response.get("explanation", "Risk assessment based on vital signs trends"),
                confidence=risk_response.get("score", 0.0)
            )
        )
        
        # Log model output for MAPE-K monitoring
        UserActionService.create_action(
            db,
            UserActionCreate(
                user_id=current_user.user_id,
                patient_id=patient_id,
                action_type="model_output",
                action_metadata={
                    "model_type": "vital_risk",
                    "model_version": risk_response.get("version", "1.0.0"),
                    "output_data": risk_response,
                    "patient_id": str(patient_id)
                }
            )
        )
        
        return {
            **risk_response,
            "suggestion_id": str(suggestion.id),
            "stored_at": suggestion.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in vital risk prediction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing vital risk prediction: {str(e)}"
        )


@router.post("/image-analysis")
async def analyze_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Analyze a medical image for abnormalities.
    Routes to image analysis model service and stores result in database.
    """
    try:
        # Get image metadata to determine type and patient_id
        from services.imaging_service import ImagingService
        imaging = ImagingService.get_imaging_by_id(db, image_id)
        
        if not imaging:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Call image analysis service
        analysis_response = await ai_service_client.analyze_image(
            str(image_id),
            imaging.type
        )
        
        if not analysis_response:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Image analysis service is unavailable"
            )
        
        # Store suggestion in database
        classification = analysis_response.get("classification", "unknown")
        abnormality_score = analysis_response.get("abnormality_score", 0.0)
        
        suggestion = SuggestionService.create_suggestion(
            db,
            SuggestionCreate(
                patient_id=imaging.patient_id,
                type="image_analysis",
                text=f"Image analysis: {classification} findings (abnormality score: {abnormality_score:.2f})",
                source="image_analysis_model",
                explanation=analysis_response.get("explanation", "Image analysis completed"),
                confidence=abnormality_score
            )
        )
        
        # Log model output for MAPE-K monitoring
        UserActionService.create_action(
            db,
            UserActionCreate(
                user_id=current_user.user_id,
                patient_id=imaging.patient_id,
                action_type="model_output",
                action_metadata={
                    "model_type": "image_analysis",
                    "model_version": analysis_response.get("version", "1.0.0"),
                    "output_data": analysis_response,
                    "patient_id": str(imaging.patient_id)
                }
            )
        )
        
        return {
            **analysis_response,
            "suggestion_id": str(suggestion.id),
            "stored_at": suggestion.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in image analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image analysis: {str(e)}"
        )


@router.post("/diagnosis-helper")
async def suggest_diagnosis(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Generate diagnosis suggestions based on patient data.
    Routes to diagnosis helper service and stores results in database.
    """
    try:
        # Get patient data
        patient = PatientService.get_patient_by_id(db, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Get recent vitals (last 12 hours)
        recent_vitals = VitalService.get_recent_vitals(db, patient_id, hours=12)
        vitals_data = [
            {
                "timestamp": v.timestamp.isoformat(),
                "hr": v.hr,
                "bp_sys": v.bp_sys,
                "bp_dia": v.bp_dia,
                "spo2": v.spo2,
                "rr": v.rr,
                "temp": v.temp,
                "pain": v.pain,
            }
            for v in recent_vitals
        ]
        
        # Get recent labs
        from schemas.lab import LabFilterParams
        labs, _ = LabService.get_labs_by_patient_id(
            db,
            patient_id,
            filter_params=LabFilterParams(page=1, page_size=50)  # Get up to 50 recent labs
        )
        labs_data = [
            {
                "timestamp": lab.timestamp.isoformat(),
                "lab_type": lab.lab_type,
                "value": lab.value,
                "normal_range": lab.normal_range,
            }
            for lab in labs
        ]
        
        # Prepare patient data for diagnosis helper
        patient_data = {
            "age": patient.age,
            "sex": patient.sex,
            "primary_diagnosis": patient.primary_diagnosis,
            "vitals": vitals_data,
            "labs": labs_data,
            "diagnoses": [patient.primary_diagnosis] if patient.primary_diagnosis else []
        }
        
        # Call diagnosis helper service
        suggestions_response = await ai_service_client.suggest_diagnosis(
            str(patient_id),
            patient_data
        )
        
        if not suggestions_response:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Diagnosis helper service is unavailable"
            )
        
        # Store all suggestions in database
        stored_suggestions = []
        for suggestion_data in suggestions_response.get("suggestions", []):
            suggestion = SuggestionService.create_suggestion(
                db,
                SuggestionCreate(
                    patient_id=patient_id,
                    type="diagnosis",
                    text=suggestion_data.get("text", ""),
                    source=suggestion_data.get("source", "rules"),
                    explanation=suggestion_data.get("explanation", ""),
                    confidence=suggestion_data.get("confidence")
                )
            )
            stored_suggestions.append(suggestion)
        
        # Log model output for MAPE-K monitoring
        UserActionService.create_action(
            db,
            UserActionCreate(
                user_id=current_user.user_id,
                patient_id=patient_id,
                action_type="model_output",
                action_metadata={
                    "model_type": "diagnosis_helper",
                    "model_version": suggestions_response.get("version", "1.0.0"),
                    "output_data": suggestions_response,
                    "patient_id": str(patient_id)
                }
            )
        )
        
        return {
            "version": suggestions_response.get("version", "1.0.0"),
            "suggestions": [
                {
                    "id": suggestion_data.get("id", ""),
                    "text": suggestion_data.get("text", ""),
                    "confidence": suggestion_data.get("confidence"),
                    "source": suggestion_data.get("source", "rules"),
                    "explanation": suggestion_data.get("explanation", ""),
                    "suggestion_id": str(s.id),
                    "stored_at": s.created_at.isoformat()
                }
                for suggestion_data, s in zip(
                    suggestions_response.get("suggestions", []),
                    stored_suggestions
                )
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in diagnosis suggestion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing diagnosis suggestions: {str(e)}"
        )


@router.get("/suggestions/{patient_id}", response_model=SuggestionListResponse)
async def get_patient_suggestions(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Get all AI-generated suggestions for a patient.
    """
    suggestions, total = SuggestionService.get_suggestions_by_patient_id(db, patient_id)
    return SuggestionListResponse(
        items=[SuggestionResponse.model_validate(s) for s in suggestions],
        total=total,
        patient_id=patient_id
    )

