"""
Pydantic schemas for Vital Risk Model Service
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class VitalReading(BaseModel):
    """Single vital reading"""
    timestamp: datetime
    hr: Optional[int] = Field(None, ge=0, le=300, description="Heart Rate (beats per minute)")
    bp_sys: Optional[int] = Field(None, ge=0, le=300, description="Systolic Blood Pressure (mmHg)")
    bp_dia: Optional[int] = Field(None, ge=0, le=200, description="Diastolic Blood Pressure (mmHg)")
    spo2: Optional[float] = Field(None, ge=0.0, le=100.0, description="Oxygen Saturation (%)")
    rr: Optional[int] = Field(None, ge=0, le=100, description="Respiratory Rate (breaths per minute)")
    temp: Optional[float] = Field(None, ge=25.0, le=45.0, description="Temperature (Celsius)")
    pain: Optional[int] = Field(None, ge=0, le=10, description="Pain scale (0-10)")


class VitalRiskRequest(BaseModel):
    """Request schema for vital risk prediction"""
    patient_id: str = Field(..., description="Patient ID")
    vitals: List[VitalReading] = Field(..., min_length=1, description="Most recent 12-hour vital trends")


class VitalRiskResponse(BaseModel):
    """Response schema for vital risk prediction"""
    version: str = Field(..., description="Model version")
    risk_level: str = Field(..., description="Risk level: 'routine', 'needs_attention', or 'high_concern'")
    score: float = Field(..., ge=0.0, le=1.0, description="Risk score (0.0-1.0)")
    top_features: List[str] = Field(..., description="Top contributing features to the risk assessment")
    explanation: str = Field(..., description="Human-readable explanation of the risk assessment")

