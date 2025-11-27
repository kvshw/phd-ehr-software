"""
Medications API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, require_clinician
from services.medication_service import MedicationService
from schemas.medication import MedicationCreate, MedicationUpdate, MedicationResponse

router = APIRouter(prefix="/medications", tags=["medications"])


@router.post("", response_model=MedicationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication(
    medication_data: MedicationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Create a new medication"""
    # Set prescriber to current user if not specified
    if not medication_data.prescriber_id:
        medication_data.prescriber_id = current_user.user_id
    
    medication = MedicationService.create_medication(db, medication_data)
    return MedicationResponse.model_validate(medication)


@router.get("/patient/{patient_id}", response_model=List[MedicationResponse])
async def get_patient_medications(
    patient_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all medications for a patient"""
    medications = MedicationService.get_medications_by_patient(db, patient_id, status_filter)
    return [MedicationResponse.model_validate(medication) for medication in medications]


@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    medication_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get a medication by ID"""
    medication = MedicationService.get_medication_by_id(db, medication_id)
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found",
        )
    return MedicationResponse.model_validate(medication)


@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: UUID,
    medication_data: MedicationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Update a medication"""
    medication = MedicationService.update_medication(db, medication_id, medication_data)
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found",
        )
    return MedicationResponse.model_validate(medication)


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication(
    medication_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Delete a medication"""
    success = MedicationService.delete_medication(db, medication_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found",
        )
    return None

