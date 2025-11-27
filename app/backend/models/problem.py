"""
Problem List model for tracking active and resolved medical problems
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from core.database import Base


class Problem(Base):
    """Problem list entry model"""
    __tablename__ = "problems"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Problem details
    problem_name = Column(String(500), nullable=False)  # e.g., "Type 2 Diabetes", "Hypertension"
    icd_code = Column(String(20), nullable=True)  # ICD-10 code if available
    status = Column(String(20), nullable=False, default="active")  # active, resolved, chronic, inactive
    
    # Dates
    onset_date = Column(DateTime(timezone=True), nullable=True)  # When problem started
    resolved_date = Column(DateTime(timezone=True), nullable=True)  # When resolved (if applicable)
    
    # Additional info
    notes = Column(Text, nullable=True)  # Additional notes about the problem
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", backref="problems")

