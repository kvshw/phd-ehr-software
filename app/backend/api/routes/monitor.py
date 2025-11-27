"""
MAPE-K Monitor Component API endpoints
Collects user behavior and system data for adaptation engine
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel

from core.database import get_db
from core.dependencies import get_current_user, require_role
from services.user_action_service import UserActionService
from schemas.user_action import (
    UserActionCreate,
    UserActionResponse,
    NavigationActionMetadata,
    SuggestionActionMetadata,
    RiskChangeMetadata,
    ModelOutputMetadata
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitor", tags=["monitor"])


@router.post("/log-action", response_model=UserActionResponse, status_code=status.HTTP_201_CREATED)
async def log_action(
    action_data: UserActionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),  # All authenticated users can log actions
):
    """
    Log a user action for MAPE-K monitoring.
    
    Action types:
    - "navigation": User navigation between sections
    - "suggestion_action": User interaction with suggestions (accept/ignore/not_relevant)
    - "risk_change": Patient risk level changes
    - "model_output": AI model outputs captured for analysis
    
    All logged data must not contain PHI or identifiable information.
    """
    try:
        # Ensure user_id matches current user (security check)
        if str(action_data.user_id) != str(current_user.user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot log actions for other users"
            )
        
        # Validate metadata based on action type
        if action_data.action_metadata:
            if action_data.action_type == "navigation":
                # Validate navigation metadata
                NavigationActionMetadata(**action_data.action_metadata)
            elif action_data.action_type == "suggestion_action":
                # Validate suggestion action metadata
                SuggestionActionMetadata(**action_data.action_metadata)
            elif action_data.action_type == "risk_change":
                # Validate risk change metadata
                RiskChangeMetadata(**action_data.action_metadata)
            elif action_data.action_type == "model_output":
                # Validate model output metadata
                ModelOutputMetadata(**action_data.action_metadata)
        
        # Create action log
        action = UserActionService.create_action(db, action_data)
        
        logger.info(f"Logged {action_data.action_type} action for user {current_user.user_id}")
        
        return UserActionResponse.model_validate(action)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging user action: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging action: {str(e)}"
        )


class LogNavigationRequest(BaseModel):
    """Request schema for logging navigation"""
    patient_id: Optional[UUID] = None
    from_section: Optional[str] = None
    to_section: str


class LogSuggestionActionRequest(BaseModel):
    """Request schema for logging suggestion action"""
    suggestion_id: str
    action: str  # "accept", "ignore", "not_relevant"
    suggestion_type: Optional[str] = None
    suggestion_source: Optional[str] = None
    patient_id: Optional[UUID] = None


class LogRiskChangeRequest(BaseModel):
    """Request schema for logging risk change"""
    patient_id: UUID
    new_risk_level: str
    previous_risk_level: Optional[str] = None
    risk_score: Optional[float] = None


class LogModelOutputRequest(BaseModel):
    """Request schema for logging model output"""
    model_type: str
    model_version: str
    output_data: Dict[str, Any]
    patient_id: Optional[UUID] = None


@router.post("/log-navigation")
async def log_navigation(
    request: LogNavigationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Log user navigation between sections.
    Convenience endpoint for navigation tracking.
    """
    action_metadata = {
        "from_section": request.from_section,
        "to_section": request.to_section,
        "patient_id": str(request.patient_id) if request.patient_id else None
    }
    
    action_data = UserActionCreate(
        user_id=current_user.user_id,
        patient_id=request.patient_id,
        action_type="navigation",
        action_metadata=action_metadata
    )
    
    action = UserActionService.create_action(db, action_data)
    return UserActionResponse.model_validate(action)


