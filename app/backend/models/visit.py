"""
Visit/Encounter model
Represents patient visits/encounters in the healthcare system
Enhanced with Finnish healthcare context
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Numeric, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from core.database import Base


class Visit(Base):
    """
    Visit/Encounter model for tracking patient visits
    
    Supports both standard and Finnish visit types:
    - Standard: outpatient, inpatient, emergency, follow_up, consult, procedure
    - Finnish: terveyskeskus, erikoislääkäri, päivystys, kotikäynti, etäkonsultaatio, toimenpide
    """
    __tablename__ = "visits"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)  # Primary provider
    
    # Visit type and status
    visit_type = Column(String(50), nullable=False)  # Standard types: outpatient, inpatient, emergency, follow_up, consult, procedure
    visit_type_fi = Column(String(50), nullable=True)  # Finnish types: terveyskeskus, erikoislääkäri, päivystys, kotikäynti, etäkonsultaatio, toimenpide
    visit_status = Column(String(50), nullable=False, default='scheduled', index=True)  # scheduled, in_progress, completed, cancelled, no_show
    
    # Visit details
    chief_complaint = Column(Text, nullable=True)
    visit_date = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    discharge_date = Column(DateTime(timezone=True), nullable=True)
    location = Column(String(255), nullable=True)  # Room, department, etc.
    notes = Column(Text, nullable=True)
    
    # Finnish healthcare context
    service_type = Column(String(20), nullable=True, default='public', index=True)  # public, private
    municipality_code = Column(String(10), nullable=True, index=True)
    kela_reimbursement_amount = Column(Numeric(10, 2), nullable=True)  # Kela reimbursement amount
    
    # Referrals (Finnish healthcare system)
    referral_from = Column(String(255), nullable=True)  # Referring unit/physician
    referral_to = Column(String(255), nullable=True)  # Referred to unit/physician
    heti_number = Column(String(20), nullable=True)  # Healthcare professional HETI number
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", backref="visits")
    provider = relationship("User", backref="visits")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "visit_type IN ('outpatient', 'inpatient', 'emergency', 'follow_up', 'consult', 'procedure')",
            name="valid_visit_type"
        ),
        CheckConstraint(
            "visit_type_fi IS NULL OR visit_type_fi IN ('terveyskeskus', 'erikoislääkäri', 'päivystys', 'kotikäynti', 'etäkonsultaatio', 'toimenpide')",
            name="valid_visit_type_fi"
        ),
        CheckConstraint(
            "visit_status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show')",
            name="valid_visit_status"
        ),
    )

