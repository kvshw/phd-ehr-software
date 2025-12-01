"""
Referral API routes for patient referrals between nurses and doctors.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from core.database import get_db
from core.dependencies import get_current_user
from services.referral_service import ReferralService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/referrals", tags=["referrals"])


class CreateReferralRequest(BaseModel):
    """Request to create a patient referral."""
    patient_id: str
    target_specialty: str
    priority: str = "standard"
    chief_complaint: Optional[str] = None
    symptoms: Optional[List[str]] = None
    vitals: Optional[Dict[str, Any]] = None
    triage_notes: Optional[str] = None
    ai_suggested_specialty: Optional[str] = None
    ai_confidence: Optional[float] = None
    nurse_override: bool = False


class UpdateReferralStatusRequest(BaseModel):
    """Request to update referral status."""
    status: str  # pending, accepted, in_progress, completed, cancelled
    notes: Optional[str] = None


@router.post("/create")
async def create_referral(
    request: CreateReferralRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a patient referral (Nurse → Doctor).
    
    Used by nurses to send patients to specific specialties/doctors.
    """
    try:
        # Validate patient_id is a valid UUID
        try:
            patient_uuid = UUID(request.patient_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid patient ID format: {request.patient_id}. Must be a valid UUID."
            )
        
        # Verify patient exists
        from models.patient import Patient
        patient = db.query(Patient).filter(Patient.id == patient_uuid).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {request.patient_id} not found"
            )
        
        referral = ReferralService.create_referral(
            db=db,
            patient_id=patient_uuid,
            referred_by_id=current_user.user_id,
            target_specialty=request.target_specialty,
            priority=request.priority,
            chief_complaint=request.chief_complaint,
            symptoms=request.symptoms,
            vitals=request.vitals,
            triage_notes=request.triage_notes,
            ai_suggested_specialty=request.ai_suggested_specialty,
            ai_confidence=request.ai_confidence,
            nurse_override=request.nurse_override,
        )
        
        return {
            "success": True,
            "message": f"Patient referred to {request.target_specialty}",
            "referral": referral,
        }
    except HTTPException:
        raise
    except ValueError as e:
        error_msg = str(e)
        if "table does not exist" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except Exception as e:
        logger.error(f"Error creating referral: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating referral: {str(e)}"
        )


@router.get("/doctor/queue")
async def get_doctor_referral_queue(
    specialty: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get referral queue for a doctor's dashboard.
    
    Shows patients referred to their specialty or directly to them.
    """
    try:
        # Get user's specialty from database if not provided
        if not specialty:
            from models.user import User
            user = db.query(User).filter(User.id == current_user.user_id).first()
            specialty = user.specialty if user else "general"
        
        referrals = ReferralService.get_referrals_for_doctor(
            db=db,
            doctor_id=current_user.user_id,
            specialty=specialty,
            status=status_filter,
        )
        
        return {
            "referrals": referrals,
            "specialty": specialty,
            "count": len(referrals),
        }
    except Exception as e:
        logger.error(f"Error fetching doctor queue: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching referrals: {str(e)}"
        )


@router.get("/nurse/sent")
async def get_nurse_sent_referrals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get referrals sent by the current nurse.
    
    Shows history of patients the nurse has referred.
    """
    try:
        referrals = ReferralService.get_nurse_referrals(
            db=db,
            nurse_id=current_user.user_id,
        )
        
        return {
            "referrals": referrals,
            "count": len(referrals),
        }
    except Exception as e:
        logger.error(f"Error fetching nurse referrals: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching referrals: {str(e)}"
        )


@router.put("/{referral_id}/status")
async def update_referral_status(
    referral_id: str,
    request: UpdateReferralStatusRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update referral status (Doctor action).
    
    Doctors use this to accept, complete, or cancel referrals.
    """
    try:
        valid_statuses = ["pending", "accepted", "in_progress", "completed", "cancelled", "transferred"]
        if request.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
            )
        
        referral = ReferralService.update_referral_status(
            db=db,
            referral_id=UUID(referral_id),
            new_status=request.status,
            updated_by_id=current_user.user_id,
            notes=request.notes,
        )
        
        if not referral:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Referral not found"
            )
        
        return {
            "success": True,
            "message": f"Referral status updated to {request.status}",
            "referral": referral,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating referral status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating referral: {str(e)}"
        )


@router.get("/admin/overview")
async def get_admin_referral_overview(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get anonymized referral overview for admin dashboard.
    
    Shows statistics and anonymized referral data for oversight.
    Patient names and direct identifiers are removed.
    """
    try:
        # Verify admin or researcher role
        from models.user import User
        user = db.query(User).filter(User.id == current_user.user_id).first()
        if user.role not in ["admin", "researcher"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin or researcher access required"
            )
        
        overview = ReferralService.get_referrals_for_admin_anonymized(
            db=db,
            days=days,
        )
        
        return {
            "success": True,
            "overview": overview,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching admin overview: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching overview: {str(e)}"
        )


@router.get("/specialty/{specialty}/available-doctors")
async def get_available_doctors(
    specialty: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get list of doctors available in a specialty.
    
    Used by nurses to see which doctors are available for referrals.
    """
    try:
        from models.user import User
        
        doctors = db.query(User).filter(
            User.specialty == specialty,
            User.role.in_(["clinician", "doctor"]),
        ).all()
        
        return {
            "specialty": specialty,
            "doctors": [
                {
                    "id": str(doc.id),
                    "name": f"{doc.title or 'Dr.'} {doc.first_name or ''} {doc.last_name or doc.email.split('@')[0]}".strip(),
                    "department": doc.department,
                }
                for doc in doctors
            ],
            "count": len(doctors),
        }
    except Exception as e:
        logger.error(f"Error fetching doctors: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching doctors: {str(e)}"
        )