@router.post("/log-suggestion-action")
async def log_suggestion_action(
    request: LogSuggestionActionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Log user interaction with a suggestion.
    Convenience endpoint for suggestion action tracking.
    """
    if request.action not in ["accept", "ignore", "not_relevant"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be one of: 'accept', 'ignore', 'not_relevant'"
        )
    
    action_metadata = {
        "suggestion_id": request.suggestion_id,
        "action": request.action,
        "suggestion_type": request.suggestion_type,
        "suggestion_source": request.suggestion_source
    }
    
    action_data = UserActionCreate(
        user_id=current_user.user_id,
        patient_id=request.patient_id,
        action_type="suggestion_action",
        action_metadata=action_metadata
    )
    
    action = UserActionService.create_action(db, action_data)
    return UserActionResponse.model_validate(action)


@router.post("/log-risk-change")
async def log_risk_change(
    request: LogRiskChangeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Log patient risk level change.
    Typically called automatically when risk assessments are updated.
    """
    action_metadata = {
        "previous_risk_level": request.previous_risk_level,
        "new_risk_level": request.new_risk_level,
        "risk_score": request.risk_score,
        "patient_id": str(request.patient_id)
    }
    
    action_data = UserActionCreate(
        user_id=current_user.user_id,
        patient_id=request.patient_id,
        action_type="risk_change",
        action_metadata=action_metadata
    )
    
    action = UserActionService.create_action(db, action_data)
    return UserActionResponse.model_validate(action)


@router.post("/log-model-output")
async def log_model_output(
    request: LogModelOutputRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Log AI model output for analysis.
    Typically called automatically when model services return results.
    """
    action_metadata = {
        "model_type": request.model_type,
        "model_version": request.model_version,
        "output_data": request.output_data,
        "patient_id": str(request.patient_id) if request.patient_id else None
    }
    
    action_data = UserActionCreate(
        user_id=current_user.user_id,
        patient_id=request.patient_id,
        action_type="model_output",
        action_metadata=action_metadata
    )
    
    action = UserActionService.create_action(db, action_data)
    return UserActionResponse.model_validate(action)


@router.get("/navigation-patterns")
async def get_navigation_patterns(
    patient_id: Optional[UUID] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),  # Only researchers and admins can view patterns
):
    """
    Get navigation patterns for the current user.
    Used by MAPE-K Analyze component.
    """
    patterns = UserActionService.get_navigation_patterns(
        db,
        current_user.user_id,
        patient_id=patient_id,
        days=days
    )
    return {"patterns": patterns, "user_id": str(current_user.user_id)}


@router.get("/suggestion-actions")
async def get_suggestion_actions(
    patient_id: Optional[UUID] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Get suggestion accept/ignore actions.
    Used by MAPE-K Analyze component.
    """
    actions = UserActionService.get_suggestion_actions(
        db,
        user_id=current_user.user_id,
        patient_id=patient_id,
        days=days
    )
    return {"actions": actions}


@router.get("/risk-changes/{patient_id}")
async def get_risk_changes(
    patient_id: UUID,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Get risk change events for a patient.
    Used by MAPE-K Analyze component.
    """
    changes = UserActionService.get_risk_changes(
        db,
        patient_id=patient_id,
        days=days
    )
    return {"risk_changes": changes, "patient_id": str(patient_id)}


@router.get("/model-outputs")
async def get_model_outputs(
    patient_id: Optional[UUID] = None,
    model_type: Optional[str] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Get captured model outputs.
    Used by MAPE-K Analyze component and researcher dashboard.
    """
    outputs = UserActionService.get_model_outputs(
        db,
        patient_id=patient_id,
        model_type=model_type,
        days=days
    )
    return {"outputs": outputs}


@router.post("/dashboard-action", status_code=status.HTTP_201_CREATED)
async def log_dashboard_action(
    action_type: str,  # 'quick_action_click', 'feature_access', 'navigation', etc.
    feature_id: str,   # 'ecg_review', 'bp_trends', etc.
    metadata: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Log dashboard-specific user actions for MAPE-K monitoring.
    
    Action types:
    - quick_action_click: User clicked a quick action button
    - feature_access: User accessed a feature (via menu, search, etc.)
    - navigation: User navigated between dashboard sections
    - patient_card_click: User opened a patient from dashboard
    - search_query: User performed a search
    - filter_applied: User applied a filter
    """
    try:
        from datetime import datetime
        
        # Create action data
        action_data = UserActionCreate(
            user_id=current_user.user_id,
            action_type=f"dashboard_{action_type}",
            action_metadata={
                "feature_id": feature_id,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
        
        # Log the action
        action = UserActionService.create_action(db, action_data)
        
        return {
            "success": True,
            "action_id": str(action.id),
            "message": "Dashboard action logged successfully"
        }
    except Exception as e:
        logger.error(f"Error logging dashboard action: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging dashboard action: {str(e)}"
        )

