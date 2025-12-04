"""
Regret Analysis Service for Thompson Sampling Bandits

This service provides formal regret tracking and analysis for the
bandit-based UI adaptation system. Essential for academic publications
and demonstrating algorithmic convergence.

References:
- Agrawal & Goyal (2012): Analysis of Thompson Sampling for the Multi-armed Bandit Problem
- Russo et al. (2018): A Tutorial on Thompson Sampling

Key Metrics:
- Instantaneous regret: r_t = μ* - μ_chosen
- Cumulative regret: R_T = Σ r_t for t=1 to T
- Bayesian regret bound: E[R_T] ≤ O(√(K·T·log(T)))
"""

from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
from datetime import datetime, timedelta
from dataclasses import dataclass
import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func, text

logger = logging.getLogger(__name__)


@dataclass
class RegretDataPoint:
    """Single regret observation"""
    timestamp: datetime
    chosen_arm: str
    optimal_arm: str
    chosen_reward: float
    optimal_reward: float
    instantaneous_regret: float
    cumulative_regret: float
    context: Dict[str, Any]


@dataclass
class RegretAnalysisResult:
    """Comprehensive regret analysis result"""
    total_rounds: int
    cumulative_regret: float
    average_regret: float
    regret_per_arm: Dict[str, float]
    theoretical_bound: float
    empirical_vs_theoretical_ratio: float
    convergence_detected: bool
    convergence_round: Optional[int]
    regret_curve: List[Tuple[int, float]]  # (round, cumulative_regret)
    arm_selection_frequency: Dict[str, int]
    optimal_arm_selection_rate: float


