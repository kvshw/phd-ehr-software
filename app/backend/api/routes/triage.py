"""
Triage API routes for patient categorization and routing.

This module provides endpoints for:
- AI-powered symptom analysis and specialty recommendations
- Priority assessment
- Triage queue management
- Nurse override logging
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from core.database import get_db
from core.dependencies import get_current_user
from services.triage_service import TriageService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/triage", tags=["triage"])


class SymptomAnalysisRequest(BaseModel):
    """Request model for symptom analysis"""
    symptoms: List[str]
    chief_complaint: Optional[str] = ""
    vitals: Optional[Dict[str, Any]] = None
    patient_age: Optional[int] = None


class SymptomAnalysisResponse(BaseModel):
    """Response model for symptom analysis"""
    specialty: str
    specialty_confidence: float
    alternative_specialties: Dict[str, float]
    priority: str
    matched_symptoms: List[str]
    explanation: str
    ai_disclaimer: str
    timestamp: str


class TriageDecisionRequest(BaseModel):
    """Request model for logging triage decisions"""
    patient_id: str
    ai_recommendation: Dict[str, Any]
    final_specialty: str
    nurse_override: bool
    notes: Optional[str] = None


class TriageDecisionResponse(BaseModel):
    """Response model for triage decision logging"""
    success: bool
    message: str
    decision: Dict[str, Any]


@router.post("/analyze", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(
    request: SymptomAnalysisRequest,
    current_user=Depends(get_current_user),
):
    """
    Analyze patient symptoms and provide specialty recommendation.
    
    This endpoint uses AI to analyze symptoms and suggest the most appropriate
    medical specialty. The recommendation includes a confidence score and
    alternative options.
    
    **Important**: This is an AI-assisted recommendation. Final triage decisions
    should always be made by qualified healthcare staff.
    """
    try:
        recommendation = TriageService.get_triage_recommendation(
            symptoms=request.symptoms,
            chief_complaint=request.chief_complaint or "",
            vitals=request.vitals,
            patient_age=request.patient_age,
        )
        
        return SymptomAnalysisResponse(**recommendation)
    
    except Exception as e:
        logger.error(f"Error analyzing symptoms: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing symptoms: {str(e)}"
        )


@router.post("/decide", response_model=TriageDecisionResponse)
async def log_triage_decision(
    request: TriageDecisionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Log a triage decision for audit and ML improvement.
    
    This endpoint logs whether the nurse accepted the AI suggestion or overrode it.
    This data is used to improve the AI recommendation system over time.
    """
    try:
        decision = TriageService.log_triage_decision(
            patient_id=request.patient_id,
            ai_recommendation=request.ai_recommendation,
            final_specialty=request.final_specialty,
            nurse_override=request.nurse_override,
            nurse_id=str(current_user.user_id),
            notes=request.notes,
        )
        
        return TriageDecisionResponse(
            success=True,
            message="Triage decision logged successfully",
            decision=decision,
        )
    
    except Exception as e:
        logger.error(f"Error logging triage decision: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging decision: {str(e)}"
        )


@router.get("/specialties")
async def get_specialties(
    current_user=Depends(get_current_user),
):
    """
    Get list of available medical specialties for triage routing.
    """
    specialties = [
        {"id": "cardiology", "name": "Cardiology", "icon": "❤️", "description": "Heart and cardiovascular conditions"},
        {"id": "neurology", "name": "Neurology", "icon": "🧠", "description": "Brain, spine, and nervous system"},
        {"id": "orthopedics", "name": "Orthopedics", "icon": "🦴", "description": "Bones, joints, and musculoskeletal"},
        {"id": "pediatrics", "name": "Pediatrics", "icon": "👶", "description": "Children and adolescent care"},
        {"id": "psychiatry", "name": "Psychiatry", "icon": "🧘", "description": "Mental health and behavioral"},
        {"id": "emergency", "name": "Emergency Medicine", "icon": "🚑", "description": "Acute and urgent care"},
        {"id": "internal", "name": "Internal Medicine", "icon": "🩺", "description": "Adult general medicine"},
        {"id": "surgery", "name": "Surgery", "icon": "⚕️", "description": "Surgical procedures"},
        {"id": "dermatology", "name": "Dermatology", "icon": "🔬", "description": "Skin conditions"},
        {"id": "oncology", "name": "Oncology", "icon": "🎗️", "description": "Cancer treatment"},
        {"id": "general", "name": "General Practice", "icon": "👨‍⚕️", "description": "Primary care"},
    ]
    
    return {"specialties": specialties}


@router.get("/priorities")
async def get_priorities(
    current_user=Depends(get_current_user),
):
    """
    Get list of triage priority levels with descriptions.
    """
    priorities = [
        {
            "id": "critical",
            "name": "Critical",
            "color": "red",
            "description": "Immediate life-threatening conditions requiring immediate intervention",
            "target_wait_time": "0 min",
        },
        {
            "id": "urgent",
            "name": "Urgent",
            "color": "orange",
            "description": "Serious conditions requiring prompt attention",
            "target_wait_time": "15 min",
        },
        {
            "id": "standard",
            "name": "Standard",
            "color": "yellow",
            "description": "Conditions requiring assessment but not immediately life-threatening",
            "target_wait_time": "60 min",
        },
        {
            "id": "non_urgent",
            "name": "Non-Urgent",
            "color": "green",
            "description": "Minor conditions that can wait",
            "target_wait_time": "120 min",
        },
    ]
    
    return {"priorities": priorities}


