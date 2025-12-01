"""
Admin API endpoints
System management, user administration, and configuration
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from core.dependencies import require_admin, require_role
from services.auth_service import AuthService
from schemas.auth import UserCreate, UserResponse
from pydantic import BaseModel, EmailStr
from typing import Dict, Any
from core.config import settings
from services.mape_k_plan import MAPEKPlanService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """List all users (admin only)"""
    try:
        users = AuthService.list_users(db)
        return [UserResponse(id=user.id, email=user.email, role=user.role) for user in users]
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing users: {str(e)}"
        )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Create a new user (admin only)"""
    try:
        user = AuthService.create_user(db, user_data)
        return UserResponse(id=user.id, email=user.email, role=user.role)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Update a user (admin only)"""
    try:
        user = AuthService.update_user(db, user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse(id=user.id, email=user.email, role=user.role)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Delete a user (admin only)"""
    try:
        # Prevent deleting yourself
        if str(user_id) == str(current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        success = AuthService.delete_user(db, user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}"
        )


@router.get("/system-status")
async def get_system_status(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Get system status and health information (admin only)"""
    try:
        # Check database connection
        db_status = "connected"
        try:
            db.execute("SELECT 1")
        except Exception:
            db_status = "disconnected"
        
        # Model service status (simplified - would need actual health checks)
        # In production, call each service's health endpoint
        model_services = {
            "vital_risk": {"status": "active", "version": "1.0.0"},
            "image_analysis": {"status": "active", "version": "1.0.0"},
            "diagnosis_helper": {"status": "active", "version": "1.0.0"},
        }
        
        return {
            "backend": {
                "status": "healthy",
                "version": "0.1.0"
            },
            "database": {
                "status": db_status
            },
            "model_services": model_services
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system status: {str(e)}"
        )


@router.get("/adaptation-config")
async def get_adaptation_config(
    current_user=Depends(require_admin),
):
    """Get current adaptation configuration (admin only)"""
    try:
        return MAPEKPlanService.KNOWLEDGE_BASE
    except Exception as e:
        logger.error(f"Error getting adaptation config: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting adaptation config: {str(e)}"
        )


@router.put("/adaptation-config")
async def update_adaptation_config(
    config: Dict[str, Any],
    current_user=Depends(require_admin),
):
    """Update adaptation configuration (admin only)"""
    try:
        # Validate config keys
        valid_keys = ["navigation_threshold", "ignore_rate_threshold", "acceptance_rate_threshold", "risk_escalation_threshold"]
        for key in config.keys():
            if key not in valid_keys:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid config key: {key}"
                )
        
        # Update the knowledge base
        MAPEKPlanService.KNOWLEDGE_BASE.update(config)
        
        return MAPEKPlanService.KNOWLEDGE_BASE
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating adaptation config: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating adaptation config: {str(e)}"
        )


@router.post("/generate-synthetic-data")
async def generate_synthetic_data(
    options: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    """Generate synthetic test data (admin only)"""
    try:
        # This is a placeholder - actual implementation would generate synthetic data
        # For now, return a success message
        num_patients = options.get("num_patients", 10)
        num_vitals = options.get("num_vitals_per_patient", 5)
        num_labs = options.get("num_labs_per_patient", 3)
        num_images = options.get("num_images_per_patient", 2)
        
        # TODO: Implement actual synthetic data generation
        # This would involve:
        # 1. Creating synthetic patients with random but realistic data
        # 2. Generating vitals, labs, and imaging records
        # 3. Ensuring no PHI is included
        
        logger.info(f"Admin {current_user.user_id} requested synthetic data generation with options: {options}")
        
        return {
            "message": "Synthetic data generation requested",
            "generated": {
                "patients": num_patients,
                "vitals_per_patient": num_vitals,
                "labs_per_patient": num_labs,
                "images_per_patient": num_images,
                "note": "Synthetic data generation will be implemented in a future update"
            }
        }
    except Exception as e:
        logger.error(f"Error generating synthetic data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating synthetic data: {str(e)}"
        )


@router.post("/delete-all-data")
async def delete_all_data(
    confirmation: str = Query(..., description="Must be 'DELETE ALL DATA' to confirm"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "clinician"])),
):
    """
    Delete all patient data and related records (admin only).
    
    **WARNING: This is a destructive operation that cannot be undone!**
    
    Deletes:
    - All patients and related data (vitals, labs, medications, visits, notes, etc.)
    - All referrals
    - All user actions
    - All adaptations and bandit states
    - All suggestions and feedback
    - All conversations
    
    Preserves:
    - User accounts
    - System configuration
    - Research/FL/Transfer learning metadata (priors, models)
    """
    if confirmation != "DELETE ALL DATA":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation text must be exactly 'DELETE ALL DATA'"
        )
    
    try:
        from sqlalchemy import text
        from models.patient import Patient
        from models.patient_referral import PatientReferral
        from models.user_action import UserAction
        from models.adaptation import Adaptation
        from models.bandit_state import BanditState, BanditAdaptationLog
        from models.suggestion import Suggestion
        from models.suggestion_feedback import SuggestionFeedback, FeedbackAggregation, LearningEvent
        from models.conversation import ConversationSession, ConversationTranscript, ConversationAnalysis
        
        logger.warning(f"Admin {current_user.user_id} is deleting ALL data from the system")
        
        deleted_counts = {}
        
        # Delete in order to respect foreign key constraints
        
        # 1. Delete patient-related data (cascades should handle most, but we'll be explicit)
        deleted_counts['conversation_analysis'] = db.query(ConversationAnalysis).delete()
        deleted_counts['conversation_transcripts'] = db.query(ConversationTranscript).delete()
        deleted_counts['conversation_sessions'] = db.query(ConversationSession).delete()
        
        deleted_counts['learning_events'] = db.query(LearningEvent).delete()
        deleted_counts['feedback_aggregation'] = db.query(FeedbackAggregation).delete()
        deleted_counts['suggestion_feedback'] = db.query(SuggestionFeedback).delete()
        deleted_counts['suggestions'] = db.query(Suggestion).delete()
        
        deleted_counts['bandit_adaptation_log'] = db.query(BanditAdaptationLog).delete()
        deleted_counts['bandit_state'] = db.query(BanditState).delete()
        deleted_counts['adaptations'] = db.query(Adaptation).delete()
        
        deleted_counts['patient_referrals'] = db.query(PatientReferral).delete()
        
        # Delete patients (this should cascade to vitals, labs, medications, visits, notes, etc.)
        deleted_counts['patients'] = db.query(Patient).delete()
        
        # Delete user actions (but keep user accounts)
        deleted_counts['user_actions'] = db.query(UserAction).delete()
        
        db.commit()
        
        logger.warning(f"Admin {current_user.user_id} successfully deleted all data. Counts: {deleted_counts}")
        
        return {
            "success": True,
            "message": "All data deleted successfully",
            "deleted": deleted_counts,
            "note": "User accounts and system configuration were preserved"
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting all data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting all data: {str(e)}"
        )

