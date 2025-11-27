"""
Medication schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class MedicationBase(BaseModel):
    """Base medication schema"""
    medication_name: str = Field(..., max_length=255, description="Name of medication")
    generic_name: Optional[str] = Field(None, max_length=255, description="Generic name")
    dosage: Optional[str] = Field(None, max_length=100, description="Dosage (e.g., '10mg')")
    frequency: Optional[str] = Field(None, max_length=100, description="Frequency (e.g., 'twice daily')")
    route: Optional[str] = Field(None, max_length=50, description="Route (oral, IV, IM, etc.)")
    quantity: Optional[str] = Field(None, max_length=50, description="Quantity (e.g., '30 tablets')")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date (if discontinued)")
    status: str = Field(default="active", description="Status: active, discontinued, completed")
    indication: Optional[str] = Field(None, max_length=500, description="Why prescribed")
    notes: Optional[str] = Field(None, description="Additional notes")


class MedicationCreate(MedicationBase):
    """Schema for creating a medication"""
    patient_id: UUID = Field(..., description="Patient ID")
    prescriber_id: Optional[UUID] = Field(None, description="Prescriber user ID")


class MedicationUpdate(BaseModel):
    """Schema for updating a medication"""
    medication_name: Optional[str] = Field(None, max_length=255)
    generic_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    quantity: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    indication: Optional[str] = None
    notes: Optional[str] = None


class MedicationResponse(MedicationBase):
    """Schema for medication response"""
    id: UUID
    patient_id: UUID
    prescriber_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

