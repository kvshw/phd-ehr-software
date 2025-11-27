"""
Suggestion schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class SuggestionBase(BaseModel):
    """Base suggestion schema"""
    patient_id: UUID = Field(..., description="ID of the patient")
    type: str = Field(..., max_length=50, description="Type of suggestion (e.g., 'vital_risk', 'diagnosis', 'image_analysis')")
    text: str = Field(..., min_length=1, max_length=1000, description="Suggestion text")
    source: str = Field(..., max_length=100, description="Source of suggestion (e.g., 'rules', 'vital_risk_model')")
    explanation: str = Field(..., min_length=1, max_length=2000, description="Explanation of the suggestion")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")


class SuggestionCreate(SuggestionBase):
    """Schema for creating a new suggestion"""
    pass


class SuggestionResponse(SuggestionBase):
    """Schema for returning suggestion data"""
    id: UUID = Field(..., description="Unique identifier for the suggestion")
    created_at: datetime = Field(..., description="Timestamp of when the suggestion was created")

    class Config:
        from_attributes = True


class SuggestionListResponse(BaseModel):
    """Schema for listing multiple suggestions"""
    items: List[SuggestionResponse]
    total: int
    patient_id: UUID

