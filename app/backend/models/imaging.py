"""
Medical imaging model
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from core.database import Base


class Imaging(Base):
    """Medical imaging model for patient image metadata"""
    __tablename__ = "imaging"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True, comment="Image type (e.g., 'X-ray', 'MRI', 'CT')")
    file_path = Column(String(500), nullable=False, comment="Path to image file in object storage")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

