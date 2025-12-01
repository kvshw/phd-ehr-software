"""
MAPE-K Adaptation Engine API endpoints
Analyze and Plan components
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
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
    
    **Assurance Integration:**
    - Logs adaptation with full provenance via ChangeLogService
    - Captures old state for comparison
    - Records explanation and confidence
    """
    try:
        # Get current adaptation state (old state for provenance)
        old_adaptation = AdaptationService.get_latest_adaptation(
            db, current_user.user_id, patient_id
        )
        old_state = old_adaptation.plan_json if old_adaptation else {}
        
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
        
        # Log adaptation with full provenance (assurance layer integration)
        try:
            from services.change_log_service import ChangeLogService
            change_log = ChangeLogService(db)
            
            new_state = plan_result.get("adaptation", {}).get("plan_json", {})
            explanation = new_state.get("explanation", "Dashboard adapted based on usage patterns")
            
            change_log.log_adaptation(
                user_id=current_user.user_id,
                adaptation_type="dashboard_layout",
                old_state=old_state,
                new_state=new_state,
                explanation=explanation,
                trigger_reason="mape_k_analysis",
                confidence_score=analysis_data.get("confidence", 0.8),
                metrics_before={
                    "total_actions": analysis_data.get("total_actions", 0),
                    "suggestions_shown": analysis_data.get("suggestions_shown", 0),
                    "suggestions_accepted": analysis_data.get("suggestions_accepted", 0),
                }
            )
        except Exception as log_error:
            logger.warning(f"Failed to log adaptation: {log_error}")
        
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


# ============================================================================
# Bandit-Based Planning Endpoints (Thompson Sampling)
# ============================================================================

@router.post("/plan/bandit")
async def plan_with_bandit(
    patient_id: Optional[UUID] = None,
    specialty: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Generate an adaptation plan using Thompson Sampling bandit algorithm.
    
    This is the advanced planning endpoint that uses exploration/exploitation
    to learn optimal UI layouts over time.
    
    **Algorithm Details:**
    - Uses Beta distributions to model uncertainty about feature preferences
    - Thompson Sampling for principled exploration vs exploitation
    - Constraints prevent layout thrashing and protect critical features
    
    **Assurance Integration:**
    - Logs adaptation with full provenance via ChangeLogService
    - Captures exploration/exploitation decision
    - Records confidence from Thompson Sampling
    
    **Parameters:**
    - patient_id: Optional patient context
    - specialty: User's medical specialty (affects priors)
    """
    try:
        # Get user specialty if not provided
        if not specialty:
            from models.user import User
            user = db.query(User).filter(User.id == current_user.user_id).first()
            specialty = user.specialty if user else None
        
        # Get current adaptation state (old state for provenance)
        old_adaptation = AdaptationService.get_latest_adaptation(
            db, current_user.user_id, patient_id
        )
        old_state = old_adaptation.plan_json if old_adaptation else {}
        
        # Generate bandit-based plan
        plan_result = MAPEKPlanService.generate_plan_with_bandit(
            db,
            current_user.user_id,
            patient_id,
            specialty=specialty,
        )
        
        # Log adaptation with full provenance (assurance layer integration)
        try:
            from services.change_log_service import ChangeLogService
            change_log = ChangeLogService(db)
            
            new_state = plan_result.get("layout", {})
            explanation = plan_result.get("explanation", "Dashboard adapted using Thompson Sampling")
            confidence = plan_result.get("confidence", 0.8)
            
            change_log.log_adaptation(
                user_id=current_user.user_id,
                adaptation_type="dashboard_layout",
                old_state=old_state,
                new_state=new_state,
                explanation=explanation,
                trigger_reason="bandit_thompson_sampling",
                confidence_score=confidence,
                metrics_before={
                    "specialty": specialty or "general",
                    "exploration_mode": plan_result.get("exploration", False),
                }
            )
        except Exception as log_error:
            logger.warning(f"Failed to log bandit adaptation: {log_error}")
        
        return plan_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bandit planning: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating bandit plan: {str(e)}"
        )


@router.post("/plan/smart")
async def smart_plan(
    patient_id: Optional[UUID] = None,
    specialty: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Generate adaptation plan using the best available algorithm.
    
    Automatically selects between rule-based and bandit-based planning
    based on configuration and A/B testing assignment.
    
    This is the recommended endpoint for production use.
    """
    try:
        # Get user specialty if not provided
        if not specialty:
            from models.user import User
            user = db.query(User).filter(User.id == current_user.user_id).first()
            specialty = user.specialty if user else None
        
        # Check if user should use bandit planning
        use_bandit = MAPEKPlanService.should_use_bandit(current_user.user_id)
        
        if use_bandit:
            plan_result = MAPEKPlanService.generate_plan_with_bandit(
                db,
                current_user.user_id,
                patient_id,
                specialty=specialty,
            )
        else:
            # Use rule-based planning
            analysis_result = MAPEKAnalyzeService.analyze(
                db,
                current_user.user_id,
                patient_id=patient_id,
                days=30
            )
            plan_result = MAPEKPlanService.generate_plan(
                db,
                current_user.user_id,
                patient_id,
                analysis_data=analysis_result
            )
            plan_result["algorithm"] = "rule_based"
        
        # Add A/B testing info
        plan_result["ab_test"] = {
            "group": "bandit" if use_bandit else "rule_based",
            "user_id": str(current_user.user_id),
        }
        
        return plan_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in smart planning: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating smart plan: {str(e)}"
        )


