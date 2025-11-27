"""
User action model for MAPE-K monitoring
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from core.database import Base


class UserAction(Base):
    """User action model for tracking user behavior and system events"""
    __tablename__ = "user_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True, index=True)
    action_type = Column(String(100), nullable=False, index=True)  # e.g., "navigation", "suggestion_action", "risk_change", "model_output"
    action_metadata = Column("metadata", JSON, nullable=True)  # Flexible JSON for action-specific data (Python name 'action_metadata' maps to DB column 'metadata')
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

    user = relationship("User", backref="actions")
    patient = relationship("Patient", backref="actions")

