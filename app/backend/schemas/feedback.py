"""
Feedback Schemas
Pydantic models for suggestion feedback API
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class FeedbackCreate(BaseModel):
    """Schema for creating new feedback"""
    suggestion_id: UUID = Field(..., description="ID of the suggestion")
    action: str = Field(..., description="Action taken: accept, ignore, not_relevant, partially_agree, incorrect")
    patient_id: Optional[UUID] = Field(None, description="Patient ID (optional, fetched from suggestion)")
    
    # Optional ratings (1-5 Likert scale)
    clinical_relevance: Optional[int] = Field(None, ge=1, le=5, description="Clinical relevance rating")
    agreement_rating: Optional[int] = Field(None, ge=1, le=5, description="Agreement with suggestion")
    explanation_quality: Optional[int] = Field(None, ge=1, le=5, description="Quality of explanation")
    would_act_on: Optional[int] = Field(None, ge=1, le=5, description="Would act on this suggestion")
    
    # Optional comments
    comment: Optional[str] = Field(None, max_length=2000, description="General comment")
    improvement_suggestion: Optional[str] = Field(None, max_length=2000, description="How to improve")
    
    class Config:
        json_schema_extra = {
            "example": {
                "suggestion_id": "123e4567-e89b-12d3-a456-426614174000",
                "action": "accept",
                "clinical_relevance": 4,
                "comment": "Helpful suggestion, aligned with clinical judgment"
            }
        }


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    id: UUID
    suggestion_id: UUID
    patient_id: Optional[UUID]
    clinician_id: UUID
    action: str
    suggestion_text: str
    suggestion_source: str
    suggestion_confidence: Optional[float]
    clinical_relevance: Optional[int]
    agreement_rating: Optional[int]
    explanation_quality: Optional[int]
    would_act_on: Optional[int]
    clinician_comment: Optional[str]
    improvement_suggestion: Optional[str]
    was_helpful: Optional[bool]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackStatsResponse(BaseModel):
    """Schema for aggregated feedback statistics"""
    total_feedback: int
    acceptance_rate: float
    actions: Dict[str, int]
    by_source: Dict[str, int]
    avg_ratings: Dict[str, float]
    learning_ready: bool
    period_days: int


class FeedbackTimelinePoint(BaseModel):
    """Single point in feedback timeline"""
    period: str
    total: int
    accepted: int
    ignored: int
    not_relevant: int
    acceptance_rate: float


class LearningEventResponse(BaseModel):
    """Schema for learning event response"""
    id: UUID
    event_type: str
    affected_source: str
    affected_rule_id: Optional[str]
    previous_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    trigger_reason: str
    feedback_count_used: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class ConfidenceAdjustmentResponse(BaseModel):
    """Schema for confidence adjustment query"""
    source: str
    adjustment: float
    description: str


class FeedbackAnalyticsResponse(BaseModel):
    """Comprehensive analytics response"""
    stats: FeedbackStatsResponse
    timeline: List[FeedbackTimelinePoint]
    recent_learning_events: List[LearningEventResponse]
    confidence_adjustments: Dict[str, float]

