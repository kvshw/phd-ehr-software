"""
Suggestion model for AI-generated suggestions
"""
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from core.database import Base


class Suggestion(Base):
    """Suggestion model for AI-generated clinical suggestions"""
    __tablename__ = "suggestions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)  # e.g., "vital_risk", "diagnosis", "image_analysis"
    text = Column(String(1000), nullable=False)  # Suggestion text
    source = Column(String(100), nullable=False)  # e.g., "rules", "vital_risk_model", "image_analysis_model"
    explanation = Column(String(2000), nullable=False)  # Explanation of the suggestion
    confidence = Column(Float, nullable=True)  # Confidence score (0.0-1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    patient = relationship("Patient", backref="suggestions")

