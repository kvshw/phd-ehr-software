"""
User action service for MAPE-K monitoring

Enhanced with privacy-preserving capabilities:
- Hashed user IDs for analytics storage
- Bucketed timestamps for temporal privacy
- Consent-aware recording
- Aggregate-only exports
"""
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
import logging

from models.user_action import UserAction
from schemas.user_action import UserActionCreate

logger = logging.getLogger(__name__)


class UserActionService:
    """Service for user action operations with privacy support"""

    @staticmethod
    def create_action(db: Session, action_data: UserActionCreate) -> UserAction:
        """Create a new user action log entry"""
        db_action = UserAction(**action_data.model_dump())
        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        return db_action

    @staticmethod
    def create_privacy_preserving_action(
        db: Session,
        action_data: UserActionCreate,
        check_consent: bool = True
    ) -> Optional[UserAction]:
        """
        Create a user action with privacy protections.
        
        - Checks user consent before recording
        - Buckets timestamp to 15-minute intervals
        - Removes sensitive metadata fields
        
        Args:
            db: Database session
            action_data: Action data to record
            check_consent: Whether to verify consent first
        
        Returns:
            Created action or None if consent not given
        """
        from services.privacy_service import PrivacyService
        
        privacy_service = PrivacyService(db)
        
        # Check consent if required
        if check_consent:
            has_consent = privacy_service.check_consent(
                action_data.user_id,
                "analytics"
            )
            if not has_consent:
                logger.debug(f"User {action_data.user_id} has not consented to analytics")
                return None
        
        # Create privacy-preserving version
        bucketed_timestamp = privacy_service.bucket_timestamp(
            action_data.timestamp or datetime.utcnow()
        )
        
        # Clean metadata
        clean_metadata = privacy_service._clean_metadata(
            action_data.action_metadata or {}
        )
        
        # Create action with privacy protections
        privacy_action_data = UserActionCreate(
            user_id=action_data.user_id,
            patient_id=action_data.patient_id,
            action_type=action_data.action_type,
            action_metadata=clean_metadata,
            timestamp=bucketed_timestamp
        )
        
        return UserActionService.create_action(db, privacy_action_data)

    @staticmethod
    def get_aggregated_actions(
        db: Session,
        user_id: Optional[UUID] = None,
        action_type: Optional[str] = None,
        days: int = 30,
        group_by: List[str] = None
    ) -> Dict[str, Any]:
        """
        Get privacy-preserving aggregated action statistics.
        
        Returns aggregates only, not individual actions.
        Applies k-anonymity by suppressing small groups.
        """
        from services.privacy_service import PrivacyService
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        privacy_service = PrivacyService(db)
        
        # Build query
        conditions = [UserAction.timestamp >= cutoff_date]
        
        if user_id:
            conditions.append(UserAction.user_id == user_id)
        if action_type:
            conditions.append(UserAction.action_type == action_type)
        
        query = select(UserAction).where(and_(*conditions))
        result = db.execute(query)
        actions = list(result.scalars().all())
        
        # Convert to dictionaries for aggregation
        action_dicts = []
        for action in actions:
            action_dicts.append({
                "user_id": str(action.user_id),
                "action_type": action.action_type,
                "timestamp": action.timestamp.isoformat() if action.timestamp else None,
                "patient_id": str(action.patient_id) if action.patient_id else None,
            })
        
        # Aggregate with privacy
        if group_by is None:
            group_by = ["action_type"]
        
        aggregates = privacy_service.aggregate_events(
            action_dicts,
            group_by=group_by,
            metrics=["count", "unique_users"]
        )
        
        return aggregates

    @staticmethod
    def export_for_research(
        db: Session,
        days: int = 90,
        epsilon: float = 1.0
    ) -> Dict[str, Any]:
        """
        Export action data for research with differential privacy.
        
        Returns only aggregated statistics with added noise.
        No individual-level data is exported.
        
        Args:
            db: Database session
            days: Number of days to include
            epsilon: Differential privacy parameter (lower = more privacy)
        
        Returns:
            Privacy-preserving research dataset
        """
        from services.privacy_service import PrivacyService
        
        privacy_service = PrivacyService(db)
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get action type counts
        type_query = select(
            UserAction.action_type,
            func.count(UserAction.id).label('count'),
            func.count(func.distinct(UserAction.user_id)).label('unique_users')
        ).where(
            UserAction.timestamp >= cutoff_date
        ).group_by(UserAction.action_type)
        
        result = db.execute(type_query)
        
        # Apply differential privacy to counts
        action_stats = []
        for row in result:
            action_stats.append({
                "action_type": row.action_type,
                "count": privacy_service.private_count(row.count, epsilon=epsilon),
                "unique_users": privacy_service.private_count(row.unique_users, epsilon=epsilon)
            })
        
        # Get daily activity counts (with noise)
        daily_query = select(
            func.date_trunc('day', UserAction.timestamp).label('date'),
            func.count(UserAction.id).label('count')
        ).where(
            UserAction.timestamp >= cutoff_date
        ).group_by(
            func.date_trunc('day', UserAction.timestamp)
        ).order_by(
            func.date_trunc('day', UserAction.timestamp)
        )
        
        daily_result = db.execute(daily_query)
        
        daily_stats = []
        for row in daily_result:
            daily_stats.append({
                "date": row.date.isoformat() if row.date else None,
                "count": privacy_service.private_count(row.count, epsilon=epsilon)
            })
        
        return {
            "export_date": datetime.utcnow().isoformat(),
            "period_days": days,
            "privacy_epsilon": epsilon,
            "action_type_statistics": action_stats,
            "daily_activity": daily_stats,
            "methodology": "differential_privacy_laplace"
        }

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

