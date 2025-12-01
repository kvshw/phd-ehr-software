"""
Federated Learning Models
Stores FL rounds, client updates, and model versions for privacy-preserving multi-site learning
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from core.database import Base


class FLRound(Base):
    """
    Represents a federated learning round.
    Tracks global model aggregation across multiple sites/clients.
    """
    __tablename__ = "fl_rounds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_number = Column(Integer, nullable=False, unique=True)
    
    # Model information
    model_type = Column(String(50), nullable=False)  # 'vital_risk', 'adaptation_policy', etc.
    global_model_version = Column(String(20), nullable=False)
    aggregation_method = Column(String(50), default="fedavg")  # 'fedavg', 'dual_aggregated', etc.
    
    # Round statistics
    participant_count = Column(Integer, default=0)
    total_samples = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default="pending")  # 'pending', 'in_progress', 'completed', 'failed'
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata (renamed to avoid SQLAlchemy reserved word conflict)
    round_metadata = Column(JSON, nullable=True)  # Additional round information
    
    def __repr__(self):
        return f"<FLRound(round={self.round_number}, model={self.model_type}, status={self.status})>"


class FLClientUpdate(Base):
    """
    Stores weight updates from FL clients (sites/departments).
    Each client trains locally and sends only weight updates (not raw data).
    """
    __tablename__ = "fl_client_updates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_id = Column(UUID(as_uuid=True), ForeignKey("fl_rounds.id"), nullable=False)
    
    # Client identification
    client_id = Column(String(100), nullable=False)  # Site/department identifier
    client_type = Column(String(50), nullable=False)  # 'site', 'department', 'user_group'
    
    # Update information
    model_weights_hash = Column(String(64), nullable=False)  # Hash of weights for verification
    sample_count = Column(Integer, nullable=False)  # Number of samples used in training
    training_loss = Column(Float, nullable=True)  # Local training loss
    validation_loss = Column(Float, nullable=True)  # Local validation loss
    
    # Weight update (stored as JSON for flexibility)
    # In production, might want to store compressed or encrypted
    weight_updates = Column(JSON, nullable=True)  # Actual weight deltas
    
    # Security
    signature = Column(Text, nullable=True)  # Digital signature for verification
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    status = Column(String(20), default="pending")  # 'pending', 'aggregated', 'rejected'
    rejection_reason = Column(String(255), nullable=True)
    
    def __repr__(self):
        return f"<FLClientUpdate(client={self.client_id}, round={self.round_id}, samples={self.sample_count})>"


class FLGlobalModel(Base):
    """
    Stores global model snapshots after aggregation.
    Versioned for rollback and audit purposes.
    """
    __tablename__ = "fl_global_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_id = Column(UUID(as_uuid=True), ForeignKey("fl_rounds.id"), nullable=True)
    
    # Model information
    model_type = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False, unique=True)
    
    # Model weights (JSON representation)
    model_weights = Column(JSON, nullable=False)
    model_weights_hash = Column(String(64), nullable=False)
    
    # Performance metrics
    global_accuracy = Column(Float, nullable=True)
    global_loss = Column(Float, nullable=True)
    test_accuracy = Column(Float, nullable=True)
    
    # Aggregation metadata
    aggregation_method = Column(String(50), nullable=False)
    participant_count = Column(Integer, nullable=False)
    total_samples = Column(Integer, nullable=False)
    
    # Status
    is_active = Column(String(10), default="false")  # 'true' or 'false' (string for JSON compatibility)
    is_deployed = Column(String(10), default="false")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata (renamed to avoid SQLAlchemy reserved word conflict)
    model_metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<FLGlobalModel(version={self.version}, type={self.model_type}, active={self.is_active})>"


class FLClient(Base):
    """
    Represents a federated learning client (site/department).
    Tracks client participation and local model state.
    """
    __tablename__ = "fl_clients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(String(100), nullable=False, unique=True)
    client_name = Column(String(255), nullable=True)
    client_type = Column(String(50), nullable=False)  # 'site', 'department', 'user_group'
    
    # Client status
    is_active = Column(String(10), default="true")
    last_participation = Column(DateTime(timezone=True), nullable=True)
    participation_count = Column(Integer, default=0)
    
    # Local model state
    local_model_version = Column(String(20), nullable=True)
    local_data_count = Column(Integer, default=0)
    
    # Security
    public_key = Column(Text, nullable=True)  # For signature verification
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Metadata (renamed to avoid SQLAlchemy reserved word conflict)
    client_metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<FLClient(id={self.client_id}, type={self.client_type}, active={self.is_active})>"


class FLPolicyRound(Base):
    """
    Federated learning rounds specifically for adaptation policies (bandit parameters).
    Aggregates UI adaptation policies across users/specialties.
    """
    __tablename__ = "fl_policy_rounds"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_number = Column(Integer, nullable=False, unique=True)
    
    # Policy information
    policy_type = Column(String(50), nullable=False)  # 'bandit_prior', 'specialty_prior', etc.
    specialty = Column(String(100), nullable=True)  # If specialty-specific
    
    # Aggregation statistics
    participant_count = Column(Integer, default=0)
    total_features = Column(Integer, default=0)
    
    # Status
    status = Column(String(20), default="pending")
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<FLPolicyRound(round={self.round_number}, type={self.policy_type}, specialty={self.specialty})>"


class FLPolicyUpdate(Base):
    """
    Policy updates from individual users for federated aggregation.
    Contains aggregated bandit parameters (alpha/beta) per feature.
    """
    __tablename__ = "fl_policy_updates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_id = Column(UUID(as_uuid=True), ForeignKey("fl_policy_rounds.id"), nullable=False)
    
    # User/site identification
    user_id = Column(UUID(as_uuid=True), nullable=True)  # If user-level
    client_id = Column(String(100), nullable=True)  # If site-level
    specialty = Column(String(100), nullable=True)
    
    # Policy parameters (aggregated per feature)
    # Format: {feature_key: {alpha: float, beta: float, interactions: int}}
    policy_parameters = Column(JSON, nullable=False)
    
    # Statistics
    total_interactions = Column(Integer, default=0)
    total_features = Column(Integer, default=0)
    
    # Timestamps
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    status = Column(String(20), default="pending")
    
    def __repr__(self):
        return f"<FLPolicyUpdate(round={self.round_id}, user={self.user_id}, features={self.total_features})>"

