"""
Imaging service for business logic
"""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from models.imaging import Imaging
from schemas.imaging import ImagingCreate
from services.storage_service import storage_service
import logging

logger = logging.getLogger(__name__)


class ImagingService:
    """Service for imaging operations"""

    @staticmethod
    def get_imaging_by_patient_id(
        db: Session,
        patient_id: UUID
    ) -> Tuple[List[Imaging], int]:
        """Get all images for a patient"""
        stmt = select(Imaging).where(Imaging.patient_id == patient_id)
        count_stmt = select(func.count()).select_from(Imaging).where(Imaging.patient_id == patient_id)

        # Get total count
        total = db.execute(count_stmt).scalar_one()

        # Order by created_at descending (most recent first)
        stmt = stmt.order_by(Imaging.created_at.desc())

        # Execute query
        result = db.execute(stmt)
        images = result.scalars().all()

        return list(images), total

    @staticmethod
    def get_imaging_by_id(
        db: Session,
        image_id: UUID
    ) -> Optional[Imaging]:
        """Get a specific image by ID"""
        stmt = select(Imaging).where(Imaging.id == image_id)
        result = db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def create_imaging(
        db: Session,
        imaging_data: ImagingCreate,
        file_obj,
        filename: str
    ) -> Optional[Imaging]:
        """Create a new imaging record and upload file to object storage"""
        # Create database record first to get the ID
        db_imaging = Imaging(
            patient_id=imaging_data.patient_id,
            type=imaging_data.type,
            file_path="",  # Will be updated after upload
        )
        db.add(db_imaging)
        db.commit()
        db.refresh(db_imaging)

        # Generate object key (path in storage) using the actual ID
        import uuid
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        object_key = f"{imaging_data.patient_id}/{db_imaging.id}/{uuid.uuid4()}.{file_extension}"

        # Upload file to object storage
        content_type = None
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif filename.lower().endswith('.png'):
            content_type = 'image/png'
        elif filename.lower().endswith('.dcm'):
            content_type = 'application/dicom'

        upload_success = storage_service.upload_file(
            file_obj,
            object_key,
            content_type=content_type
        )

        if not upload_success:
            logger.error(f"Failed to upload image file: {object_key}")
            # Rollback database record
            db.delete(db_imaging)
            db.commit()
            return None

        # Update file_path in database
        db_imaging.file_path = object_key
        db.commit()
        db.refresh(db_imaging)

        return db_imaging

    @staticmethod
    def delete_imaging(db: Session, image_id: UUID) -> bool:
        """Delete an image record and file from object storage"""
        imaging = ImagingService.get_imaging_by_id(db, image_id)
        if not imaging:
            return False

        # Delete file from object storage
        delete_success = storage_service.delete_file(imaging.file_path)
        if not delete_success:
            logger.warning(f"Failed to delete file from storage: {imaging.file_path}")

        # Delete database record
        db.delete(imaging)
        db.commit()
        return True

    @staticmethod
    def get_file_content(image_id: UUID, db: Session) -> Optional[bytes]:
        """Get file content from object storage"""
        imaging = ImagingService.get_imaging_by_id(db, image_id)
        if not imaging:
            return None

        return storage_service.get_file(imaging.file_path)

