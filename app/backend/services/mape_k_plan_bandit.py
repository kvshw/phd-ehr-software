"""
MAPE-K Bandit-Based Plan Service
Uses Thompson Sampling with constraints for intelligent feature ordering

This replaces simple rule-based planning with a principled exploration-exploitation
approach that learns optimal layouts per user over time.
"""
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
import random
import hashlib
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from models.bandit_state import BanditState, BanditAdaptationLog
from services.adaptation_transfer_service import AdaptationTransferService

logger = logging.getLogger(__name__)


# Configuration
class BanditConfig:
    """Configuration for bandit-based planning"""
    
    # Cooldown periods (prevent layout thrashing)
    PROMOTION_COOLDOWN_HOURS = 24    # Min hours between promotions
    DEMOTION_COOLDOWN_HOURS = 168    # Min hours between demotions (7 days)
    
    # Constraints
    MAX_PROMOTIONS_PER_CYCLE = 3     # Max features to promote in one adaptation
    MAX_DEMOTIONS_PER_CYCLE = 1      # Max features to demote in one adaptation
    CONFIDENCE_THRESHOLD = 0.6       # Min confidence to make a change
    
    # Prior parameters (initial uncertainty)
    DEFAULT_ALPHA = 1.0              # Uniform prior
    DEFAULT_BETA = 1.0               # Uniform prior
    
    # Learning rates
    SUCCESS_WEIGHT = 1.0             # Weight for positive feedback
    FAILURE_WEIGHT = 0.5             # Weight for negative feedback (less punishing)
    
    # Critical features that cannot be demoted
    CRITICAL_FEATURES = {
        "allergies",
        "safety",
        "medications",
        "vitals",
    }
    
    # Default feature order (baseline)
    DEFAULT_FEATURE_ORDER = [
        "summary",
        "demographics", 
        "diagnoses",
        "medications",
        "allergies",
        "vitals",
        "labs",
        "imaging",
        "suggestions",
        "safety",
    ]
    
    # Specialty-specific feature preferences (prior adjustments)
    SPECIALTY_PRIORS = {
        "cardiology": {"vitals": 2.0, "labs": 1.5, "imaging": 1.5},
        "neurology": {"imaging": 2.0, "vitals": 1.5},
        "emergency": {"vitals": 2.5, "allergies": 2.0, "medications": 2.0},
        "geriatrics": {"medications": 2.0, "allergies": 1.5},
        "oncology": {"labs": 2.0, "imaging": 1.8},
        "pediatrics": {"vitals": 1.8, "growth": 2.0},
        "psychiatry": {"history": 2.0, "medications": 1.5},
    }


