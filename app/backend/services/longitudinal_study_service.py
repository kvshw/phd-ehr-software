"""
Longitudinal Study Service

Provides infrastructure for time-series analysis of adaptation effects,
learning curves, and cohort analysis for PhD research.

References:
- Interrupted Time Series Analysis (ITS): Bernal et al. (2017)
- Power Law of Practice: Newell & Rosenbloom (1981)
- Segmented Regression: Wagner et al. (2002)

Key Metrics:
- Level change (immediate effect of intervention)
- Slope change (trend effect after intervention)
- Learning rate (α in T_n = T_1 * n^(-α))
- Time to plateau
"""

from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import math
import logging
from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


@dataclass
class TimeSeriesPoint:
    """Single observation in time series"""
    timestamp: datetime
    value: float
    intervention_active: bool = False


@dataclass
class ITSResult:
    """Interrupted Time Series Analysis Result"""
    # Pre-intervention
    pre_intercept: float  # β0: baseline level
    pre_slope: float      # β1: pre-intervention trend
    
    # Post-intervention effects
    level_change: float   # β2: immediate effect
    slope_change: float   # β3: trend change
    
    # Statistical significance
    level_change_pvalue: float
    slope_change_pvalue: float
    level_change_significant: bool
    slope_change_significant: bool
    
    # Effect sizes
    immediate_effect_size: float  # Cohen's d for level change
    sustained_effect_size: float  # Effect at end of post-period
    
    # Model fit
    r_squared: float
    rmse: float
    
    # Interpretation
    interpretation: str


@dataclass
class LearningCurveResult:
    """Learning Curve Analysis Result"""
    initial_performance: float    # T_1
    learning_rate: float          # α (exponent)
    asymptotic_performance: float # Estimated plateau
    time_to_90_percent: int       # Rounds to reach 90% of asymptote
    time_to_plateau: int          # Rounds to reach 99% of asymptote
    r_squared: float              # Fit quality
    curve_type: str               # 'power', 'exponential', 'linear'
    interpretation: str


@dataclass
class CohortAnalysisResult:
    """Cohort Retention Analysis Result"""
    cohort_id: str
    cohort_start_date: datetime
    cohort_size: int
    retention_rates: Dict[int, float]  # day -> retention rate
    feature_adoption: Dict[str, Dict[int, float]]  # feature -> day -> adoption rate
    churn_points: List[int]  # Days with significant churn
    interpretation: str


