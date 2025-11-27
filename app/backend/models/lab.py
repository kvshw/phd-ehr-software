"""
Laboratory results model
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from core.database import Base


class Lab(Base):
    """Laboratory results model for patient lab data"""
    __tablename__ = "labs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    lab_type = Column(String(100), nullable=False, index=True, comment="Type of lab test (e.g., 'CBC', 'Glucose', 'Creatinine')")
    value = Column(Float, nullable=True, comment="Lab result value")
    normal_range = Column(String(50), nullable=True, comment="Normal range for this lab type (e.g., '70-100', '<1.0')")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

