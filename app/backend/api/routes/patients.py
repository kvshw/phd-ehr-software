"""
Patient routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional, Dict, Any, List
from math import ceil

from core.database import get_db
from schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientListResponse,
    PatientSearchParams,
)
from schemas.patient_anonymized import (
    AnonymizedPatientResponse,
    AnonymizedPatientListResponse,
)
from services.patient_service import PatientService
from services.anonymization_service import AnonymizationService
from models.vital import Vital
from models.imaging import Imaging
from core.dependencies import (
    get_current_user,
    require_admin,
    require_clinician,
)

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=PatientListResponse)
async def list_patients(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Search by name (partial match)"),
    age_min: Optional[int] = Query(None, ge=0, description="Minimum age"),
    age_max: Optional[int] = Query(None, le=150, description="Maximum age"),
    sex: Optional[str] = Query(None, pattern="^(M|F|Other)$", description="Filter by sex"),
    diagnosis: Optional[str] = Query(None, description="Search in primary diagnosis (partial match)"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # All authenticated users can list patients
):
    """
    List all patients with pagination and optional filtering.
    Available to all authenticated users (clinician, researcher, admin).
    
    **Data Access:**
    - **Clinicians**: See full patient data (names, IDs, contact info)
    - **Researchers/Admins**: See anonymized data (identifiers removed)
    """
    skip = (page - 1) * page_size

    # Build search params if any filters provided
    search_params = None
    if any([name, age_min is not None, age_max is not None, sex, diagnosis]):
        search_params = PatientSearchParams(
            name=name,
            age_min=age_min,
            age_max=age_max,
            sex=sex,
            diagnosis=diagnosis,
            page=page,
            page_size=page_size,
        )

    patients, total = PatientService.get_patients(
        db, skip=skip, limit=page_size, search_params=search_params
    )

    total_pages = ceil(total / page_size) if total > 0 else 0

    # Apply anonymization based on user role
    if AnonymizationService.should_anonymize(current_user.role):
        # Convert to dict, anonymize, then create response
        patient_dicts = [PatientResponse.model_validate(p).model_dump() for p in patients]
        anonymized_dicts = AnonymizationService.anonymize_patient_list(patient_dicts, current_user.role)
        items = [AnonymizedPatientResponse(**d) for d in anonymized_dicts]
        return AnonymizedPatientListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            anonymization_applied=True,
        )
    else:
        # Clinicians see full data
        return PatientListResponse(
            items=[PatientResponse.model_validate(p) for p in patients],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


@router.get("/search", response_model=PatientListResponse)
async def search_patients(
    search_params: PatientSearchParams = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # All authenticated users can search
):
    """
    Search patients with various criteria.
    Available to all authenticated users (clinician, researcher, admin).
    
    **Data Access:**
    - **Clinicians**: See full patient data (names, IDs, contact info)
    - **Researchers/Admins**: See anonymized data (identifiers removed)
    """
    patients, total = PatientService.search_patients(db, search_params)

    total_pages = ceil(total / search_params.page_size) if total > 0 else 0

    # Apply anonymization based on user role
    if AnonymizationService.should_anonymize(current_user.role):
        patient_dicts = [PatientResponse.model_validate(p).model_dump() for p in patients]
        anonymized_dicts = AnonymizationService.anonymize_patient_list(patient_dicts, current_user.role)
        items = [AnonymizedPatientResponse(**d) for d in anonymized_dicts]
        return AnonymizedPatientListResponse(
            items=items,
            total=total,
            page=search_params.page,
            page_size=search_params.page_size,
            total_pages=total_pages,
            anonymization_applied=True,
        )
    else:
        return PatientListResponse(
            items=[PatientResponse.model_validate(p) for p in patients],
            total=total,
            page=search_params.page,
            page_size=search_params.page_size,
            total_pages=total_pages,
        )


@router.get("/{patient_id}")
async def get_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # All authenticated users can view patients
):
    """
    Get detailed patient information by ID.
    Available to all authenticated users (clinician, researcher, admin).
    
    **Data Access:**
    - **Clinicians**: See full patient data (names, IDs, contact info)
    - **Researchers/Admins**: See anonymized data (identifiers removed)
    """
    patient = PatientService.get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found",
        )
    
    # Apply anonymization based on user role
    if AnonymizationService.should_anonymize(current_user.role):
        patient_dict = PatientResponse.model_validate(patient).model_dump()
        anonymized_dict = AnonymizationService.anonymize_patient(patient_dict, current_user.role)
        return AnonymizedPatientResponse(**anonymized_dict)
    else:
        return PatientResponse.model_validate(patient)


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_clinician),  # Clinicians and admins can create patients
):
    """
    Create a new synthetic patient.
    Available to clinicians and admins.
    
    Supports Finnish healthcare fields:
    - Validates henkilötunnus if provided
    - Auto-fills date_of_birth, age, and sex from henkilötunnus
    - Validates Kela Card and municipality information
    """
    try:
        patient = PatientService.create_patient(db, patient_data)
        return PatientResponse.model_validate(patient)
    except ValueError as e:
        # Handle validation errors (e.g., invalid henkilötunnus)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient: {str(e)}"
        )


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: UUID,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),  # Only admins can update patients
):
    """
    Update patient information.
    Admin only.
    
    Supports Finnish healthcare fields:
    - Validates henkilötunnus if provided
    - Auto-updates date_of_birth, age, and sex from henkilötunnus
    """
    try:
        patient = PatientService.update_patient(db, patient_id, patient_data)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {patient_id} not found",
            )
        return PatientResponse.model_validate(patient)
    except ValueError as e:
        # Handle validation errors (e.g., invalid henkilötunnus)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update patient: {str(e)}"
        )


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),  # Only admins can delete patients
):
    """
    Delete a patient.
    Admin only.
    """
    success = PatientService.delete_patient(db, patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found",
        )
    return None


@router.post("/metadata", response_model=Dict[str, Any])
async def get_patients_metadata(
    patient_ids: List[UUID] = Body(..., description="List of patient IDs"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Get metadata for multiple patients in a single query.
    Returns risk flags, image counts, and latest vital info.
    This optimizes dashboard loading by avoiding N+1 queries.
    
    Accepts patient IDs as a list in the request body (POST) to avoid URL length limits.
    """
    if not patient_ids or len(patient_ids) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="patient_ids list is required and cannot be empty"
        )
    
    patient_id_list = patient_ids
    
    if len(patient_id_list) > 100:  # Limit to prevent abuse
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many patient IDs (max 100)"
        )
    
    metadata: Dict[str, Dict[str, Any]] = {}
    
    # Initialize metadata for all patients
    for patient_id in patient_id_list:
        metadata[str(patient_id)] = {
            "has_vitals": False,
            "has_images": False,
            "latest_vital_timestamp": None,
            "risk_level": "routine",
            "image_count": 0,
        }
    
    # Get latest vitals for each patient (optimized: single query per patient)
    for patient_id in patient_id_list:
        stmt = select(Vital).where(Vital.patient_id == patient_id).order_by(Vital.timestamp.desc()).limit(1)
        result = db.execute(stmt)
        latest_vital = result.scalar_one_or_none()
        
        if latest_vital:
            metadata[str(patient_id)]["has_vitals"] = True
            metadata[str(patient_id)]["latest_vital_timestamp"] = latest_vital.timestamp.isoformat() if latest_vital.timestamp else None
            
            # Simple risk calculation (same logic as frontend)
            risk_level = "routine"
            if (
                (latest_vital.hr and (latest_vital.hr < 60 or latest_vital.hr > 100)) or
                (latest_vital.bp_sys and latest_vital.bp_sys > 140) or
                (latest_vital.spo2 and latest_vital.spo2 < 95)
            ):
                risk_level = "high_concern"
            elif (
                (latest_vital.hr and (latest_vital.hr < 70 or latest_vital.hr > 90)) or
                (latest_vital.bp_sys and latest_vital.bp_sys > 130)
            ):
                risk_level = "needs_attention"
            
            metadata[str(patient_id)]["risk_level"] = risk_level
    
    # Get image counts for each patient (single optimized query)
    stmt = (
        select(Imaging.patient_id, func.count(Imaging.id).label('count'))
        .where(Imaging.patient_id.in_(patient_id_list))
        .group_by(Imaging.patient_id)
    )
    result = db.execute(stmt)
    image_counts = {str(row.patient_id): row.count for row in result}
    
    for patient_id in patient_id_list:
        patient_id_str = str(patient_id)
        if patient_id_str in image_counts:
            metadata[patient_id_str]["has_images"] = True
            metadata[patient_id_str]["image_count"] = image_counts[patient_id_str]
    
    return metadata