class RegretAnalysisService:
    """
    Track and analyze regret for Thompson Sampling bandits.
    
    This service enables:
    1. Real-time regret tracking during adaptation
    2. Post-hoc regret analysis for research papers
    3. Convergence detection
    4. Comparison with theoretical bounds
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_instantaneous_regret(
        self,
        chosen_arm: str,
        true_rewards: Dict[str, float]
    ) -> Tuple[float, str]:
        """
        Calculate instantaneous regret: r_t = μ* - μ_chosen
        
        Args:
            chosen_arm: The arm selected by the bandit
            true_rewards: Dictionary of arm -> true reward probability
            
        Returns:
            Tuple of (instantaneous_regret, optimal_arm)
        """
        if not true_rewards:
            return 0.0, chosen_arm
            
        optimal_arm = max(true_rewards.keys(), key=lambda k: true_rewards[k])
        optimal_reward = true_rewards[optimal_arm]
        chosen_reward = true_rewards.get(chosen_arm, 0.0)
        
        instantaneous_regret = optimal_reward - chosen_reward
        return max(0.0, instantaneous_regret), optimal_arm
    
    def get_bayesian_regret_bound(
        self,
        num_arms: int,
        time_horizon: int
    ) -> float:
        """
        Calculate theoretical Bayesian regret bound for Thompson Sampling.
        
        Thompson Sampling achieves:
        E[R_T] ≤ O(√(K·T·log(T)))
        
        More precisely (Agrawal & Goyal, 2012):
        E[R_T] ≤ C · √(K·T·log(T)) where C is a constant ~1-2
        
        Args:
            num_arms: Number of arms (K)
            time_horizon: Number of rounds (T)
            
        Returns:
            Theoretical regret bound
        """
        if time_horizon <= 0 or num_arms <= 0:
            return 0.0
            
        # Use constant C ≈ 1.5 (empirically reasonable)
        C = 1.5
        return C * math.sqrt(num_arms * time_horizon * max(1, math.log(time_horizon)))
    
    def log_regret_observation(
        self,
        user_id: UUID,
        chosen_arm: str,
        reward: float,  # 0 or 1 (success/failure)
        estimated_rewards: Dict[str, float],
        context: Optional[Dict[str, Any]] = None
    ) -> RegretDataPoint:
        """
        Log a single regret observation to the database.
        
        Args:
            user_id: User identifier
            chosen_arm: Selected feature/arm
            reward: Observed reward (0 or 1)
            estimated_rewards: Estimated true rewards from historical data
            context: Additional context (specialty, time_of_day, etc.)
            
        Returns:
            RegretDataPoint with calculated regret
        """
        instantaneous_regret, optimal_arm = self.calculate_instantaneous_regret(
            chosen_arm, estimated_rewards
        )
        
        # Get previous cumulative regret
        prev_cumulative = self._get_latest_cumulative_regret(user_id)
        cumulative_regret = prev_cumulative + instantaneous_regret
        
        # Store in database
        try:
            self.db.execute(text("""
                INSERT INTO regret_observations (
                    user_id, chosen_arm, optimal_arm, chosen_reward, optimal_reward,
                    instantaneous_regret, cumulative_regret, context, created_at
                ) VALUES (
                    :user_id, :chosen_arm, :optimal_arm, :chosen_reward, :optimal_reward,
                    :instantaneous_regret, :cumulative_regret, :context, NOW()
                )
            """), {
                "user_id": str(user_id),
                "chosen_arm": chosen_arm,
                "optimal_arm": optimal_arm,
                "chosen_reward": reward,
                "optimal_reward": estimated_rewards.get(optimal_arm, 0.0),
                "instantaneous_regret": instantaneous_regret,
                "cumulative_regret": cumulative_regret,
                "context": str(context or {}),
            })
            self.db.commit()
        except Exception as e:
            logger.warning(f"Could not log regret observation: {e}")
            self.db.rollback()
        
        return RegretDataPoint(
            timestamp=datetime.utcnow(),
            chosen_arm=chosen_arm,
            optimal_arm=optimal_arm,
            chosen_reward=reward,
            optimal_reward=estimated_rewards.get(optimal_arm, 0.0),
            instantaneous_regret=instantaneous_regret,
            cumulative_regret=cumulative_regret,
            context=context or {},
        )
    
    def _get_latest_cumulative_regret(self, user_id: UUID) -> float:
        """Get the latest cumulative regret for a user."""
        try:
            result = self.db.execute(text("""
                SELECT cumulative_regret 
                FROM regret_observations 
                WHERE user_id = :user_id 
                ORDER BY created_at DESC 
                LIMIT 1
            """), {"user_id": str(user_id)}).fetchone()
            
            return result[0] if result else 0.0
        except Exception:
            return 0.0
    
    def analyze_regret(
        self,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> RegretAnalysisResult:
        """
        Comprehensive regret analysis for research purposes.
        
        Args:
            user_id: Optional user filter
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            RegretAnalysisResult with all metrics
        """
        # Build query
        query_params = {}
        where_clauses = []
        
        if user_id:
            where_clauses.append("user_id = :user_id")
            query_params["user_id"] = str(user_id)
        
        if start_date:
            where_clauses.append("created_at >= :start_date")
            query_params["start_date"] = start_date
            
        if end_date:
            where_clauses.append("created_at <= :end_date")
            query_params["end_date"] = end_date
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        try:
            # Get observations
            result = self.db.execute(text(f"""
                SELECT 
                    chosen_arm,
                    optimal_arm,
                    instantaneous_regret,
                    cumulative_regret,
                    created_at
                FROM regret_observations
                WHERE {where_clause}
                ORDER BY created_at ASC
            """), query_params).fetchall()
            
            if not result:
                return self._empty_analysis_result()
            
            # Calculate metrics
            total_rounds = len(result)
            cumulative_regret = result[-1][3] if result else 0.0
            average_regret = cumulative_regret / total_rounds if total_rounds > 0 else 0.0
            
            # Regret per arm
            regret_per_arm: Dict[str, float] = {}
            arm_counts: Dict[str, int] = {}
            optimal_selections = 0
            regret_curve = []
            
            for i, row in enumerate(result):
                arm = row[0]
                optimal = row[1]
                inst_regret = row[2]
                cum_regret = row[3]
                
                regret_per_arm[arm] = regret_per_arm.get(arm, 0.0) + inst_regret
                arm_counts[arm] = arm_counts.get(arm, 0) + 1
                
                if arm == optimal:
                    optimal_selections += 1
                
                # Sample regret curve (every 10 rounds to reduce data)
                if i % 10 == 0 or i == total_rounds - 1:
                    regret_curve.append((i + 1, cum_regret))
            
            # Get number of unique arms
            num_arms = len(arm_counts)
            theoretical_bound = self.get_bayesian_regret_bound(num_arms, total_rounds)
            
            # Detect convergence (regret growth rate decreasing)
            convergence_detected, convergence_round = self._detect_convergence(regret_curve)
            
            return RegretAnalysisResult(
                total_rounds=total_rounds,
                cumulative_regret=cumulative_regret,
                average_regret=average_regret,
                regret_per_arm=regret_per_arm,
                theoretical_bound=theoretical_bound,
                empirical_vs_theoretical_ratio=cumulative_regret / theoretical_bound if theoretical_bound > 0 else 0.0,
                convergence_detected=convergence_detected,
                convergence_round=convergence_round,
                regret_curve=regret_curve,
                arm_selection_frequency=arm_counts,
                optimal_arm_selection_rate=optimal_selections / total_rounds if total_rounds > 0 else 0.0,
            )
            
        except Exception as e:
            logger.error(f"Error analyzing regret: {e}")
            return self._empty_analysis_result()
    
    def _detect_convergence(
        self,
        regret_curve: List[Tuple[int, float]],
        window_size: int = 20,
        threshold: float = 0.1
    ) -> Tuple[bool, Optional[int]]:
        """
        Detect if the bandit has converged (regret growth rate stabilized).
        
        Convergence is detected when the regret growth rate (slope) decreases
        below a threshold for a sustained period.
        """
        if len(regret_curve) < window_size * 2:
            return False, None
        
        # Calculate slopes for sliding windows
        slopes = []
        for i in range(len(regret_curve) - window_size):
            start = regret_curve[i]
            end = regret_curve[i + window_size]
            
            rounds_diff = end[0] - start[0]
            regret_diff = end[1] - start[1]
            
            slope = regret_diff / rounds_diff if rounds_diff > 0 else 0
            slopes.append((start[0], slope))
        
        # Find first point where slope drops below threshold
        for round_num, slope in slopes:
            if slope < threshold:
                # Check if it stays low
                subsequent_slopes = [s for r, s in slopes if r >= round_num]
                if len(subsequent_slopes) >= 5 and sum(subsequent_slopes) / len(subsequent_slopes) < threshold:
                    return True, round_num
        
        return False, None
    
    def _empty_analysis_result(self) -> RegretAnalysisResult:
        """Return empty analysis result."""
        return RegretAnalysisResult(
            total_rounds=0,
            cumulative_regret=0.0,
            average_regret=0.0,
            regret_per_arm={},
            theoretical_bound=0.0,
            empirical_vs_theoretical_ratio=0.0,
            convergence_detected=False,
            convergence_round=None,
            regret_curve=[],
            arm_selection_frequency={},
            optimal_arm_selection_rate=0.0,
        )
    
    def estimate_true_rewards_from_history(
        self,
        user_id: UUID,
        lookback_days: int = 30
    ) -> Dict[str, float]:
        """
        Estimate true reward probabilities from historical data.
        
        This uses the observed acceptance rates as estimates of true rewards.
        """
        try:
            result = self.db.execute(text("""
                SELECT 
                    bs.feature_key,
                    bs.alpha / (bs.alpha + bs.beta) as estimated_reward
                FROM bandit_state bs
                WHERE bs.user_id = :user_id
                AND bs.updated_at >= :lookback_date
            """), {
                "user_id": str(user_id),
                "lookback_date": datetime.utcnow() - timedelta(days=lookback_days),
            }).fetchall()
            
            return {row[0]: row[1] for row in result}
        except Exception as e:
            logger.warning(f"Could not estimate rewards: {e}")
            return {}
    
    def generate_regret_report(
        self,
        user_id: Optional[UUID] = None,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive regret report for research papers.
        
        Returns:
            Dictionary with all metrics formatted for reporting
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=time_range_days)
        
        analysis = self.analyze_regret(user_id, start_date, end_date)
        
        return {
            "summary": {
                "total_rounds": analysis.total_rounds,
                "cumulative_regret": round(analysis.cumulative_regret, 4),
                "average_regret_per_round": round(analysis.average_regret, 4),
                "optimal_arm_selection_rate": f"{analysis.optimal_arm_selection_rate * 100:.1f}%",
            },
            "theoretical_analysis": {
                "theoretical_bound": round(analysis.theoretical_bound, 4),
                "empirical_vs_theoretical_ratio": round(analysis.empirical_vs_theoretical_ratio, 4),
                "bound_interpretation": self._interpret_bound_ratio(analysis.empirical_vs_theoretical_ratio),
            },
            "convergence_analysis": {
                "converged": analysis.convergence_detected,
                "convergence_round": analysis.convergence_round,
                "interpretation": "Bandit has converged to near-optimal policy" if analysis.convergence_detected else "Bandit still exploring",
            },
            "arm_performance": {
                "selection_frequency": analysis.arm_selection_frequency,
                "regret_per_arm": {k: round(v, 4) for k, v in analysis.regret_per_arm.items()},
            },
            "regret_curve": {
                "data_points": len(analysis.regret_curve),
                "curve": analysis.regret_curve,  # All points for full visualization
            },
            "metadata": {
                "analysis_period_days": time_range_days,
                "generated_at": datetime.utcnow().isoformat(),
                "user_scope": str(user_id) if user_id else "all_users",
            },
        }
    
    def _interpret_bound_ratio(self, ratio: float) -> str:
        """Interpret the empirical vs theoretical bound ratio."""
        if ratio <= 0.5:
            return "Excellent - significantly below theoretical bound"
        elif ratio <= 0.8:
            return "Good - well within theoretical bound"
        elif ratio <= 1.0:
            return "Expected - near theoretical bound"
        elif ratio <= 1.5:
            return "Elevated - slightly above bound (may indicate suboptimal exploration)"
        else:
            return "High - significantly above bound (requires investigation)"

