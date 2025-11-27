"""
MAPE-K Adaptation Engine API endpoints
Analyze and Plan components
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, require_role
from services.mape_k_analyze import MAPEKAnalyzeService
from services.mape_k_plan import MAPEKPlanService
from services.adaptation_service import AdaptationService
from schemas.adaptation import (
    AnalyzeRequest,
    AnalyzeResponse,
    PlanRequest,
    PlanResponse,
    AdaptationResponse
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mape-k", tags=["mape-k"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Analyze user behavior and system data to generate insights.
    Part of MAPE-K Monitor -> Analyze flow.
    """
    try:
        # Ensure user can only analyze their own data (unless admin/researcher)
        if str(request.user_id) != str(current_user.user_id) and current_user.role not in ["admin", "researcher"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot analyze other users' data"
            )
        
        analysis_result = MAPEKAnalyzeService.analyze(
            db,
            request.user_id,
            patient_id=request.patient_id,
            days=request.days
        )
        
        return AnalyzeResponse(**analysis_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in MAPE-K analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing analysis: {str(e)}"
        )


@router.post("/plan", response_model=PlanResponse)
async def plan(
    patient_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Generate an adaptation plan based on analysis.
    Part of MAPE-K Analyze -> Plan flow.
    Automatically uses the current user's ID.
    """
    try:
        # Perform analysis automatically
        analysis_result = MAPEKAnalyzeService.analyze(
            db,
            current_user.user_id,
            patient_id=patient_id,
            days=30  # Default to 30 days
        )
        analysis_data = analysis_result
        
        # Generate plan
        plan_result = MAPEKPlanService.generate_plan(
            db,
            current_user.user_id,
            patient_id,
            analysis_data=analysis_data
        )
        
        return PlanResponse(**plan_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in MAPE-K planning: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating plan: {str(e)}"
        )


@router.get("/adaptation/latest", response_model=AdaptationResponse)
async def get_latest_adaptation(
    patient_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get the most recent adaptation plan for the current user.
    Used by frontend to apply adaptations.
    """
    adaptation = AdaptationService.get_latest_adaptation(
        db,
        current_user.user_id,
        patient_id=patient_id
    )
    
    if not adaptation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No adaptation plan found"
        )
    
    # Convert plan_json back to AdaptationPlan
    from schemas.adaptation import AdaptationPlan
    plan = AdaptationPlan(**adaptation.plan_json)
    
    return AdaptationResponse(
        id=adaptation.id,
        user_id=adaptation.user_id,
        patient_id=adaptation.patient_id,
        plan_json=plan,
        timestamp=adaptation.timestamp
    )


@router.get("/adaptations", response_model=list[AdaptationResponse])
async def get_adaptations(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),  # Only researchers and admins can view all adaptations
):
    """
    Get all adaptation plans for the current user.
    Used by researcher dashboard.
    """
    adaptations = AdaptationService.get_adaptations_by_user(
        db,
        current_user.user_id,
        limit=limit
    )
    
    from schemas.adaptation import AdaptationPlan
    return [
        AdaptationResponse(
            id=adaptation.id,
            user_id=adaptation.user_id,
            patient_id=adaptation.patient_id,
            plan_json=AdaptationPlan(**adaptation.plan_json),
            timestamp=adaptation.timestamp
        )
        for adaptation in adaptations
    ]


@router.get("/dashboard/analyze")
async def analyze_dashboard(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Analyze dashboard usage patterns for the current user.
    Returns feature frequencies, most/least used features, and workflow patterns.
    """
    try:
        analysis = MAPEKAnalyzeService.analyze_dashboard_usage(
            db,
            current_user.user_id,
            days=days
        )
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing dashboard usage: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing dashboard: {str(e)}"
        )


@router.get("/dashboard/plan")
async def get_dashboard_plan(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get dashboard adaptation plan for the current user.
    Returns feature priorities, sizes, hidden features, and quick stats.
    """
    try:
        # Analyze dashboard usage
        dashboard_analysis = MAPEKAnalyzeService.analyze_dashboard_usage(
            db,
            current_user.user_id,
            days=30
        )
        
        # Generate dashboard plan
        plan = MAPEKPlanService.generate_dashboard_plan(
            db,
            current_user.user_id,
            dashboard_analysis=dashboard_analysis
        )
        
        return plan
    except Exception as e:
        logger.error(f"Error generating dashboard plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating dashboard plan: {str(e)}"
        )

