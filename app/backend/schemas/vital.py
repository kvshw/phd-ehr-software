"""
Vital signs schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class VitalBase(BaseModel):
    """Base vital signs schema"""
    patient_id: UUID
    timestamp: datetime
    hr: Optional[int] = Field(None, ge=0, le=300, description="Heart rate (bpm)")
    bp_sys: Optional[int] = Field(None, ge=0, le=300, description="Systolic blood pressure (mmHg)")
    bp_dia: Optional[int] = Field(None, ge=0, le=200, description="Diastolic blood pressure (mmHg)")
    spo2: Optional[float] = Field(None, ge=0, le=100, description="Oxygen saturation (%)")
    rr: Optional[int] = Field(None, ge=0, le=60, description="Respiratory rate (breaths/min)")
    temp: Optional[float] = Field(None, ge=30, le=45, description="Temperature (°C)")
    pain: Optional[int] = Field(None, ge=0, le=10, description="Pain score (0-10)")


class VitalCreate(VitalBase):
    """Schema for creating a new vital record"""
    pass


class VitalResponse(VitalBase):
    """Schema for vital response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class VitalListResponse(BaseModel):
    """Schema for vitals list response"""
    items: list[VitalResponse]
    total: int
    patient_id: UUID


class VitalTimeRangeParams(BaseModel):
    """Schema for time range filtering"""
    start_time: Optional[datetime] = Field(None, description="Start of time range")
    end_time: Optional[datetime] = Field(None, description="End of time range")
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Maximum number of records to return")

