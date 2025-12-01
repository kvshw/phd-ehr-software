"""
Runtime Assurance API Routes
Phase 4: Ethics, Safety, and Transparency

Endpoints for:
- Shadow testing
- Gradual rollouts
- Change logs
- Bias/drift monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from core.database import get_db
from core.dependencies import get_current_user, require_role
from services.assurance_service import AssuranceService
from services.change_log_service import ChangeLogService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assurance", tags=["assurance"])


# ==========================================
# Pydantic Models
# ==========================================

class CreateShadowTestRequest(BaseModel):
    name: str = Field(..., description="Name of the test")
    policy_type: str = Field(..., description="Type of policy: layout, suggestion, alert")
    control_policy: Dict[str, Any] = Field(..., description="Current policy (control)")
    test_policy: Dict[str, Any] = Field(..., description="New policy to test")
    duration_days: int = Field(default=7, ge=1, le=30)
    test_group_percentage: float = Field(default=0.0, ge=0.0, le=1.0, description="0 for shadow mode")
    success_metrics: Optional[List[str]] = None
    success_threshold: float = Field(default=0.05, ge=0.0, le=1.0)
    description: str = ""


class EvaluateTestRequest(BaseModel):
    control_metrics: Dict[str, float]
    test_metrics: Dict[str, float]


class StartRolloutRequest(BaseModel):
    stages: List[float] = Field(default=[0.1, 0.25, 0.5, 0.75, 1.0])
    regression_threshold: float = Field(default=-0.05)


class AdvanceRolloutRequest(BaseModel):
    current_metrics: Dict[str, float]
    baseline_metrics: Dict[str, float]


class LogAdaptationRequest(BaseModel):
    adaptation_type: str
    old_state: Dict[str, Any]
    new_state: Dict[str, Any]
    explanation: str
    trigger_reason: str = "automatic"
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)
    metrics_before: Optional[Dict[str, float]] = None
    feature_name: Optional[str] = None


class UpdateMetricsRequest(BaseModel):
    metrics_after: Dict[str, float]


# ==========================================
# Shadow Testing Endpoints
# ==========================================

@router.post("/shadow-tests")
async def create_shadow_test(
    request: CreateShadowTestRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"]))
):
    """
    Create a new shadow test or A/B test.
    
    **Admin/Researcher Only**
    
    - Shadow mode (test_group_percentage=0): Test policy runs in parallel, no user impact
    - A/B mode (test_group_percentage>0): Some users get test policy
    """
    try:
        service = AssuranceService(db)
        result = service.create_shadow_test(
            name=request.name,
            policy_type=request.policy_type,
            control_policy=request.control_policy,
            test_policy=request.test_policy,
            duration_days=request.duration_days,
            test_group_percentage=request.test_group_percentage,
            success_metrics=request.success_metrics,
            success_threshold=request.success_threshold,
            description=request.description
        )
        return result
    except Exception as e:
        logger.error(f"Error creating shadow test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/shadow-tests")
async def list_shadow_tests(
    status_filter: Optional[str] = Query(None, alias="status"),
    policy_type: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"]))
):
    """
    List shadow/A/B tests.
    
    **Admin/Researcher Only**
    """
    try:
        service = AssuranceService(db)
        data = service.get_assurance_dashboard_data()
        return {"tests": data.get("active_tests", [])}
    except Exception as e:
        logger.error(f"Error listing shadow tests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/shadow-tests/{test_id}/evaluate")
async def evaluate_shadow_test(
    test_id: UUID,
    request: EvaluateTestRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"]))
):
    """
    Evaluate results of a shadow test.
    
    **Admin/Researcher Only**
    
    Returns recommendation: approve, reject, extend, or modify.
    """
    try:
        service = AssuranceService(db)
        result = service.evaluate_shadow_test(
            test_id=test_id,
            control_metrics=request.control_metrics,
            test_metrics=request.test_metrics
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error evaluating shadow test: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================
# Gradual Rollout Endpoints
# ==========================================

@router.post("/shadow-tests/{test_id}/rollout")
async def start_rollout(
    test_id: UUID,
    request: StartRolloutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"]))
):
    """
    Start gradual rollout of an approved policy.
    
    **Admin Only**
    
    Only works for tests with 'approve' recommendation.
    """
    try:
        service = AssuranceService(db)
        result = service.start_gradual_rollout(
            test_id=test_id,
            stages=request.stages,
            regression_threshold=request.regression_threshold
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting rollout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/shadow-tests/{test_id}/rollout/advance")
async def advance_rollout(
    test_id: UUID,
    request: AdvanceRolloutRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"]))
):
    """
    Advance rollout to next stage or rollback if regression detected.
    
    **Admin Only**
    
    Automatically rolls back if metrics regress beyond threshold.
    """
    try:
        service = AssuranceService(db)
        result = service.advance_rollout(
            test_id=test_id,
            current_metrics=request.current_metrics,
            baseline_metrics=request.baseline_metrics
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error advancing rollout: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================
# Change Log Endpoints
# ==========================================

@router.post("/logs")
async def log_adaptation(
    request: LogAdaptationRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Log an adaptation change.
    
    Called by MAPE-K when making adaptation decisions.
    Stores full provenance for transparency and audit.
    """
    try:
        service = ChangeLogService(db)
        result = service.log_adaptation(
            user_id=current_user.user_id,
            adaptation_type=request.adaptation_type,
            old_state=request.old_state,
            new_state=request.new_state,
            explanation=request.explanation,
            trigger_reason=request.trigger_reason,
            confidence_score=request.confidence_score,
            metrics_before=request.metrics_before,
            feature_name=request.feature_name
        )
        return result
    except Exception as e:
        logger.error(f"Error logging adaptation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/logs/{log_id}/metrics")
