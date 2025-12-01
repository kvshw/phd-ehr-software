"""
Referral Service
Handles patient referrals between nurses and doctors.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, func
import logging

logger = logging.getLogger(__name__)


class ReferralService:
    """
    Service for managing patient referrals from nurses to doctors.
    
    Provides:
    - Create referral (nurse → doctor)
    - Get referrals for doctor dashboard
    - Get referrals for admin (anonymized)
    - Update referral status
    """
    
    @staticmethod
    def create_referral(
        db: Session,
        patient_id: UUID,
        referred_by_id: UUID,
        target_specialty: str,
        priority: str = "standard",
        chief_complaint: Optional[str] = None,
        symptoms: Optional[List[str]] = None,
        vitals: Optional[Dict[str, Any]] = None,
        triage_notes: Optional[str] = None,
        ai_suggested_specialty: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        nurse_override: bool = False,
        assigned_doctor_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
        """Create a new patient referral from nurse to doctor/specialty."""
        from models.patient_referral import PatientReferral
        
        referral = PatientReferral(
            patient_id=patient_id,
            referred_by_id=referred_by_id,
            target_specialty=target_specialty,
            priority=priority,
            status="pending",
            chief_complaint=chief_complaint,
            symptoms=symptoms or [],
            vitals=vitals or {},
            triage_notes=triage_notes,
            ai_suggested_specialty=ai_suggested_specialty,
            ai_confidence=str(ai_confidence) if ai_confidence else None,
            nurse_override=str(nurse_override).lower(),
            assigned_doctor_id=assigned_doctor_id,
            status_history=[{
                "status": "pending",
                "timestamp": datetime.utcnow().isoformat(),
                "by": str(referred_by_id),
                "note": "Referral created",
            }],
        )
        
        try:
            db.add(referral)
            db.commit()
            db.refresh(referral)
            
            logger.info(f"Referral created: {referral.id} for patient {patient_id} to {target_specialty}")
            
            return ReferralService._referral_to_dict(referral)
        except Exception as e:
            db.rollback()
            error_msg = str(e)
            if "does not exist" in error_msg or "relation" in error_msg.lower():
                logger.error(f"Database table error: {error_msg}")
                raise ValueError(
                    "patient_referrals table does not exist. Please run the SQL migration script: "
                    "scripts/fix_user_role_constraint.sql in Supabase SQL Editor."
                )
            raise
    
    @staticmethod
    def get_referrals_for_doctor(
        db: Session,
        doctor_id: UUID,
        specialty: str,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get referrals for a doctor's dashboard (by specialty or direct assignment)."""
        from models.patient_referral import PatientReferral
        from models.patient import Patient
        
        try:
            query = db.query(PatientReferral, Patient).join(
                Patient, PatientReferral.patient_id == Patient.id
            ).filter(
                or_(
                    PatientReferral.target_specialty == specialty,
                    PatientReferral.assigned_doctor_id == doctor_id,
                )
            )
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg or "relation" in error_msg.lower():
                logger.warning(f"patient_referrals table does not exist. Please run SQL migration.")
                return []  # Return empty list instead of crashing
            raise
        
        if status:
            query = query.filter(PatientReferral.status == status)
        else:
            # Default: show pending and accepted
            query = query.filter(PatientReferral.status.in_(["pending", "accepted", "in_progress"]))
        
        query = query.order_by(
            # Priority order: critical first
            PatientReferral.priority.desc(),
            PatientReferral.created_at.asc(),
        ).limit(limit)
        
        results = query.all()
        
        return [
            {
                **ReferralService._referral_to_dict(referral),
                "patient": {
                    "id": str(patient.id),
                    "name": patient.name or "Unknown Patient",
                    "age": patient.age if patient.age else ReferralService._calculate_age(patient.date_of_birth),
                    "gender": patient.sex if hasattr(patient, 'sex') else None,
                    "mrn": getattr(patient, 'mrn', None),  # MRN might not exist
                },
            }
            for referral, patient in results
        ]
    
    @staticmethod
    def get_referrals_for_admin_anonymized(
        db: Session,
        limit: int = 100,
        days: int = 7,
    ) -> Dict[str, Any]:
        """Get anonymized referral data for admin dashboard."""
        from models.patient_referral import PatientReferral
        from datetime import timedelta
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get all referrals in timeframe
        referrals = db.query(PatientReferral).filter(
            PatientReferral.created_at >= cutoff
        ).order_by(PatientReferral.created_at.desc()).limit(limit).all()
        
        # Aggregate statistics
        stats = {
            "total_referrals": len(referrals),
            "by_status": {},
            "by_specialty": {},
            "by_priority": {},
            "avg_wait_time_minutes": 0,
            "nurse_override_rate": 0,
        }
        
        total_wait = 0
        wait_count = 0
        override_count = 0
        
        for ref in referrals:
            # Count by status
            stats["by_status"][ref.status] = stats["by_status"].get(ref.status, 0) + 1
            # Count by specialty
            stats["by_specialty"][ref.target_specialty] = stats["by_specialty"].get(ref.target_specialty, 0) + 1
            # Count by priority
            stats["by_priority"][ref.priority] = stats["by_priority"].get(ref.priority, 0) + 1
            
            # Calculate wait time if accepted
            if ref.accepted_at and ref.created_at:
                wait_minutes = (ref.accepted_at - ref.created_at).total_seconds() / 60
                total_wait += wait_minutes
                wait_count += 1
            
            # Count overrides
            if ref.nurse_override == "true":
                override_count += 1
        
        if wait_count > 0:
            stats["avg_wait_time_minutes"] = round(total_wait / wait_count, 1)
        
        if len(referrals) > 0:
            stats["nurse_override_rate"] = round(override_count / len(referrals) * 100, 1)
        
        # Anonymized referral list (no patient names)
        anonymized_referrals = [
            {
                "id": str(ref.id),
                "patient_hash": ReferralService._anonymize_id(ref.patient_id),
                "specialty": ref.target_specialty,
                "priority": ref.priority,
                "status": ref.status,
                "ai_suggested": ref.ai_suggested_specialty,
                "nurse_override": ref.nurse_override == "true",
                "created_at": ref.created_at.isoformat() if ref.created_at else None,
                "wait_time_bucket": ReferralService._bucket_wait_time(ref),
            }
            for ref in referrals[:50]  # Limit to 50 for display
        ]
        
        return {
            "statistics": stats,
            "referrals": anonymized_referrals,
            "period_days": days,
        }
    
    @staticmethod
    def update_referral_status(
        db: Session,
        referral_id: UUID,
        new_status: str,
        updated_by_id: UUID,
        notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update referral status (accept, complete, cancel, etc.)."""
        from models.patient_referral import PatientReferral
        
        referral = db.query(PatientReferral).filter(
            PatientReferral.id == referral_id
        ).first()
        
        if not referral:
            return None
        
        # Update status
        old_status = referral.status
        referral.status = new_status
        
        # Set timestamps
        now = datetime.utcnow()
        if new_status == "accepted":
            referral.accepted_at = now
            referral.assigned_doctor_id = updated_by_id
        elif new_status == "completed":
            referral.completed_at = now
        
        # Add notes if provided
        if notes:
            referral.doctor_notes = notes
        
        # Update status history
        history = referral.status_history or []
        history.append({
            "status": new_status,
            "from_status": old_status,
            "timestamp": now.isoformat(),
            "by": str(updated_by_id),
            "note": notes,
        })
        referral.status_history = history
        
        db.commit()
        db.refresh(referral)
        
        logger.info(f"Referral {referral_id} status updated: {old_status} → {new_status}")
        
        return ReferralService._referral_to_dict(referral)
    
    @staticmethod
    def get_nurse_referrals(
        db: Session,
        nurse_id: UUID,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get referrals created by a specific nurse."""
        from models.patient_referral import PatientReferral
        from models.patient import Patient
        
        results = db.query(PatientReferral, Patient).join(
            Patient, PatientReferral.patient_id == Patient.id
        ).filter(
            PatientReferral.referred_by_id == nurse_id
        ).order_by(
            PatientReferral.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                **ReferralService._referral_to_dict(referral),
                "patient": {
                    "id": str(patient.id),
                    "name": patient.name or "Unknown Patient",
                    "age": patient.age if patient.age else ReferralService._calculate_age(patient.date_of_birth),
                },
            }
            for referral, patient in results
        ]
    
    @staticmethod
    def _referral_to_dict(referral) -> Dict[str, Any]:
        """Convert referral model to dictionary."""
        return {
            "id": str(referral.id),
            "patient_id": str(referral.patient_id),
            "referred_by_id": str(referral.referred_by_id),
            "target_specialty": referral.target_specialty,
            "assigned_doctor_id": str(referral.assigned_doctor_id) if referral.assigned_doctor_id else None,
            "priority": referral.priority,
            "status": referral.status,
            "chief_complaint": referral.chief_complaint,
            "symptoms": referral.symptoms,
            "vitals": referral.vitals,
            "triage_notes": referral.triage_notes,
            "ai_suggested_specialty": referral.ai_suggested_specialty,
            "ai_confidence": referral.ai_confidence,
            "nurse_override": referral.nurse_override == "true",
            "created_at": referral.created_at.isoformat() if referral.created_at else None,
            "accepted_at": referral.accepted_at.isoformat() if referral.accepted_at else None,
            "completed_at": referral.completed_at.isoformat() if referral.completed_at else None,
            "doctor_notes": referral.doctor_notes,
        }
    
    @staticmethod
    def _calculate_age(dob) -> int:
        """Calculate age from date of birth."""
        if not dob:
            return 0
        today = date.today()
        # Handle different date formats
        if isinstance(dob, datetime):
            dob = dob.date()
        elif isinstance(dob, str):
            try:
                dob = datetime.fromisoformat(dob).date()
            except (ValueError, AttributeError):
                return 0
        elif not isinstance(dob, date):
            return 0
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    
    @staticmethod
    def _anonymize_id(id_val) -> str:
        """Create anonymized hash of an ID."""
        import hashlib
        return hashlib.sha256(str(id_val).encode()).hexdigest()[:8]
    
    @staticmethod
    def _bucket_wait_time(referral) -> str:
        """Bucket wait time into ranges for anonymization."""
        if not referral.accepted_at or not referral.created_at:
            return "pending"
        
        wait_minutes = (referral.accepted_at - referral.created_at).total_seconds() / 60
        
        if wait_minutes < 5:
            return "0-5 min"
        elif wait_minutes < 15:
            return "5-15 min"
        elif wait_minutes < 30:
            return "15-30 min"
        elif wait_minutes < 60:
            return "30-60 min"
        else:
            return "60+ min"

