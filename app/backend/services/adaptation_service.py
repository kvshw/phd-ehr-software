"""
Adaptation service for managing adaptation plans
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.adaptation import Adaptation
from schemas.adaptation import AdaptationCreate, AdaptationPlan
from core.logging_utils import StructuredLogger


class AdaptationService:
    """Service for adaptation operations"""

    @staticmethod
    def create_adaptation(db: Session, adaptation_data: AdaptationCreate) -> Adaptation:
        """Create a new adaptation plan"""
        # Convert plan_json (AdaptationPlan) to dict for storage
        if hasattr(adaptation_data.plan_json, 'model_dump'):
            plan_dict = adaptation_data.plan_json.model_dump()
        elif isinstance(adaptation_data.plan_json, dict):
            plan_dict = adaptation_data.plan_json
        else:
            plan_dict = adaptation_data.plan_json
        
        db_adaptation = Adaptation(
            user_id=adaptation_data.user_id,
            patient_id=adaptation_data.patient_id,
            plan_json=plan_dict
        )
        db.add(db_adaptation)
        db.commit()
        db.refresh(db_adaptation)
        
        # Log adaptation creation for audit trail
        StructuredLogger.log_adaptation(
            adaptation_id=str(db_adaptation.id),
            user_id=str(db_adaptation.user_id),
            patient_id=str(db_adaptation.patient_id) if db_adaptation.patient_id else None,
            plan_type="ui_layout",
            metadata={
                "section_order": plan_dict.get("order", []),
                "suggestion_density": plan_dict.get("suggestion_density", "medium"),
                "explanation": plan_dict.get("explanation", "")[:200],  # Truncate explanation
            }
        )
        
        return db_adaptation

    @staticmethod
    def get_latest_adaptation(
        db: Session,
        user_id: UUID,
        patient_id: Optional[UUID] = None
    ) -> Optional[Adaptation]:
        """Get the most recent adaptation plan for a user/patient"""
        query = select(Adaptation).where(Adaptation.user_id == user_id)
        
        if patient_id:
            query = query.where(Adaptation.patient_id == patient_id)
        else:
            query = query.where(Adaptation.patient_id.is_(None))
        
        query = query.order_by(Adaptation.timestamp.desc()).limit(1)
        
        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def get_adaptations_by_user(
        db: Session,
        user_id: UUID,
        limit: Optional[int] = None
    ) -> List[Adaptation]:
        """Get all adaptations for a user"""
        query = select(Adaptation).where(Adaptation.user_id == user_id)
        query = query.order_by(Adaptation.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = db.execute(query)
        return list(result.scalars().all())

