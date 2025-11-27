"""
Allergies API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, require_clinician
from services.allergy_service import AllergyService
from schemas.allergy import AllergyCreate, AllergyUpdate, AllergyResponse

router = APIRouter(prefix="/allergies", tags=["allergies"])


@router.post("", response_model=AllergyResponse, status_code=status.HTTP_201_CREATED)
async def create_allergy(
    allergy_data: AllergyCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Create a new allergy"""
    allergy = AllergyService.create_allergy(db, allergy_data)
    return AllergyResponse.model_validate(allergy)


@router.get("/patient/{patient_id}", response_model=List[AllergyResponse])
async def get_patient_allergies(
    patient_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get all allergies for a patient"""
    allergies = AllergyService.get_allergies_by_patient(db, patient_id, status_filter)
    return [AllergyResponse.model_validate(allergy) for allergy in allergies]


@router.get("/{allergy_id}", response_model=AllergyResponse)
async def get_allergy(
    allergy_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Get an allergy by ID"""
    allergy = AllergyService.get_allergy_by_id(db, allergy_id)
    if not allergy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allergy not found",
        )
    return AllergyResponse.model_validate(allergy)


@router.put("/{allergy_id}", response_model=AllergyResponse)
async def update_allergy(
    allergy_id: UUID,
    allergy_data: AllergyUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Update an allergy"""
    allergy = AllergyService.update_allergy(db, allergy_id, allergy_data)
    if not allergy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allergy not found",
        )
    return AllergyResponse.model_validate(allergy)


@router.delete("/{allergy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_allergy(
    allergy_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_clinician),
):
    """Delete an allergy"""
    success = AllergyService.delete_allergy(db, allergy_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Allergy not found",
        )
    return None

