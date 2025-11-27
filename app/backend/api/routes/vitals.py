"""
Vital signs routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from datetime import datetime

from core.database import get_db
from schemas.vital import (
    VitalCreate,
    VitalResponse,
    VitalListResponse,
    VitalTimeRangeParams,
)
from services.vital_service import VitalService
from core.dependencies import (
    get_current_user,
    require_researcher,
)

router = APIRouter(prefix="/vitals", tags=["vitals"])


@router.get("/{patient_id}", response_model=VitalListResponse)
async def get_patient_vitals(
    patient_id: UUID,
    start_time: Optional[datetime] = Query(None, description="Start of time range"),
    end_time: Optional[datetime] = Query(None, description="End of time range"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # All authenticated users can view vitals
):
    """
    Get time-series vitals data for a patient with optional time range filtering.
    Available to all authenticated users (clinician, researcher, admin).
    """
    time_range = None
    if start_time or end_time or limit:
        time_range = VitalTimeRangeParams(
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )

    vitals, total = VitalService.get_vitals_by_patient_id(
        db, patient_id, time_range=time_range
    )

    return VitalListResponse(
        items=[VitalResponse.model_validate(v) for v in vitals],
        total=total,
        patient_id=patient_id,
    )


@router.post("", response_model=VitalResponse, status_code=status.HTTP_201_CREATED)
async def create_vital(
    vital_data: VitalCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_researcher),  # Admin/researcher only
):
    """
    Add synthetic vitals data.
    Admin and researcher only.
    """
    vital = VitalService.create_vital(db, vital_data)
    return VitalResponse.model_validate(vital)

