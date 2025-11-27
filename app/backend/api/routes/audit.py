"""
Audit Trail API endpoints
Comprehensive logging and audit trail system
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import datetime

from core.database import get_db
from core.dependencies import require_role
from services.audit_service import AuditService
from schemas.audit import (
    AuditLogResponse,
    AuditLogFilter,
    SuggestionAuditFilter,
    AdaptationAuditFilter,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/logs", response_model=AuditLogResponse)
async def get_audit_logs(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[datetime] = Query(None, description="Start date for time range"),
    end_date: Optional[datetime] = Query(None, description="End date for time range"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),  # Only researchers and admins can view audit logs
):
    """
    Get comprehensive audit logs with filtering and pagination.
    
    Returns structured log entries from:
    - User actions (navigation, suggestion interactions, risk changes, model outputs)
    - AI suggestions (creation and presentation)
    - System adaptations (plan generation and execution)
    
    All logs are timestamped and associated with users.
    No PHI or identifiable information is included in logs.
    """
    try:
        logs, total = AuditService.get_audit_logs(
            db=db,
            user_id=user_id,
            patient_id=patient_id,
            action_type=action_type,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        
        # Filter by category if provided
        if category:
            logs = [log for log in logs if log.get("category") == category]
            total = len(logs)  # Recalculate total after filtering
        
        # Convert to response format
        log_entries = []
        for log in logs:
            entry = {
                "id": log["id"],
                "type": log["type"],
                "timestamp": log["timestamp"],
                "user_id": log.get("user_id"),
                "patient_id": log.get("patient_id"),
                "category": log.get("category", "other"),
                "metadata": {k: v for k, v in log.items() if k not in ["id", "type", "timestamp", "user_id", "patient_id", "category"]},
            }
            log_entries.append(entry)
        
        total_pages = (total + page_size - 1) // page_size
        
        return AuditLogResponse(
            items=log_entries,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
        
    except Exception as e:
        logger.error(f"Error retrieving audit logs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving audit logs: {str(e)}"
        )


@router.get("/suggestions", response_model=AuditLogResponse)
async def get_suggestion_audit_trail(
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    suggestion_id: Optional[UUID] = Query(None, description="Filter by specific suggestion ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for time range"),
    end_date: Optional[datetime] = Query(None, description="End date for time range"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Get audit trail for AI suggestions.
    
    Includes:
    - Suggestion creation (when suggestions were generated)
    - User interactions (accept, ignore, not_relevant)
    
    All suggestion text is truncated to prevent PHI leakage.
    """
    try:
        logs, total = AuditService.get_suggestion_audit_trail(
            db=db,
            patient_id=patient_id,
            suggestion_id=suggestion_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        
        # Convert to response format
        log_entries = []
        for log in logs:
            entry = {
                "id": log["id"],
                "type": log["type"],
                "timestamp": log["timestamp"],
                "user_id": log.get("user_id"),
                "patient_id": log.get("patient_id"),
                "category": log.get("category", "ai_suggestion"),
                "metadata": {k: v for k, v in log.items() if k not in ["id", "type", "timestamp", "user_id", "patient_id", "category"]},
            }
            log_entries.append(entry)
        
        total_pages = (total + page_size - 1) // page_size
        
        return AuditLogResponse(
            items=log_entries,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
        
    except Exception as e:
        logger.error(f"Error retrieving suggestion audit trail: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving suggestion audit trail: {str(e)}"
        )


@router.get("/adaptations", response_model=AuditLogResponse)
async def get_adaptation_audit_trail(
    user_id: Optional[UUID] = Query(None, description="Filter by user ID"),
    patient_id: Optional[UUID] = Query(None, description="Filter by patient ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for time range"),
    end_date: Optional[datetime] = Query(None, description="End date for time range"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Get audit trail for system adaptations.
    
    Includes:
    - Adaptation plan generation (when plans were created)
    - Plan details (section ordering, suggestion density, explanation)
    
    All adaptations are timestamped and associated with users.
    """
    try:
        logs, total = AuditService.get_adaptation_audit_trail(
            db=db,
            user_id=user_id,
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        
        # Convert to response format
        log_entries = []
        for log in logs:
            entry = {
                "id": log["id"],
                "type": log["type"],
                "timestamp": log["timestamp"],
                "user_id": log.get("user_id"),
                "patient_id": log.get("patient_id"),
                "category": log.get("category", "system_adaptation"),
                "metadata": {k: v for k, v in log.items() if k not in ["id", "type", "timestamp", "user_id", "patient_id", "category"]},
            }
            log_entries.append(entry)
        
        total_pages = (total + page_size - 1) // page_size
        
        return AuditLogResponse(
            items=log_entries,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )
        
    except Exception as e:
        logger.error(f"Error retrieving adaptation audit trail: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving adaptation audit trail: {str(e)}"
        )


@router.get("/summary")
async def get_audit_summary(
    days: int = Query(7, ge=1, le=365, description="Number of days to summarize"),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Get summary statistics of audit logs.
    
    Returns counts by category and type for the specified time period.
    """
    try:
        from datetime import datetime, timedelta
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        logs, _ = AuditService.get_audit_logs(
            db=db,
            start_date=start_date,
            end_date=end_date,
            page=1,
            page_size=10000,  # Get all logs for summary
        )
        
        # Calculate summary statistics
        summary = {
            "period_days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_events": len(logs),
            "by_category": {},
            "by_type": {},
            "by_action_type": {},
        }
        
        for log in logs:
            # Count by category
            category = log.get("category", "other")
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
            
            # Count by type
            log_type = log.get("type", "unknown")
            summary["by_type"][log_type] = summary["by_type"].get(log_type, 0) + 1
            
            # Count by action type (for user actions)
            if log.get("type") == "user_action":
                action_type = log.get("action_type", "unknown")
                summary["by_action_type"][action_type] = summary["by_action_type"].get(action_type, 0) + 1
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating audit summary: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating audit summary: {str(e)}"
        )

