"""
Allergy model for tracking patient allergies and adverse reactions
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from core.database import Base


class Allergy(Base):
    """Allergy record model"""
    __tablename__ = "allergies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Allergy details
    allergen = Column(String(255), nullable=False)  # e.g., "Penicillin", "Latex", "Peanuts"
    allergen_type = Column(String(50), nullable=True)  # medication, food, environmental, other
    severity = Column(String(20), nullable=True)  # mild, moderate, severe, life-threatening
    reaction = Column(Text, nullable=True)  # Description of reaction (e.g., "Hives", "Anaphylaxis")
    
    # Dates
    onset_date = Column(DateTime(timezone=True), nullable=True)  # When allergy was first identified
    
    # Additional info
    notes = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), nullable=False, default="active")  # active, resolved, unconfirmed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", backref="allergies")

