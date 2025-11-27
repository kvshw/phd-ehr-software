"""
Medication Service
Handles business logic for medications
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from models.medication import Medication
from schemas.medication import MedicationCreate, MedicationUpdate


class MedicationService:
    """Service for managing medications"""

    @staticmethod
    def create_medication(db: Session, medication_data: MedicationCreate) -> Medication:
        """Create a new medication"""
        medication = Medication(
            patient_id=medication_data.patient_id,
            prescriber_id=medication_data.prescriber_id,
            medication_name=medication_data.medication_name,
            generic_name=medication_data.generic_name,
            dosage=medication_data.dosage,
            frequency=medication_data.frequency,
            route=medication_data.route,
            quantity=medication_data.quantity,
            start_date=medication_data.start_date,
            end_date=medication_data.end_date,
            status=medication_data.status,
            indication=medication_data.indication,
            notes=medication_data.notes,
        )
        db.add(medication)
        db.commit()
        db.refresh(medication)
        return medication

    @staticmethod
    def get_medications_by_patient(
        db: Session,
        patient_id: UUID,
        status: Optional[str] = None
    ) -> List[Medication]:
        """Get medications for a patient, optionally filtered by status"""
        query = db.query(Medication).filter(Medication.patient_id == patient_id)
        if status:
            query = query.filter(Medication.status == status)
        return query.order_by(Medication.start_date.desc() if status == "active" else Medication.created_at.desc()).all()

    @staticmethod
    def get_medication_by_id(db: Session, medication_id: UUID) -> Optional[Medication]:
        """Get a medication by ID"""
        return db.query(Medication).filter(Medication.id == medication_id).first()

    @staticmethod
    def update_medication(
        db: Session,
        medication_id: UUID,
        medication_data: MedicationUpdate
    ) -> Optional[Medication]:
        """Update a medication"""
        medication = MedicationService.get_medication_by_id(db, medication_id)
        if not medication:
            return None

        update_data = medication_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(medication, field, value)

        db.commit()
        db.refresh(medication)
        return medication

    @staticmethod
    def delete_medication(db: Session, medication_id: UUID) -> bool:
        """Delete a medication"""
        medication = MedicationService.get_medication_by_id(db, medication_id)
        if not medication:
            return False

        db.delete(medication)
        db.commit()
        return True

