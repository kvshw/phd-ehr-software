"""
Clinical Note Service
Handles business logic for clinical notes
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from models.clinical_note import ClinicalNote
from schemas.clinical_note import ClinicalNoteCreate, ClinicalNoteUpdate


class ClinicalNoteService:
    """Service for managing clinical notes"""

    @staticmethod
    def create_note(db: Session, note_data: ClinicalNoteCreate, user_id: UUID) -> ClinicalNote:
        """Create a new clinical note"""
        note = ClinicalNote(
            patient_id=note_data.patient_id,
            user_id=user_id,
            note_type=note_data.note_type,
            encounter_date=note_data.encounter_date,
            chief_complaint=note_data.chief_complaint,
            history_of_present_illness=note_data.history_of_present_illness,
            review_of_systems=note_data.review_of_systems,
            physical_exam=note_data.physical_exam,
            assessment=note_data.assessment,
            plan=note_data.plan,
            note_text=note_data.note_text,
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def get_notes_by_patient(
        db: Session,
        patient_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[ClinicalNote]:
        """Get all notes for a patient, most recent first"""
        return (
            db.query(ClinicalNote)
            .filter(ClinicalNote.patient_id == patient_id)
            .order_by(ClinicalNote.encounter_date.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_note_by_id(db: Session, note_id: UUID) -> Optional[ClinicalNote]:
        """Get a note by ID"""
        return db.query(ClinicalNote).filter(ClinicalNote.id == note_id).first()

    @staticmethod
    def update_note(
        db: Session,
        note_id: UUID,
        note_data: ClinicalNoteUpdate
    ) -> Optional[ClinicalNote]:
        """Update a clinical note"""
        note = ClinicalNoteService.get_note_by_id(db, note_id)
        if not note:
            return None

        update_data = note_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(note, field, value)

        db.commit()
        db.refresh(note)
        return note

    @staticmethod
    def delete_note(db: Session, note_id: UUID) -> bool:
        """Delete a clinical note"""
        note = ClinicalNoteService.get_note_by_id(db, note_id)
        if not note:
            return False

        db.delete(note)
        db.commit()
        return True

