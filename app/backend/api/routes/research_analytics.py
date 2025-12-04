"""
Research Analytics API Endpoints

Provides API access to advanced research services:
- Regret Analysis
- Counterfactual Explanations
- Longitudinal Study Analysis
- Fairness Audits
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging

from core.database import get_db
from core.dependencies import get_current_user, require_role
from services.regret_analysis_service import RegretAnalysisService
from services.counterfactual_service import CounterfactualExplanationService
from services.longitudinal_study_service import LongitudinalStudyService
from services.fairness_analysis_service import FairnessAnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research-analytics", tags=["research-analytics"])


# ============================================================================
# REGRET ANALYSIS ENDPOINTS
# ============================================================================

class RegretReportResponse(BaseModel):
    """Response schema for regret analysis"""
    summary: Dict[str, Any]
    theoretical_analysis: Dict[str, Any]
    convergence_analysis: Dict[str, Any]
    arm_performance: Dict[str, Any]
    regret_curve: Dict[str, Any]
    metadata: Dict[str, Any]


@router.get("/regret/report", response_model=RegretReportResponse)
async def get_regret_report(
    user_id: Optional[UUID] = None,
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin", "clinician", "doctor"])),
):
    """
    Get comprehensive regret analysis report for Thompson Sampling bandits.
    
    Returns:
    - Cumulative regret metrics
    - Theoretical bound comparison
    - Convergence detection
    - Arm selection statistics
    
    Research Use: Demonstrates algorithmic performance for publications.
    """
    try:
        service = RegretAnalysisService(db)
        report = service.generate_regret_report(user_id, days)
        return RegretReportResponse(**report)
    except Exception as e:
        logger.error(f"Error generating regret report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating regret report: {str(e)}"
        )


@router.get("/regret/theoretical-bound")
async def get_theoretical_regret_bound(
    num_arms: int = Query(default=10, ge=1, le=100),
    time_horizon: int = Query(default=1000, ge=10, le=100000),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin", "clinician", "doctor"])),
):
    """
    Calculate theoretical Bayesian regret bound for Thompson Sampling.
    
    E[R_T] ≤ O(√(K·T·log(T)))
    
    Reference: Agrawal & Goyal, 2012
    """
    try:
        service = RegretAnalysisService(db)
        bound = service.get_bayesian_regret_bound(num_arms, time_horizon)
        return {
            "num_arms": num_arms,
            "time_horizon": time_horizon,
            "theoretical_bound": bound,
            "bound_formula": "E[R_T] ≤ C · √(K·T·log(T))",
            "reference": "Agrawal & Goyal (2012): Analysis of Thompson Sampling"
        }
    except Exception as e:
        logger.error(f"Error calculating bound: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COUNTERFACTUAL EXPLANATION ENDPOINTS
# ============================================================================

class CounterfactualRequest(BaseModel):
    """Request for counterfactual generation"""
    patient_features: Dict[str, Any]
    current_prediction: str
    desired_prediction: str = "low_risk"
    condition_type: str = "cardiovascular"
    max_features_to_change: int = 3


class CounterfactualResponse(BaseModel):
    """Counterfactual explanation response"""
    original_prediction: str
    counterfactual_prediction: str
    perturbations: List[Dict[str, Any]]
    total_change_cost: float
    confidence: float
    explanation_text: str
    actionable_steps: List[str]


@router.post("/counterfactual/generate", response_model=CounterfactualResponse)
async def generate_counterfactual(
    request: CounterfactualRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Generate counterfactual explanation for a prediction.
    
    Answers: "What would need to change for a different outcome?"
    
    XAI Feature: Provides GDPR-compliant "right to explanation".
    """
    try:
        service = CounterfactualExplanationService(db)
        result = service.generate_counterfactual(
            patient_features=request.patient_features,
            current_prediction=request.current_prediction,
            desired_prediction=request.desired_prediction,
            condition_type=request.condition_type,
            max_features_to_change=request.max_features_to_change,
        )
        return CounterfactualResponse(
            original_prediction=result.original_prediction,
            counterfactual_prediction=result.counterfactual_prediction,
            perturbations=[
                {
                    "feature": p.feature_name,
                    "current": p.current_value,
                    "target": p.counterfactual_value,
                    "change_magnitude": p.change_magnitude,
                    "is_actionable": p.is_actionable,
                    "clinical_meaning": p.clinical_meaning,
                }
                for p in result.perturbations
            ],
            total_change_cost=result.total_change_cost,
            confidence=result.confidence,
            explanation_text=result.explanation_text,
            actionable_steps=result.actionable_steps,
        )
    except Exception as e:
        logger.error(f"Error generating counterfactual: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/counterfactual/explain-suggestion/{suggestion_id}")
