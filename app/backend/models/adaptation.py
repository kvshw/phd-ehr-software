"""
Adaptation model for MAPE-K adaptation plans
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from core.database import Base


class Adaptation(Base):
    """Adaptation model for storing MAPE-K adaptation plans"""
    __tablename__ = "adaptations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True, index=True)
    plan_json = Column(JSON, nullable=False)  # JSON layout plan
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    user = relationship("User", backref="adaptations")
    patient = relationship("Patient", backref="adaptations")

