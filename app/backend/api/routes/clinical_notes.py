"""
Clinical Notes API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, require_clinician
from services.clinical_note_service import ClinicalNoteService
from schemas.clinical_note import (
    ClinicalNoteCreate,
    ClinicalNoteUpdate,
    ClinicalNoteResponse,
)

router = APIRouter(prefix="/clinical-notes", tags=["clinical-notes"])


@router.post("", response_model=ClinicalNoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: ClinicalNoteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Create a new clinical note"""
    note = ClinicalNoteService.create_note(db, note_data, current_user.user_id)
    return ClinicalNoteResponse.model_validate(note)


@router.get("/patient/{patient_id}", response_model=List[ClinicalNoteResponse])
async def get_patient_notes(
    patient_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all clinical notes for a patient"""
    notes = ClinicalNoteService.get_notes_by_patient(db, patient_id, limit, offset)
    return [ClinicalNoteResponse.model_validate(note) for note in notes]


@router.get("/{note_id}", response_model=ClinicalNoteResponse)
async def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a clinical note by ID"""
    note = ClinicalNoteService.get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found",
        )
    return ClinicalNoteResponse.model_validate(note)


@router.put("/{note_id}", response_model=ClinicalNoteResponse)
async def update_note(
    note_id: UUID,
    note_data: ClinicalNoteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Update a clinical note"""
    note = ClinicalNoteService.update_note(db, note_id, note_data)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found",
        )
    return ClinicalNoteResponse.model_validate(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Delete a clinical note"""
    success = ClinicalNoteService.delete_note(db, note_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical note not found",
        )
    return None

