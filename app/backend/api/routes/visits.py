"""
Visit/Encounter API Routes
Endpoints for managing patient visits and encounters
Supports both standard and Finnish visit types
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from core.database import get_db
from core.dependencies import get_current_user, require_role
from schemas.auth import TokenData
from schemas.visit import (
    VisitCreate,
    VisitUpdate,
    VisitResponse,
    VisitListResponse,
)
from services.visit_service import VisitService
from services.anonymization_service import AnonymizationService

router = APIRouter(prefix="/visits", tags=["Visits"])


@router.post("", response_model=VisitResponse, status_code=status.HTTP_201_CREATED)
async def create_visit(
    visit_data: VisitCreate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_role(["clinician", "admin"]))
):
    """
    Create a new visit/encounter for a patient.
    
    Supports both standard and Finnish visit types:
    - Standard: outpatient, inpatient, emergency, follow_up, consult, procedure
    - Finnish: terveyskeskus, erikoislääkäri, päivystys, kotikäynti, etäkonsultaatio, toimenpide
    """
    visit = VisitService.create_visit(db, visit_data)
    return visit


@router.get("/patient/{patient_id}", response_model=VisitListResponse)
async def get_patient_visits(
    patient_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all visits for a specific patient.
    Returns visits ordered by most recent first.
    
    **Data Access:**
    - **Clinicians**: See full visit data with provider information
    - **Researchers/Admins**: See anonymized visits (provider IDs removed)
    """
    skip = (page - 1) * page_size
    visits, total = VisitService.get_visits_by_patient(db, patient_id, skip, page_size)
    
    total_pages = (total + page_size - 1) // page_size
    
    # Apply anonymization based on user role
    if AnonymizationService.should_anonymize(current_user.role):
        visit_dicts = [VisitResponse.model_validate(v).model_dump() for v in visits]
        anonymized_dicts = AnonymizationService.anonymize_visit_list(visit_dicts, current_user.role)
        anonymized_visits = [VisitResponse(**d) for d in anonymized_dicts]
        return VisitListResponse(
            items=anonymized_visits,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    else:
        visit_responses = [VisitResponse.model_validate(v) for v in visits]
        return VisitListResponse(
            items=visit_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


@router.get("/my-visits", response_model=VisitListResponse)
async def get_my_visits(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_role(["clinician", "admin"]))
):
    """
    Get all visits for the current healthcare provider.
    """
    skip = (page - 1) * page_size
    visits, total = VisitService.get_visits_by_user(db, current_user.user_id, skip, page_size)
    
    total_pages = (total + page_size - 1) // page_size
    
    return VisitListResponse(
        items=visits,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get a specific visit by ID.
    
    **Data Access:**
    - **Clinicians**: See full visit data with provider information
    - **Researchers/Admins**: See anonymized visit (provider IDs removed)
    """
    visit = VisitService.get_visit_by_id(db, visit_id)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Visit with ID {visit_id} not found",
        )
    
    # Apply anonymization based on user role
    if AnonymizationService.should_anonymize(current_user.role):
        visit_dict = VisitResponse.model_validate(visit).model_dump() if hasattr(visit, '__dict__') else visit
        if isinstance(visit_dict, dict):
            anonymized_dict = AnonymizationService.anonymize_visit(visit_dict, current_user.role)
            return VisitResponse(**anonymized_dict)
        else:
            # If visit is already a VisitResponse, convert to dict first
            visit_dict = visit.model_dump() if hasattr(visit, 'model_dump') else dict(visit)
            anonymized_dict = AnonymizationService.anonymize_visit(visit_dict, current_user.role)
            return VisitResponse(**anonymized_dict)
    else:
        if hasattr(visit, '__dict__'):
            return VisitResponse.model_validate(visit)
        else:
            return visit
    visit = VisitService.get_visit_by_id(db, visit_id)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )
    
    # Apply anonymization based on user role
    if AnonymizationService.should_anonymize(current_user.role):
        visit_dict = VisitResponse.model_validate(visit).model_dump()
        anonymized_dict = AnonymizationService.anonymize_visit(visit_dict, current_user.role)
        return VisitResponse(**anonymized_dict)
    else:
        return VisitResponse.model_validate(visit)


@router.put("/{visit_id}", response_model=VisitResponse)
async def update_visit(
    visit_id: UUID,
    visit_data: VisitUpdate,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_role(["clinician", "admin"]))
):
    """
    Update an existing visit.
    Only the current provider or admin can update visits.
    """
    visit = VisitService.get_visit_by_id(db, visit_id)
    if not visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )
    
    # Check if user is the provider or admin
    if visit.user_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this visit"
        )
    
    updated_visit = VisitService.update_visit(db, visit_id, visit_data)
    if not updated_visit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )
    return updated_visit


@router.delete("/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visit(
    visit_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(require_role(["admin"]))
):
    """
    Delete a visit.
    Only admins can delete visits.
    """
    success = VisitService.delete_visit(db, visit_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visit not found"
        )


@router.get("/patient/{patient_id}/active", response_model=List[VisitResponse])
async def get_active_visits(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get active (in_progress) visits for a patient.
    """
    visits = VisitService.get_active_visits(db, patient_id=patient_id)
    return visits


@router.get("/patient/{patient_id}/upcoming", response_model=List[VisitResponse])
async def get_upcoming_visits(
    patient_id: UUID,
    days_ahead: int = Query(7, ge=1, le=90, description="Number of days ahead to look"),
    db: Session = Depends(get_db),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get upcoming scheduled visits for a patient.
    """
    visits = VisitService.get_upcoming_visits(db, patient_id=patient_id, days_ahead=days_ahead)
    return visits

