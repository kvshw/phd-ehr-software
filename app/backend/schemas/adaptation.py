"""
Adaptation schemas for request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class AdaptationPlan(BaseModel):
    """Schema for adaptation plan JSON structure"""
    order: List[str] = Field(..., description="Ordered list of section IDs")
    suggestion_density: str = Field(..., description="Suggestion density: 'low', 'medium', 'high'")
    flags: Optional[Dict[str, Any]] = Field(None, description="Additional flags and configuration")
    explanation: Optional[str] = Field(None, description="Explanation of why this adaptation was generated")


class AdaptationBase(BaseModel):
    """Base adaptation schema"""
    user_id: UUID = Field(..., description="ID of the user this adaptation is for")
    patient_id: Optional[UUID] = Field(None, description="ID of the patient (if patient-specific)")
    plan_json: AdaptationPlan = Field(..., description="The adaptation plan")


class AdaptationCreate(AdaptationBase):
    """Schema for creating a new adaptation"""
    pass


class AdaptationResponse(AdaptationBase):
    """Schema for returning adaptation data"""
    id: UUID = Field(..., description="Unique identifier for the adaptation")
    timestamp: datetime = Field(..., description="Timestamp of when the adaptation was created")

    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    """Schema for analyze endpoint request"""
    user_id: UUID = Field(..., description="ID of the user to analyze")
    patient_id: Optional[UUID] = Field(None, description="ID of the patient (if patient-specific analysis)")
    days: int = Field(30, ge=1, le=365, description="Number of days of data to analyze")


class AnalyzeResponse(BaseModel):
    """Schema for analyze endpoint response"""
    user_id: UUID
    patient_id: Optional[UUID]
    navigation_patterns: Dict[str, Any] = Field(..., description="Analyzed navigation patterns")
    suggestion_actions: Dict[str, Any] = Field(..., description="Analyzed suggestion interactions")
    risk_changes: Optional[List[Dict[str, Any]]] = Field(None, description="Risk change events")
    insights: List[str] = Field(..., description="List of insights derived from analysis")
    recommendations: List[str] = Field(..., description="List of adaptation recommendations")


class PlanRequest(BaseModel):
    """Schema for plan endpoint request"""
    user_id: UUID = Field(..., description="ID of the user to generate plan for")
    patient_id: Optional[UUID] = Field(None, description="ID of the patient (if patient-specific plan)")
    analysis_data: Optional[AnalyzeResponse] = Field(None, description="Pre-computed analysis data (optional)")


class PlanResponse(BaseModel):
    """Schema for plan endpoint response"""
    plan: AdaptationPlan = Field(..., description="The generated adaptation plan")
    adaptation_id: UUID = Field(..., description="ID of the stored adaptation record")
    explanation: str = Field(..., description="Explanation of the adaptation plan")

