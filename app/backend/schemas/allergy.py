"""
Allergy schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class AllergyBase(BaseModel):
    """Base allergy schema"""
    allergen: str = Field(..., max_length=255, description="Allergen name")
    allergen_type: Optional[str] = Field(None, max_length=50, description="Type: medication, food, environmental, other")
    severity: Optional[str] = Field(None, max_length=20, description="Severity: mild, moderate, severe, life-threatening")
    reaction: Optional[str] = Field(None, description="Description of reaction")
    onset_date: Optional[datetime] = Field(None, description="Date allergy identified")
    notes: Optional[str] = Field(None, description="Additional notes")
    status: str = Field(default="active", description="Status: active, resolved, unconfirmed")


class AllergyCreate(AllergyBase):
    """Schema for creating an allergy"""
    patient_id: UUID = Field(..., description="Patient ID")


class AllergyUpdate(BaseModel):
    """Schema for updating an allergy"""
    allergen: Optional[str] = Field(None, max_length=255)
    allergen_type: Optional[str] = None
    severity: Optional[str] = None
    reaction: Optional[str] = None
    onset_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class AllergyResponse(AllergyBase):
    """Schema for allergy response"""
    id: UUID
    patient_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

