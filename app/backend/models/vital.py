"""
Vital signs model
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from core.database import Base


class Vital(Base):
    """Vital signs model for time-series patient data"""
    __tablename__ = "vitals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Vital signs measurements
    hr = Column(Integer, nullable=True, comment="Heart rate (bpm)")
    bp_sys = Column(Integer, nullable=True, comment="Systolic blood pressure (mmHg)")
    bp_dia = Column(Integer, nullable=True, comment="Diastolic blood pressure (mmHg)")
    spo2 = Column(Float, nullable=True, comment="Oxygen saturation (%)")
    rr = Column(Integer, nullable=True, comment="Respiratory rate (breaths/min)")
    temp = Column(Float, nullable=True, comment="Temperature (°C)")
    pain = Column(Integer, nullable=True, comment="Pain score (0-10)")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

