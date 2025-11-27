"""
Conversation schemas for API requests/responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class ConversationSessionCreate(BaseModel):
    patient_id: UUID


class ConversationSessionResponse(BaseModel):
    id: UUID
    patient_id: UUID
    clinician_id: UUID
    session_date: datetime
    duration_seconds: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationTranscriptCreate(BaseModel):
    session_id: UUID
    speaker: str = Field(..., pattern="^(doctor|patient)$")
    text: str
    timestamp_seconds: Optional[int] = None
    confidence: Optional[float] = None


class ConversationTranscriptResponse(BaseModel):
    id: UUID
    session_id: UUID
    speaker: str
    text: str
    timestamp_seconds: Optional[int] = None
    confidence: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationAnalysisResponse(BaseModel):
    id: UUID
    session_id: UUID
    full_transcript: str
    key_points: Optional[List[str]] = None
    summary: Optional[str] = None
    medical_terms: Optional[List[str]] = None
    concerns_identified: Optional[List[str]] = None
    recommendations: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationSessionWithAnalysis(ConversationSessionResponse):
    analysis: Optional[ConversationAnalysisResponse] = None
    transcripts: Optional[List[ConversationTranscriptResponse]] = None