async def explain_suggestion_counterfactually(
    suggestion_id: UUID,
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Get comprehensive counterfactual explanation for an AI suggestion.
    """
    try:
        service = CounterfactualExplanationService(db)
        return service.explain_suggestion(suggestion_id, patient_id)
    except Exception as e:
        logger.error(f"Error explaining suggestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/counterfactual/recourse")
async def generate_actionable_recourse(
    request: CounterfactualRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Generate actionable recourse recommendations.
    
    Unlike counterfactuals (any change), recourse focuses on changes
    that clinicians/patients can actually make.
    """
    try:
        service = CounterfactualExplanationService(db)
        return service.generate_actionable_recourse(
            patient_features=request.patient_features,
            current_prediction=request.current_prediction,
            desired_prediction=request.desired_prediction,
        )
    except Exception as e:
        logger.error(f"Error generating recourse: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# LONGITUDINAL STUDY ENDPOINTS
# ============================================================================

class ITSAnalysisRequest(BaseModel):
    """Request for ITS analysis"""
    user_id: UUID
    metric: str
    intervention_date: datetime
    pre_period_days: int = 30
    post_period_days: int = 30


@router.post("/longitudinal/its-analysis")
async def run_its_analysis(
    request: ITSAnalysisRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Run Interrupted Time Series (ITS) analysis.
    
    ITS Model: Y_t = β0 + β1*time + β2*intervention + β3*time_after + ε
    
    Returns:
    - Level change (immediate effect)
    - Slope change (trend effect)
    - Effect sizes and significance
    
    Research Use: Quasi-experimental design for causality.
    """
    try:
        service = LongitudinalStudyService(db)
        result = service.interrupted_time_series_analysis(
            user_id=request.user_id,
            metric=request.metric,
            intervention_date=request.intervention_date,
            pre_period_days=request.pre_period_days,
            post_period_days=request.post_period_days,
        )
        return {
            "pre_intercept": result.pre_intercept,
            "pre_slope": result.pre_slope,
            "level_change": result.level_change,
            "slope_change": result.slope_change,
            "level_change_significant": result.level_change_significant,
            "slope_change_significant": result.slope_change_significant,
            "immediate_effect_size": result.immediate_effect_size,
            "sustained_effect_size": result.sustained_effect_size,
            "r_squared": result.r_squared,
            "rmse": result.rmse,
            "interpretation": result.interpretation,
        }
    except Exception as e:
        logger.error(f"Error running ITS analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/longitudinal/learning-curve/{user_id}")
async def get_learning_curve_analysis(
    user_id: UUID,
    metric: str = Query(default="time_to_target"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Analyze learning curve for a user.
    
    Power Law of Practice: T_n = T_1 * n^(-α)
    
    Returns:
    - Learning rate (α)
    - Asymptotic performance
    - Time to plateau
    
    Research Use: Demonstrates adaptation benefit over time.
    """
    try:
        service = LongitudinalStudyService(db)
        result = service.learning_curve_analysis(user_id, metric)
        return {
            "initial_performance": result.initial_performance,
            "learning_rate": result.learning_rate,
            "asymptotic_performance": result.asymptotic_performance,
            "time_to_90_percent": result.time_to_90_percent,
            "time_to_plateau": result.time_to_plateau,
            "r_squared": result.r_squared,
            "curve_type": result.curve_type,
            "interpretation": result.interpretation,
        }
    except Exception as e:
        logger.error(f"Error analyzing learning curve: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/longitudinal/cohort-retention")
async def get_cohort_retention_analysis(
    cohort_start_date: datetime,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Analyze cohort retention and feature adoption.
    
    Returns:
    - Day-over-day retention rates
    - Feature adoption curves
    - Churn point detection
    """
    try:
        service = LongitudinalStudyService(db)
        result = service.cohort_retention_analysis(cohort_start_date)
        return {
            "cohort_id": result.cohort_id,
            "cohort_size": result.cohort_size,
            "retention_rates": result.retention_rates,
            "feature_adoption": result.feature_adoption,
            "churn_points": result.churn_points,
            "interpretation": result.interpretation,
        }
    except Exception as e:
        logger.error(f"Error analyzing cohort: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# FAIRNESS ANALYSIS ENDPOINTS
# ============================================================================

@router.get("/fairness/audit")
async def run_fairness_audit(
    sensitive_attribute: str = Query(default="specialty"),
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Run comprehensive fairness audit.
    
    Analyzes:
    - Demographic Parity: P(Ŷ=1|A=0) = P(Ŷ=1|A=1)
    - Equalized Odds: TPR and FPR equal across groups
    - Individual Fairness: Similar users → similar adaptations
    - Calibration: Predicted probabilities match outcomes
    
    Research Use: Essential for ethical AI publication.
    """
    try:
        service = FairnessAnalysisService(db)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get data
        predictions = service._get_adaptation_predictions(start_date, end_date)
        users = service._get_user_profiles()
        adaptations = service._get_adaptations(start_date, end_date)
        
        # Run comprehensive audit
        result = service.comprehensive_fairness_audit(
            predictions, users, adaptations, sensitive_attribute
        )
        
        return {
            "analysis_date": result.analysis_date.isoformat(),
            "sensitive_attribute": result.sensitive_attribute,
            "overall_fairness_score": result.overall_fairness_score,
            "demographic_parity": {
                "is_fair": result.demographic_parity.is_fair,
                "parity_ratio": result.demographic_parity.parity_ratio,
                "parity_gap": result.demographic_parity.parity_gap,
                "interpretation": result.demographic_parity.interpretation,
            },
            "equalized_odds": {
                "is_fair": result.equalized_odds.is_fair,
                "tpr_gap": result.equalized_odds.tpr_gap,
                "fpr_gap": result.equalized_odds.fpr_gap,
                "interpretation": result.equalized_odds.interpretation,
            },
            "individual_fairness": {
                "is_fair": result.individual_fairness.is_fair,
                "consistency_score": result.individual_fairness.consistency_score,
                "violations": result.individual_fairness.lipschitz_violations,
                "interpretation": result.individual_fairness.interpretation,
            },
            "calibration": {
                "errors": result.calibration.calibration_error,
                "is_well_calibrated": result.calibration.is_well_calibrated,
                "interpretation": result.calibration.interpretation,
            },
            "critical_issues": result.critical_issues,
            "recommendations": result.recommendations,
        }
    except Exception as e:
        logger.error(f"Error running fairness audit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fairness/all-attributes")
async def run_all_fairness_audits(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Run fairness audit across all sensitive attributes.
    
    Returns summary for: specialty, experience_level, department, shift_type
    """
    try:
        service = FairnessAnalysisService(db)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        reports = service.analyze_adaptation_fairness(start_date, end_date)
        
        summary = {}
        for attr, report in reports.items():
            summary[attr] = {
                "overall_score": report.overall_fairness_score,
                "is_fair": len(report.critical_issues) == 0,
                "critical_issues": report.critical_issues,
            }
        
        return {
            "analysis_period_days": days,
            "attributes_analyzed": list(reports.keys()),
            "summary": summary,
            "overall_status": "FAIR" if all(s["is_fair"] for s in summary.values()) else "ISSUES_DETECTED",
        }
    except Exception as e:
        logger.error(f"Error running all audits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# COMBINED RESEARCH EXPORT
# ============================================================================

@router.get("/export/comprehensive-report")
async def export_comprehensive_research_report(
    user_id: Optional[UUID] = None,
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Export comprehensive research report for thesis/publication.
    
    Includes:
    - Regret analysis
    - Fairness audit
    - Learning curves
    - Statistical summaries
    """
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Initialize services
        regret_service = RegretAnalysisService(db)
        fairness_service = FairnessAnalysisService(db)
        longitudinal_service = LongitudinalStudyService(db)
        
        # Generate reports
        regret_report = regret_service.generate_regret_report(user_id, days)
        
        # Fairness across attributes
        fairness_reports = {}
        for attr in ["specialty", "department"]:
            try:
                predictions = fairness_service._get_adaptation_predictions(start_date, end_date)
                users = fairness_service._get_user_profiles()
                adaptations = fairness_service._get_adaptations(start_date, end_date)
                result = fairness_service.comprehensive_fairness_audit(
                    predictions, users, adaptations, attr
                )
                fairness_reports[attr] = {
                    "overall_score": result.overall_fairness_score,
                    "issues": result.critical_issues,
                }
            except Exception:
                fairness_reports[attr] = {"error": "Insufficient data"}
        
        return {
            "report_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "analysis_period_days": days,
                "user_scope": str(user_id) if user_id else "all_users",
            },
            "bandit_performance": regret_report,
            "fairness_analysis": fairness_reports,
            "export_format": "JSON",
            "citation_info": {
                "platform": "Self-Adaptive AI-Assisted EHR Research Platform",
                "architecture": "MAPE-K with Thompson Sampling",
                "key_features": [
                    "Contextual bandits for UI adaptation",
                    "Counterfactual explanations",
                    "Fairness monitoring",
                    "Longitudinal learning analysis",
                ],
            },
        }
    except Exception as e:
        logger.error(f"Error generating comprehensive report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

