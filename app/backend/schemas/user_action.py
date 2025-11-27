"""
User action schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class UserActionBase(BaseModel):
    """Base user action schema"""
    user_id: UUID = Field(..., description="ID of the user performing the action")
    patient_id: Optional[UUID] = Field(None, description="ID of the patient (if applicable)")
    action_type: str = Field(..., max_length=100, description="Type of action (e.g., 'navigation', 'suggestion_action', 'risk_change', 'model_output')")
    action_metadata: Optional[Dict[str, Any]] = Field(None, description="Action-specific metadata (JSON)")


class UserActionCreate(UserActionBase):
    """Schema for creating a new user action"""
    pass


class UserActionResponse(UserActionBase):
    """Schema for returning user action data"""
    id: UUID = Field(..., description="Unique identifier for the action")
    timestamp: datetime = Field(..., description="Timestamp of when the action occurred")

    class Config:
        from_attributes = True


# Specific action type schemas for validation
class NavigationActionMetadata(BaseModel):
    """Metadata for navigation actions"""
    from_section: Optional[str] = Field(None, description="Source section")
    to_section: Optional[str] = Field(None, description="Destination section")
    patient_id: Optional[str] = Field(None, description="Patient ID (as string for metadata)")


class SuggestionActionMetadata(BaseModel):
    """Metadata for suggestion actions"""
    suggestion_id: str = Field(..., description="ID of the suggestion")
    action: str = Field(..., description="Action taken: 'accept', 'ignore', 'not_relevant'")
    suggestion_type: Optional[str] = Field(None, description="Type of suggestion")
    suggestion_source: Optional[str] = Field(None, description="Source of suggestion")


class RiskChangeMetadata(BaseModel):
    """Metadata for risk change monitoring"""
    previous_risk_level: Optional[str] = Field(None, description="Previous risk level")
    new_risk_level: str = Field(..., description="New risk level")
    risk_score: Optional[float] = Field(None, description="Risk score")
    patient_id: Optional[str] = Field(None, description="Patient ID (as string for metadata)")


class ModelOutputMetadata(BaseModel):
    """Metadata for model output capture"""
    model_type: str = Field(..., description="Type of model (e.g., 'vital_risk', 'image_analysis', 'diagnosis_helper')")
    model_version: Optional[str] = Field(None, description="Model version")
    output_data: Dict[str, Any] = Field(..., description="Model output data")
    patient_id: Optional[str] = Field(None, description="Patient ID (as string for metadata)")

