"""
Transfer Learning Models for MAPE-K Adaptation
Stores global and specialty-specific priors for cold-start handling
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from core.database import Base


class GlobalFeaturePrior(Base):
    """
    Global priors learned from all users.
    Used for cold-start when no specialty or user data exists.
    """
    __tablename__ = "global_feature_priors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_key = Column(String(100), nullable=False, unique=True)
    
    # Aggregated statistics from all users
    total_users = Column(Integer, default=0)
    total_interactions = Column(Float, default=0)
    total_successes = Column(Float, default=0)
    
    # Beta distribution parameters (aggregated)
    alpha_prior = Column(Float, default=1.0)
    beta_prior = Column(Float, default=1.0)
    
    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<GlobalFeaturePrior(feature={self.feature_key}, α={self.alpha_prior:.2f}, β={self.beta_prior:.2f})>"


class SpecialtyFeaturePrior(Base):
    """
    Specialty-specific priors learned from users in the same specialty.
    Used for cold-start when user has specialty but no personal data.
    """
    __tablename__ = "specialty_feature_priors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    specialty = Column(String(100), nullable=False)
    feature_key = Column(String(100), nullable=False)
    
    # Aggregated statistics from specialty users
    total_users = Column(Integer, default=0)
    total_interactions = Column(Float, default=0)
    total_successes = Column(Float, default=0)
    
    # Beta distribution parameters (aggregated)
    alpha_prior = Column(Float, default=1.0)
    beta_prior = Column(Float, default=1.0)
    
    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('specialty', 'feature_key', name='uq_specialty_feature'),
    )
    
    def __repr__(self):
        return f"<SpecialtyFeaturePrior(specialty={self.specialty}, feature={self.feature_key}, α={self.alpha_prior:.2f}, β={self.beta_prior:.2f})>"


class TransferLearningLog(Base):
    """
    Logs when transfer learning is applied to users.
    Tracks cold-start handling and transfer effectiveness.
    """
    __tablename__ = "transfer_learning_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Transfer details
    transfer_type = Column(String(50), nullable=False)  # "global", "specialty", "blended"
    specialty = Column(String(100), nullable=True)
    user_experience_days = Column(Integer, nullable=False)
    
    # Prior source
    prior_source = Column(String(100), nullable=False)  # "global_prior", "specialty_prior", "blended"
    features_transferred = Column(Integer, default=0)
    
    # Blending weights (if blended)
    global_weight = Column(Float, nullable=True)
    specialty_weight = Column(Float, nullable=True)
    personal_weight = Column(Float, nullable=True)
    
    # Outcome tracking
    adaptation_applied = Column(JSON, nullable=True)  # Store the adaptation plan
    user_feedback_after = Column(Float, nullable=True)  # User satisfaction (if collected)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<TransferLearningLog(user={self.user_id}, type={self.transfer_type}, days={self.user_experience_days})>"

