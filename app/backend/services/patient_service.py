"""
Patient service for business logic
Enhanced with Finnish healthcare field validation and processing
"""
from typing import Optional, List, Tuple
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, and_
from models.patient import Patient
from schemas.patient import PatientCreate, PatientUpdate, PatientSearchParams
from utils.finnish_id_validator import FinnishIDValidator


class PatientService:
    """Service for patient operations"""

    @staticmethod
    def get_patient_by_id(db: Session, patient_id: UUID) -> Optional[Patient]:
        """Get a patient by ID"""
        stmt = select(Patient).where(Patient.id == patient_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def get_patients(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search_params: Optional[PatientSearchParams] = None
    ) -> Tuple[List[Patient], int]:
        """Get a list of patients with optional filtering and pagination"""
        # Build base query
        stmt = select(Patient)
        count_stmt = select(func.count()).select_from(Patient)

        # Apply filters if search_params provided
        if search_params:
            conditions = []

            if search_params.name:
                conditions.append(Patient.name.ilike(f"%{search_params.name}%"))

            if search_params.age_min is not None:
                conditions.append(Patient.age >= search_params.age_min)

            if search_params.age_max is not None:
                conditions.append(Patient.age <= search_params.age_max)

            if search_params.sex:
                conditions.append(Patient.sex == search_params.sex)

            if search_params.diagnosis:
                conditions.append(Patient.primary_diagnosis.ilike(f"%{search_params.diagnosis}%"))

            if conditions:
                filter_condition = and_(*conditions)
                stmt = stmt.where(filter_condition)
                count_stmt = count_stmt.where(filter_condition)

        # Get total count
        total = db.execute(count_stmt).scalar_one()

        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)

        # Order by updated_at descending (most recent first)
        stmt = stmt.order_by(Patient.updated_at.desc())

        # Execute query
        result = db.execute(stmt)
        patients = result.scalars().all()

        return list(patients), total

    @staticmethod
    def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
        """
        Create a new patient with Finnish field validation and processing
        
        Validates henkilötunnus if provided and auto-fills:
        - date_of_birth from henkilötunnus
        - age from date_of_birth (if not provided)
        - sex from henkilötunnus (if not provided)
        """
        # Convert Pydantic model to dict
        patient_dict = patient_data.model_dump(exclude_unset=True)
        
        # Validate and process henkilötunnus if provided
        if patient_dict.get('henkilotunnus'):
            henkilotunnus = patient_dict['henkilotunnus'].strip()
            
            # Validate format
            is_valid, error = FinnishIDValidator.validate(henkilotunnus)
            if not is_valid:
                raise ValueError(f"Invalid henkilötunnus: {error}")
            
            # Extract information from henkilötunnus
            info = FinnishIDValidator.extract_info(henkilotunnus)
            if info:
                # Auto-fill date_of_birth if not provided
                if not patient_dict.get('date_of_birth') and info.get('birth_date'):
                    patient_dict['date_of_birth'] = info['birth_date']
                
                # Auto-fill age if not provided or if it doesn't match
                if info.get('age'):
                    calculated_age = info['age']
                    if not patient_dict.get('age') or abs(patient_dict.get('age', 0) - calculated_age) > 1:
                        patient_dict['age'] = calculated_age
                
                # Auto-fill sex if not provided
                if not patient_dict.get('sex') and info.get('gender'):
                    patient_dict['sex'] = info['gender']
            
            # Format henkilötunnus to standard format
            patient_dict['henkilotunnus'] = FinnishIDValidator.format_henkilotunnus(henkilotunnus)
        
        # Convert date_of_birth string to date object if provided
        if patient_dict.get('date_of_birth') and isinstance(patient_dict['date_of_birth'], str):
            try:
                patient_dict['date_of_birth'] = datetime.fromisoformat(patient_dict['date_of_birth'].replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                # Try alternative format
                try:
                    patient_dict['date_of_birth'] = datetime.strptime(patient_dict['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("Invalid date_of_birth format. Use YYYY-MM-DD")
        
        # Convert ehic_expiry_date string to date if provided
        if patient_dict.get('ehic_expiry_date') and isinstance(patient_dict['ehic_expiry_date'], str):
            try:
                patient_dict['ehic_expiry_date'] = datetime.fromisoformat(patient_dict['ehic_expiry_date'].replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                try:
                    patient_dict['ehic_expiry_date'] = datetime.strptime(patient_dict['ehic_expiry_date'], '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("Invalid ehic_expiry_date format. Use YYYY-MM-DD")
        
        # Set registration_completed_at if status is complete
        if patient_dict.get('registration_status') == 'complete':
            patient_dict['registration_completed_at'] = datetime.now()
        
        # Create patient object
        db_patient = Patient(**patient_dict)
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        return db_patient

    @staticmethod
    def update_patient(
        db: Session,
        patient_id: UUID,
        patient_data: PatientUpdate
    ) -> Optional[Patient]:
        """
        Update a patient with Finnish field validation and processing
        
        Validates henkilötunnus if provided and auto-fills related fields
        """
        patient = PatientService.get_patient_by_id(db, patient_id)
        if not patient:
            return None

        # Update only provided fields
        update_data = patient_data.model_dump(exclude_unset=True)
        
        # Validate and process henkilötunnus if being updated
        if 'henkilotunnus' in update_data and update_data['henkilotunnus']:
            henkilotunnus = update_data['henkilotunnus'].strip()
            
            # Validate format
            is_valid, error = FinnishIDValidator.validate(henkilotunnus)
            if not is_valid:
                raise ValueError(f"Invalid henkilötunnus: {error}")
            
            # Extract information
            info = FinnishIDValidator.extract_info(henkilotunnus)
            if info:
                # Auto-update date_of_birth if not explicitly provided
                if 'date_of_birth' not in update_data and info.get('birth_date'):
                    update_data['date_of_birth'] = info['birth_date']
                
                # Auto-update age if not explicitly provided
                if 'age' not in update_data and info.get('age'):
                    update_data['age'] = info['age']
                
                # Auto-update sex if not explicitly provided
                if 'sex' not in update_data and info.get('gender'):
                    update_data['sex'] = info['gender']
            
            # Format henkilötunnus
            update_data['henkilotunnus'] = FinnishIDValidator.format_henkilotunnus(henkilotunnus)
        
        # Convert date strings to date objects
        if 'date_of_birth' in update_data and isinstance(update_data['date_of_birth'], str):
            try:
                update_data['date_of_birth'] = datetime.fromisoformat(update_data['date_of_birth'].replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                try:
                    update_data['date_of_birth'] = datetime.strptime(update_data['date_of_birth'], '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("Invalid date_of_birth format. Use YYYY-MM-DD")
        
        if 'ehic_expiry_date' in update_data and isinstance(update_data['ehic_expiry_date'], str):
            try:
                update_data['ehic_expiry_date'] = datetime.fromisoformat(update_data['ehic_expiry_date'].replace('Z', '+00:00')).date()
            except (ValueError, AttributeError):
                try:
                    update_data['ehic_expiry_date'] = datetime.strptime(update_data['ehic_expiry_date'], '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("Invalid ehic_expiry_date format. Use YYYY-MM-DD")
        
        # Update registration_completed_at if status changed to complete
        if update_data.get('registration_status') == 'complete' and patient.registration_status != 'complete':
            update_data['registration_completed_at'] = datetime.now()
        
        # Apply updates
        for field, value in update_data.items():
            setattr(patient, field, value)

        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def delete_patient(db: Session, patient_id: UUID) -> bool:
        """Delete a patient"""
        patient = PatientService.get_patient_by_id(db, patient_id)
        if not patient:
            return False

        db.delete(patient)
        db.commit()
        return True

    @staticmethod
    def search_patients(
        db: Session,
        search_params: PatientSearchParams
    ) -> Tuple[List[Patient], int]:
        """Search patients with various criteria"""
        skip = (search_params.page - 1) * search_params.page_size
        return PatientService.get_patients(
            db,
            skip=skip,
            limit=search_params.page_size,
            search_params=search_params
        )

