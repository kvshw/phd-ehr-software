"""
Clinical Note schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ClinicalNoteBase(BaseModel):
    """Base clinical note schema"""
    note_type: str = Field(default="progress", description="Type of note (progress, admission, discharge, consult)")
    encounter_date: datetime = Field(default_factory=datetime.now, description="Date/time of encounter")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint (CC)")
    history_of_present_illness: Optional[str] = Field(None, description="History of present illness (HPI)")
    review_of_systems: Optional[str] = Field(None, description="Review of systems (ROS)")
    physical_exam: Optional[str] = Field(None, description="Physical examination findings")
    assessment: Optional[str] = Field(None, description="Assessment")
    plan: Optional[str] = Field(None, description="Plan")
    note_text: Optional[str] = Field(None, description="Free-form note text")


class ClinicalNoteCreate(ClinicalNoteBase):
    """Schema for creating a clinical note"""
    patient_id: UUID = Field(..., description="Patient ID")


class ClinicalNoteUpdate(BaseModel):
    """Schema for updating a clinical note"""
    note_type: Optional[str] = None
    encounter_date: Optional[datetime] = None
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    review_of_systems: Optional[str] = None
    physical_exam: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None
    note_text: Optional[str] = None


class ClinicalNoteResponse(ClinicalNoteBase):
    """Schema for clinical note response"""
    id: UUID
    patient_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

