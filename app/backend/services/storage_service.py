"""
Storage service for MinIO/S3 integration
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import Optional, BinaryIO
from core.config import settings
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """Service for object storage operations (MinIO/S3)"""

    def __init__(self):
        """Initialize S3 client"""
        self.endpoint = getattr(settings, 'MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = getattr(settings, 'MINIO_ACCESS_KEY', 'minioadmin')
        self.secret_key = getattr(settings, 'MINIO_SECRET_KEY', 'minioadmin')
        self.bucket_name = getattr(settings, 'MINIO_BUCKET_NAME', 'ehr-images')
        self.use_ssl = False  # MinIO typically uses HTTP in development

        # Create S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{self.endpoint}" if not self.use_ssl else f"https://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='us-east-1',  # Default region
        )

    def ensure_bucket_exists(self) -> bool:
        """Ensure the bucket exists, create if it doesn't"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"Created bucket: {self.bucket_name}")
                    return True
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    return False
            else:
                logger.error(f"Error checking bucket: {e}")
                return False

    def upload_file(
        self,
        file_obj: BinaryIO,
        object_key: str,
        content_type: Optional[str] = None
    ) -> bool:
        """Upload a file to object storage"""
        try:
            # Ensure bucket exists
            self.ensure_bucket_exists()

            # Upload file
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type

            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                object_key,
                ExtraArgs=extra_args
            )
            logger.info(f"Uploaded file: {object_key}")
            return True
        except (ClientError, NoCredentialsError) as e:
            logger.error(f"Failed to upload file: {e}")
            return False

    def get_file_url(self, object_key: str, expires_in: int = 3600) -> Optional[str]:
        """Generate a presigned URL for accessing a file"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=expires_in
            )
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return None

    def delete_file(self, object_key: str) -> bool:
        """Delete a file from object storage"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            logger.info(f"Deleted file: {object_key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            return False

    def get_file(self, object_key: str) -> Optional[bytes]:
        """Get file content from object storage"""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=object_key)
            return response['Body'].read()
        except ClientError as e:
            logger.error(f"Failed to get file: {e}")
            return None


# Global storage service instance
storage_service = StorageService()

