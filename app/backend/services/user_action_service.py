"""
User action service for MAPE-K monitoring
"""
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from models.user_action import UserAction
from schemas.user_action import UserActionCreate


class UserActionService:
    """Service for user action operations"""

    @staticmethod
    def create_action(db: Session, action_data: UserActionCreate) -> UserAction:
        """Create a new user action log entry"""
        db_action = UserAction(**action_data.model_dump())
        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        return db_action

    @staticmethod
    def get_actions_by_user(
        db: Session,
        user_id: UUID,
        limit: Optional[int] = None
    ) -> List[UserAction]:
        """Get actions for a specific user"""
        query = select(UserAction).where(UserAction.user_id == user_id)
        query = query.order_by(UserAction.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_actions_by_patient(
        db: Session,
        patient_id: UUID,
        limit: Optional[int] = None
    ) -> List[UserAction]:
        """Get actions for a specific patient"""
        query = select(UserAction).where(UserAction.patient_id == patient_id)
        query = query.order_by(UserAction.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_navigation_patterns(
        db: Session,
        user_id: UUID,
        patient_id: Optional[UUID] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get navigation patterns for a user"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(UserAction).where(
            and_(
                UserAction.user_id == user_id,
                UserAction.action_type == "navigation",
                UserAction.timestamp >= cutoff_date
            )
        )
        
        if patient_id:
            query = query.where(UserAction.patient_id == patient_id)
        
        query = query.order_by(UserAction.timestamp.asc())
        
        result = db.execute(query)
        actions = list(result.scalars().all())
        
        # Extract navigation patterns
        patterns = []
        for action in actions:
            if action.action_metadata:
                patterns.append({
                    "from_section": action.action_metadata.get("from_section"),
                    "to_section": action.action_metadata.get("to_section"),
                    "timestamp": action.timestamp.isoformat()
                })
        
        return patterns

    @staticmethod
    def get_suggestion_actions(
        db: Session,
        user_id: Optional[UUID] = None,
        patient_id: Optional[UUID] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get suggestion accept/ignore actions"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(UserAction).where(
            and_(
                UserAction.action_type == "suggestion_action",
                UserAction.timestamp >= cutoff_date
            )
        )
        
        if user_id:
            query = query.where(UserAction.user_id == user_id)
        if patient_id:
            query = query.where(UserAction.patient_id == patient_id)
        
        query = query.order_by(UserAction.timestamp.desc())
        
        result = db.execute(query)
        actions = list(result.scalars().all())
        
        # Extract suggestion actions
        suggestion_actions = []
        for action in actions:
            if action.action_metadata:
                suggestion_actions.append({
                    "suggestion_id": action.action_metadata.get("suggestion_id"),
                    "action": action.action_metadata.get("action"),  # accept, ignore, not_relevant
                    "suggestion_type": action.action_metadata.get("suggestion_type"),
                    "timestamp": action.timestamp.isoformat()
                })
        
        return suggestion_actions

    @staticmethod
    def get_risk_changes(
        db: Session,
        patient_id: UUID,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get patient risk change events"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(UserAction).where(
            and_(
                UserAction.patient_id == patient_id,
                UserAction.action_type == "risk_change",
                UserAction.timestamp >= cutoff_date
            )
        )
        query = query.order_by(UserAction.timestamp.desc())
        
        result = db.execute(query)
        actions = list(result.scalars().all())
        
        # Extract risk changes
        risk_changes = []
        for action in actions:
            if action.action_metadata:
                risk_changes.append({
                    "previous_risk_level": action.action_metadata.get("previous_risk_level"),
                    "new_risk_level": action.action_metadata.get("new_risk_level"),
                    "risk_score": action.action_metadata.get("risk_score"),
                    "timestamp": action.timestamp.isoformat()
                })
        
        return risk_changes

    @staticmethod
    def get_model_outputs(
        db: Session,
        patient_id: Optional[UUID] = None,
        model_type: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get model output captures"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(UserAction).where(
            and_(
                UserAction.action_type == "model_output",
                UserAction.timestamp >= cutoff_date
            )
        )
        
        if patient_id:
            query = query.where(UserAction.patient_id == patient_id)
        
        query = query.order_by(UserAction.timestamp.desc())
        
        result = db.execute(query)
        actions = list(result.scalars().all())
        
        # Extract model outputs
        model_outputs = []
        for action in actions:
            if action.action_metadata:
                metadata = action.action_metadata
                if model_type and metadata.get("model_type") != model_type:
                    continue
                
                model_outputs.append({
                    "model_type": metadata.get("model_type"),
                    "model_version": metadata.get("model_version"),
                    "output_data": metadata.get("output_data", {}),
                    "timestamp": action.timestamp.isoformat()
                })
        
        return model_outputs

