"""
Suggestion service for managing AI-generated suggestions
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.suggestion import Suggestion
from schemas.suggestion import SuggestionCreate
from core.logging_utils import StructuredLogger


class SuggestionService:
    """Service for suggestion operations"""

    @staticmethod
    def get_suggestions_by_patient_id(
        db: Session,
        patient_id: UUID,
    ) -> tuple[List[Suggestion], int]:
        """Get suggestions for a patient"""
        query = select(Suggestion).where(Suggestion.patient_id == patient_id)
        query = query.order_by(Suggestion.created_at.desc())

        suggestions = db.execute(query).scalars().all()
        total = len(suggestions)

        return suggestions, total

    @staticmethod
    def create_suggestion(db: Session, suggestion_data: SuggestionCreate) -> Suggestion:
        """Create a new suggestion and log it for audit trail"""
        db_suggestion = Suggestion(**suggestion_data.model_dump())
        db.add(db_suggestion)
        db.commit()
        db.refresh(db_suggestion)
        
        # Log suggestion creation for audit trail
        StructuredLogger.log_ai_suggestion(
            suggestion_id=str(db_suggestion.id),
            patient_id=str(db_suggestion.patient_id),
            suggestion_type=db_suggestion.type,
            source=db_suggestion.source,
            confidence=db_suggestion.confidence,
            metadata={
                "text_preview": db_suggestion.text[:100] + "..." if len(db_suggestion.text) > 100 else db_suggestion.text,
            }
        )
        
        return db_suggestion

    @staticmethod
    def create_suggestions_batch(
        db: Session,
        suggestions_data: List[SuggestionCreate]
    ) -> List[Suggestion]:
        """Create multiple suggestions in a batch"""
        db_suggestions = [Suggestion(**s.model_dump()) for s in suggestions_data]
        db.add_all(db_suggestions)
        db.commit()
        for suggestion in db_suggestions:
            db.refresh(suggestion)
        return db_suggestions

