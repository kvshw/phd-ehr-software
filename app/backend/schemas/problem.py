"""
Problem schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProblemBase(BaseModel):
    """Base problem schema"""
    problem_name: str = Field(..., max_length=500, description="Name of the problem")
    icd_code: Optional[str] = Field(None, max_length=20, description="ICD-10 code")
    status: str = Field(default="active", description="Status: active, resolved, chronic, inactive")
    onset_date: Optional[datetime] = Field(None, description="Date problem started")
    resolved_date: Optional[datetime] = Field(None, description="Date problem resolved")
    notes: Optional[str] = Field(None, description="Additional notes")


class ProblemCreate(ProblemBase):
    """Schema for creating a problem"""
    patient_id: UUID = Field(..., description="Patient ID")


class ProblemUpdate(BaseModel):
    """Schema for updating a problem"""
    problem_name: Optional[str] = Field(None, max_length=500)
    icd_code: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = None
    onset_date: Optional[datetime] = None
    resolved_date: Optional[datetime] = None
    notes: Optional[str] = None


class ProblemResponse(ProblemBase):
    """Schema for problem response"""
    id: UUID
    patient_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

