"""
Suggestion Feedback Model
Stores clinician feedback on AI suggestions for learning and adaptation
"""
from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from core.database import Base


class FeedbackAction(str, enum.Enum):
    """Types of actions clinicians can take on suggestions"""
    ACCEPT = "accept"
    IGNORE = "ignore"
    NOT_RELEVANT = "not_relevant"
    PARTIALLY_AGREE = "partially_agree"
    INCORRECT = "incorrect"


class SuggestionFeedback(Base):
    """
    Stores individual feedback events from clinicians on AI suggestions.
    Used for:
    - Tracking suggestion acceptance/rejection rates
    - Training AI models (self-adaptive learning)
    - Research analytics on AI performance
    - MAPE-K knowledge base
    """
    __tablename__ = "suggestion_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Suggestion reference
    suggestion_id = Column(UUID(as_uuid=True), ForeignKey("suggestions.id"), nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    clinician_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Action taken
    action = Column(String(50), nullable=False, index=True)  # accept, ignore, not_relevant, etc.
    
    # Context at time of feedback
    suggestion_text = Column(Text, nullable=False)  # Snapshot of suggestion text
    suggestion_source = Column(String(100), nullable=False)  # rules, ai_model, hybrid
    suggestion_confidence = Column(Float, nullable=True)  # Original confidence score
    suggestion_type = Column(String(100), nullable=True)  # Type of suggestion
    
    # Clinician ratings (1-5 Likert scale, nullable for quick actions)
    clinical_relevance = Column(Integer, nullable=True)
    agreement_rating = Column(Integer, nullable=True)
    explanation_quality = Column(Integer, nullable=True)
    would_act_on = Column(Integer, nullable=True)
    
    # Free text feedback
    clinician_comment = Column(Text, nullable=True)
    improvement_suggestion = Column(Text, nullable=True)
    
    # For learning
    was_helpful = Column(Boolean, nullable=True)  # Simple helpful/not helpful flag
    
    # Context data for pattern learning
    patient_age = Column(Integer, nullable=True)
    patient_sex = Column(String(10), nullable=True)
    patient_diagnosis = Column(String(500), nullable=True)
    
    # Learning metadata
    feedback_used_for_training = Column(Boolean, default=False)  # Has this been used to update model?
    training_batch_id = Column(String(100), nullable=True)  # Which training batch used this
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    suggestion = relationship("Suggestion", backref="feedback")
    patient = relationship("Patient", backref="suggestion_feedback")
    clinician = relationship("User", backref="suggestion_feedback")


class FeedbackAggregation(Base):
    """
    Aggregated feedback statistics for suggestions.
    Updated periodically to track patterns for self-adaptive AI.
    """
    __tablename__ = "feedback_aggregation"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # What this aggregation is for
    suggestion_source = Column(String(100), nullable=False, index=True)  # rules, ai_model, hybrid
    suggestion_type = Column(String(100), nullable=True, index=True)
    rule_id = Column(String(100), nullable=True, index=True)  # For tracking specific rules
    
    # Aggregated statistics
    total_shown = Column(Integer, default=0)
    total_accepted = Column(Integer, default=0)
    total_ignored = Column(Integer, default=0)
    total_not_relevant = Column(Integer, default=0)
    total_incorrect = Column(Integer, default=0)
    
    # Calculated metrics
    acceptance_rate = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    
    # Average ratings
    avg_clinical_relevance = Column(Float, nullable=True)
    avg_agreement = Column(Float, nullable=True)
    avg_explanation_quality = Column(Float, nullable=True)
    
    # Confidence adjustment (for self-adaptive AI)
    confidence_adjustment = Column(Float, default=0.0)  # Positive = increase, negative = decrease
    
    # Time period
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LearningEvent(Base):
    """
    Tracks when and how the AI system learned from feedback.
    Creates an audit trail for self-adaptive behavior.
    """
    __tablename__ = "learning_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # What triggered learning
    event_type = Column(String(100), nullable=False)  # confidence_adjustment, rule_disabled, etc.
    
    # What was affected
    affected_source = Column(String(100), nullable=False)  # rules, ai_model, hybrid
    affected_rule_id = Column(String(100), nullable=True)
    
    # What changed
    previous_value = Column(JSONB, nullable=True)  # Previous configuration
    new_value = Column(JSONB, nullable=True)  # New configuration
    
    # Reasoning
    trigger_reason = Column(Text, nullable=False)  # Why this learning occurred
    feedback_count_used = Column(Integer, default=0)  # How many feedback items triggered this
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(100), default="system")  # system or admin user
    
    # Audit
    is_active = Column(Boolean, default=True)  # Can be rolled back
    rollback_event_id = Column(UUID(as_uuid=True), nullable=True)  # If rolled back, points to that event

