"""
Audit Trail Service
Comprehensive logging and audit trail system for user actions, AI suggestions, and system adaptations
"""
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_
from models.user_action import UserAction
from models.suggestion import Suggestion
from models.adaptation import Adaptation
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit trail operations"""

    @staticmethod
    def get_audit_logs(
        db: Session,
        user_id: Optional[UUID] = None,
        patient_id: Optional[UUID] = None,
        action_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get comprehensive audit logs with filtering and pagination.
        Returns structured log entries from user_actions, suggestions, and adaptations.
        """
        logs: List[Dict[str, Any]] = []
        
        # Build base query for user actions
        action_query = select(UserAction)
        conditions = []
        
        if user_id:
            conditions.append(UserAction.user_id == user_id)
        if patient_id:
            conditions.append(UserAction.patient_id == patient_id)
        if action_type:
            conditions.append(UserAction.action_type == action_type)
        if start_date:
            conditions.append(UserAction.timestamp >= start_date)
        if end_date:
            conditions.append(UserAction.timestamp <= end_date)
        
        if conditions:
            action_query = action_query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(UserAction)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_actions = db.execute(count_query).scalar_one()
        
        # Apply pagination
        skip = (page - 1) * page_size
        action_query = action_query.order_by(UserAction.timestamp.desc()).offset(skip).limit(page_size)
        
        # Execute query
        actions = db.execute(action_query).scalars().all()
        
        # Convert to structured log format
        for action in actions:
            log_entry = {
                "id": str(action.id),
                "type": "user_action",
                "timestamp": action.timestamp.isoformat(),
                "user_id": str(action.user_id),
                "patient_id": str(action.patient_id) if action.patient_id else None,
                "action_type": action.action_type,
                "metadata": action.action_metadata or {},
                "category": AuditService._categorize_action(action.action_type),
            }
            logs.append(log_entry)
        
        # If we need more logs, also fetch suggestions and adaptations
        # (For now, we'll focus on user_actions as the primary audit source)
        # Suggestions and adaptations can be queried separately if needed
        
        return logs, total_actions

    @staticmethod
    def get_suggestion_audit_trail(
        db: Session,
        patient_id: Optional[UUID] = None,
        suggestion_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get audit trail for AI suggestions.
        Includes suggestion creation and user interactions.
        """
        logs: List[Dict[str, Any]] = []
        
        # Get suggestions
        suggestion_query = select(Suggestion)
        conditions = []
        
        if patient_id:
            conditions.append(Suggestion.patient_id == patient_id)
        if suggestion_id:
            conditions.append(Suggestion.id == suggestion_id)
        if start_date:
            conditions.append(Suggestion.created_at >= start_date)
        if end_date:
            conditions.append(Suggestion.created_at <= end_date)
        
        if conditions:
            suggestion_query = suggestion_query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(Suggestion)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_suggestions = db.execute(count_query).scalar_one()
        
        # Apply pagination
        skip = (page - 1) * page_size
        suggestion_query = suggestion_query.order_by(Suggestion.created_at.desc()).offset(skip).limit(page_size)
        
        suggestions = db.execute(suggestion_query).scalars().all()
        
        # Convert to structured log format
        for suggestion in suggestions:
            log_entry = {
                "id": str(suggestion.id),
                "type": "suggestion",
                "timestamp": suggestion.created_at.isoformat(),
                "patient_id": str(suggestion.patient_id),
                "suggestion_type": suggestion.type,
                "source": suggestion.source,
                "confidence": suggestion.confidence,
                "text_preview": suggestion.text[:100] + "..." if len(suggestion.text) > 100 else suggestion.text,  # Truncate to avoid PHI
                "category": "ai_suggestion",
            }
            logs.append(log_entry)
        
        # Also get user interactions with these suggestions
        if suggestions:
            suggestion_ids = [str(s.id) for s in suggestions]
            # Get all suggestion actions and filter in Python (PostgreSQL JSON query can be complex)
            all_interactions = db.execute(
                select(UserAction).where(UserAction.action_type == "suggestion_action")
            ).scalars().all()
            
            # Filter interactions that match our suggestion IDs
            interactions = [
                ia for ia in all_interactions
                if ia.action_metadata and ia.action_metadata.get("suggestion_id") in suggestion_ids
            ]
            
            for interaction in interactions:
                log_entry = {
                    "id": str(interaction.id),
                    "type": "suggestion_interaction",
                    "timestamp": interaction.timestamp.isoformat(),
                    "user_id": str(interaction.user_id),
                    "patient_id": str(interaction.patient_id) if interaction.patient_id else None,
                    "suggestion_id": interaction.action_metadata.get("suggestion_id") if interaction.action_metadata else None,
                    "action": interaction.action_metadata.get("action") if interaction.action_metadata else None,
                    "category": "user_interaction",
                }
                logs.append(log_entry)
        
        # Sort all logs by timestamp
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return logs, total_suggestions

    @staticmethod
    def get_adaptation_audit_trail(
        db: Session,
        user_id: Optional[UUID] = None,
        patient_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get audit trail for system adaptations.
        Includes adaptation plan generation and execution.
        """
        logs: List[Dict[str, Any]] = []
        
        # Get adaptations
        adaptation_query = select(Adaptation)
        conditions = []
        
        if user_id:
            conditions.append(Adaptation.user_id == user_id)
        if patient_id:
            conditions.append(Adaptation.patient_id == patient_id)
        if start_date:
            conditions.append(Adaptation.timestamp >= start_date)
        if end_date:
            conditions.append(Adaptation.timestamp <= end_date)
        
        if conditions:
            adaptation_query = adaptation_query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(Adaptation)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_adaptations = db.execute(count_query).scalar_one()
        
        # Apply pagination
        skip = (page - 1) * page_size
        adaptation_query = adaptation_query.order_by(Adaptation.timestamp.desc()).offset(skip).limit(page_size)
        
        adaptations = db.execute(adaptation_query).scalars().all()
        
        # Convert to structured log format
        for adaptation in adaptations:
            plan = adaptation.plan_json or {}
            log_entry = {
                "id": str(adaptation.id),
                "type": "adaptation",
                "timestamp": adaptation.timestamp.isoformat(),
                "user_id": str(adaptation.user_id),
                "patient_id": str(adaptation.patient_id) if adaptation.patient_id else None,
                "section_order": plan.get("order", []),
                "suggestion_density": plan.get("suggestion_density", "medium"),
                "explanation": plan.get("explanation", ""),
                "category": "system_adaptation",
            }
            logs.append(log_entry)
        
        return logs, total_adaptations

    @staticmethod
    def _categorize_action(action_type: str) -> str:
        """Categorize action types for easier filtering"""
        categories = {
            "navigation": "user_navigation",
            "suggestion_action": "user_interaction",
            "risk_change": "system_event",
            "model_output": "ai_activity",
        }
        return categories.get(action_type, "other")

    @staticmethod
    def validate_no_phi(data: Dict[str, Any]) -> bool:
        """
        Validate that data does not contain PHI.
        This is a basic check - in production, use more sophisticated PHI detection.
        """
        # Common PHI patterns to check for
        phi_patterns = [
            "ssn", "social security",
            "dob", "date of birth",
            "address", "street",
            "phone", "telephone",
            "email", "@",
            "name",  # Patient names should not be in logs
        ]
        
        # Convert data to string for checking
        data_str = str(data).lower()
        
        # Check for PHI patterns (this is a simplified check)
        # In production, use a proper PHI detection library
        for pattern in phi_patterns:
            if pattern in data_str:
                logger.warning(f"Potential PHI detected in log data: {pattern}")
                return False
        
        return True

