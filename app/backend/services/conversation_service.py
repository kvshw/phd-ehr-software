"""
Conversation service for managing doctor-patient conversations
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta

from models.conversation import ConversationSession, ConversationTranscript, ConversationAnalysis
from schemas.conversation import (
    ConversationSessionCreate,
    ConversationTranscriptCreate,
)


class ConversationService:
    """Service for conversation management"""

    @staticmethod
    def create_session(
        db: Session,
        patient_id: UUID,
        clinician_id: UUID
    ) -> ConversationSession:
        """Create a new conversation session"""
        session = ConversationSession(
            patient_id=patient_id,
            clinician_id=clinician_id,
            status='recording'
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_session(db: Session, session_id: UUID) -> Optional[ConversationSession]:
        """Get a conversation session by ID"""
        stmt = select(ConversationSession).where(ConversationSession.id == session_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def get_patient_sessions(
        db: Session,
        patient_id: UUID,
        limit: int = 10
    ) -> List[ConversationSession]:
        """Get all conversation sessions for a patient"""
        stmt = (
            select(ConversationSession)
            .where(ConversationSession.patient_id == patient_id)
            .order_by(ConversationSession.session_date.desc())
            .limit(limit)
        )
        result = db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def add_transcript(
        db: Session,
        transcript_data: ConversationTranscriptCreate
    ) -> ConversationTranscript:
        """Add a transcript entry to a session"""
        transcript = ConversationTranscript(
            session_id=transcript_data.session_id,
            speaker=transcript_data.speaker,
            text=transcript_data.text,
            timestamp_seconds=transcript_data.timestamp_seconds,
            confidence=transcript_data.confidence
        )
        db.add(transcript)
        db.commit()
        db.refresh(transcript)
        return transcript

    @staticmethod
    def get_session_transcripts(
        db: Session,
        session_id: UUID
    ) -> List[ConversationTranscript]:
        """Get all transcripts for a session"""
        stmt = (
            select(ConversationTranscript)
            .where(ConversationTranscript.session_id == session_id)
            .order_by(ConversationTranscript.created_at.asc())
        )
        result = db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def complete_session(
        db: Session,
        session_id: UUID,
        duration_seconds: Optional[int] = None
    ) -> ConversationSession:
        """Mark a session as completed"""
        session = ConversationService.get_session(db, session_id)
        if not session:
            raise ValueError("Session not found")
        
        session.status = 'completed'
        if duration_seconds:
            session.duration_seconds = duration_seconds
        session.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def save_analysis(
        db: Session,
        session_id: UUID,
        full_transcript: str,
        key_points: Optional[List[str]] = None,
        summary: Optional[str] = None,
        medical_terms: Optional[List[str]] = None,
        concerns_identified: Optional[List[str]] = None,
        recommendations: Optional[str] = None
    ) -> ConversationAnalysis:
        """Save conversation analysis results"""
        # Check if analysis already exists
        stmt = select(ConversationAnalysis).where(ConversationAnalysis.session_id == session_id)
        existing = db.execute(stmt).scalar_one_or_none()
        
        if existing:
            # Update existing
            existing.full_transcript = full_transcript
            existing.key_points = key_points
            existing.summary = summary
            existing.medical_terms = medical_terms
            existing.concerns_identified = concerns_identified
            existing.recommendations = recommendations
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Create new
            analysis = ConversationAnalysis(
                session_id=session_id,
                full_transcript=full_transcript,
                key_points=key_points,
                summary=summary,
                medical_terms=medical_terms,
                concerns_identified=concerns_identified,
                recommendations=recommendations
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
            return analysis

    @staticmethod
    def get_session_analysis(
        db: Session,
        session_id: UUID
    ) -> Optional[ConversationAnalysis]:
        """Get analysis for a session"""
        stmt = select(ConversationAnalysis).where(ConversationAnalysis.session_id == session_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

