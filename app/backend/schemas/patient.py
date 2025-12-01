"""
Patient schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
from datetime import datetime, date
from uuid import UUID


class PatientBase(BaseModel):
    """Base patient schema with common fields"""
    name: str = Field(..., min_length=1, max_length=255, description="Patient name")
    age: int = Field(..., ge=0, le=150, description="Patient age")
    sex: str = Field(..., pattern="^(M|F|Other)$", description="Patient sex (M, F, Other)")
    primary_diagnosis: Optional[str] = Field(None, max_length=500, description="Primary diagnosis")
    past_medical_history: Optional[str] = Field(None, description="Past medical history (PMH)")
    past_surgical_history: Optional[str] = Field(None, description="Past surgical history (PSH)")
    family_history: Optional[str] = Field(None, description="Family medical history")
    social_history: Optional[str] = Field(None, description="Social history (smoking, alcohol, occupation, etc.)")
    
    # Finnish identification fields
    henkilotunnus: Optional[str] = Field(None, max_length=11, description="Finnish personal ID (YYMMDD-XXXX)")
    kela_card_number: Optional[str] = Field(None, max_length=20, description="Kela health insurance card number")
    date_of_birth: Optional[str] = Field(None, description="Date of birth (YYYY-MM-DD), can be auto-filled from henkilötunnus")
    
    # Finnish healthcare eligibility
    kela_eligible: Optional[bool] = Field(True, description="Eligible for Kela benefits")
    municipality_code: Optional[str] = Field(None, max_length=10, description="Municipality code for public healthcare")
    municipality_name: Optional[str] = Field(None, max_length=255, description="Municipality name")
    primary_care_center: Optional[str] = Field(None, max_length=255, description="Primary care center (Terveyskeskus)")
    
    # International patients (EU/EEA)
    ehic_number: Optional[str] = Field(None, max_length=20, description="European Health Insurance Card number")
    ehic_country_code: Optional[str] = Field(None, max_length=3, description="EHIC country code (ISO)")
    ehic_expiry_date: Optional[str] = Field(None, description="EHIC expiry date (YYYY-MM-DD)")
    is_temporary_visitor: Optional[bool] = Field(False, description="Is temporary visitor from EU/EEA")
    
    # Contact information
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    address: Optional[str] = Field(None, description="Street address")
    postal_code: Optional[str] = Field(None, max_length=10, description="Postal code")
    city: Optional[str] = Field(None, max_length=100, description="City")
    
    # Emergency contact
    emergency_contact_name: Optional[str] = Field(None, max_length=255, description="Emergency contact name")
    emergency_contact_phone: Optional[str] = Field(None, max_length=20, description="Emergency contact phone")
    emergency_contact_relation: Optional[str] = Field(None, max_length=100, description="Emergency contact relation")
    
    # Registration status
    registration_status: Optional[str] = Field("complete", description="Registration status: complete, pending, incomplete")
    
    # Insurance (for compatibility)
    insurance_provider: Optional[str] = Field(None, max_length=255, description="Insurance provider")
    insurance_id: Optional[str] = Field(None, max_length=100, description="Insurance ID")


class PatientCreate(PatientBase):
    """Schema for creating a new patient"""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating a patient"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    sex: Optional[str] = Field(None, pattern="^(M|F|Other)$")
    primary_diagnosis: Optional[str] = Field(None, max_length=500)
    past_medical_history: Optional[str] = None
    past_surgical_history: Optional[str] = None
    family_history: Optional[str] = None
    social_history: Optional[str] = None
    
    # Finnish fields (all optional for updates)
    henkilotunnus: Optional[str] = Field(None, max_length=11)
    kela_card_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[str] = None
    kela_eligible: Optional[bool] = None
    municipality_code: Optional[str] = Field(None, max_length=10)
    municipality_name: Optional[str] = Field(None, max_length=255)
    primary_care_center: Optional[str] = Field(None, max_length=255)
    ehic_number: Optional[str] = Field(None, max_length=20)
    ehic_country_code: Optional[str] = Field(None, max_length=3)
    ehic_expiry_date: Optional[str] = None
    is_temporary_visitor: Optional[bool] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = None
    postal_code: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=100)
    emergency_contact_name: Optional[str] = Field(None, max_length=255)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    emergency_contact_relation: Optional[str] = Field(None, max_length=100)
    registration_status: Optional[str] = None
    insurance_provider: Optional[str] = Field(None, max_length=255)
    insurance_id: Optional[str] = Field(None, max_length=100)


class PatientResponse(PatientBase):
    """Schema for patient response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    @field_validator('date_of_birth', 'ehic_expiry_date', mode='before')
    @classmethod
    def convert_date_to_string(cls, v: Any) -> Optional[str]:
        """Convert date objects to ISO format strings"""
        if v is None:
            return None
        if isinstance(v, date):
            return v.isoformat()
        if isinstance(v, str):
            return v
        return str(v)

    class Config:
        from_attributes = True


class PatientListResponse(BaseModel):
    """Schema for paginated patient list response"""
    items: list[PatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class PatientSearchParams(BaseModel):
    """Schema for patient search parameters"""
    name: Optional[str] = Field(None, description="Search by name (partial match)")
    age_min: Optional[int] = Field(None, ge=0, description="Minimum age")
    age_max: Optional[int] = Field(None, le=150, description="Maximum age")
    sex: Optional[str] = Field(None, pattern="^(M|F|Other)$", description="Filter by sex")
    diagnosis: Optional[str] = Field(None, description="Search in primary diagnosis (partial match)")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

