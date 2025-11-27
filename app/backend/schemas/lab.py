"""
Laboratory results schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class LabBase(BaseModel):
    """Base lab schema"""
    patient_id: UUID
    timestamp: datetime
    lab_type: str = Field(..., min_length=1, max_length=100, description="Type of lab test")
    value: Optional[float] = Field(None, description="Lab result value")
    normal_range: Optional[str] = Field(None, max_length=50, description="Normal range for this lab type")


class LabCreate(LabBase):
    """Schema for creating a new lab record"""
    pass


class LabResponse(LabBase):
    """Schema for lab response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LabListResponse(BaseModel):
    """Schema for labs list response"""
    items: list[LabResponse]
    total: int
    patient_id: UUID


class LabFilterParams(BaseModel):
    """Schema for lab filtering parameters"""
    lab_type: Optional[str] = Field(None, description="Filter by lab type")
    start_time: Optional[datetime] = Field(None, description="Start of time range")
    end_time: Optional[datetime] = Field(None, description="End of time range")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(20, ge=1, le=100, description="Items per page")

