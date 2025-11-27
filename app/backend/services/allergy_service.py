"""
Allergy Service
Handles business logic for allergies
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from models.allergy import Allergy
from schemas.allergy import AllergyCreate, AllergyUpdate


class AllergyService:
    """Service for managing allergies"""

    @staticmethod
    def create_allergy(db: Session, allergy_data: AllergyCreate) -> Allergy:
        """Create a new allergy"""
        allergy = Allergy(
            patient_id=allergy_data.patient_id,
            allergen=allergy_data.allergen,
            allergen_type=allergy_data.allergen_type,
            severity=allergy_data.severity,
            reaction=allergy_data.reaction,
            onset_date=allergy_data.onset_date,
            notes=allergy_data.notes,
            status=allergy_data.status,
        )
        db.add(allergy)
        db.commit()
        db.refresh(allergy)
        return allergy

    @staticmethod
    def get_allergies_by_patient(
        db: Session,
        patient_id: UUID,
        status: Optional[str] = None
    ) -> List[Allergy]:
        """Get allergies for a patient, optionally filtered by status"""
        query = db.query(Allergy).filter(Allergy.patient_id == patient_id)
        if status:
            query = query.filter(Allergy.status == status)
        return query.order_by(Allergy.created_at.desc()).all()

    @staticmethod
    def get_allergy_by_id(db: Session, allergy_id: UUID) -> Optional[Allergy]:
        """Get an allergy by ID"""
        return db.query(Allergy).filter(Allergy.id == allergy_id).first()

    @staticmethod
    def update_allergy(
        db: Session,
        allergy_id: UUID,
        allergy_data: AllergyUpdate
    ) -> Optional[Allergy]:
        """Update an allergy"""
        allergy = AllergyService.get_allergy_by_id(db, allergy_id)
        if not allergy:
            return None

        update_data = allergy_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(allergy, field, value)

        db.commit()
        db.refresh(allergy)
        return allergy

    @staticmethod
    def delete_allergy(db: Session, allergy_id: UUID) -> bool:
        """Delete an allergy"""
        allergy = AllergyService.get_allergy_by_id(db, allergy_id)
        if not allergy:
            return False

        db.delete(allergy)
        db.commit()
        return True

