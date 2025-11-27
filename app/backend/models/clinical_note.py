"""
Clinical Note model for progress notes and documentation
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from core.database import Base


class ClinicalNote(Base):
    """Clinical progress note model"""
    __tablename__ = "clinical_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # Clinician who wrote the note
    
    # Note metadata
    note_type = Column(String(50), nullable=False, default="progress")  # progress, admission, discharge, consult, etc.
    encounter_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    
    # SOAP note structure
    chief_complaint = Column(Text, nullable=True)  # CC
    history_of_present_illness = Column(Text, nullable=True)  # HPI
    review_of_systems = Column(Text, nullable=True)  # ROS
    physical_exam = Column(Text, nullable=True)  # Physical Examination
    assessment = Column(Text, nullable=True)  # Assessment
    plan = Column(Text, nullable=True)  # Plan
    
    # Full note text (for free-form notes)
    note_text = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", backref="clinical_notes")
    author = relationship("User", backref="clinical_notes")

