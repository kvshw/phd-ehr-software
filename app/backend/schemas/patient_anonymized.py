"""
Anonymized patient schemas for non-clinician roles
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class AnonymizedPatientResponse(BaseModel):
    """Anonymized patient response schema for researchers/admins"""
    id: UUID
    name: str = Field(..., description="Anonymized patient identifier (e.g., 'Patient abc12345')")
    age: int = Field(..., ge=0, le=150, description="Patient age")
    sex: str = Field(..., pattern="^(M|F|Other)$", description="Patient sex")
    primary_diagnosis: Optional[str] = Field(None, max_length=500, description="Primary diagnosis")
    
    # Medical history (kept for research, but may be generalized)
    past_medical_history: Optional[str] = Field(None, description="Past medical history")
    past_surgical_history: Optional[str] = Field(None, description="Past surgical history")
    family_history: Optional[str] = Field(None, description="Family medical history")
    social_history: Optional[str] = Field(None, description="Social history (generalized)")
    
    # Finnish identification - REMOVED
    henkilotunnus: Optional[str] = Field(None, description="REMOVED for privacy")
    kela_card_number: Optional[str] = Field(None, description="REMOVED for privacy")
    date_of_birth: Optional[str] = Field(None, description="Year only (YYYY-01-01) for age calculation")
    
    # Healthcare eligibility (generalized)
    kela_eligible: Optional[bool] = Field(None, description="Eligible for Kela benefits")
    municipality_code: Optional[str] = Field(None, max_length=10, description="Municipality code")
    municipality_name: Optional[str] = Field(None, max_length=255, description="Municipality name")
    primary_care_center: Optional[str] = Field(None, max_length=255, description="Primary care center")
    
    # International patients (generalized)
    ehic_country_code: Optional[str] = Field(None, max_length=3, description="EHIC country code (generalized)")
    is_temporary_visitor: Optional[bool] = Field(None, description="Is temporary visitor")
    # ehic_number removed
    
    # Contact information - REMOVED
    phone: Optional[str] = Field(None, description="REMOVED for privacy")
    email: Optional[str] = Field(None, description="REMOVED for privacy")
    address: Optional[str] = Field(None, description="REMOVED for privacy")
    postal_code: Optional[str] = Field(None, description="REMOVED for privacy")
    city: Optional[str] = Field(None, max_length=100, description="City (generalized location)")
    
    # Emergency contact - REMOVED
    emergency_contact_name: Optional[str] = Field(None, description="REMOVED for privacy")
    emergency_contact_phone: Optional[str] = Field(None, description="REMOVED for privacy")
    emergency_contact_relation: Optional[str] = Field(None, description="REMOVED for privacy")
    
    # Registration status
    registration_status: Optional[str] = Field(None, description="Registration status")
    
    # Insurance (generalized)
    insurance_provider: Optional[str] = Field(None, max_length=255, description="Insurance provider category")
    # insurance_id removed
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    is_anonymized: bool = Field(True, description="Flag indicating data is anonymized")
    anonymization_note: str = Field(
        "Data anonymized for research purposes. Direct identifiers removed.",
        description="Note about anonymization"
    )
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Patient abc12345",
                "age": 45,
                "sex": "M",
                "primary_diagnosis": "Hypertension",
                "city": "Helsinki",
                "municipality_code": "091",
                "is_anonymized": True,
                "anonymization_note": "Data anonymized for research purposes. Direct identifiers removed."
            }
        }


class AnonymizedPatientListResponse(BaseModel):
    """Schema for paginated anonymized patient list response"""
    items: list[AnonymizedPatientResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    anonymization_applied: bool = Field(True, description="Anonymization applied to all items")

