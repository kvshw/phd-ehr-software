"""
Feedback API Routes
Endpoints for managing clinician feedback on AI suggestions
and viewing self-adaptive learning history
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, require_researcher, require_admin
from schemas.auth import TokenData
from schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
    FeedbackStatsResponse,
    FeedbackTimelinePoint,
    LearningEventResponse,
    ConfidenceAdjustmentResponse,
    FeedbackAnalyticsResponse,
)
from services.feedback_service import FeedbackService
from models.suggestion_feedback import SuggestionFeedback, LearningEvent

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Submit feedback on an AI suggestion.
    
    This is called when a clinician accepts, ignores, or marks a suggestion as not relevant.
    The feedback is used for:
    - Research analytics
    - Self-adaptive AI learning
    - MAPE-K knowledge base
    """
    # Prepare ratings dict
    ratings = {}
    if feedback_data.clinical_relevance:
        ratings["clinical_relevance"] = feedback_data.clinical_relevance
    if feedback_data.agreement_rating:
        ratings["agreement_rating"] = feedback_data.agreement_rating
    if feedback_data.explanation_quality:
        ratings["explanation_quality"] = feedback_data.explanation_quality
    if feedback_data.would_act_on:
        ratings["would_act_on"] = feedback_data.would_act_on
    
    # Prepare comments dict
    comments = {}
    if feedback_data.comment:
        comments["comment"] = feedback_data.comment
    if feedback_data.improvement_suggestion:
        comments["improvement"] = feedback_data.improvement_suggestion
    
    feedback = FeedbackService.create_feedback(
        db=db,
        suggestion_id=feedback_data.suggestion_id,
        clinician_id=current_user.user_id,
        action=feedback_data.action,
        patient_id=feedback_data.patient_id,
        ratings=ratings if ratings else None,
        comments=comments if comments else None,
    )
    
    return feedback


@router.get("/stats", response_model=FeedbackStatsResponse)
async def get_feedback_stats(
    source: Optional[str] = Query(None, description="Filter by suggestion source"),
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_researcher)
):
    """
    Get aggregated feedback statistics.
    
    Researcher and admin only.
    """
    stats = FeedbackService.get_feedback_stats(db, source=source, days=days)
    return stats


@router.get("/timeline", response_model=List[FeedbackTimelinePoint])
async def get_feedback_timeline(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    granularity: str = Query("day", description="Granularity: hour, day, or week"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_researcher)
):
    """
    Get feedback trends over time for visualization.
    
    Researcher and admin only.
    """
    if granularity not in ["hour", "day", "week"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Granularity must be 'hour', 'day', or 'week'"
        )
    
    timeline = FeedbackService.get_feedback_timeline(db, days=days, granularity=granularity)
    return timeline


@router.get("/learning-events", response_model=List[LearningEventResponse])
async def get_learning_events(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of events"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_researcher)
):
    """
    Get history of self-adaptive learning events.
    
    Shows when and why the AI system adjusted its behavior based on feedback.
    Researcher and admin only.
    """
    events = FeedbackService.get_learning_history(db, limit=limit)
    return events


@router.get("/confidence-adjustments")
async def get_confidence_adjustments(
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_researcher)
):
    """
    Get current confidence adjustments for all sources.
    
    Shows how much the AI has adjusted confidence based on learning.
    Researcher and admin only.
    """
    sources = ["rules", "ai_model", "hybrid", "vital_risk", "image_analysis", "diagnosis_helper"]
    
    adjustments = {}
    for source in sources:
        adj = FeedbackService.get_confidence_adjustment(db, source)
        adjustments[source] = {
            "adjustment": adj,
            "description": f"{'Increased' if adj > 0 else 'Decreased' if adj < 0 else 'No change'} by {abs(adj)*100:.1f}%"
        }
    
    return adjustments


@router.get("/analytics", response_model=FeedbackAnalyticsResponse)
async def get_feedback_analytics(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_researcher)
):
    """
    Get comprehensive feedback analytics.
    
    Includes stats, timeline, learning events, and confidence adjustments.
    Researcher and admin only.
    """
    stats = FeedbackService.get_feedback_stats(db, days=days)
    timeline = FeedbackService.get_feedback_timeline(db, days=days)
    learning_events = FeedbackService.get_learning_history(db, limit=10)
    
    sources = ["rules", "ai_model", "hybrid"]
    adjustments = {
        source: FeedbackService.get_confidence_adjustment(db, source)
        for source in sources
    }
    
    return {
        "stats": stats,
        "timeline": timeline,
        "recent_learning_events": learning_events,
        "confidence_adjustments": adjustments,
    }


@router.get("/my-feedback", response_model=List[FeedbackResponse])
async def get_my_feedback(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get feedback submitted by the current clinician.
    
    Allows clinicians to see their own feedback history.
    """
    feedback = FeedbackService.get_feedback_by_clinician(
        db,
        clinician_id=current_user.user_id,
        limit=limit
    )
    return feedback


@router.get("/suggestion/{suggestion_id}", response_model=List[FeedbackResponse])
async def get_suggestion_feedback(
    suggestion_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_researcher)
):
    """
    Get all feedback for a specific suggestion.
    
    Researcher and admin only.
    """
    feedback = FeedbackService.get_feedback_by_suggestion(db, suggestion_id)
    return feedback