@router.post("/bandit/feedback")
async def record_bandit_feedback(
    feature_key: str,
    success: bool,
    specialty: Optional[str] = None,
    weight: float = 1.0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Record user feedback for bandit learning.
    
    Call this endpoint when:
    - User quickly accesses a feature (success=True)
    - User spends significant time on a feature (success=True)
    - User ignores/scrolls past a feature (success=False)
    - User accepts AI suggestion (success=True, feature="suggestions")
    - User ignores AI suggestion (success=False, feature="suggestions")
    
    **Parameters:**
    - feature_key: Feature that received feedback (e.g., "vitals", "medications")
    - success: Whether the interaction was positive
    - specialty: User's specialty (for context-aware learning)
    - weight: Weight of this feedback (default 1.0)
    """
    try:
        from services.mape_k_plan_bandit import BanditPlanService
        
        # Get user specialty if not provided
        if not specialty:
            from models.user import User
            user = db.query(User).filter(User.id == current_user.user_id).first()
            specialty = user.specialty if user else None
        
        bandit_service = BanditPlanService(db)
        bandit_service.record_feedback(
            user_id=current_user.user_id,
            feature_key=feature_key,
            success=success,
            specialty=specialty,
            weight=weight,
        )
        
        return {
            "status": "recorded",
            "feature_key": feature_key,
            "success": success,
            "specialty": specialty,
        }
        
    except Exception as e:
        logger.error(f"Error recording bandit feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording feedback: {str(e)}"
        )


@router.get("/bandit/status")
async def get_bandit_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get bandit learning status for the current user.
    
    Returns:
    - Current feature beliefs (alpha/beta parameters)
    - Expected values and confidence intervals
    - Recent adaptation history
    """
    try:
        from sqlalchemy import select
        from models.bandit_state import BanditState, BanditAdaptationLog
        
        # Get bandit states
        states_stmt = select(BanditState).where(
            BanditState.user_id == current_user.user_id
        )
        states = db.execute(states_stmt).scalars().all()
        
        # Get recent logs
        logs_stmt = select(BanditAdaptationLog).where(
            BanditAdaptationLog.user_id == current_user.user_id
        ).order_by(BanditAdaptationLog.created_at.desc()).limit(20)
        logs = db.execute(logs_stmt).scalars().all()
        
        return {
            "user_id": str(current_user.user_id),
            "using_bandit": MAPEKPlanService.should_use_bandit(current_user.user_id),
            "feature_beliefs": [
                {
                    "feature_key": s.feature_key,
                    "context_hash": s.context_hash,
                    "alpha": round(s.alpha, 3),
                    "beta": round(s.beta, 3),
                    "expected_value": round(s.expected_value, 3),
                    "confidence_interval": [round(v, 3) for v in s.confidence_interval],
                    "total_interactions": s.total_interactions,
                    "is_critical": s.is_critical,
                }
                for s in states
            ],
            "recent_adaptations": [
                {
                    "feature_key": log.feature_key,
                    "action": log.action,
                    "sampled_value": round(log.sampled_value, 3),
                    "constraint_applied": log.constraint_applied,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ],
        }
        
    except Exception as e:
        logger.error(f"Error getting bandit status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting bandit status: {str(e)}"
        )


# ============================================================================
# Transfer Learning Endpoints
# ============================================================================

@router.post("/transfer/update-priors")
async def update_priors(
    specialty: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Update global or specialty-specific priors by aggregating user data.
    
    **Admin/Researcher Only**
    
    This endpoint aggregates bandit states from all users (or specialty users)
    to create/update priors for cold-start handling.
    
    Should be run periodically (e.g., daily cron job).
    """
    try:
        from services.adaptation_transfer_service import AdaptationTransferService
        
        transfer_service = AdaptationTransferService(db)
        
        if specialty:
            transfer_service.update_specialty_priors(specialty)
            return {
                "status": "success",
                "message": f"Updated priors for specialty: {specialty}",
                "specialty": specialty,
            }
        else:
            transfer_service.update_global_priors()
            return {
                "status": "success",
                "message": "Updated global priors",
            }
        
    except Exception as e:
        logger.error(f"Error updating priors: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating priors: {str(e)}"
        )


@router.get("/transfer/status")
async def get_transfer_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get transfer learning status for the current user.
    
    Shows:
    - Experience level (cold-start, warm-start, personalized)
    - Which priors are being used
    - Blending weights (if in warm-start)
    """
    try:
        from services.adaptation_transfer_service import AdaptationTransferService
        from models.user import User
        
        transfer_service = AdaptationTransferService(db)
        user = db.query(User).filter(User.id == current_user.user_id).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        experience_days = transfer_service._calculate_experience_days(current_user.user_id)
        
        # Determine stage
        if experience_days < 7:
            stage = "cold_start"
            stage_name = "Cold Start"
            description = "Using transferred priors from similar users"
        elif experience_days < 30:
            stage = "warm_start"
            stage_name = "Warm Start"
            description = "Blending transferred priors with your personal data"
        else:
            stage = "personalized"
            stage_name = "Personalized"
            description = "Using your personal adaptation data"
        
        # Get transferred priors to show details
        try:
            priors = transfer_service.get_transferred_priors(
                current_user.user_id,
                user.specialty
            )
            
            # Count by source
            source_counts = {}
            for prior in priors.values():
                source = prior.get("source", "unknown")
                source_counts[source] = source_counts.get(source, 0) + 1
            
            # Get blending weights if warm-start
            blending_info = None
            if stage == "warm_start" and priors:
                first_prior = next(iter(priors.values()))
                blending_info = {
                    "prior_weight": first_prior.get("prior_weight", 0.0),
                    "personal_weight": first_prior.get("weight", 0.0),
                    "prior_source": first_prior.get("prior_source", "unknown"),
                }
        except Exception as e:
            logger.warning(f"Failed to get priors: {e}")
            priors = {}
            source_counts = {}
            blending_info = None
        
        return {
            "user_id": str(current_user.user_id),
            "specialty": user.specialty,
            "experience_days": experience_days,
            "stage": stage,
            "stage_name": stage_name,
            "description": description,
            "features_with_priors": len(priors),
            "source_distribution": source_counts,
            "blending_info": blending_info,
            "days_until_personalized": max(0, 30 - experience_days) if stage != "personalized" else 0,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transfer status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting transfer status: {str(e)}"
        )


@router.get("/transfer/priors")
async def get_priors(
    specialty: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Get global or specialty-specific priors.
    
    **Researcher/Admin Only**
    
    Useful for research analysis of learned patterns.
    """
    try:
        from models.transfer_learning import GlobalFeaturePrior, SpecialtyFeaturePrior
        
        if specialty:
            priors = db.query(SpecialtyFeaturePrior).filter(
                SpecialtyFeaturePrior.specialty == specialty
            ).all()
            
            return {
                "type": "specialty",
                "specialty": specialty,
                "priors": [
                    {
                        "feature_key": p.feature_key,
                        "alpha": p.alpha_prior,
                        "beta": p.beta_prior,
                        "total_users": p.total_users,
                        "total_interactions": p.total_interactions,
                        "total_successes": p.total_successes,
                        "last_updated": p.last_updated.isoformat() if p.last_updated else None,
                    }
                    for p in priors
                ],
            }
        else:
            priors = db.query(GlobalFeaturePrior).all()
            
            return {
                "type": "global",
                "priors": [
                    {
                        "feature_key": p.feature_key,
                        "alpha": p.alpha_prior,
                        "beta": p.beta_prior,
                        "total_users": p.total_users,
                        "total_interactions": p.total_interactions,
                        "total_successes": p.total_successes,
                        "last_updated": p.last_updated.isoformat() if p.last_updated else None,
                    }
                    for p in priors
                ],
            }
        
    except Exception as e:
        logger.error(f"Error getting priors: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting priors: {str(e)}"
        )


# ============================================================================
# Federated Learning Endpoints
# ============================================================================

@router.post("/fl/rounds/start")
async def start_fl_round(
    model_type: str,
    global_model_version: str,
    aggregation_method: str = "fedavg",
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Start a new federated learning round.
    
    **Admin/Researcher Only**
    
    Coordinates a new FL round where clients can participate.
    """
    try:
        from services.federated_learning_service import FederatedLearningService
        
        fl_service = FederatedLearningService(db)
        fl_round = fl_service.start_round(
            model_type=model_type,
            global_model_version=global_model_version,
            aggregation_method=aggregation_method,
        )
        
        return {
            "round_id": str(fl_round.id),
            "round_number": fl_round.round_number,
            "model_type": fl_round.model_type,
            "status": fl_round.status,
            "started_at": fl_round.started_at.isoformat() if fl_round.started_at else None,
        }
        
    except Exception as e:
        logger.error(f"Error starting FL round: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting FL round: {str(e)}"
        )


@router.post("/fl/rounds/{round_id}/submit")
async def submit_fl_update(
    round_id: UUID,
    client_id: str,
    weight_updates: Dict[str, Any],
    sample_count: int,
    training_loss: Optional[float] = None,
    validation_loss: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Submit weight updates from an FL client.
    
    **Admin/Researcher Only** (in production, clients would have their own auth)
    
    Clients train locally and send only weight updates (not raw data).
    """
    try:
        from services.federated_learning_service import FederatedLearningService
        
        fl_service = FederatedLearningService(db)
        update = fl_service.submit_client_update(
            round_id=round_id,
            client_id=client_id,
            weight_updates=weight_updates,
            sample_count=sample_count,
            training_loss=training_loss,
            validation_loss=validation_loss,
        )
        
        return {
            "update_id": str(update.id),
            "round_id": str(round_id),
            "client_id": client_id,
            "sample_count": sample_count,
            "status": update.status,
            "sent_at": update.sent_at.isoformat() if update.sent_at else None,
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error submitting FL update: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting FL update: {str(e)}"
        )


@router.post("/fl/rounds/{round_id}/aggregate")
async def aggregate_fl_updates(
    round_id: UUID,
    min_participants: int = 3,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Aggregate client updates for an FL round.
    
    **Admin/Researcher Only**
    
    Uses FedAvg (Federated Averaging) to combine weight updates.
    """
    try:
        from services.federated_learning_service import FederatedLearningService
        
        fl_service = FederatedLearningService(db)
        result = fl_service.aggregate_updates(round_id, min_participants)
        
        return {
            "round_id": str(round_id),
            "aggregated": True,
            "participant_count": result["participant_count"],
            "total_samples": result["total_samples"],
            "round_number": result["round_number"],
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error aggregating FL updates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error aggregating FL updates: {str(e)}"
        )


@router.post("/fl/rounds/{round_id}/save-model")
async def save_fl_model(
    round_id: UUID,
    model_weights: Dict[str, Any],
    performance_metrics: Optional[Dict[str, float]] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Save aggregated model as new global model version.
    
    **Admin/Researcher Only**
    """
    try:
        from services.federated_learning_service import FederatedLearningService
        
        fl_service = FederatedLearningService(db)
        global_model = fl_service.save_global_model(
            round_id=round_id,
            model_weights=model_weights,
            performance_metrics=performance_metrics,
        )
        
        return {
            "model_id": str(global_model.id),
            "version": global_model.version,
            "model_type": global_model.model_type,
            "is_active": global_model.is_active == "true",
            "created_at": global_model.created_at.isoformat() if global_model.created_at else None,
        }
        
    except Exception as e:
        logger.error(f"Error saving FL model: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving FL model: {str(e)}"
        )


@router.get("/fl/rounds/{round_id}/status")
async def get_fl_round_status(
    round_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Get status of an FL round.
    
    **Admin/Researcher Only**
    """
    try:
        from services.federated_learning_service import FederatedLearningService
        
        fl_service = FederatedLearningService(db)
        status = fl_service.get_round_status(round_id)
        
        return status
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting FL round status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting FL round status: {str(e)}"
        )


@router.get("/fl/models/latest")
async def get_latest_fl_model(
    model_type: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Get the latest active global model for a model type.
    
    **Admin/Researcher Only**
    """
    try:
        from services.federated_learning_service import FederatedLearningService
        
        fl_service = FederatedLearningService(db)
        model = fl_service.get_latest_global_model(model_type)
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active model found for type: {model_type}"
            )
        
        return {
            "model_id": str(model.id),
            "version": model.version,
            "model_type": model.model_type,
            "global_accuracy": model.global_accuracy,
            "global_loss": model.global_loss,
            "test_accuracy": model.test_accuracy,
            "participant_count": model.participant_count,
            "total_samples": model.total_samples,
            "created_at": model.created_at.isoformat() if model.created_at else None,
            # Note: model_weights not included for security (too large)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest FL model: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting latest FL model: {str(e)}"
        )


@router.post("/fl/clients/register")
async def register_fl_client(
    client_id: str,
    client_name: Optional[str] = None,
    client_type: str = "site",
    public_key: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Register a new FL client (site/department).
    
    **Admin/Researcher Only**
    """
    try:
        from services.federated_learning_service import FederatedLearningService
        
        fl_service = FederatedLearningService(db)
        client = fl_service.register_client(
            client_id=client_id,
            client_name=client_name,
            client_type=client_type,
            public_key=public_key,
        )
        
        return {
            "client_id": client.client_id,
            "client_name": client.client_name,
            "client_type": client.client_type,
            "is_active": client.is_active == "true",
            "created_at": client.created_at.isoformat() if client.created_at else None,
        }
        
    except Exception as e:
        logger.error(f"Error registering FL client: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering FL client: {str(e)}"
        )


# ============================================================================
# Phase 6: Multi-Window Analysis Endpoints
# ============================================================================

@router.post("/analyze/multi-window")
async def analyze_multi_window(
    patient_id: Optional[UUID] = None,
    windows: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Analyze user behavior across multiple time windows (7/30/90 days).
    
    Uses exponential decay to weight recent data more heavily while
    maintaining stability from long-term patterns.
    
    **Features:**
    - Multi-window analysis (short/medium/long-term)
    - Exponential decay weighting (7d: 50%, 30d: 30%, 90d: 20%)
    - Drift detection (identifies changing behavior)
    - Confidence scoring based on data availability
    
    **Parameters:**
    - patient_id: Optional patient context
    - windows: Custom window sizes in days (default: [7, 30, 90])
    
    **Returns:**
    - Per-window analysis results
    - Combined weighted analysis
    - Drift detection (emerging/declining features)
    - Window-aware insights
    - Confidence level
    """
    try:
        # Default windows
        if windows is None:
            windows = [7, 30, 90]
        
        # Validate windows
        if not all(isinstance(w, int) and w > 0 for w in windows):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Windows must be positive integers"
            )
        
        analysis = MAPEKAnalyzeService.analyze_with_windows(
            db,
            user_id=current_user.user_id,
            patient_id=patient_id,
            windows=windows,
        )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in multi-window analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing multi-window analysis: {str(e)}"
        )


@router.post("/analyze/context-aware")
async def analyze_context_aware(
    context: Dict[str, Any],
    windows: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Context-aware multi-window analysis.
    
    Adjusts analysis parameters based on context (role, specialty, workload).
    
    **Context Fields:**
    - role: User's role (nurse, doctor, researcher)
    - specialty: Medical specialty
    - time_of_day: Current time context (morning, afternoon, evening)
    - workload: Current workload level (high, medium, low)
    
    **Returns:**
    - Context-adjusted analysis
    - Custom decay weights based on role
    - Specialty-specific insights
    """
    try:
        if windows is None:
            windows = [7, 30, 90]
        
        analysis = MAPEKAnalyzeService.analyze_with_context(
            db,
            user_id=current_user.user_id,
            context=context,
            windows=windows,
        )
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error in context-aware analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing context-aware analysis: {str(e)}"
        )


@router.get("/analyze/drift")
async def get_drift_analysis(
    patient_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get drift analysis comparing recent vs long-term behavior.
    
    Identifies:
    - Emerging features (usage increasing)
    - Declining features (usage decreasing)
    - Stable features (consistent usage)
    - Suggestion preference changes
    
    Useful for understanding behavioral changes over time.
    """
    try:
        analysis = MAPEKAnalyzeService.analyze_with_windows(
            db,
            user_id=current_user.user_id,
            patient_id=patient_id,
            windows=[7, 30, 90],
        )
        
        drift = analysis.get("drift_analysis", {})
        insights = analysis.get("insights", [])
        confidence = analysis.get("confidence", {})
        
        return {
            "user_id": str(current_user.user_id),
            "drift_detected": drift.get("drift_detected", False),
            "emerging_features": drift.get("emerging_features", []),
            "declining_features": drift.get("declining_features", []),
            "stable_features": drift.get("stable_features", []),
            "suggestion_drift": drift.get("suggestion_preference_drift"),
            "insights": insights,
            "confidence": confidence,
            "recommendations": [
                i.get("recommendation") for i in insights 
                if i.get("recommendation")
            ],
        }
        
    except Exception as e:
        logger.error(f"Error in drift analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing drift analysis: {str(e)}"
        )


@router.post("/plan/multi-window")
async def plan_with_multi_window(
    patient_id: Optional[UUID] = None,
    windows: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Generate adaptation plan using multi-window analysis.
    
    Combines short-term responsiveness with long-term stability:
    - Recent changes are weighted more heavily
    - Long-term patterns provide stability
    - Drift detection prevents thrashing
    
    **Parameters:**
    - patient_id: Optional patient context
    - windows: Custom window sizes (default: [7, 30, 90])
    
    **Returns:**
    - Adaptation plan based on weighted analysis
    - Confidence-adjusted recommendations
    - Drift-aware feature ordering
    """
    try:
        if windows is None:
            windows = [7, 30, 90]
        
        # Get multi-window analysis
        analysis = MAPEKAnalyzeService.analyze_with_windows(
            db,
            user_id=current_user.user_id,
            patient_id=patient_id,
            windows=windows,
        )
        
        # Extract combined analysis for planning
        combined = analysis.get("combined_analysis", {})
        drift = analysis.get("drift_analysis", {})
        confidence = analysis.get("confidence", {})
        
        # Build plan based on weighted features
        top_features = combined.get("top_features", [])
        weighted_scores = combined.get("weighted_feature_scores", {})
        
        # Adjust for drift - boost emerging, demote declining
        feature_order = []
        for feature in top_features:
            score = weighted_scores.get(feature, 0)
            
            # Check if emerging
            emerging = [e for e in drift.get("emerging_features", []) if e.get("feature") == feature]
            if emerging:
                score *= 1.2  # 20% boost for emerging features
            
            # Check if declining
            declining = [d for d in drift.get("declining_features", []) if d.get("feature") == feature]
            if declining:
                score *= 0.8  # 20% penalty for declining features
            
            feature_order.append({"feature": feature, "score": score})
        
        # Re-sort by adjusted score
        feature_order.sort(key=lambda x: x["score"], reverse=True)
        
        # Adjust suggestion density based on acceptance rate
        acceptance_rate = combined.get("weighted_acceptance_rate", 0.5)
        if acceptance_rate > 0.6:
            suggestion_density = "high"
        elif acceptance_rate > 0.3:
            suggestion_density = "medium"
        else:
            suggestion_density = "low"
        
        plan = {
            "user_id": str(current_user.user_id),
            "patient_id": str(patient_id) if patient_id else None,
            "layout": {
                "section_order": [f["feature"] for f in feature_order],
                "feature_scores": {f["feature"]: round(f["score"], 3) for f in feature_order},
                "suggestion_density": suggestion_density,
            },
            "analysis_summary": {
                "windows_analyzed": windows,
                "drift_detected": drift.get("drift_detected", False),
                "confidence_level": confidence.get("level", "medium"),
                "confidence_score": confidence.get("overall_score", 0.5),
            },
            "insights": analysis.get("insights", []),
            "methodology": "multi_window_weighted_planning",
        }
        
        # Save adaptation
        try:
            from schemas.adaptation import AdaptationCreate
            adaptation_data = AdaptationCreate(
                user_id=current_user.user_id,
                patient_id=patient_id,
                plan_json=plan["layout"],
            )
            AdaptationService.create_adaptation(db, adaptation_data)
        except Exception as save_error:
            logger.warning(f"Failed to save adaptation: {save_error}")
        
        return plan
        
    except Exception as e:
        logger.error(f"Error in multi-window planning: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating multi-window plan: {str(e)}"
        )

