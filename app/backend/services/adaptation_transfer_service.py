"""
Transfer Learning Service for MAPE-K Adaptation
Handles cold-start by transferring learned patterns from similar users/specialties
"""
from typing import Dict, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func

from models.transfer_learning import (
    GlobalFeaturePrior,
    SpecialtyFeaturePrior,
    TransferLearningLog,
)
from models.bandit_state import BanditState
from models.user import User

logger = logging.getLogger(__name__)


class AdaptationTransferService:
    """
    Service for transferring learned adaptation patterns to new users.
    
    Implements a three-tier cold-start strategy:
    1. Days 0-7: Use specialty priors (or global if no specialty)
    2. Days 7-30: Blend priors with personal data (gradual transition)
    3. Days 30+: Use personal data only (fully personalized)
    """
    
    # Cold-start thresholds
    COLD_START_DAYS = 7      # Use priors only
    WARM_START_DAYS = 30     # Blend priors and personal
    
    # Blending weights (for warm-start period)
    INITIAL_PRIOR_WEIGHT = 0.7   # Start with 70% prior, 30% personal
    FINAL_PRIOR_WEIGHT = 0.0     # End with 0% prior, 100% personal
    
    # Minimum users required for specialty prior
    MIN_SPECIALTY_USERS = 3
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_transferred_priors(
        self,
        user_id: UUID,
        specialty: Optional[str] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Get transferred priors for a user based on experience level.
        
        Returns:
            Dictionary mapping feature_key to {alpha, beta, source, weight}
        """
        # Calculate user experience
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        experience_days = self._calculate_experience_days(user_id)
        
        # Determine transfer strategy
        if experience_days < self.COLD_START_DAYS:
            # Cold-start: Use priors only
            priors = self._get_cold_start_priors(specialty)
            transfer_type = "specialty" if specialty else "global"
        elif experience_days < self.WARM_START_DAYS:
            # Warm-start: Blend priors with personal data
            priors = self._get_warm_start_priors(user_id, specialty, experience_days)
            transfer_type = "blended"
        else:
            # Fully personalized: Use personal data only
            priors = self._get_personal_priors(user_id)
            transfer_type = "personal"
        
        # Log transfer application
        self._log_transfer(user_id, specialty, experience_days, transfer_type, priors)
        
        return priors
    
    def _calculate_experience_days(self, user_id: UUID) -> int:
        """Calculate how many days the user has been using the system"""
        from datetime import datetime, timedelta
        
        # Check first bandit interaction (more reliable than user.created_at)
        first_interaction = self.db.query(func.min(BanditState.created_at)).filter(
            BanditState.user_id == user_id
        ).scalar()
        
        # Check first user action as fallback
        if not first_interaction:
            from models.user_action import UserAction
            first_action = self.db.query(func.min(UserAction.created_at)).filter(
                UserAction.user_id == user_id
            ).scalar()
            first_interaction = first_action
        
        if first_interaction:
            # Handle both datetime and date objects
            if isinstance(first_interaction, datetime):
                start_date = first_interaction
            else:
                start_date = datetime.combine(first_interaction, datetime.min.time())
            
            days = (datetime.utcnow() - start_date).days
            return max(0, days)
        else:
            # No interactions found - user is brand new
            return 0
    
    def _get_cold_start_priors(
        self,
        specialty: Optional[str],
    ) -> Dict[str, Dict[str, float]]:
        """
        Get cold-start priors (specialty or global).
        Used for users with < 7 days experience.
        """
        priors = {}
        
        # Try specialty priors first
        if specialty:
            specialty_priors = self._get_specialty_priors(specialty)
            if specialty_priors:
                for feature, stats in specialty_priors.items():
                    priors[feature] = {
                        "alpha": stats["alpha_prior"],
                        "beta": stats["beta_prior"],
                        "source": "specialty",
                        "weight": 1.0,
                        "total_users": stats["total_users"],
                    }
                logger.info(f"Using specialty priors for {specialty}: {len(priors)} features")
                return priors
        
        # Fall back to global priors
        global_priors = self._get_global_priors()
        for feature, stats in global_priors.items():
            priors[feature] = {
                "alpha": stats["alpha_prior"],
                "beta": stats["beta_prior"],
                "source": "global",
                "weight": 1.0,
                "total_users": stats["total_users"],
            }
        
        logger.info(f"Using global priors: {len(priors)} features")
        return priors
    
    def _get_warm_start_priors(
        self,
        user_id: UUID,
        specialty: Optional[str],
        experience_days: int,
    ) -> Dict[str, Dict[str, float]]:
        """
        Get warm-start priors (blended).
        Used for users with 7-30 days experience.
        """
        # Get personal data
        personal_states = self._get_personal_states(user_id)
        
        # Get prior data
        if specialty:
            prior_data = self._get_specialty_priors(specialty)
            prior_source = "specialty"
        else:
            prior_data = self._get_global_priors()
            prior_source = "global"
        
        # Calculate blending weights
        # Linear interpolation from INITIAL_PRIOR_WEIGHT to FINAL_PRIOR_WEIGHT
        days_in_warm = experience_days - self.COLD_START_DAYS
        total_warm_days = self.WARM_START_DAYS - self.COLD_START_DAYS
        progress = days_in_warm / total_warm_days
        
        prior_weight = self.INITIAL_PRIOR_WEIGHT * (1 - progress) + self.FINAL_PRIOR_WEIGHT * progress
        personal_weight = 1 - prior_weight
        
        # Blend priors
        priors = {}
        all_features = set(list(prior_data.keys()) + list(personal_states.keys()))
        
        for feature in all_features:
            prior_stats = prior_data.get(feature, {"alpha_prior": 1.0, "beta_prior": 1.0, "total_users": 0})
            personal_state = personal_states.get(feature)
            
            if personal_state:
                # Blend: weighted average of prior and personal
                blended_alpha = prior_weight * prior_stats["alpha_prior"] + personal_weight * personal_state.alpha
                blended_beta = prior_weight * prior_stats["beta_prior"] + personal_weight * personal_state.beta
            else:
                # No personal data yet, use prior
                blended_alpha = prior_stats["alpha_prior"]
                blended_beta = prior_stats["beta_prior"]
            
            priors[feature] = {
                "alpha": blended_alpha,
                "beta": blended_beta,
                "source": "blended",
                "weight": personal_weight,
                "prior_weight": prior_weight,
                "prior_source": prior_source,
            }
        
        logger.info(
            f"Blended priors for user {user_id}: {prior_weight:.2f} prior, {personal_weight:.2f} personal"
        )
        return priors
    
    def _get_personal_priors(self, user_id: UUID) -> Dict[str, Dict[str, float]]:
        """Get fully personalized priors (user's own data)."""
        personal_states = self._get_personal_states(user_id)
        
        priors = {}
        for feature, state in personal_states.items():
            priors[feature] = {
                "alpha": state.alpha,
                "beta": state.beta,
                "source": "personal",
                "weight": 1.0,
            }
        
        return priors
    
    def _get_specialty_priors(self, specialty: str) -> Dict[str, Dict]:
        """Get specialty-specific priors from database"""
        stmt = select(SpecialtyFeaturePrior).where(
            SpecialtyFeaturePrior.specialty == specialty
        )
        results = self.db.execute(stmt).scalars().all()
        
        if not results or len(results) < self.MIN_SPECIALTY_USERS:
            return {}
        
        priors = {}
        for prior in results:
            priors[prior.feature_key] = {
                "alpha_prior": prior.alpha_prior,
                "beta_prior": prior.beta_prior,
                "total_users": prior.total_users,
            }
        
        return priors
    
    def _get_global_priors(self) -> Dict[str, Dict]:
        """Get global priors from database"""
        stmt = select(GlobalFeaturePrior)
        results = self.db.execute(stmt).scalars().all()
        
        priors = {}
        for prior in results:
            priors[prior.feature_key] = {
                "alpha_prior": prior.alpha_prior,
                "beta_prior": prior.beta_prior,
                "total_users": prior.total_users,
            }
        
        return priors
    
    def _get_personal_states(self, user_id: UUID) -> Dict[str, BanditState]:
        """Get user's personal bandit states"""
        stmt = select(BanditState).where(BanditState.user_id == user_id)
        results = self.db.execute(stmt).scalars().all()
        
        states = {}
        for state in results:
            states[state.feature_key] = state
        
        return states
    
    def _log_transfer(
        self,
        user_id: UUID,
        specialty: Optional[str],
        experience_days: int,
        transfer_type: str,
        priors: Dict[str, Dict[str, float]],
    ) -> None:
        """Log transfer learning application for research"""
        # Determine prior source
        if transfer_type == "blended":
            first_prior = next(iter(priors.values()))
            prior_source = first_prior.get("prior_source", "unknown")
            global_weight = first_prior.get("prior_weight", 0.0) if prior_source == "global" else None
            specialty_weight = first_prior.get("prior_weight", 0.0) if prior_source == "specialty" else None
            personal_weight = first_prior.get("weight", 0.0)
        elif transfer_type == "specialty":
            prior_source = "specialty_prior"
            global_weight = None
            specialty_weight = 1.0
            personal_weight = 0.0
        else:
            prior_source = "global_prior" if not specialty else "specialty_prior"
            global_weight = 1.0 if not specialty else None
            specialty_weight = 1.0 if specialty else None
            personal_weight = 0.0
        
        log = TransferLearningLog(
            user_id=user_id,
            transfer_type=transfer_type,
            specialty=specialty,
            user_experience_days=experience_days,
            prior_source=prior_source,
            features_transferred=len(priors),
            global_weight=global_weight,
            specialty_weight=specialty_weight,
            personal_weight=personal_weight,
        )
        
        self.db.add(log)
        self.db.commit()
    
    def update_global_priors(self) -> None:
        """
        Update global priors by aggregating all user bandit states.
        Should be run periodically (e.g., daily cron job).
        """
        logger.info("Updating global feature priors...")
        
        # Aggregate all bandit states
        stmt = select(
            BanditState.feature_key,
            func.count(func.distinct(BanditState.user_id)).label("user_count"),
            func.sum(BanditState.total_interactions).label("total_interactions"),
            func.sum(BanditState.total_successes).label("total_successes"),
            func.avg(BanditState.alpha).label("avg_alpha"),
            func.avg(BanditState.beta).label("avg_beta"),
        ).group_by(BanditState.feature_key)
        
        results = self.db.execute(stmt).all()
        
        for row in results:
            # Get or create global prior
            prior = self.db.query(GlobalFeaturePrior).filter(
                GlobalFeaturePrior.feature_key == row.feature_key
            ).first()
            
            if not prior:
                prior = GlobalFeaturePrior(feature_key=row.feature_key)
                self.db.add(prior)
            
            # Update aggregated statistics
            prior.total_users = row.user_count or 0
            prior.total_interactions = float(row.total_interactions or 0)
            prior.total_successes = float(row.total_successes or 0)
            prior.alpha_prior = float(row.avg_alpha or 1.0)
            prior.beta_prior = float(row.avg_beta or 1.0)
            prior.last_updated = datetime.utcnow()
        
        self.db.commit()
        logger.info(f"Updated {len(results)} global feature priors")
    
    def update_specialty_priors(self, specialty: str) -> None:
        """
        Update specialty-specific priors by aggregating bandit states from specialty users.
        Should be run periodically.
        """
        logger.info(f"Updating specialty priors for {specialty}...")
        
        # Get users with this specialty
        specialty_users = self.db.query(User.id).filter(User.specialty == specialty).all()
        user_ids = [u.id for u in specialty_users]
        
        if len(user_ids) < self.MIN_SPECIALTY_USERS:
            logger.warning(f"Not enough users ({len(user_ids)}) for specialty {specialty}")
            return
        
        # Aggregate bandit states for these users
        stmt = select(
            BanditState.feature_key,
            func.count(func.distinct(BanditState.user_id)).label("user_count"),
            func.sum(BanditState.total_interactions).label("total_interactions"),
            func.sum(BanditState.total_successes).label("total_successes"),
            func.avg(BanditState.alpha).label("avg_alpha"),
            func.avg(BanditState.beta).label("avg_beta"),
        ).where(
            BanditState.user_id.in_(user_ids)
        ).group_by(BanditState.feature_key)
        
        results = self.db.execute(stmt).all()
        
        for row in results:
            # Get or create specialty prior
            prior = self.db.query(SpecialtyFeaturePrior).filter(
                and_(
                    SpecialtyFeaturePrior.specialty == specialty,
                    SpecialtyFeaturePrior.feature_key == row.feature_key,
                )
            ).first()
            
            if not prior:
                prior = SpecialtyFeaturePrior(
                    specialty=specialty,
                    feature_key=row.feature_key,
                )
                self.db.add(prior)
            
            # Update aggregated statistics
            prior.total_users = row.user_count or 0
            prior.total_interactions = float(row.total_interactions or 0)
            prior.total_successes = float(row.total_successes or 0)
            prior.alpha_prior = float(row.avg_alpha or 1.0)
            prior.beta_prior = float(row.avg_beta or 1.0)
            prior.last_updated = datetime.utcnow()
        
        self.db.commit()
        logger.info(f"Updated {len(results)} specialty priors for {specialty}")


def get_transfer_service(db: Session) -> AdaptationTransferService:
    """Factory function to get AdaptationTransferService instance"""
    return AdaptationTransferService(db)

