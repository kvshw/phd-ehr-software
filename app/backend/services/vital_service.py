"""
Vital signs service for business logic
"""
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from models.vital import Vital
from schemas.vital import VitalCreate, VitalTimeRangeParams


class VitalService:
    """Service for vital signs operations"""

    @staticmethod
    def get_vitals_by_patient_id(
        db: Session,
        patient_id: UUID,
        time_range: Optional[VitalTimeRangeParams] = None
    ) -> Tuple[List[Vital], int]:
        """Get time-series vitals data for a patient with optional time range filtering"""
        # Base query
        stmt = select(Vital).where(Vital.patient_id == patient_id)
        count_stmt = select(func.count()).select_from(Vital).where(Vital.patient_id == patient_id)

        # Apply time range filters if provided
        if time_range:
            conditions = []
            if time_range.start_time:
                conditions.append(Vital.timestamp >= time_range.start_time)
            if time_range.end_time:
                conditions.append(Vital.timestamp <= time_range.end_time)
            
            if conditions:
                filter_condition = and_(*conditions)
                stmt = stmt.where(filter_condition)
                count_stmt = count_stmt.where(filter_condition)

        # Get total count
        total = db.execute(count_stmt).scalar_one()

        # Order by timestamp descending (most recent first)
        stmt = stmt.order_by(Vital.timestamp.desc())

        # Apply limit if provided
        if time_range and time_range.limit:
            stmt = stmt.limit(time_range.limit)
        else:
            # Default limit for time-series data (last 12 hours worth, or 100 records)
            stmt = stmt.limit(100)

        # Execute query
        result = db.execute(stmt)
        vitals = result.scalars().all()

        return list(vitals), total

    @staticmethod
    def get_recent_vitals(
        db: Session,
        patient_id: UUID,
        hours: int = 12
    ) -> List[Vital]:
        """Get most recent vitals for a patient (default: last 12 hours)"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        stmt = (
            select(Vital)
            .where(
                and_(
                    Vital.patient_id == patient_id,
                    Vital.timestamp >= cutoff_time
                )
            )
            .order_by(Vital.timestamp.desc())
        )
        result = db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    def create_vital(db: Session, vital_data: VitalCreate) -> Vital:
        """Create a new vital record"""
        db_vital = Vital(
            patient_id=vital_data.patient_id,
            timestamp=vital_data.timestamp,
            hr=vital_data.hr,
            bp_sys=vital_data.bp_sys,
            bp_dia=vital_data.bp_dia,
            spo2=vital_data.spo2,
            rr=vital_data.rr,
            temp=vital_data.temp,
            pain=vital_data.pain,
        )
        db.add(db_vital)
        db.commit()
        db.refresh(db_vital)
        return db_vital