async def update_log_metrics(
    log_id: UUID,
    request: UpdateMetricsRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Update adaptation log with post-adaptation metrics.
    
    Called after measuring the effect of an adaptation.
    """
    try:
        service = ChangeLogService(db)
        success = service.update_metrics_after(log_id, request.metrics_after)
        if success:
            return {"status": "updated", "log_id": str(log_id)}
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    except Exception as e:
        logger.error(f"Error updating log metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/logs/me")
async def get_my_change_log(
    days: int = Query(default=30, le=90),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get current user's adaptation change log.
    
    Returns a user-friendly log grouped by date with explanations.
    Used for the Change Log Drawer in the UI.
    """
    try:
        service = ChangeLogService(db)
        log = service.get_user_change_log(
            user_id=current_user.user_id,
            days=days,
            include_explanations=True
        )
        return {"change_log": log, "days": days}
    except Exception as e:
        logger.error(f"Error getting change log: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/logs/recent")
async def get_recent_adaptations(
    hours: int = Query(default=24, le=168),
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"]))
):
    """
    Get recent adaptations across all users.
    
    **Admin/Researcher Only**
    """
    try:
        service = ChangeLogService(db)
        adaptations = service.get_recent_adaptations(hours=hours, limit=limit)
        return {"adaptations": adaptations, "hours": hours}
    except Exception as e:
        logger.error(f"Error getting recent adaptations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/logs/statistics")
async def get_adaptation_statistics(
    days: int = Query(default=30, le=90),
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"]))
):
    """
    Get adaptation statistics.
    
    **Admin/Researcher Only**
    
    Returns counts, rollback rates, and breakdown by type.
    """
    try:
        service = ChangeLogService(db)
        stats = service.get_adaptation_statistics(user_id=user_id, days=days)
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/logs/{log_id}/rollback")
async def rollback_adaptation(
    log_id: UUID,
    reason: str = Query(..., description="Reason for rollback"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"]))
):
    """
    Rollback a specific adaptation.
    
    **Admin Only**
    
    Creates a new log entry reversing the original adaptation.
    """
    try:
        service = ChangeLogService(db)
        result = service.log_rollback(log_id, reason)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Error rolling back adaptation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================
# Bias & Drift Detection Endpoints
# ==========================================

@router.get("/bias")
async def detect_bias(
    group_type: str = Query(default="specialty"),
    period_days: int = Query(default=30, le=90),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"]))
):
    """
    Detect potential bias in adaptation effectiveness.
    
    **Admin/Researcher Only**
    
    Checks if certain user groups benefit more or less from adaptations.
    """
    try:
        service = AssuranceService(db)
        findings = service.detect_bias(group_type=group_type, period_days=period_days)
        return {
            "group_type": group_type,
            "period_days": period_days,
            "findings": findings,
            "has_bias": any(f["is_potential_bias"] for f in findings)
        }
    except Exception as e:
        logger.error(f"Error detecting bias: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/drift")
async def detect_drift(
    metric_name: str = Query(..., description="Metric to check for drift"),
    baseline_days: int = Query(default=30, le=90),
    current_days: int = Query(default=7, le=30),
    threshold: float = Query(default=2.0, ge=0.5, le=5.0),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"]))
):
    """
    Detect drift in a specific metric.
    
    **Admin/Researcher Only**
    
    Compares current period to baseline using statistical distance.
    """
    try:
        service = AssuranceService(db)
        result = service.detect_drift(
            metric_name=metric_name,
            baseline_period_days=baseline_days,
            current_period_days=current_days,
            drift_threshold=threshold
        )
        return result
    except Exception as e:
        logger.error(f"Error detecting drift: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================
# Dashboard Endpoint
# ==========================================

@router.get("/dashboard")
async def get_assurance_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"]))
):
    """
    Get comprehensive assurance dashboard data.
    
    **Admin/Researcher Only**
    
    Returns active tests, rollouts, bias alerts, drift alerts, and summary stats.
    """
    try:
        service = AssuranceService(db)
        data = service.get_assurance_dashboard_data()
        return data
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==========================================
# User Explanation Endpoint
# ==========================================

@router.get("/explain/{feature}")
async def get_feature_explanation(
    feature: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Get explanation for why a feature was adapted.
    
    Returns usage statistics and explanation for transparency.
    """
    try:
        service = ChangeLogService(db)
        
        # Get most recent adaptation for this feature
        adaptations = service.get_user_adaptations(
            user_id=current_user.user_id,
            limit=1
        )
        
        # Filter to this feature
        feature_adaptations = [
            a for a in adaptations 
            if a.get("feature_name") == feature
        ]
        
        if not feature_adaptations:
            return {
                "feature": feature,
                "has_adaptation": False,
                "message": "No adaptations found for this feature"
            }
        
        adapt = feature_adaptations[0]
        
        return {
            "feature": feature,
            "has_adaptation": True,
            "explanation": adapt.get("explanation"),
            "adapted_at": adapt.get("applied_at"),
            "confidence": adapt.get("confidence_score"),
            "metrics": adapt.get("metrics_before"),
            "type": adapt.get("adaptation_type")
        }
    except Exception as e:
        logger.error(f"Error getting feature explanation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

