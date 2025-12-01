"""
Adaptation service for managing adaptation plans
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.adaptation import Adaptation
from schemas.adaptation import AdaptationCreate, AdaptationPlan
from core.logging_utils import StructuredLogger
import logging

logger = logging.getLogger(__name__)


class AdaptationService:
    """Service for adaptation operations"""

    @staticmethod
    def create_adaptation(
        db: Session, 
        adaptation_data: AdaptationCreate,
        old_plan: Optional[Dict] = None,
        trigger_reason: str = "automatic",
        confidence_score: float = 1.0
    ) -> Adaptation:
        """Create a new adaptation plan with full provenance tracking"""
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
        
        # Log adaptation creation for audit trail (legacy)
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
        
        # Log with new ChangeLogService for full provenance tracking
        try:
            from services.change_log_service import ChangeLogService
            change_log = ChangeLogService(db)
            
            # Generate explanation from plan
            explanation = plan_dict.get("explanation", "")
            if not explanation:
                explanation = AdaptationService._generate_explanation(plan_dict, old_plan)
            
            change_log.log_adaptation(
                user_id=adaptation_data.user_id,
                adaptation_type="dashboard_layout",
                old_state=old_plan or {},
                new_state=plan_dict,
                explanation=explanation,
                trigger_reason=trigger_reason,
                confidence_score=confidence_score,
                metrics_before=None,  # Can be populated by caller
                feature_name=None
            )
        except Exception as e:
            # Don't fail the main adaptation if logging fails
            logger.warning(f"Failed to log adaptation with ChangeLogService: {e}")
        
        return db_adaptation
    
    @staticmethod
    def _generate_explanation(new_plan: Dict, old_plan: Optional[Dict]) -> str:
        """Generate a human-readable explanation for the adaptation."""
        changes = []
        
        # Check section order changes
        new_order = new_plan.get("order", [])
        old_order = old_plan.get("order", []) if old_plan else []
        
        if new_order and old_order and new_order != old_order:
            # Find promoted sections
            for i, section in enumerate(new_order[:3]):  # Top 3
                if section in old_order:
                    old_pos = old_order.index(section)
                    if i < old_pos:
                        changes.append(f"'{section}' moved up")
        
        # Check suggestion density
        new_density = new_plan.get("suggestion_density", "medium")
        old_density = old_plan.get("suggestion_density", "medium") if old_plan else "medium"
        
        if new_density != old_density:
            changes.append(f"suggestion density changed to {new_density}")
        
        if changes:
            return f"Dashboard adapted: {', '.join(changes)}. Based on your usage patterns."
        
        return "Dashboard layout optimized based on your usage patterns."

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

