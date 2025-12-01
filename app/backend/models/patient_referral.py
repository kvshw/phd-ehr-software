"""
Patient Referral Model
Tracks patient referrals from nurses to doctors/specialties
"""
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from core.database import Base


class ReferralStatus(str, enum.Enum):
    PENDING = "pending"          # Waiting for doctor to accept
    ACCEPTED = "accepted"        # Doctor accepted the referral
    IN_PROGRESS = "in_progress"  # Doctor is seeing the patient
    COMPLETED = "completed"      # Consultation completed
    CANCELLED = "cancelled"      # Referral cancelled
    TRANSFERRED = "transferred"  # Transferred to another specialty


class ReferralPriority(str, enum.Enum):
    CRITICAL = "critical"
    URGENT = "urgent"
    STANDARD = "standard"
    NON_URGENT = "non_urgent"


class PatientReferral(Base):
    """
    Patient referral from nurse to doctor/specialty.
    
    This creates the connection between:
    - Nurse Dashboard (sender)
    - Doctor Dashboard (receiver)
    - Admin Dashboard (anonymized oversight)
    """
    __tablename__ = "patient_referrals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Patient info
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    
    # Referral source (nurse)
    referred_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    referred_by_role = Column(String(50), default="nurse")
    
    # Referral destination (doctor/specialty)
    target_specialty = Column(String(100), nullable=False, index=True)
    assigned_doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Referral details
    priority = Column(String(20), default="standard", index=True)
    status = Column(String(20), default="pending", index=True)
    
    # Clinical info
    chief_complaint = Column(Text, nullable=True)
    symptoms = Column(JSONB, default=list)
    vitals = Column(JSONB, default=dict)
    triage_notes = Column(Text, nullable=True)
    
    # AI recommendation (from triage)
    ai_suggested_specialty = Column(String(100), nullable=True)
    ai_confidence = Column(String(10), nullable=True)
    nurse_override = Column(String(10), default="false")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Notes and history
    doctor_notes = Column(Text, nullable=True)
    status_history = Column(JSONB, default=list)  # Track all status changes