@router.get("/symptoms")
async def get_symptom_keywords(
    current_user=Depends(get_current_user),
):
    """
    Get list of recognized symptom keywords for triage input.
    """
    symptoms = list(TriageService.SYMPTOM_SPECIALTY_MAP.keys())
    
    # Group by category
    categories = {
        "Cardiovascular": ["chest_pain", "palpitations", "shortness_of_breath", "dyspnea", "edema", "syncope"],
        "Neurological": ["headache", "migraine", "seizure", "dizziness", "numbness", "vision_changes", "weakness", "confusion"],
        "Musculoskeletal": ["fracture", "joint_pain", "back_pain", "arm_pain", "leg_pain", "swelling", "limited_mobility"],
        "Pediatric": ["fever_child", "ear_pain", "rash_child", "cough_child", "irritability"],
        "Psychiatric": ["anxiety", "depression", "panic_attacks", "insomnia", "mood_changes", "hallucinations"],
        "Emergency": ["trauma", "severe_bleeding", "unconscious", "difficulty_breathing", "high_fever"],
        "General": ["fatigue", "weight_loss", "nausea", "abdominal_pain", "diabetes_symptoms"],
        "Dermatological": ["rash", "skin_lesion", "itching"],
        "Oncological": ["lump", "unexplained_weight_loss", "night_sweats"],
    }
    
    return {"symptoms": symptoms, "categories": categories}


@router.get("/patient/{patient_id}", response_model=SymptomAnalysisResponse)
async def get_patient_triage_suggestion(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get AI triage suggestion for a specific patient using their real data.
    
    This endpoint:
    - Extracts symptoms from patient's clinical notes and visits
    - Gets recent vitals
    - Gets chief complaint from most recent visit
    - Returns AI-powered specialty recommendation
    
    Used by nurses to get AI suggestions before creating referrals.
    """
    try:
        from models.patient import Patient
        from models.visit import Visit
        from models.clinical_note import ClinicalNote
        from services.vital_service import VitalService
        from sqlalchemy import desc
        
        # Get patient
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found"
            )
        
        # Get most recent visit for chief complaint
        recent_visit = db.query(Visit).filter(
            Visit.patient_id == patient_id
        ).order_by(desc(Visit.visit_date)).first()
        
        chief_complaint = recent_visit.chief_complaint if recent_visit else None
        
        # Extract symptoms from clinical notes (last 3 notes)
        recent_notes = db.query(ClinicalNote).filter(
            ClinicalNote.patient_id == patient_id
        ).order_by(desc(ClinicalNote.created_at)).limit(3).all()
        
        symptoms = []
        symptom_text = ""
        
        # Extract from notes
        for note in recent_notes:
            if note.chief_complaint:
                symptom_text += " " + note.chief_complaint.lower()
            if note.subjective:
                symptom_text += " " + note.subjective.lower()
            if note.assessment:
                symptom_text += " " + note.assessment.lower()
        
        # Also add chief complaint from visit
        if chief_complaint:
            symptom_text += " " + chief_complaint.lower()
        
        # Match symptom keywords
        symptom_text_lower = symptom_text.lower()
        for symptom_key in TriageService.SYMPTOM_SPECIALTY_MAP.keys():
            symptom_words = symptom_key.replace("_", " ")
            if symptom_words in symptom_text_lower or symptom_key in symptom_text_lower:
                if symptom_key not in symptoms:
                    symptoms.append(symptom_key)
        
        # If no symptoms found, try to extract from primary diagnosis
        if not symptoms and patient.primary_diagnosis:
            diagnosis_lower = patient.primary_diagnosis.lower()
            for symptom_key in TriageService.SYMPTOM_SPECIALTY_MAP.keys():
                symptom_words = symptom_key.replace("_", " ")
                if symptom_words in diagnosis_lower:
                    if symptom_key not in symptoms:
                        symptoms.append(symptom_key)
        
        # Get most recent vitals
        recent_vitals_list = VitalService.get_recent_vitals(db, patient_id, hours=24)
        vitals = None
        if recent_vitals_list and len(recent_vitals_list) > 0:
            latest_vital = recent_vitals_list[0]  # Most recent first
            vitals = {
                "hr": latest_vital.hr,
                "bp": f"{latest_vital.bp_sys}/{latest_vital.bp_dia}" if latest_vital.bp_sys and latest_vital.bp_dia else None,
                "spo2": latest_vital.spo2,
                "temp": latest_vital.temp,
                "rr": latest_vital.rr,
            }
        
        # If no symptoms found and no chief complaint, use primary diagnosis or default to general
        if not symptoms and not chief_complaint:
            # Try to extract from primary diagnosis
            if patient.primary_diagnosis:
                chief_complaint = patient.primary_diagnosis
                # Try to match symptoms from diagnosis text
                diagnosis_lower = patient.primary_diagnosis.lower()
                for symptom_key in TriageService.SYMPTOM_SPECIALTY_MAP.keys():
                    symptom_words = symptom_key.replace("_", " ")
                    if symptom_words in diagnosis_lower:
                        if symptom_key not in symptoms:
                            symptoms.append(symptom_key)
        
        # Get AI triage recommendation
        recommendation = TriageService.get_triage_recommendation(
            symptoms=symptoms if symptoms else [],  # Ensure it's a list
            chief_complaint=chief_complaint or "",
            vitals=vitals,
            patient_age=patient.age,
        )
        
        logger.info(f"AI triage suggestion for patient {patient_id}: {recommendation.get('specialty')} (confidence: {recommendation.get('specialty_confidence')})")
        
        return SymptomAnalysisResponse(**recommendation)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient triage suggestion: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting patient triage suggestion: {str(e)}"
        )

