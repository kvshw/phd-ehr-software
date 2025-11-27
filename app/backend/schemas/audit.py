"""
Pydantic schemas for audit trail data
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class AuditLogEntry(BaseModel):
    """Schema for a single audit log entry"""
    id: str = Field(..., description="Unique identifier for the log entry")
    type: str = Field(..., description="Type of log entry (user_action, suggestion, adaptation, etc.)")
    timestamp: str = Field(..., description="ISO timestamp of the event")
    user_id: Optional[str] = Field(None, description="User ID associated with the event")
    patient_id: Optional[str] = Field(None, description="Patient ID (if applicable)")
    category: str = Field(..., description="Category of the event")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional event-specific metadata")


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs"""
    user_id: Optional[UUID] = Field(None, description="Filter by user ID")
    patient_id: Optional[UUID] = Field(None, description="Filter by patient ID")
    action_type: Optional[str] = Field(None, description="Filter by action type")
    category: Optional[str] = Field(None, description="Filter by category")
    start_date: Optional[datetime] = Field(None, description="Start date for time range filter")
    end_date: Optional[datetime] = Field(None, description="End date for time range filter")
    page: int = Field(1, ge=1, description="Page number for pagination")
    page_size: int = Field(50, ge=1, le=100, description="Number of items per page")


class AuditLogResponse(BaseModel):
    """Schema for audit log response"""
    items: List[AuditLogEntry] = Field(..., description="List of audit log entries")
    total: int = Field(..., description="Total number of matching log entries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")


class SuggestionAuditFilter(BaseModel):
    """Schema for filtering suggestion audit logs"""
    patient_id: Optional[UUID] = Field(None, description="Filter by patient ID")
    suggestion_id: Optional[UUID] = Field(None, description="Filter by specific suggestion ID")
    start_date: Optional[datetime] = Field(None, description="Start date for time range filter")
    end_date: Optional[datetime] = Field(None, description="End date for time range filter")
    page: int = Field(1, ge=1, description="Page number for pagination")
    page_size: int = Field(50, ge=1, le=100, description="Number of items per page")


class AdaptationAuditFilter(BaseModel):
    """Schema for filtering adaptation audit logs"""
    user_id: Optional[UUID] = Field(None, description="Filter by user ID")
    patient_id: Optional[UUID] = Field(None, description="Filter by patient ID")
    start_date: Optional[datetime] = Field(None, description="Start date for time range filter")
    end_date: Optional[datetime] = Field(None, description="End date for time range filter")
    page: int = Field(1, ge=1, description="Page number for pagination")
    page_size: int = Field(50, ge=1, le=100, description="Number of items per page")

