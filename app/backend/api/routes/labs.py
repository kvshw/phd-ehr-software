"""
Laboratory results routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from datetime import datetime
from math import ceil

from core.database import get_db
from schemas.lab import (
    LabCreate,
    LabResponse,
    LabListResponse,
    LabFilterParams,
)
from services.lab_service import LabService
from core.dependencies import (
    get_current_user,
    require_researcher,
)

router = APIRouter(prefix="/labs", tags=["labs"])


@router.get("/{patient_id}", response_model=LabListResponse)
async def get_patient_labs(
    patient_id: UUID,
    lab_type: Optional[str] = Query(None, description="Filter by lab type"),
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # All authenticated users can view labs
):
    """
    Get labs data for a patient with optional filtering and pagination.
    Available to all authenticated users (clinician, researcher, admin).
    """
    filter_params = None
    if any([lab_type, start_time, end_time]):
        filter_params = LabFilterParams(
            lab_type=lab_type,
            start_time=start_time,
            end_time=end_time,
            page=page,
            page_size=page_size,
        )
    else:
        filter_params = LabFilterParams(page=page, page_size=page_size)

    labs, total = LabService.get_labs_by_patient_id(
        db, patient_id, filter_params=filter_params
    )

    return LabListResponse(
        items=[LabResponse.model_validate(l) for l in labs],
        total=total,
        patient_id=patient_id,
    )


@router.post("", response_model=LabResponse, status_code=status.HTTP_201_CREATED)
async def create_lab(
    lab_data: LabCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_researcher),  # Admin/researcher only
):
    """
    Insert synthetic labs data.
    Admin and researcher only.
    """
    lab = LabService.create_lab(db, lab_data)
    return LabResponse.model_validate(lab)