class BanditPlanService:
    """
    Thompson Sampling-based plan generation for MAPE-K adaptation.
    
    Uses Beta distributions to model uncertainty about feature preferences,
    and applies constraints to ensure safety and prevent layout thrashing.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.config = BanditConfig()
    
    def generate_plan(
        self,
        user_id: UUID,
        specialty: Optional[str] = None,
        time_of_day: Optional[str] = None,
        workflow_state: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate an adaptation plan using Thompson Sampling.
        
        Args:
            user_id: User ID
            specialty: User's medical specialty (e.g., "cardiology")
            time_of_day: Time context ("morning", "afternoon", "evening", "night")
            workflow_state: Current workflow ("viewing", "editing", "reviewing")
        
        Returns:
            Dictionary with adapted feature order, density, and explanation
        """
        # Build context hash
        context_hash = self._build_context_hash(specialty, time_of_day)
        
        # Get or initialize bandit states for all features
        feature_states = self._get_or_init_feature_states(user_id, context_hash, specialty)
        
        # Sample from Beta distributions (Thompson Sampling)
        sampled_values = self._thompson_sample(feature_states)
        
        # Apply constraints and generate ordered list
        ordered_features, actions, constraints = self._apply_constraints_and_order(
            feature_states, sampled_values
        )
        
        # Log adaptation decisions
        self._log_adaptations(user_id, specialty, context_hash, feature_states, sampled_values, actions, constraints)
        
        # Build plan
        plan = self._build_plan(ordered_features, feature_states, sampled_values)
        
        # Generate explanation
        explanation = self._generate_explanation(actions, constraints, specialty)
        
        return {
            "plan": plan,
            "order": ordered_features,
            "sampled_values": {k: round(v, 4) for k, v in sampled_values.items()},
            "actions": actions,
            "constraints_applied": constraints,
            "explanation": explanation,
            "algorithm": "thompson_sampling",
            "context": {
                "specialty": specialty,
                "time_of_day": time_of_day,
                "context_hash": context_hash,
            }
        }
    
    def record_feedback(
        self,
        user_id: UUID,
        feature_key: str,
        success: bool,
        specialty: Optional[str] = None,
        time_of_day: Optional[str] = None,
        weight: float = 1.0,
    ) -> None:
        """
        Record feedback for a feature to update bandit parameters.
        
        Args:
            user_id: User ID
            feature_key: Feature that received feedback
            success: True if positive interaction, False if negative
            specialty: User's specialty for context
            time_of_day: Time context
            weight: Weight of this feedback (default 1.0)
        """
        context_hash = self._build_context_hash(specialty, time_of_day)
        
        state = self._get_bandit_state(user_id, feature_key, context_hash)
        if not state:
            state = self._init_bandit_state(user_id, feature_key, context_hash, specialty)
        
        # Update Beta distribution parameters
        if success:
            state.alpha += weight * self.config.SUCCESS_WEIGHT
            state.total_successes += 1
        else:
            state.beta += weight * self.config.FAILURE_WEIGHT
        
        state.total_interactions += 1
        state.updated_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(
            f"Bandit feedback recorded: user={user_id}, feature={feature_key}, "
            f"success={success}, new_alpha={state.alpha:.2f}, new_beta={state.beta:.2f}"
        )
    
    def _build_context_hash(
        self,
        specialty: Optional[str],
        time_of_day: Optional[str],
    ) -> str:
        """Build a context hash for grouping similar contexts"""
        context_str = f"{specialty or 'general'}_{time_of_day or 'default'}"
        return hashlib.md5(context_str.encode()).hexdigest()[:16]
    
    def _get_or_init_feature_states(
        self,
        user_id: UUID,
        context_hash: str,
        specialty: Optional[str],
    ) -> Dict[str, BanditState]:
        """Get existing bandit states or initialize new ones for all features"""
        states = {}
        
        for feature in self.config.DEFAULT_FEATURE_ORDER:
            state = self._get_bandit_state(user_id, feature, context_hash)
            if not state:
                state = self._init_bandit_state(user_id, feature, context_hash, specialty)
            states[feature] = state
        
        return states
    
    def _get_bandit_state(
        self,
        user_id: UUID,
        feature_key: str,
        context_hash: str,
    ) -> Optional[BanditState]:
        """Get bandit state for a specific user/feature/context"""
        stmt = select(BanditState).where(
            and_(
                BanditState.user_id == user_id,
                BanditState.feature_key == feature_key,
                BanditState.context_hash == context_hash,
            )
        )
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    def _init_bandit_state(
        self,
        user_id: UUID,
        feature_key: str,
        context_hash: str,
        specialty: Optional[str],
    ) -> BanditState:
        """Initialize bandit state with transfer learning priors"""
        # Try to get transferred priors first
        transfer_service = AdaptationTransferService(self.db)
        try:
            transferred_priors = transfer_service.get_transferred_priors(user_id, specialty)
            if feature_key in transferred_priors:
                prior = transferred_priors[feature_key]
                alpha = prior["alpha"]
                beta = prior["beta"]
                logger.info(
                    f"Using transferred prior for {feature_key}: "
                    f"α={alpha:.2f}, β={beta:.2f} (source: {prior.get('source', 'unknown')})"
                )
            else:
                # Fall back to specialty-specific prior if available
                alpha = self.config.DEFAULT_ALPHA
                if specialty and specialty in self.config.SPECIALTY_PRIORS:
                    specialty_priors = self.config.SPECIALTY_PRIORS[specialty]
                    alpha = specialty_priors.get(feature_key, self.config.DEFAULT_ALPHA)
                beta = self.config.DEFAULT_BETA
        except Exception as e:
            # Fall back to defaults if transfer learning fails
            logger.warning(f"Transfer learning failed, using defaults: {e}")
            alpha = self.config.DEFAULT_ALPHA
            if specialty and specialty in self.config.SPECIALTY_PRIORS:
                specialty_priors = self.config.SPECIALTY_PRIORS[specialty]
                alpha = specialty_priors.get(feature_key, self.config.DEFAULT_ALPHA)
            beta = self.config.DEFAULT_BETA
        
        state = BanditState(
            user_id=user_id,
            feature_key=feature_key,
            context_hash=context_hash,
            alpha=alpha,
            beta=beta,
            is_critical=feature_key in self.config.CRITICAL_FEATURES,
        )
        
        self.db.add(state)
        self.db.commit()
        self.db.refresh(state)
        
        return state
    
    def _thompson_sample(self, feature_states: Dict[str, BanditState]) -> Dict[str, float]:
        """Sample from Beta distributions for each feature (Thompson Sampling)"""
        sampled = {}
        for feature, state in feature_states.items():
            # Sample from Beta(alpha, beta)
            sampled[feature] = random.betavariate(state.alpha, state.beta)
        return sampled
    
    def _apply_constraints_and_order(
        self,
        feature_states: Dict[str, BanditState],
        sampled_values: Dict[str, float],
    ) -> Tuple[List[str], Dict[str, str], List[str]]:
        """
        Apply constraints and generate final feature ordering.
        
        Returns:
            - Ordered list of features
            - Actions taken for each feature
            - Constraints that were applied
        """
        now = datetime.utcnow()
        actions = {}
        constraints_applied = []
        
        # Sort features by sampled value (descending)
        sorted_features = sorted(
            sampled_values.keys(),
            key=lambda f: sampled_values[f],
            reverse=True
        )
        
        # Get default positions for comparison
        default_positions = {
            f: i for i, f in enumerate(self.config.DEFAULT_FEATURE_ORDER)
        }
        
        # Track promotions/demotions
        promotions = 0
        demotions = 0
        
        final_order = []
        
        for feature in sorted_features:
            state = feature_states[feature]
            default_pos = default_positions.get(feature, len(final_order))
            new_pos = len(final_order)
            
            action = "maintained"
            constraint = None
            
            # Check if this would be a promotion or demotion
            is_promotion = new_pos < default_pos
            is_demotion = new_pos > default_pos
            
            # Apply constraints
            if is_demotion and state.is_critical:
                # Cannot demote critical features - put at original position
                constraint = "critical_feature"
                constraints_applied.append(f"{feature}: critical feature, cannot demote")
                action = "maintained"
            
            elif is_promotion:
                # Check promotion cooldown
                if state.last_promoted:
                    hours_since = (now - state.last_promoted).total_seconds() / 3600
                    if hours_since < self.config.PROMOTION_COOLDOWN_HOURS:
                        constraint = "promotion_cooldown"
                        constraints_applied.append(f"{feature}: promotion cooldown ({hours_since:.1f}h < {self.config.PROMOTION_COOLDOWN_HOURS}h)")
                        action = "maintained"
                
                # Check max promotions
                if promotions >= self.config.MAX_PROMOTIONS_PER_CYCLE and constraint is None:
                    constraint = "max_promotions"
                    constraints_applied.append(f"{feature}: max promotions reached ({self.config.MAX_PROMOTIONS_PER_CYCLE})")
                    action = "maintained"
                
                if constraint is None:
                    action = "promoted"
                    promotions += 1
                    state.last_promoted = now
                    state.promotion_count += 1
            
            elif is_demotion:
                # Check demotion cooldown
                if state.last_demoted:
                    hours_since = (now - state.last_demoted).total_seconds() / 3600
                    if hours_since < self.config.DEMOTION_COOLDOWN_HOURS:
                        constraint = "demotion_cooldown"
                        constraints_applied.append(f"{feature}: demotion cooldown ({hours_since:.1f}h < {self.config.DEMOTION_COOLDOWN_HOURS}h)")
                        action = "maintained"
                
                # Check max demotions
                if demotions >= self.config.MAX_DEMOTIONS_PER_CYCLE and constraint is None:
                    constraint = "max_demotions"
                    constraints_applied.append(f"{feature}: max demotions reached ({self.config.MAX_DEMOTIONS_PER_CYCLE})")
                    action = "maintained"
                
                # Check confidence threshold
                if state.variance > 0.1 and constraint is None:  # High uncertainty
                    constraint = "low_confidence"
                    constraints_applied.append(f"{feature}: low confidence (variance={state.variance:.3f})")
                    action = "maintained"
                
                if constraint is None:
                    action = "demoted"
                    demotions += 1
                    state.last_demoted = now
                    state.demotion_count += 1
            
            actions[feature] = action
            final_order.append(feature)
        
        # Commit state updates
        self.db.commit()
        
        # If too many constraints applied, fall back to default order
        if len(constraints_applied) > len(feature_states) // 2:
            final_order = self.config.DEFAULT_FEATURE_ORDER.copy()
            constraints_applied.append("Too many constraints - using default order")
        
        return final_order, actions, constraints_applied
    
    def _log_adaptations(
        self,
        user_id: UUID,
        specialty: Optional[str],
        context_hash: str,
        feature_states: Dict[str, BanditState],
        sampled_values: Dict[str, float],
        actions: Dict[str, str],
        constraints: List[str],
    ) -> None:
        """Log all adaptation decisions for research analysis"""
        default_positions = {
            f: i for i, f in enumerate(self.config.DEFAULT_FEATURE_ORDER)
        }
        
        for feature, action in actions.items():
            state = feature_states[feature]
            
            # Find constraint for this feature
            constraint = None
            for c in constraints:
                if c.startswith(f"{feature}:"):
                    constraint = c.split(": ", 1)[1] if ": " in c else c
                    break
            
            log = BanditAdaptationLog(
                user_id=user_id,
                specialty=specialty,
                context_hash=context_hash,
                feature_key=feature,
                action=action,
                alpha_before=state.alpha,
                beta_before=state.beta,
                sampled_value=sampled_values[feature],
                old_position=default_positions.get(feature),
                constraint_applied=constraint,
            )
            self.db.add(log)
        
        self.db.commit()
    
    def _build_plan(
        self,
        ordered_features: List[str],
        feature_states: Dict[str, BanditState],
        sampled_values: Dict[str, float],
    ) -> Dict[str, Any]:
        """Build the final adaptation plan"""
        return {
            "order": ordered_features,
            "suggestion_density": self._calculate_suggestion_density(feature_states),
            "flags": {
                "bandit_based": True,
                "feature_confidence": {
                    f: round(s.expected_value, 3)
                    for f, s in feature_states.items()
                },
            },
        }
    
    def _calculate_suggestion_density(
        self,
        feature_states: Dict[str, BanditState],
    ) -> str:
        """Calculate suggestion density based on overall acceptance"""
        suggestions_state = feature_states.get("suggestions")
        if suggestions_state:
            acceptance_rate = suggestions_state.expected_value
            if acceptance_rate > 0.7:
                return "high"
            elif acceptance_rate > 0.4:
                return "medium"
            else:
                return "low"
        return "medium"
    
    def _generate_explanation(
        self,
        actions: Dict[str, str],
        constraints: List[str],
        specialty: Optional[str],
    ) -> str:
        """Generate human-readable explanation of the adaptation"""
        parts = []
        
        # Summarize actions
        promoted = [f for f, a in actions.items() if a == "promoted"]
        demoted = [f for f, a in actions.items() if a == "demoted"]
        
        if promoted:
            parts.append(f"Promoted: {', '.join(promoted)}")
        if demoted:
            parts.append(f"Demoted: {', '.join(demoted)}")
        if not promoted and not demoted:
            parts.append("Layout maintained (no changes)")
        
        # Add specialty context
        if specialty:
            parts.append(f"Adapted for {specialty} specialty")
        
        # Mention constraints if relevant
        if constraints:
            parts.append(f"({len(constraints)} constraint(s) applied)")
        
        return ". ".join(parts) + "."


# Utility functions for integration
def get_bandit_plan_service(db: Session) -> BanditPlanService:
    """Factory function to get BanditPlanService instance"""
    return BanditPlanService(db)


def record_feature_interaction(
    db: Session,
    user_id: UUID,
    feature_key: str,
    interaction_type: str,
    specialty: Optional[str] = None,
) -> None:
    """
    Record a user interaction with a feature for bandit learning.
    
    Args:
        db: Database session
        user_id: User ID
        feature_key: Feature interacted with
        interaction_type: Type of interaction:
            - "quick_access": User quickly accessed feature (success)
            - "prolonged_use": User spent significant time (success)
            - "ignored": User ignored/scrolled past (failure)
            - "suggestion_accepted": AI suggestion accepted (success)
            - "suggestion_ignored": AI suggestion ignored (failure)
        specialty: User's specialty
    """
    success_interactions = {"quick_access", "prolonged_use", "suggestion_accepted"}
    success = interaction_type in success_interactions
    
    service = BanditPlanService(db)
    service.record_feedback(
        user_id=user_id,
        feature_key=feature_key,
        success=success,
        specialty=specialty,
    )

