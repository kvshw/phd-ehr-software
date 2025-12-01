"""
Bandit State Model for Thompson Sampling MAPE-K Planning
Stores the alpha/beta parameters for each feature per user context
"""
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from core.database import Base


class BanditState(Base):
    """
    Stores Thompson Sampling parameters for each feature per user context.
    
    Thompson Sampling uses Beta distribution with alpha (successes) and beta (failures)
    to balance exploration vs exploitation in feature ordering.
    """
    __tablename__ = "bandit_state"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Feature identification
    feature_key = Column(String(100), nullable=False)  # e.g., "vitals", "medications", "labs"
    
    # Context hash for specialty + time_of_day combination
    # Allows different behaviors for different contexts
    context_hash = Column(String(64), nullable=False, default="default")
    
    # Thompson Sampling Beta distribution parameters
    alpha = Column(Float, default=1.0)  # Prior successes (quick access, acceptance)
    beta = Column(Float, default=1.0)   # Prior failures (slow access, ignore)
    
    # Feature flags
    is_critical = Column(Boolean, default=False)  # Never demote critical features
    
    # Promotion/demotion tracking for cooldowns
    last_promoted = Column(DateTime(timezone=True), nullable=True)
    last_demoted = Column(DateTime(timezone=True), nullable=True)
    promotion_count = Column(Float, default=0)  # Total times promoted
    demotion_count = Column(Float, default=0)   # Total times demoted
    
    # Metrics
    total_interactions = Column(Float, default=0)
    total_successes = Column(Float, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        UniqueConstraint('user_id', 'feature_key', 'context_hash', name='uq_user_feature_context'),
    )
    
    def __repr__(self):
        return f"<BanditState(user={self.user_id}, feature={self.feature_key}, α={self.alpha}, β={self.beta})>"
    
    @property
    def expected_value(self) -> float:
        """Expected value (mean) of the Beta distribution"""
        return self.alpha / (self.alpha + self.beta)
    
    @property
    def variance(self) -> float:
        """Variance of the Beta distribution"""
        total = self.alpha + self.beta
        return (self.alpha * self.beta) / (total * total * (total + 1))
    
    @property
    def confidence_interval(self) -> tuple:
        """95% credible interval approximation"""
        import math
        mean = self.expected_value
        std = math.sqrt(self.variance)
        return (max(0, mean - 1.96 * std), min(1, mean + 1.96 * std))


class BanditAdaptationLog(Base):
    """
    Logs each bandit-based adaptation decision for research analysis
    """
    __tablename__ = "bandit_adaptation_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Context
    specialty = Column(String(100), nullable=True)
    context_hash = Column(String(64), nullable=False)
    
    # Decision details
    feature_key = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)  # "promoted", "demoted", "maintained"
    
    # Bandit state at decision time
    alpha_before = Column(Float, nullable=False)
    beta_before = Column(Float, nullable=False)
    sampled_value = Column(Float, nullable=False)  # Thompson sample value
    
    # Position change
    old_position = Column(Float, nullable=True)
    new_position = Column(Float, nullable=True)
    
    # Constraints applied
    constraint_applied = Column(String(100), nullable=True)  # e.g., "cooldown", "critical", "max_promotions"
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<BanditAdaptationLog(user={self.user_id}, feature={self.feature_key}, action={self.action})>"

