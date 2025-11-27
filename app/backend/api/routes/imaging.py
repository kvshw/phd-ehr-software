"""
Medical imaging routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
from io import BytesIO

from core.database import get_db
from schemas.imaging import (
    ImagingCreate,
    ImagingResponse,
    ImagingListResponse,
    ImagingUploadResponse,
)
from services.imaging_service import ImagingService
from services.storage_service import storage_service
from core.dependencies import (
    get_current_user,
    require_researcher,
    require_admin,
)

router = APIRouter(prefix="/imaging", tags=["imaging"])


@router.get("/{patient_id}", response_model=ImagingListResponse)
async def get_patient_images(
    patient_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # All authenticated users can view images
):
    """
    List all images for a patient.
    Available to all authenticated users (clinician, researcher, admin).
    """
    images, total = ImagingService.get_imaging_by_patient_id(db, patient_id)

    return ImagingListResponse(
        items=[ImagingResponse.model_validate(img) for img in images],
        total=total,
        patient_id=patient_id,
    )


@router.get("/metadata/{image_id}", response_model=ImagingResponse)
async def get_image_metadata(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # All authenticated users can view metadata
):
    """
    Get specific image metadata by ID.
    Available to all authenticated users (clinician, researcher, admin).
    """
    imaging = ImagingService.get_imaging_by_id(db, image_id)
    if not imaging:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found",
        )
    return ImagingResponse.model_validate(imaging)


@router.get("/file/{image_id}")
async def get_image_file(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),  # All authenticated users can view images
):
    """
    Stream image file from object storage.
    Available to all authenticated users (clinician, researcher, admin).
    """
    imaging = ImagingService.get_imaging_by_id(db, image_id)
    if not imaging:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found",
        )

    # Get file content from storage
    file_content = ImagingService.get_file_content(image_id, db)
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image file not found in storage",
        )

    # Determine content type based on file extension
    content_type = "image/jpeg"  # Default
    if imaging.file_path.lower().endswith('.png'):
        content_type = "image/png"
    elif imaging.file_path.lower().endswith('.dcm'):
        content_type = "application/dicom"

    return StreamingResponse(
        BytesIO(file_content),
        media_type=content_type,
        headers={
            "Content-Disposition": f"inline; filename={imaging.file_path.split('/')[-1]}"
        }
    )


@router.post("", response_model=ImagingUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    patient_id: UUID = Form(...),
    image_type: str = Form(..., description="Image type (e.g., 'X-ray', 'MRI', 'CT')"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(require_researcher),  # Admin/researcher only
):
    """
    Upload new image with metadata.
    Admin and researcher only.
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )

    # Create imaging data
    imaging_data = ImagingCreate(
        patient_id=patient_id,
        type=image_type,
        file_path="",  # Will be set by service
    )

    # Read file content
    file_content = await file.read()
    file_obj = BytesIO(file_content)

    # Create imaging record and upload file
    imaging = ImagingService.create_imaging(
        db,
        imaging_data,
        file_obj,
        file.filename or "image.jpg"
    )

    if not imaging:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image",
        )

    # Generate presigned URL for file access
    file_url = storage_service.get_file_url(imaging.file_path, expires_in=3600)

    return ImagingUploadResponse(
        id=imaging.id,
        patient_id=imaging.patient_id,
        type=imaging.type,
        file_path=imaging.file_path,
        file_url=file_url or f"/api/v1/imaging/file/{imaging.id}",
        created_at=imaging.created_at,
    )


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(require_admin),  # Admin only
):
    """
    Delete an image.
    Admin only.
    """
    success = ImagingService.delete_imaging(db, image_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with ID {image_id} not found",
        )
    return None

