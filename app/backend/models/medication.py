"""
Medication model for tracking patient medications
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from core.database import Base


class Medication(Base):
    """Medication record model"""
    __tablename__ = "medications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    prescriber_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Clinician who prescribed
    
    # Medication details
    medication_name = Column(String(255), nullable=False)
    generic_name = Column(String(255), nullable=True)
    dosage = Column(String(100), nullable=True)  # e.g., "10mg", "500mg twice daily"
    frequency = Column(String(100), nullable=True)  # e.g., "twice daily", "as needed"
    route = Column(String(50), nullable=True)  # oral, IV, IM, topical, etc.
    quantity = Column(String(50), nullable=True)  # e.g., "30 tablets"
    
    # Dates
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)  # When stopped (if applicable)
    
    # Status
    status = Column(String(20), nullable=False, default="active")  # active, discontinued, completed
    
    # Additional info
    indication = Column(String(500), nullable=True)  # Why it was prescribed
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", backref="medications")
    prescriber = relationship("User", backref="prescribed_medications")