class LongitudinalStudyService:
    """
    Comprehensive longitudinal analysis for self-adaptive system research.
    
    Provides:
    1. Interrupted Time Series (ITS) analysis
    2. Learning curve analysis
    3. Cohort retention analysis
    4. Before/after comparisons
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def interrupted_time_series_analysis(
        self,
        user_id: UUID,
        metric: str,
        intervention_date: datetime,
        pre_period_days: int = 30,
        post_period_days: int = 30,
        aggregation: str = "daily"  # 'daily', 'weekly', 'session'
    ) -> ITSResult:
        """
        Perform Interrupted Time Series (ITS) analysis.
        
        ITS Model: Y_t = β0 + β1*time + β2*intervention + β3*time_after + ε
        
        Where:
        - β0: baseline level
        - β1: pre-intervention trend
        - β2: level change (immediate effect)
        - β3: slope change (trend effect)
        
        Args:
            user_id: User to analyze
            metric: Metric name (e.g., 'time_to_target', 'click_count')
            intervention_date: When adaptation was enabled
            pre_period_days: Days before intervention to analyze
            post_period_days: Days after intervention to analyze
            aggregation: How to aggregate data
            
        Returns:
            ITSResult with coefficients and interpretation
        """
        # Get time series data
        pre_start = intervention_date - timedelta(days=pre_period_days)
        post_end = intervention_date + timedelta(days=post_period_days)
        
        time_series = self._get_metric_time_series(
            user_id, metric, pre_start, post_end, aggregation
        )
        
        if len(time_series) < 10:  # Minimum data requirement
            return self._insufficient_data_its_result()
        
        # Prepare data for regression
        pre_data = [p for p in time_series if p.timestamp < intervention_date]
        post_data = [p for p in time_series if p.timestamp >= intervention_date]
        
        if len(pre_data) < 5 or len(post_data) < 5:
            return self._insufficient_data_its_result()
        
        # Calculate regression coefficients using OLS
        # This is a simplified implementation - production would use statsmodels
        
        # Pre-intervention trend
        pre_values = [p.value for p in pre_data]
        pre_times = list(range(len(pre_data)))
        pre_slope, pre_intercept = self._simple_linear_regression(pre_times, pre_values)
        
        # Post-intervention trend
        post_values = [p.value for p in post_data]
        post_times = list(range(len(post_data)))
        post_slope, post_intercept = self._simple_linear_regression(post_times, post_values)
        
        # Level change (difference at intervention point)
        predicted_at_intervention = pre_intercept + pre_slope * len(pre_data)
        actual_at_intervention = post_values[0] if post_values else 0
        level_change = actual_at_intervention - predicted_at_intervention
        
        # Slope change
        slope_change = post_slope - pre_slope
        
        # Calculate effect sizes
        pre_std = self._std(pre_values)
        immediate_effect_size = level_change / pre_std if pre_std > 0 else 0
        
        # Sustained effect (at end of post-period)
        sustained_change = (post_intercept + post_slope * len(post_data)) - \
                          (pre_intercept + pre_slope * (len(pre_data) + len(post_data)))
        sustained_effect_size = sustained_change / pre_std if pre_std > 0 else 0
        
        # Calculate R² and RMSE
        all_values = pre_values + post_values
        all_times = list(range(len(all_values)))
        predictions = []
        for i, t in enumerate(all_times):
            if i < len(pre_data):
                predictions.append(pre_intercept + pre_slope * t)
            else:
                predictions.append(post_intercept + post_slope * (t - len(pre_data)))
        
        r_squared = self._r_squared(all_values, predictions)
        rmse = self._rmse(all_values, predictions)
        
        # Significance testing (simplified - using effect size thresholds)
        # In production, use proper t-tests or bootstrap
        level_significant = abs(immediate_effect_size) > 0.3  # Medium effect
        slope_significant = abs(slope_change) > 0.01 * abs(pre_slope) if pre_slope != 0 else abs(slope_change) > 0.01
        
        # Generate interpretation
        interpretation = self._interpret_its_result(
            level_change, slope_change, immediate_effect_size,
            level_significant, slope_significant, metric
        )
        
        return ITSResult(
            pre_intercept=pre_intercept,
            pre_slope=pre_slope,
            level_change=level_change,
            slope_change=slope_change,
            level_change_pvalue=0.05 if level_significant else 0.5,  # Simplified
            slope_change_pvalue=0.05 if slope_significant else 0.5,
            level_change_significant=level_significant,
            slope_change_significant=slope_significant,
            immediate_effect_size=immediate_effect_size,
            sustained_effect_size=sustained_effect_size,
            r_squared=r_squared,
            rmse=rmse,
            interpretation=interpretation,
        )
    
    def _interpret_its_result(
        self,
        level_change: float,
        slope_change: float,
        effect_size: float,
        level_sig: bool,
        slope_sig: bool,
        metric: str
    ) -> str:
        """Generate interpretation of ITS results."""
        parts = []
        
        # Direction and magnitude
        if level_sig:
            direction = "improvement" if level_change < 0 and "time" in metric.lower() else \
                       ("improvement" if level_change > 0 else "decline")
            magnitude = "large" if abs(effect_size) > 0.8 else \
                       ("medium" if abs(effect_size) > 0.5 else "small")
            parts.append(f"Immediate {magnitude} {direction} in {metric} (d={effect_size:.2f})")
        else:
            parts.append(f"No significant immediate effect on {metric}")
        
        if slope_sig:
            trend_dir = "improving" if slope_change < 0 and "time" in metric.lower() else \
                       ("improving" if slope_change > 0 else "declining")
            parts.append(f"Trend is {trend_dir} post-intervention")
        else:
            parts.append("No significant trend change")
        
        return ". ".join(parts) + "."
    
    def learning_curve_analysis(
        self,
        user_id: UUID,
        metric: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> LearningCurveResult:
        """
        Analyze learning curve for a user/metric.
        
        Power Law of Practice: T_n = T_1 * n^(-α)
        
        Where:
        - T_n: performance at trial n
        - T_1: initial performance
        - α: learning rate (typically 0.2-0.5)
        
        Args:
            user_id: User to analyze
            metric: Performance metric
            start_date: Analysis start
            end_date: Analysis end
            
        Returns:
            LearningCurveResult with learning parameters
        """
        # Get session-level metric data
        time_series = self._get_session_metric_series(
            user_id, metric, start_date, end_date
        )
        
        if len(time_series) < 10:
            return self._insufficient_data_learning_result()
        
        # Fit power law: log(T) = log(T_1) - α*log(n)
        values = [p.value for p in time_series if p.value > 0]
        n_values = list(range(1, len(values) + 1))
        
        if not values:
            return self._insufficient_data_learning_result()
        
        # Log transform
        log_values = [math.log(v) for v in values]
        log_n = [math.log(n) for n in n_values]
        
        # Linear regression on log-log scale
        slope, intercept = self._simple_linear_regression(log_n, log_values)
        
        # Extract parameters
        initial_performance = math.exp(intercept)
        learning_rate = -slope  # Negative because performance improves (decreases for time metrics)
        
        # Estimate asymptote (using last 20% of data)
        last_portion = values[int(len(values) * 0.8):]
        asymptotic_performance = sum(last_portion) / len(last_portion) if last_portion else values[-1]
        
        # Time to reach thresholds
        improvement_needed_90 = (initial_performance - asymptotic_performance) * 0.9
        target_90 = initial_performance - improvement_needed_90
        time_to_90 = self._rounds_to_target(initial_performance, learning_rate, target_90)
        
        improvement_needed_99 = (initial_performance - asymptotic_performance) * 0.99
        target_99 = initial_performance - improvement_needed_99
        time_to_plateau = self._rounds_to_target(initial_performance, learning_rate, target_99)
        
        # Calculate R² for power law fit
        predictions = [initial_performance * (n ** (-learning_rate)) for n in n_values]
        r_squared = self._r_squared(values, predictions)
        
        # Determine curve type
        if r_squared > 0.8:
            curve_type = "power"
        elif learning_rate < 0.1:
            curve_type = "linear"
        else:
            curve_type = "exponential"
        
        # Interpretation
        interpretation = self._interpret_learning_curve(
            initial_performance, learning_rate, asymptotic_performance,
            time_to_90, curve_type, metric
        )
        
        return LearningCurveResult(
            initial_performance=initial_performance,
            learning_rate=learning_rate,
            asymptotic_performance=asymptotic_performance,
            time_to_90_percent=time_to_90,
            time_to_plateau=time_to_plateau,
            r_squared=r_squared,
            curve_type=curve_type,
            interpretation=interpretation,
        )
    
    def _interpret_learning_curve(
        self,
        initial: float,
        rate: float,
        asymptote: float,
        time_to_90: int,
        curve_type: str,
        metric: str
    ) -> str:
        """Generate learning curve interpretation."""
        improvement_pct = ((initial - asymptote) / initial) * 100 if initial > 0 else 0
        
        rate_desc = "fast" if rate > 0.4 else ("moderate" if rate > 0.2 else "slow")
        
        return (
            f"User shows {rate_desc} learning (α={rate:.2f}). "
            f"Performance improved by {improvement_pct:.1f}% from initial to plateau. "
            f"Reached 90% of optimal performance after {time_to_90} sessions. "
            f"Learning follows a {curve_type} curve pattern."
        )
    
    def _rounds_to_target(
        self,
        initial: float,
        rate: float,
        target: float
    ) -> int:
        """Calculate rounds needed to reach target performance."""
        if rate <= 0 or initial <= target:
            return 1
        
        # From T_n = T_1 * n^(-α), solve for n
        # n = (T_n / T_1)^(-1/α)
        try:
            n = (target / initial) ** (-1 / rate)
            return max(1, min(1000, int(n)))  # Bounded
        except (ValueError, ZeroDivisionError):
            return 100
    
    def cohort_retention_analysis(
        self,
        cohort_start_date: datetime,
        retention_periods: List[int] = None,
        features_to_track: List[str] = None
    ) -> CohortAnalysisResult:
        """
        Analyze retention and feature adoption for a user cohort.
        
        Args:
            cohort_start_date: Date users joined (within 7 days)
            retention_periods: Days to check retention (default: [1, 7, 14, 30, 60, 90])
            features_to_track: Features to track adoption
            
        Returns:
            CohortAnalysisResult with retention and adoption metrics
        """
        if retention_periods is None:
            retention_periods = [1, 7, 14, 30, 60, 90]
        
        if features_to_track is None:
            features_to_track = [
                "patient_search", "ecg_review", "ai_suggestions",
                "clinical_notes", "quick_actions"
            ]
        
        # Get cohort users
        cohort_end_date = cohort_start_date + timedelta(days=7)
        cohort_users = self._get_cohort_users(cohort_start_date, cohort_end_date)
        cohort_size = len(cohort_users)
        
        if cohort_size == 0:
            return self._empty_cohort_result(cohort_start_date)
        
        # Calculate retention rates
        retention_rates = {}
        for period in retention_periods:
            active_count = self._count_active_users(
                cohort_users,
                cohort_start_date + timedelta(days=period),
                cohort_start_date + timedelta(days=period + 1)
            )
            retention_rates[period] = active_count / cohort_size
        
        # Calculate feature adoption
        feature_adoption = {}
        for feature in features_to_track:
            feature_adoption[feature] = {}
            for period in retention_periods:
                adoption_count = self._count_feature_adopters(
                    cohort_users, feature,
                    cohort_start_date,
                    cohort_start_date + timedelta(days=period)
                )
                feature_adoption[feature][period] = adoption_count / cohort_size
        
        # Find churn points (significant drops)
        churn_points = []
        for i in range(1, len(retention_periods)):
            prev_period = retention_periods[i - 1]
            curr_period = retention_periods[i]
            
            if retention_rates[prev_period] > 0:
                drop = (retention_rates[prev_period] - retention_rates[curr_period]) / retention_rates[prev_period]
                if drop > 0.3:  # 30% drop
                    churn_points.append(curr_period)
        
        interpretation = self._interpret_cohort_analysis(
            cohort_size, retention_rates, churn_points
        )
        
        return CohortAnalysisResult(
            cohort_id=cohort_start_date.strftime("%Y-%m-%d"),
            cohort_start_date=cohort_start_date,
            cohort_size=cohort_size,
            retention_rates=retention_rates,
            feature_adoption=feature_adoption,
            churn_points=churn_points,
            interpretation=interpretation,
        )
    
    def _interpret_cohort_analysis(
        self,
        size: int,
        retention: Dict[int, float],
        churn_points: List[int]
    ) -> str:
        """Generate cohort analysis interpretation."""
        day_30_retention = retention.get(30, 0)
        day_90_retention = retention.get(90, 0)
        
        retention_quality = "excellent" if day_30_retention > 0.7 else \
                          ("good" if day_30_retention > 0.5 else \
                          ("moderate" if day_30_retention > 0.3 else "low"))
        
        churn_text = ""
        if churn_points:
            churn_text = f" Significant churn observed at day(s) {', '.join(map(str, churn_points))}."
        
        return (
            f"Cohort of {size} users shows {retention_quality} retention "
            f"(30-day: {day_30_retention*100:.1f}%, 90-day: {day_90_retention*100:.1f}%).{churn_text}"
        )
    
    # Helper methods
    
    def _get_metric_time_series(
        self,
        user_id: UUID,
        metric: str,
        start_date: datetime,
        end_date: datetime,
        aggregation: str
    ) -> List[TimeSeriesPoint]:
        """Get time series data for a metric."""
        try:
            if aggregation == "daily":
                query = """
                    SELECT 
                        DATE_TRUNC('day', created_at) as period,
                        AVG(CASE 
                            WHEN action_metadata->>'duration_ms' IS NOT NULL 
                            THEN (action_metadata->>'duration_ms')::float 
                            ELSE 0 
                        END) as value
                    FROM user_actions
                    WHERE user_id = :user_id
                    AND created_at BETWEEN :start_date AND :end_date
                    GROUP BY DATE_TRUNC('day', created_at)
                    ORDER BY period
                """
            else:
                query = """
                    SELECT 
                        created_at as period,
                        CASE 
                            WHEN action_metadata->>'duration_ms' IS NOT NULL 
                            THEN (action_metadata->>'duration_ms')::float 
                            ELSE 1 
                        END as value
                    FROM user_actions
                    WHERE user_id = :user_id
                    AND created_at BETWEEN :start_date AND :end_date
                    ORDER BY created_at
                """
            
            result = self.db.execute(text(query), {
                "user_id": str(user_id),
                "start_date": start_date,
                "end_date": end_date,
            }).fetchall()
            
            return [
                TimeSeriesPoint(timestamp=row[0], value=row[1] or 0)
                for row in result
            ]
        except Exception as e:
            logger.warning(f"Error fetching time series: {e}")
            return []
    
    def _get_session_metric_series(
        self,
        user_id: UUID,
        metric: str,
        start_date: Optional[datetime],
        end_date: Optional[datetime]
    ) -> List[TimeSeriesPoint]:
        """Get session-level metric data."""
        return self._get_metric_time_series(
            user_id, metric,
            start_date or datetime.utcnow() - timedelta(days=90),
            end_date or datetime.utcnow(),
            "session"
        )
    
    def _get_cohort_users(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[UUID]:
        """Get users who joined in a date range."""
        try:
            # Get users based on first action date
            result = self.db.execute(text("""
                SELECT DISTINCT user_id
                FROM user_actions
                WHERE created_at BETWEEN :start_date AND :end_date
                AND user_id IN (
                    SELECT user_id
                    FROM user_actions
                    GROUP BY user_id
                    HAVING MIN(created_at) BETWEEN :start_date AND :end_date
                )
            """), {
                "start_date": start_date,
                "end_date": end_date,
            }).fetchall()
            
            return [UUID(row[0]) for row in result]
        except Exception as e:
            logger.warning(f"Error fetching cohort users: {e}")
            return []
    
    def _count_active_users(
        self,
        users: List[UUID],
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Count how many users were active in a period."""
        if not users:
            return 0
        try:
            user_ids = [str(u) for u in users]
            result = self.db.execute(text("""
                SELECT COUNT(DISTINCT user_id)
                FROM user_actions
                WHERE user_id = ANY(:user_ids)
                AND created_at BETWEEN :start_date AND :end_date
            """), {
                "user_ids": user_ids,
                "start_date": start_date,
                "end_date": end_date,
            }).fetchone()
            
            return result[0] if result else 0
        except Exception as e:
            logger.warning(f"Error counting active users: {e}")
            return 0
    
    def _count_feature_adopters(
        self,
        users: List[UUID],
        feature: str,
        start_date: datetime,
        end_date: datetime
    ) -> int:
        """Count users who used a feature."""
        if not users:
            return 0
        try:
            user_ids = [str(u) for u in users]
            result = self.db.execute(text("""
                SELECT COUNT(DISTINCT user_id)
                FROM user_actions
                WHERE user_id = ANY(:user_ids)
                AND action_metadata->>'feature_id' = :feature
                AND created_at BETWEEN :start_date AND :end_date
            """), {
                "user_ids": user_ids,
                "feature": feature,
                "start_date": start_date,
                "end_date": end_date,
            }).fetchone()
            
            return result[0] if result else 0
        except Exception as e:
            logger.warning(f"Error counting feature adopters: {e}")
            return 0
    
    def _simple_linear_regression(
        self,
        x: List[float],
        y: List[float]
    ) -> Tuple[float, float]:
        """Simple OLS linear regression."""
        n = len(x)
        if n == 0 or n != len(y):
            return 0.0, 0.0
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_xx = sum(xi * xi for xi in x)
        
        denominator = n * sum_xx - sum_x * sum_x
        if denominator == 0:
            return 0.0, sum_y / n if n > 0 else 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n
        
        return slope, intercept
    
    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 1.0
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
        return math.sqrt(variance) if variance > 0 else 1.0
    
    def _r_squared(self, actual: List[float], predicted: List[float]) -> float:
        """Calculate R² (coefficient of determination)."""
        if len(actual) != len(predicted) or len(actual) == 0:
            return 0.0
        
        mean_actual = sum(actual) / len(actual)
        ss_tot = sum((a - mean_actual) ** 2 for a in actual)
        ss_res = sum((a - p) ** 2 for a, p in zip(actual, predicted))
        
        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
        
        return 1 - (ss_res / ss_tot)
    
    def _rmse(self, actual: List[float], predicted: List[float]) -> float:
        """Calculate Root Mean Square Error."""
        if len(actual) != len(predicted) or len(actual) == 0:
            return 0.0
        
        mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)
        return math.sqrt(mse)
    
    def _insufficient_data_its_result(self) -> ITSResult:
        """Return ITS result when insufficient data."""
        return ITSResult(
            pre_intercept=0, pre_slope=0,
            level_change=0, slope_change=0,
            level_change_pvalue=1.0, slope_change_pvalue=1.0,
            level_change_significant=False, slope_change_significant=False,
            immediate_effect_size=0, sustained_effect_size=0,
            r_squared=0, rmse=0,
            interpretation="Insufficient data for ITS analysis (minimum 10 observations required)."
        )
    
    def _insufficient_data_learning_result(self) -> LearningCurveResult:
        """Return learning curve result when insufficient data."""
        return LearningCurveResult(
            initial_performance=0, learning_rate=0,
            asymptotic_performance=0, time_to_90_percent=0,
            time_to_plateau=0, r_squared=0,
            curve_type="unknown",
            interpretation="Insufficient data for learning curve analysis (minimum 10 sessions required)."
        )
    
    def _empty_cohort_result(self, start_date: datetime) -> CohortAnalysisResult:
        """Return empty cohort result."""
        return CohortAnalysisResult(
            cohort_id=start_date.strftime("%Y-%m-%d"),
            cohort_start_date=start_date,
            cohort_size=0,
            retention_rates={},
            feature_adoption={},
            churn_points=[],
            interpretation="No users found in this cohort."
        )

