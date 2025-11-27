"""
Visit service for business logic
Handles visit/encounter management with Finnish healthcare context
"""
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, or_, desc
from decimal import Decimal

from models.visit import Visit
from models.patient import Patient
from models.user import User
from schemas.visit import VisitCreate, VisitUpdate


class VisitService:
    """Service for visit/encounter operations"""

    @staticmethod
    def get_visit_by_id(db: Session, visit_id: UUID) -> Optional[Visit]:
        """Get a visit by ID"""
        stmt = select(Visit).where(Visit.id == visit_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def get_visits_by_patient(
        db: Session,
        patient_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Visit], int]:
        """Get all visits for a patient, ordered by most recent first"""
        # Get visits
        stmt = (
            select(Visit)
            .where(Visit.patient_id == patient_id)
            .order_by(desc(Visit.visit_date))
            .offset(skip)
            .limit(limit)
        )
        visits = db.execute(stmt).scalars().all()
        
        # Get total count
        count_stmt = select(func.count()).select_from(Visit).where(Visit.patient_id == patient_id)
        total = db.execute(count_stmt).scalar_one()
        
        return list(visits), total

    @staticmethod
    def get_visits_by_user(
        db: Session,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Visit], int]:
        """Get all visits for a healthcare provider"""
        stmt = (
            select(Visit)
            .where(Visit.user_id == user_id)
            .order_by(desc(Visit.visit_date))
            .offset(skip)
            .limit(limit)
        )
        visits = db.execute(stmt).scalars().all()
        
        count_stmt = select(func.count()).select_from(Visit).where(Visit.user_id == user_id)
        total = db.execute(count_stmt).scalar_one()
        
        return list(visits), total

    @staticmethod
    def create_visit(db: Session, visit_data: VisitCreate) -> Visit:
        """Create a new visit/encounter"""
        # Convert date strings to datetime if provided
        visit_dict = visit_data.model_dump(exclude_unset=True)
        
        # Handle date_of_birth if it's a string
        if 'visit_date' in visit_dict and isinstance(visit_dict['visit_date'], str):
            visit_dict['visit_date'] = datetime.fromisoformat(visit_dict['visit_date'].replace('Z', '+00:00'))
        elif 'visit_date' not in visit_dict:
            visit_dict['visit_date'] = datetime.now()
        
        if 'discharge_date' in visit_dict and isinstance(visit_dict['discharge_date'], str):
            visit_dict['discharge_date'] = datetime.fromisoformat(visit_dict['discharge_date'].replace('Z', '+00:00'))
        
        # Convert Decimal to float for database storage
        if 'kela_reimbursement_amount' in visit_dict and visit_dict['kela_reimbursement_amount'] is not None:
            if isinstance(visit_dict['kela_reimbursement_amount'], Decimal):
                visit_dict['kela_reimbursement_amount'] = float(visit_dict['kela_reimbursement_amount'])
        
        visit = Visit(**visit_dict)
        db.add(visit)
        db.commit()
        db.refresh(visit)
        return visit

    @staticmethod
    def update_visit(db: Session, visit_id: UUID, visit_data: VisitUpdate) -> Optional[Visit]:
        """Update an existing visit"""
        visit = VisitService.get_visit_by_id(db, visit_id)
        if not visit:
            return None
        
        update_dict = visit_data.model_dump(exclude_unset=True)
        
        # Handle datetime conversions
        if 'visit_date' in update_dict and isinstance(update_dict['visit_date'], str):
            update_dict['visit_date'] = datetime.fromisoformat(update_dict['visit_date'].replace('Z', '+00:00'))
        
        if 'discharge_date' in update_dict and isinstance(update_dict['discharge_date'], str):
            update_dict['discharge_date'] = datetime.fromisoformat(update_dict['discharge_date'].replace('Z', '+00:00'))
        
        # Convert Decimal to float
        if 'kela_reimbursement_amount' in update_dict and update_dict['kela_reimbursement_amount'] is not None:
            if isinstance(update_dict['kela_reimbursement_amount'], Decimal):
                update_dict['kela_reimbursement_amount'] = float(update_dict['kela_reimbursement_amount'])
        
        # Update fields
        for key, value in update_dict.items():
            setattr(visit, key, value)
        
        db.commit()
        db.refresh(visit)
        return visit

    @staticmethod
    def delete_visit(db: Session, visit_id: UUID) -> bool:
        """Delete a visit"""
        visit = VisitService.get_visit_by_id(db, visit_id)
        if not visit:
            return False
        
        db.delete(visit)
        db.commit()
        return True

    @staticmethod
    def get_active_visits(
        db: Session,
        patient_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None
    ) -> List[Visit]:
        """Get active visits (in_progress status)"""
        stmt = select(Visit).where(Visit.visit_status == 'in_progress')
        
        if patient_id:
            stmt = stmt.where(Visit.patient_id == patient_id)
        
        if user_id:
            stmt = stmt.where(Visit.user_id == user_id)
        
        stmt = stmt.order_by(desc(Visit.visit_date))
        result = db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def get_upcoming_visits(
        db: Session,
        patient_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        days_ahead: int = 7
    ) -> List[Visit]:
        """Get upcoming scheduled visits within specified days"""
        from datetime import timedelta
        future_date = datetime.now() + timedelta(days=days_ahead)
        
        stmt = (
            select(Visit)
            .where(Visit.visit_status == 'scheduled')
            .where(Visit.visit_date >= datetime.now())
            .where(Visit.visit_date <= future_date)
        )
        
        if patient_id:
            stmt = stmt.where(Visit.patient_id == patient_id)
        
        if user_id:
            stmt = stmt.where(Visit.user_id == user_id)
        
        stmt = stmt.order_by(Visit.visit_date)
        result = db.execute(stmt)
        return list(result.scalars().all())

