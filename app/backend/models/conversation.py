"""
Conversation models for doctor-patient voice conversations
"""
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from core.database import Base


class ConversationSession(Base):
    """Conversation session model"""
    __tablename__ = "conversation_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    clinician_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    session_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    audio_file_url = Column(Text, nullable=True)  # Optional: store audio file
    status = Column(String(20), default='recording', nullable=False)  # recording, processing, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    patient = relationship("Patient", backref="conversation_sessions")
    clinician = relationship("User", backref="conversation_sessions")
    transcripts = relationship("ConversationTranscript", back_populates="session", cascade="all, delete-orphan")
    analysis = relationship("ConversationAnalysis", back_populates="session", uselist=False, cascade="all, delete-orphan")


class ConversationTranscript(Base):
    """Individual transcript entries for a conversation"""
    __tablename__ = "conversation_transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), nullable=False)
    speaker = Column(String(20), nullable=False)  # 'doctor', 'patient'
    text = Column(Text, nullable=False)
    timestamp_seconds = Column(Integer, nullable=True)  # Time in conversation (seconds)
    confidence = Column(Float, nullable=True)  # Speech recognition confidence (0.0-1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("ConversationSession", back_populates="transcripts")


class ConversationAnalysis(Base):
    """AI-generated analysis of a conversation"""
    __tablename__ = "conversation_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversation_sessions.id"), unique=True, nullable=False)
    full_transcript = Column(Text, nullable=False)
    key_points = Column(JSONB, nullable=True)  # Array of key points
    summary = Column(Text, nullable=True)
    medical_terms = Column(JSONB, nullable=True)  # Extracted medical terms
    concerns_identified = Column(JSONB, nullable=True)  # Patient concerns
    recommendations = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("ConversationSession", back_populates="analysis")

