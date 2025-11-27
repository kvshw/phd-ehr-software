"""
Visit/Encounter schemas for request/response validation
Supports both standard and Finnish visit types
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class VisitBase(BaseModel):
    """Base visit schema with common fields"""
    visit_type: str = Field(..., description="Visit type: outpatient, inpatient, emergency, follow_up, consult, procedure")
    visit_type_fi: Optional[str] = Field(None, description="Finnish visit type: terveyskeskus, erikoislääkäri, päivystys, kotikäynti, etäkonsultaatio, toimenpide")
    visit_status: str = Field("scheduled", description="Visit status: scheduled, in_progress, completed, cancelled, no_show")
    chief_complaint: Optional[str] = Field(None, description="Chief complaint")
    visit_date: Optional[datetime] = Field(None, description="Visit date and time")
    discharge_date: Optional[datetime] = Field(None, description="Discharge date and time")
    location: Optional[str] = Field(None, max_length=255, description="Location (room, department, etc.)")
    notes: Optional[str] = Field(None, description="Visit notes")
    
    # Finnish healthcare context
    service_type: Optional[str] = Field("public", description="Service type: public, private")
    municipality_code: Optional[str] = Field(None, max_length=10, description="Municipality code")
    kela_reimbursement_amount: Optional[Decimal] = Field(None, description="Kela reimbursement amount")
    referral_from: Optional[str] = Field(None, max_length=255, description="Referring unit/physician")
    referral_to: Optional[str] = Field(None, max_length=255, description="Referred to unit/physician")
    heti_number: Optional[str] = Field(None, max_length=20, description="Healthcare professional HETI number")


class VisitCreate(VisitBase):
    """Schema for creating a new visit"""
    patient_id: UUID = Field(..., description="Patient ID")
    user_id: UUID = Field(..., description="Primary provider user ID")


class VisitUpdate(BaseModel):
    """Schema for updating a visit"""
    visit_type: Optional[str] = None
    visit_type_fi: Optional[str] = None
    visit_status: Optional[str] = None
    chief_complaint: Optional[str] = None
    visit_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    location: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = None
    service_type: Optional[str] = None
    municipality_code: Optional[str] = Field(None, max_length=10)
    kela_reimbursement_amount: Optional[Decimal] = None
    referral_from: Optional[str] = Field(None, max_length=255)
    referral_to: Optional[str] = Field(None, max_length=255)
    heti_number: Optional[str] = Field(None, max_length=20)


class VisitResponse(VisitBase):
    """Schema for visit response"""
    id: UUID
    patient_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VisitListResponse(BaseModel):
    """Schema for paginated visit list response"""
    items: list[VisitResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

