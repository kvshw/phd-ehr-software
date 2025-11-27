"""
Medical imaging schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class ImagingBase(BaseModel):
    """Base imaging schema"""
    patient_id: UUID
    type: str = Field(..., min_length=1, max_length=50, description="Image type (e.g., 'X-ray', 'MRI', 'CT')")
    file_path: str = Field(..., min_length=1, max_length=500, description="Path to image file in object storage")


class ImagingCreate(ImagingBase):
    """Schema for creating a new imaging record"""
    pass


class ImagingResponse(ImagingBase):
    """Schema for imaging response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class ImagingListResponse(BaseModel):
    """Schema for imaging list response"""
    items: list[ImagingResponse]
    total: int
    patient_id: UUID


class ImagingUploadResponse(BaseModel):
    """Schema for image upload response"""
    id: UUID
    patient_id: UUID
    type: str
    file_path: str
    file_url: str = Field(..., description="URL to access the image file")
    created_at: datetime

    class Config:
        from_attributes = True

