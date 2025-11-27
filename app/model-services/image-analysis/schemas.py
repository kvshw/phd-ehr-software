"""
Pydantic schemas for Image Analysis Model Service
"""
from pydantic import BaseModel, Field
from typing import Optional


class ImageAnalysisRequest(BaseModel):
    """Request schema for image analysis"""
    image_id: str = Field(..., description="ID of the image to analyze")
    image_type: str = Field(..., description="Type of image (X-ray, MRI, CT)")


class ImageAnalysisResponse(BaseModel):
    """Response schema for image analysis"""
    version: str = Field(..., description="Model version")
    abnormality_score: float = Field(..., ge=0.0, le=1.0, description="Abnormality score (0.0-1.0)")
    classification: str = Field(..., description="Classification: 'normal', 'suspicious', or 'abnormal'")
    heatmap_url: Optional[str] = Field(None, description="URL to the generated heatmap image")
    explanation: str = Field(..., description="Human-readable explanation of the analysis")

