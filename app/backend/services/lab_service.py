"""
Laboratory results service for business logic
"""
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from math import ceil
from models.lab import Lab
from schemas.lab import LabCreate, LabFilterParams


class LabService:
    """Service for laboratory results operations"""

    @staticmethod
    def get_labs_by_patient_id(
        db: Session,
        patient_id: UUID,
        filter_params: Optional[LabFilterParams] = None
    ) -> Tuple[List[Lab], int]:
        """Get labs data for a patient with optional filtering and pagination"""
        # Base query
        stmt = select(Lab).where(Lab.patient_id == patient_id)
        count_stmt = select(func.count()).select_from(Lab).where(Lab.patient_id == patient_id)

        # Apply filters if provided
        if filter_params:
            conditions = []

            if filter_params.lab_type:
                conditions.append(Lab.lab_type.ilike(f"%{filter_params.lab_type}%"))

            if filter_params.start_time:
                conditions.append(Lab.timestamp >= filter_params.start_time)

            if filter_params.end_time:
                conditions.append(Lab.timestamp <= filter_params.end_time)

            if conditions:
                filter_condition = and_(*conditions)
                stmt = stmt.where(filter_condition)
                count_stmt = count_stmt.where(filter_condition)

        # Get total count
        total = db.execute(count_stmt).scalar_one()

        # Apply pagination
        if filter_params:
            skip = (filter_params.page - 1) * filter_params.page_size
            stmt = stmt.offset(skip).limit(filter_params.page_size)
        else:
            # Default pagination
            stmt = stmt.offset(0).limit(20)

        # Order by timestamp descending (most recent first)
        stmt = stmt.order_by(Lab.timestamp.desc())

        # Execute query
        result = db.execute(stmt)
        labs = result.scalars().all()

        return list(labs), total

    @staticmethod
    def create_lab(db: Session, lab_data: LabCreate) -> Lab:
        """Create a new lab record"""
        db_lab = Lab(
            patient_id=lab_data.patient_id,
            timestamp=lab_data.timestamp,
            lab_type=lab_data.lab_type,
            value=lab_data.value,
            normal_range=lab_data.normal_range,
        )
        db.add(db_lab)
        db.commit()
        db.refresh(db_lab)
        return db_lab

