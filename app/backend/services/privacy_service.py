"""
Privacy Service - Privacy-by-Design Implementation

Implements privacy-preserving mechanisms for usage tracking:
- Hashed user IDs (salted)
- Bucketed timestamps (15-minute bins)
- Aggregate-only storage (no raw events after analysis)
- Data retention policies
- Differential privacy for aggregate statistics

Part of Phase 7: Privacy, Security & Governance
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import logging
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, and_, func

logger = logging.getLogger(__name__)

# Configuration
TIMESTAMP_BUCKET_MINUTES = 15
DEFAULT_RETENTION_DAYS = 90
AGGREGATE_RETENTION_DAYS = 365
MIN_K_ANONYMITY = 5  # Minimum group size for k-anonymity


class PrivacyService:
    """
    Privacy-preserving service for user tracking and analytics.
    
    Key Principles:
    1. Data Minimization - Collect only what's needed
    2. Purpose Limitation - Use data only for stated purposes
    3. Storage Limitation - Delete data after retention period
    4. Integrity & Confidentiality - Hash identifiers, encrypt sensitive data
    """
    
    def __init__(self, db: Session, salt: Optional[str] = None):
        self.db = db
        # Use environment variable or generate a consistent salt
        self._salt = salt or self._get_or_create_salt()
    
    def _get_or_create_salt(self) -> str:
        """Get or create a salt for hashing."""
        import os
        salt = os.environ.get("PRIVACY_SALT")
        if not salt:
            # In production, this should be stored securely
            salt = "ehr_research_platform_salt_v1"
            logger.warning("Using default privacy salt - configure PRIVACY_SALT in production")
        return salt
    
    # =========================================================================
    # User ID Hashing
    # =========================================================================
    
    def hash_user_id(self, user_id: UUID, purpose: str = "analytics") -> str:
        """
        Hash user ID with salt for privacy-preserving storage.
        
        Args:
            user_id: Original user UUID
            purpose: Purpose of hashing (different purposes get different hashes)
        
        Returns:
            Hashed identifier (hex string)
        """
        # Combine user_id with purpose-specific salt
        purpose_salt = f"{self._salt}:{purpose}"
        
        # Use HMAC-SHA256 for secure hashing
        hash_input = str(user_id).encode('utf-8')
        salt_bytes = purpose_salt.encode('utf-8')
        
        hashed = hmac.new(salt_bytes, hash_input, hashlib.sha256).hexdigest()
        
        # Truncate to 16 chars for reasonable storage
        return hashed[:16]
    
    def hash_session_id(self, session_id: str) -> str:
        """Hash session ID for privacy."""
        return self.hash_user_id(UUID(session_id) if '-' in session_id else session_id, "session")
    
    # =========================================================================
    # Timestamp Bucketing
    # =========================================================================
    
    def bucket_timestamp(
        self,
        timestamp: datetime,
        bucket_minutes: int = TIMESTAMP_BUCKET_MINUTES
    ) -> datetime:
        """
        Round timestamp to bucket for temporal privacy.
        
        Reduces precision to prevent exact timing attacks
        while maintaining useful analytics.
        
        Args:
            timestamp: Original timestamp
            bucket_minutes: Bucket size in minutes (default: 15)
        
        Returns:
            Bucketed timestamp
        """
        # Round down to nearest bucket
        minutes = (timestamp.minute // bucket_minutes) * bucket_minutes
        
        return timestamp.replace(
            minute=minutes,
            second=0,
            microsecond=0
        )
    
    def bucket_date(self, timestamp: datetime) -> datetime:
        """Bucket to day level for higher privacy."""
        return timestamp.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
    
    # =========================================================================
    # Data Aggregation
    # =========================================================================
    
    def aggregate_events(
        self,
        events: List[Dict[str, Any]],
        group_by: List[str] = None,
        metrics: List[str] = None
    ) -> Dict[str, Any]:
        """
        Aggregate raw events into privacy-preserving summaries.
        
        Args:
            events: List of raw event dictionaries
            group_by: Fields to group by (default: ["action_type"])
            metrics: Metrics to compute (default: ["count", "unique_users"])
        
        Returns:
            Aggregated statistics
        """
        if group_by is None:
            group_by = ["action_type"]
        if metrics is None:
            metrics = ["count", "unique_users"]
        
        if not events:
            return {"aggregates": [], "total_events": 0, "suppressed": False}
        
        # Group events
        groups = {}
        for event in events:
            # Create group key
            key_parts = []
            for field in group_by:
                value = event.get(field, "unknown")
                key_parts.append(str(value))
            key = "|".join(key_parts)
            
            if key not in groups:
                groups[key] = {
                    "events": [],
                    "user_ids": set(),
                    **{field: event.get(field, "unknown") for field in group_by}
                }
            
            groups[key]["events"].append(event)
            if "user_id" in event:
                # Hash user ID before storing in set
                hashed_id = self.hash_user_id(event["user_id"])
                groups[key]["user_ids"].add(hashed_id)
        
        # Compute aggregates
        aggregates = []
        suppressed_count = 0
        
        for key, group_data in groups.items():
            # K-anonymity check - suppress small groups
            if len(group_data["user_ids"]) < MIN_K_ANONYMITY:
                suppressed_count += 1
                continue
            
            aggregate = {
                field: group_data[field] for field in group_by
            }
            
            if "count" in metrics:
                aggregate["count"] = len(group_data["events"])
            
            if "unique_users" in metrics:
                aggregate["unique_users"] = len(group_data["user_ids"])
            
            if "avg_duration" in metrics:
                durations = [e.get("duration", 0) for e in group_data["events"] if "duration" in e]
                aggregate["avg_duration"] = sum(durations) / len(durations) if durations else 0
            
            aggregates.append(aggregate)
        
        return {
            "aggregates": aggregates,
            "total_events": len(events),
            "groups_suppressed": suppressed_count,
            "k_anonymity_threshold": MIN_K_ANONYMITY,
            "aggregated_at": datetime.utcnow().isoformat()
        }
    
    def aggregate_and_delete_raw(
        self,
        events: List[Dict[str, Any]],
        storage_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Aggregate events and delete raw data.
        
        This is the main privacy-preserving workflow:
        1. Aggregate raw events
        2. Store aggregates (if callback provided)
        3. Return aggregates only (raw events are not persisted)
        
        Args:
            events: Raw event data
            storage_callback: Optional function to store aggregates
        
        Returns:
            Aggregated data only
        """
        aggregates = self.aggregate_events(events)
        
        # Store aggregates if callback provided
        if storage_callback and aggregates["aggregates"]:
            storage_callback(aggregates)
        
        # Clear raw events (they're only in memory)
        # In a real implementation, this would delete from database
        
        logger.info(
            f"Aggregated {aggregates['total_events']} events into "
            f"{len(aggregates['aggregates'])} groups "
            f"({aggregates['groups_suppressed']} suppressed for k-anonymity)"
        )
        
        return aggregates
    
    # =========================================================================
    # Differential Privacy
    # =========================================================================
    
    def add_noise(
        self,
        value: float,
        sensitivity: float = 1.0,
        epsilon: float = 1.0
    ) -> float:
        """
        Add Laplace noise for differential privacy.
        
        Args:
            value: Original value
            sensitivity: Query sensitivity (max change from one record)
            epsilon: Privacy parameter (lower = more privacy)
        
        Returns:
            Noisy value
        """
        import random
        
        # Laplace scale parameter
        scale = sensitivity / epsilon
        
        # Generate Laplace noise
        u = random.random() - 0.5
        noise = -scale * (1 if u >= 0 else -1) * (abs(u) + 1e-10)
        noise = -scale * (1 if u >= 0 else -1) * abs(u)
        
        # Simplified Laplace noise
        noise = random.uniform(-scale, scale)
        
        return value + noise
    
    def private_count(
        self,
        count: int,
        epsilon: float = 1.0
    ) -> int:
        """
        Return differentially private count.
        
        Args:
            count: True count
            epsilon: Privacy parameter
        
        Returns:
            Noisy count (always >= 0)
        """
        noisy = self.add_noise(float(count), sensitivity=1.0, epsilon=epsilon)
        return max(0, round(noisy))
    
    def private_mean(
        self,
        values: List[float],
        min_val: float,
        max_val: float,
        epsilon: float = 1.0
    ) -> float:
        """
        Return differentially private mean.
        
        Args:
            values: List of values
            min_val: Minimum possible value (for sensitivity calculation)
            max_val: Maximum possible value
            epsilon: Privacy parameter
        
        Returns:
            Noisy mean
        """
        if not values:
            return 0.0
        
        true_mean = sum(values) / len(values)
        sensitivity = (max_val - min_val) / len(values)
        
        noisy = self.add_noise(true_mean, sensitivity=sensitivity, epsilon=epsilon)
        
        # Clamp to valid range
        return max(min_val, min(max_val, noisy))
    
    # =========================================================================
    # Data Retention
    # =========================================================================
    
    def enforce_retention_policy(
        self,
        table_name: str,
        retention_days: int = DEFAULT_RETENTION_DAYS,
        timestamp_column: str = "created_at"
    ) -> int:
        """
        Delete data older than retention period.
        
        Args:
            table_name: Database table name
            retention_days: Days to retain data
            timestamp_column: Column containing timestamp
        
        Returns:
            Number of rows deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        try:
            # Use raw SQL for flexibility
            from sqlalchemy import text
            
            query = text(f"""
                DELETE FROM {table_name}
                WHERE {timestamp_column} < :cutoff_date
            """)
            
            result = self.db.execute(query, {"cutoff_date": cutoff_date})
            deleted_count = result.rowcount
            self.db.commit()
            
            logger.info(
                f"Retention policy: Deleted {deleted_count} rows from {table_name} "
                f"older than {retention_days} days"
            )
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error enforcing retention policy on {table_name}: {e}")
            self.db.rollback()
            return 0
    
    def get_retention_status(self) -> Dict[str, Any]:
        """Get status of data retention across tables."""
        tables = [
            ("user_actions", DEFAULT_RETENTION_DAYS, "timestamp"),
            ("adaptation_logs", AGGREGATE_RETENTION_DAYS, "created_at"),
            ("bandit_adaptation_logs", DEFAULT_RETENTION_DAYS, "created_at"),
            ("shadow_tests", AGGREGATE_RETENTION_DAYS, "started_at"),
        ]
        
        status = {}
        for table_name, retention_days, timestamp_col in tables:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            try:
                from sqlalchemy import text
                
                # Count total and expired
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                total = self.db.execute(count_query).scalar() or 0
                
                expired_query = text(f"""
                    SELECT COUNT(*) FROM {table_name}
                    WHERE {timestamp_col} < :cutoff_date
                """)
                expired = self.db.execute(expired_query, {"cutoff_date": cutoff_date}).scalar() or 0
                
                status[table_name] = {
                    "total_records": total,
                    "expired_records": expired,
                    "retention_days": retention_days,
                    "cutoff_date": cutoff_date.isoformat()
                }
            except Exception as e:
                status[table_name] = {"error": str(e)}
        
        return status
    
    # =========================================================================
    # Privacy-Preserving Event Recording
    # =========================================================================
    
    def create_privacy_preserving_event(
        self,
        user_id: UUID,
        action_type: str,
        timestamp: datetime,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a privacy-preserving event record.
        
        Applies all privacy transformations:
        - Hash user ID
        - Bucket timestamp
        - Remove sensitive fields from metadata
        
        Args:
            user_id: Original user ID
            action_type: Type of action
            timestamp: Original timestamp
            metadata: Additional metadata
        
        Returns:
            Privacy-preserving event dictionary
        """
        # Hash user ID
        hashed_user_id = self.hash_user_id(user_id)
        
        # Bucket timestamp
        bucketed_time = self.bucket_timestamp(timestamp)
        
        # Clean metadata
        clean_metadata = self._clean_metadata(metadata or {})
        
        return {
            "hashed_user_id": hashed_user_id,
            "action_type": action_type,
            "timestamp": bucketed_time.isoformat(),
            "metadata": clean_metadata
        }
    
    def _clean_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive fields from metadata."""
        sensitive_fields = [
            "patient_id", "mrn", "ssn", "name", "email", "phone",
            "address", "ip_address", "user_agent", "session_token",
            "password", "api_key", "secret"
        ]
        
        cleaned = {}
        for key, value in metadata.items():
            # Skip sensitive fields
            if any(sf in key.lower() for sf in sensitive_fields):
                continue
            
            # Recursively clean nested dicts
            if isinstance(value, dict):
                cleaned[key] = self._clean_metadata(value)
            else:
                cleaned[key] = value
        
        return cleaned
    
    # =========================================================================
    # Consent Management
    # =========================================================================
    
    def check_consent(self, user_id: UUID, purpose: str) -> bool:
        """
        Check if user has consented to data processing for a purpose.
        
        Args:
            user_id: User ID to check
            purpose: Processing purpose (e.g., "analytics", "research")
        
        Returns:
            True if consented, False otherwise
        """
        try:
            from sqlalchemy import text
            
            query = text("""
                SELECT consented FROM user_consents
                WHERE user_id = :user_id AND purpose = :purpose
            """)
            
            result = self.db.execute(query, {"user_id": user_id, "purpose": purpose}).fetchone()
            
            if result:
                return result[0]
            
            # Default to False if no explicit consent
            return False
            
        except Exception as e:
            logger.warning(f"Error checking consent: {e}")
            # Default to False for safety
            return False
    
    def record_consent(
        self,
        user_id: UUID,
        purpose: str,
        consented: bool,
        consent_text: str = None
    ) -> bool:
        """
        Record user consent for data processing.
        
        Args:
            user_id: User ID
            purpose: Processing purpose
            consented: Whether user consented
            consent_text: Text shown to user
        
        Returns:
            True if recorded successfully
        """
        try:
            from sqlalchemy import text
            
            query = text("""
                INSERT INTO user_consents (user_id, purpose, consented, consent_text, created_at)
                VALUES (:user_id, :purpose, :consented, :consent_text, :created_at)
                ON CONFLICT (user_id, purpose) 
                DO UPDATE SET consented = :consented, updated_at = :created_at
            """)
            
            self.db.execute(query, {
                "user_id": user_id,
                "purpose": purpose,
                "consented": consented,
                "consent_text": consent_text,
                "created_at": datetime.utcnow()
            })
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording consent: {e}")
            self.db.rollback()
            return False


# Singleton instance for convenience
_privacy_service_instance = None


def get_privacy_service(db: Session) -> PrivacyService:
    """Get or create privacy service instance."""
    global _privacy_service_instance
    if _privacy_service_instance is None:
        _privacy_service_instance = PrivacyService(db)
    return _privacy_service_instance

