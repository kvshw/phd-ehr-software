"""
Patient model
Enhanced with Finnish healthcare fields
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, Date, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from core.database import Base


class Patient(Base):
    """
    Patient model for EHR records
    
    Enhanced with Finnish healthcare fields:
    - Henkilötunnus (Finnish personal ID)
    - Kela Card number
    - Municipality registration
    - Contact information
    - Emergency contacts
    """
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(10), nullable=False)  # M, F, Other
    primary_diagnosis = Column(String(500), nullable=True)
    
    # Additional EHR fields
    past_medical_history = Column(Text, nullable=True)  # PMH
    past_surgical_history = Column(Text, nullable=True)  # PSH
    family_history = Column(Text, nullable=True)  # Family medical history
    social_history = Column(Text, nullable=True)  # Smoking, alcohol, occupation, etc.
    
    # Finnish identification
    henkilotunnus = Column(String(11), unique=True, nullable=True, index=True)  # Finnish personal ID (YYMMDD-XXXX)
    kela_card_number = Column(String(20), nullable=True, index=True)  # Kela health insurance card number
    date_of_birth = Column(Date, nullable=True)  # Can be derived from henkilötunnus
    
    # Healthcare eligibility (Finnish system)
    kela_eligible = Column(Boolean, nullable=True, default=True)  # Eligible for Kela benefits
    municipality_code = Column(String(10), nullable=True, index=True)  # Municipality code for public healthcare
    municipality_name = Column(String(255), nullable=True)
    primary_care_center = Column(String(255), nullable=True)  # Terveyskeskus assignment
    
    # International patients (EU/EEA)
    ehic_number = Column(String(20), nullable=True, index=True)  # European Health Insurance Card
    ehic_country_code = Column(String(3), nullable=True)  # ISO country code
    ehic_expiry_date = Column(Date, nullable=True)
    is_temporary_visitor = Column(Boolean, nullable=True, default=False)
    
    # Contact information (Finnish format)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    address = Column(Text, nullable=True)
    postal_code = Column(String(10), nullable=True)  # Finnish postal code format
    city = Column(String(100), nullable=True)
    
    # Emergency contact
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(100), nullable=True)
    
    # Registration status
    registration_status = Column(String(50), nullable=True, default='complete')  # complete, pending, incomplete
    registration_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Insurance (for compatibility with US-style systems)
    insurance_provider = Column(String(255), nullable=True)
    insurance_id = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

