"""
Feedback Service
Handles clinician feedback on AI suggestions and enables self-adaptive learning.
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from models.suggestion_feedback import SuggestionFeedback, FeedbackAggregation, LearningEvent
from models.suggestion import Suggestion
from models.patient import Patient
from schemas.feedback import FeedbackCreate, FeedbackResponse

logger = logging.getLogger(__name__)


class FeedbackService:
    """Service for managing suggestion feedback and self-adaptive learning"""
    
    # Thresholds for self-adaptive behavior
    MIN_FEEDBACK_FOR_LEARNING = 10  # Minimum feedback items before adjusting
    LOW_ACCEPTANCE_THRESHOLD = 0.3  # Below this, reduce confidence
    HIGH_ACCEPTANCE_THRESHOLD = 0.7  # Above this, increase confidence
    CONFIDENCE_ADJUSTMENT_STEP = 0.05  # How much to adjust confidence
    
    @staticmethod
    def create_feedback(
        db: Session,
        suggestion_id: UUID,
        clinician_id: UUID,
        action: str,
        patient_id: Optional[UUID] = None,
        ratings: Optional[Dict[str, int]] = None,
        comments: Optional[Dict[str, str]] = None,
    ) -> SuggestionFeedback:
        """
        Record clinician feedback on a suggestion.
        
        Args:
            db: Database session
            suggestion_id: ID of the suggestion being evaluated
            clinician_id: ID of the clinician providing feedback
            action: Action taken (accept, ignore, not_relevant, etc.)
            patient_id: Optional patient ID (fetched from suggestion if not provided)
            ratings: Optional dict of Likert scale ratings
            comments: Optional dict of text comments
            
        Returns:
            Created feedback record
        """
        # Get the original suggestion for context
        suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
        
        if not suggestion:
            logger.warning(f"Feedback submitted for non-existent suggestion: {suggestion_id}")
            # Create feedback anyway with available info
            suggestion_text = "Unknown suggestion"
            suggestion_source = "unknown"
            suggestion_confidence = None
            patient_id = patient_id
        else:
            suggestion_text = suggestion.text
            suggestion_source = suggestion.source
            suggestion_confidence = suggestion.confidence
            patient_id = patient_id or suggestion.patient_id
        
        # Check if feedback already exists for this suggestion from this clinician
        existing_feedback = db.query(SuggestionFeedback).filter(
            and_(
                SuggestionFeedback.suggestion_id == suggestion_id,
                SuggestionFeedback.clinician_id == clinician_id
            )
        ).first()
        
        if existing_feedback:
            # Update existing feedback instead of creating duplicate
            logger.info(f"Updating existing feedback for suggestion {suggestion_id} from clinician {clinician_id}")
            existing_feedback.action = action
            if ratings:
                existing_feedback.clinical_relevance = ratings.get("clinical_relevance")
                existing_feedback.agreement_rating = ratings.get("agreement_rating")
                existing_feedback.explanation_quality = ratings.get("explanation_quality")
                existing_feedback.would_act_on = ratings.get("would_act_on")
            if comments:
                existing_feedback.clinician_comment = comments.get("comment")
                existing_feedback.improvement_suggestion = comments.get("improvement")
            existing_feedback.was_helpful = action == "accept"
            db.commit()
            db.refresh(existing_feedback)
            return existing_feedback
        
        # Get patient context if available
        patient_age = None
        patient_sex = None
        patient_diagnosis = None
        
        if patient_id:
            patient = db.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                patient_age = patient.age
                patient_sex = patient.sex
                patient_diagnosis = patient.primary_diagnosis
        
        # Create feedback record
        feedback = SuggestionFeedback(
            suggestion_id=suggestion_id,
            patient_id=patient_id,
            clinician_id=clinician_id,
            action=action,
            suggestion_text=suggestion_text,
            suggestion_source=suggestion_source,
            suggestion_confidence=suggestion_confidence,
            patient_age=patient_age,
            patient_sex=patient_sex,
            patient_diagnosis=patient_diagnosis,
            # Ratings
            clinical_relevance=ratings.get("clinical_relevance") if ratings else None,
            agreement_rating=ratings.get("agreement_rating") if ratings else None,
            explanation_quality=ratings.get("explanation_quality") if ratings else None,
            would_act_on=ratings.get("would_act_on") if ratings else None,
            # Comments
            clinician_comment=comments.get("comment") if comments else None,
            improvement_suggestion=comments.get("improvement") if comments else None,
            # Derived
            was_helpful=action == "accept",
        )
        
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        logger.info(f"Feedback recorded: {action} on suggestion {suggestion_id} by clinician {clinician_id}")
        
        # Trigger learning check asynchronously
        FeedbackService._check_learning_trigger(db, suggestion_source)
        
        return feedback
    
    @staticmethod
    def get_feedback_by_suggestion(
        db: Session,
        suggestion_id: UUID
    ) -> List[SuggestionFeedback]:
        """Get all feedback for a specific suggestion"""
        return db.query(SuggestionFeedback).filter(
            SuggestionFeedback.suggestion_id == suggestion_id
        ).order_by(SuggestionFeedback.created_at.desc()).all()
    
    @staticmethod
    def get_feedback_by_clinician(
        db: Session,
        clinician_id: UUID,
        limit: int = 50
    ) -> List[SuggestionFeedback]:
        """Get feedback provided by a specific clinician"""
        return db.query(SuggestionFeedback).filter(
            SuggestionFeedback.clinician_id == clinician_id
        ).order_by(SuggestionFeedback.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_feedback_stats(
        db: Session,
        source: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get aggregated feedback statistics.
        
        Args:
            db: Database session
            source: Optional filter by suggestion source
            days: Number of days to look back
            
        Returns:
            Dict with statistics
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        query = db.query(SuggestionFeedback).filter(
            SuggestionFeedback.created_at >= since
        )
        
        if source:
            query = query.filter(SuggestionFeedback.suggestion_source == source)
        
        all_feedback = query.all()
        
        if not all_feedback:
            return {
                "total_feedback": 0,
                "acceptance_rate": 0.0,
                "actions": {},
                "by_source": {},
                "avg_ratings": {},
                "learning_ready": False,
                "period_days": days,
            }
        
        # Count by action
        action_counts = {}
        for fb in all_feedback:
            action_counts[fb.action] = action_counts.get(fb.action, 0) + 1
        
        # Count by source
        source_counts = {}
        for fb in all_feedback:
            source_counts[fb.suggestion_source] = source_counts.get(fb.suggestion_source, 0) + 1
        
        # Calculate acceptance rate
        total = len(all_feedback)
        accepted = action_counts.get("accept", 0)
        acceptance_rate = accepted / total if total > 0 else 0.0
        
        # Average ratings (only for feedback with ratings)
        rated_feedback = [fb for fb in all_feedback if fb.clinical_relevance is not None]
        avg_ratings = {}
        if rated_feedback:
            avg_ratings = {
                "clinical_relevance": sum(fb.clinical_relevance for fb in rated_feedback) / len(rated_feedback),
                "agreement": sum(fb.agreement_rating for fb in rated_feedback if fb.agreement_rating) / len([fb for fb in rated_feedback if fb.agreement_rating]),
                "explanation_quality": sum(fb.explanation_quality for fb in rated_feedback if fb.explanation_quality) / len([fb for fb in rated_feedback if fb.explanation_quality]),
            }
        
        return {
            "total_feedback": total,
            "acceptance_rate": round(acceptance_rate, 3),
            "actions": action_counts,
            "by_source": source_counts,
            "avg_ratings": avg_ratings,
            "learning_ready": total >= FeedbackService.MIN_FEEDBACK_FOR_LEARNING,
            "period_days": days,
        }
    
    @staticmethod
    def get_feedback_timeline(
        db: Session,
        days: int = 30,
        granularity: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Get feedback trends over time for visualization.
        
        Args:
            db: Database session
            days: Number of days to include
            granularity: "hour", "day", or "week"
            
        Returns:
            List of time-series data points
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)
        
        feedback = db.query(SuggestionFeedback).filter(
            SuggestionFeedback.created_at >= since
        ).order_by(SuggestionFeedback.created_at).all()
        
        # Group by time period
        timeline = {}
        for fb in feedback:
            if granularity == "hour":
                key = fb.created_at.strftime("%Y-%m-%d %H:00")
            elif granularity == "week":
                key = fb.created_at.strftime("%Y-W%W")
            else:  # day
                key = fb.created_at.strftime("%Y-%m-%d")
            
            if key not in timeline:
                timeline[key] = {
                    "period": key,
                    "total": 0,
                    "accepted": 0,
                    "ignored": 0,
                    "not_relevant": 0,
                }
            
            timeline[key]["total"] += 1
            if fb.action == "accept":
                timeline[key]["accepted"] += 1
            elif fb.action == "ignore":
                timeline[key]["ignored"] += 1
            elif fb.action == "not_relevant":
                timeline[key]["not_relevant"] += 1
        
        # Calculate acceptance rate for each period
        result = []
        for key, data in sorted(timeline.items()):
            data["acceptance_rate"] = round(
                data["accepted"] / data["total"] if data["total"] > 0 else 0,
                3
            )
            result.append(data)
        
        return result
    
    @staticmethod
    def _check_learning_trigger(db: Session, source: str) -> Optional[LearningEvent]:
        """
        Check if we have enough feedback to trigger self-adaptive learning.
        
        This is called after each feedback is recorded.
        """
        # Get recent feedback for this source
        recent = datetime.now(timezone.utc) - timedelta(days=7)
        feedback = db.query(SuggestionFeedback).filter(
            and_(
                SuggestionFeedback.suggestion_source == source,
                SuggestionFeedback.created_at >= recent,
                SuggestionFeedback.feedback_used_for_training == False
            )
        ).all()
        
        if len(feedback) < FeedbackService.MIN_FEEDBACK_FOR_LEARNING:
            return None
        
        # Calculate acceptance rate
        accepted = sum(1 for fb in feedback if fb.action == "accept")
        acceptance_rate = accepted / len(feedback)
        
        # Determine if adjustment needed
        adjustment = 0.0
        reason = ""
        
        if acceptance_rate < FeedbackService.LOW_ACCEPTANCE_THRESHOLD:
            adjustment = -FeedbackService.CONFIDENCE_ADJUSTMENT_STEP
            reason = f"Low acceptance rate ({acceptance_rate:.1%}) indicates suggestions may be less relevant"
        elif acceptance_rate > FeedbackService.HIGH_ACCEPTANCE_THRESHOLD:
            adjustment = FeedbackService.CONFIDENCE_ADJUSTMENT_STEP
            reason = f"High acceptance rate ({acceptance_rate:.1%}) indicates suggestions are highly relevant"
        else:
            # No adjustment needed
            return None
        
        # Create learning event
        learning_event = LearningEvent(
            event_type="confidence_adjustment",
            affected_source=source,
            previous_value={"acceptance_rate": acceptance_rate, "adjustment": 0},
            new_value={"acceptance_rate": acceptance_rate, "adjustment": adjustment},
            trigger_reason=reason,
            feedback_count_used=len(feedback),
        )
        
        db.add(learning_event)
        
        # Mark feedback as used for training
        for fb in feedback:
            fb.feedback_used_for_training = True
        
        db.commit()
        
        logger.info(f"Learning event created: {adjustment:+.2f} confidence adjustment for {source}")
        
        return learning_event
    
    @staticmethod
    def get_learning_history(
        db: Session,
        limit: int = 50
    ) -> List[LearningEvent]:
        """Get history of learning events"""
        return db.query(LearningEvent).order_by(
            LearningEvent.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_confidence_adjustment(
        db: Session,
        source: str
    ) -> float:
        """
        Get the cumulative confidence adjustment for a source.
        Used by AI services to adjust their confidence scores.
        
        Returns:
            Float adjustment to add to base confidence
        """
        events = db.query(LearningEvent).filter(
            and_(
                LearningEvent.affected_source == source,
                LearningEvent.event_type == "confidence_adjustment",
                LearningEvent.is_active == True
            )
        ).all()
        
        total_adjustment = sum(
            event.new_value.get("adjustment", 0) if event.new_value else 0
            for event in events
        )
        
        # Cap adjustment to reasonable range
        return max(-0.3, min(0.3, total_adjustment))

