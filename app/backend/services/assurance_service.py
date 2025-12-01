"""
Runtime Assurance Service
Phase 4: Ethics, Safety, and Transparency

Provides:
- Shadow testing (test new policies before applying)
- Gradual rollouts (A/B testing)
- Rollback on regression (automatic if metrics degrade)
- Bias and drift detection
"""

from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import logging
import math

logger = logging.getLogger(__name__)


# Simple statistical helpers to avoid numpy/scipy dependency
def _mean(values: List[float]) -> float:
    """Calculate mean without numpy."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def _std(values: List[float]) -> float:
    """Calculate standard deviation without numpy."""
    if len(values) < 2:
        return 0.0
    avg = _mean(values)
    variance = sum((x - avg) ** 2 for x in values) / len(values)
    return math.sqrt(variance)


class AssuranceService:
    """
    Runtime assurance layer for MAPE-K adaptations.
    Ensures ethical, safe, and transparent adaptation decisions.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================
    # Shadow Testing
    # ==========================================
    
    def create_shadow_test(
        self,
        name: str,
        policy_type: str,
        control_policy: Dict,
        test_policy: Dict,
        duration_days: int = 7,
        test_group_percentage: float = 0.0,  # 0 = pure shadow mode
        success_metrics: Optional[List[str]] = None,
        success_threshold: float = 0.05,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new shadow test or A/B test for a policy.
        
        Shadow mode (test_group_percentage=0): 
            New policy runs in parallel but doesn't affect users.
            
        A/B mode (test_group_percentage>0):
            Some users get the new policy, others get control.
        """
        is_shadow = test_group_percentage == 0
        
        if success_metrics is None:
            success_metrics = ["time_to_target", "click_count", "task_completion_rate"]
        
        query = text("""
            INSERT INTO shadow_tests (
                name, description, policy_type, control_policy, test_policy,
                test_group_percentage, is_shadow_mode, duration_days,
                success_metrics, success_threshold, scheduled_end_at, status
            ) VALUES (
                :name, :description, :policy_type, :control_policy::jsonb, :test_policy::jsonb,
                :test_group_percentage, :is_shadow_mode, :duration_days,
                :success_metrics::jsonb, :success_threshold, 
                NOW() + INTERVAL '1 day' * :duration_days, 'running'
            )
            RETURNING id, started_at, scheduled_end_at
        """)
        
        result = self.db.execute(query, {
            "name": name,
            "description": description,
            "policy_type": policy_type,
            "control_policy": json.dumps(control_policy),
            "test_policy": json.dumps(test_policy),
            "test_group_percentage": test_group_percentage,
            "is_shadow_mode": is_shadow,
            "duration_days": duration_days,
            "success_metrics": json.dumps(success_metrics),
            "success_threshold": success_threshold
        })
        
        row = result.fetchone()
        self.db.commit()
        
        logger.info(f"Created {'shadow' if is_shadow else 'A/B'} test: {name}")
        
        return {
            "test_id": str(row.id),
            "name": name,
            "mode": "shadow" if is_shadow else "a/b",
            "started_at": row.started_at.isoformat(),
            "scheduled_end_at": row.scheduled_end_at.isoformat(),
            "status": "running"
        }
    
    def evaluate_shadow_test(
        self,
        test_id: UUID,
        control_metrics: Dict[str, float],
        test_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Evaluate results of a shadow test and generate recommendation.
        
        Returns recommendation: 'approve', 'reject', 'extend', 'modify'
        """
        # Calculate improvement for each metric
        improvements = {}
        for metric in control_metrics:
            if metric in test_metrics and control_metrics[metric] > 0:
                improvement = (test_metrics[metric] - control_metrics[metric]) / control_metrics[metric]
                improvements[metric] = improvement
        
        # Get test configuration
        query = text("""
            SELECT success_threshold, success_metrics, duration_days, started_at
            FROM shadow_tests WHERE id = :test_id
        """)
        result = self.db.execute(query, {"test_id": str(test_id)})
        test_config = result.fetchone()
        
        if not test_config:
            raise ValueError(f"Shadow test {test_id} not found")
        
        threshold = test_config.success_threshold
        success_metrics = test_config.success_metrics or list(improvements.keys())
        
        # Calculate overall improvement
        relevant_improvements = [improvements.get(m, 0) for m in success_metrics if m in improvements]
        avg_improvement = _mean(relevant_improvements) if relevant_improvements else 0
        
        # Statistical significance (simplified - in production use proper A/B test stats)
        # Here we use a simple threshold-based approach
        significant = abs(avg_improvement) > threshold
        
        # Generate recommendation
        if avg_improvement >= threshold and significant:
            recommendation = "approve"
            reason = f"Test policy shows {avg_improvement:.1%} average improvement across metrics, exceeding {threshold:.1%} threshold."
        elif avg_improvement <= -threshold and significant:
            recommendation = "reject"
            reason = f"Test policy shows {avg_improvement:.1%} average degradation, below -{threshold:.1%} threshold."
        elif not significant:
            recommendation = "extend"
            reason = f"Results not statistically significant. Average improvement: {avg_improvement:.1%}. Consider extending test duration."
        else:
            recommendation = "modify"
            reason = f"Mixed results: {avg_improvement:.1%} average improvement. Some metrics improved, others degraded."
        
        # Update test record
        update_query = text("""
            UPDATE shadow_tests SET
                control_metrics = :control_metrics::jsonb,
                test_metrics = :test_metrics::jsonb,
                recommendation = :recommendation,
                recommendation_reason = :reason,
                completed_at = NOW(),
                status = 'completed'
            WHERE id = :test_id
        """)
        
        self.db.execute(update_query, {
            "test_id": str(test_id),
            "control_metrics": json.dumps(control_metrics),
            "test_metrics": json.dumps(test_metrics),
            "recommendation": recommendation,
            "reason": reason
        })
        self.db.commit()
        
        logger.info(f"Shadow test {test_id} evaluated: {recommendation}")
        
        return {
            "test_id": str(test_id),
            "recommendation": recommendation,
            "reason": reason,
            "improvements": improvements,
            "average_improvement": avg_improvement,
            "threshold": threshold,
            "significant": significant
        }
    
    # ==========================================
    # Gradual Rollout
    # ==========================================
    
    def start_gradual_rollout(
        self,
        test_id: UUID,
        stages: List[float] = [0.1, 0.25, 0.5, 0.75, 1.0],
        regression_threshold: float = -0.05
    ) -> Dict[str, Any]:
        """
        Start gradual rollout of an approved policy.
        
        Stages define the percentage of users at each stage.
        Automatically pauses if regression is detected.
        """
        # Verify test was approved
        query = text("""
            SELECT recommendation, test_policy, policy_type 
            FROM shadow_tests WHERE id = :test_id
        """)
        result = self.db.execute(query, {"test_id": str(test_id)})
        test = result.fetchone()
        
        if not test:
            raise ValueError(f"Shadow test {test_id} not found")
        
        if test.recommendation != "approve":
            raise ValueError(f"Cannot rollout: test recommendation is '{test.recommendation}', not 'approve'")
        
        # Create first rollout stage
        first_stage = stages[0]
        stage_query = text("""
            INSERT INTO rollout_stages (
                shadow_test_id, stage_number, rollout_percentage
            ) VALUES (:test_id, 1, :percentage)
            RETURNING id
        """)
        
        result = self.db.execute(stage_query, {
            "test_id": str(test_id),
            "percentage": first_stage
        })
        stage_id = result.fetchone().id
        self.db.commit()
        
        logger.info(f"Started gradual rollout for test {test_id} at {first_stage:.0%}")
        
        return {
            "test_id": str(test_id),
            "current_stage": 1,
            "total_stages": len(stages),
            "current_percentage": first_stage,
            "stages": stages,
            "stage_id": str(stage_id),
            "status": "rolling_out"
        }
    
    def advance_rollout(
        self,
        test_id: UUID,
        current_metrics: Dict[str, float],
        baseline_metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Check if rollout can advance to next stage.
        Rolls back if regression detected.
        """
        # Get current stage
        query = text("""
            SELECT rs.*, st.test_policy, st.policy_type
            FROM rollout_stages rs
            JOIN shadow_tests st ON rs.shadow_test_id = st.id
            WHERE rs.shadow_test_id = :test_id
            ORDER BY rs.stage_number DESC
            LIMIT 1
        """)
        result = self.db.execute(query, {"test_id": str(test_id)})
        current_stage = result.fetchone()
        
        if not current_stage:
            raise ValueError(f"No rollout found for test {test_id}")
        
        # Check for regression
        regression = self.check_regression(baseline_metrics, current_metrics)
        
        if regression["is_regression"]:
            # Rollback!
            logger.warning(f"Regression detected in rollout {test_id}: {regression['reason']}")
            return self._rollback_rollout(test_id, current_stage, regression["reason"])
        
        # Advance to next stage
        stages = [0.1, 0.25, 0.5, 0.75, 1.0]  # Default stages
        next_stage_num = current_stage.stage_number + 1
        
        if next_stage_num > len(stages):
            # Rollout complete
            self._complete_rollout(test_id, current_stage)
            return {
                "test_id": str(test_id),
                "status": "completed",
                "message": "Rollout completed successfully at 100%"
            }
        
        # Create next stage
        next_percentage = stages[next_stage_num - 1]
        stage_query = text("""
            INSERT INTO rollout_stages (
                shadow_test_id, stage_number, rollout_percentage, metrics_snapshot
            ) VALUES (:test_id, :stage_num, :percentage, :metrics::jsonb)
            RETURNING id
        """)
        
        self.db.execute(stage_query, {
            "test_id": str(test_id),
            "stage_num": next_stage_num,
            "percentage": next_percentage,
            "metrics": json.dumps(current_metrics)
        })
        
        # Mark previous stage complete
        self.db.execute(text("""
            UPDATE rollout_stages SET 
                completed_at = NOW(), 
                proceed_to_next = TRUE,
                metrics_snapshot = :metrics::jsonb
            WHERE id = :stage_id
        """), {
            "stage_id": str(current_stage.id),
            "metrics": json.dumps(current_metrics)
        })
        
        self.db.commit()
        
        logger.info(f"Rollout {test_id} advanced to stage {next_stage_num} ({next_percentage:.0%})")
        
        return {
            "test_id": str(test_id),
            "status": "advancing",
            "previous_stage": current_stage.stage_number,
            "current_stage": next_stage_num,
            "current_percentage": next_percentage,
            "metrics": current_metrics
        }
    
    def _rollback_rollout(
        self,
        test_id: UUID,
        current_stage,
        reason: str
    ) -> Dict[str, Any]:
        """Rollback a failed rollout."""
        # Mark stage as regression
        self.db.execute(text("""
            UPDATE rollout_stages SET 
                regression_detected = TRUE,
                completed_at = NOW(),
                proceed_to_next = FALSE,
                notes = :reason
            WHERE id = :stage_id
        """), {
            "stage_id": str(current_stage.id),
            "reason": reason
        })
        
        # Update test status
        self.db.execute(text("""
            UPDATE shadow_tests SET 
                status = 'rolled_back',
                recommendation = 'reject',
                recommendation_reason = :reason
            WHERE id = :test_id
        """), {
            "test_id": str(test_id),
            "reason": f"Rollback due to regression: {reason}"
        })
        
        self.db.commit()
        
        return {
            "test_id": str(test_id),
            "status": "rolled_back",
            "reason": reason,
            "stage_at_rollback": current_stage.stage_number
        }
    
    def _complete_rollout(self, test_id: UUID, current_stage):
        """Mark rollout as complete."""
        self.db.execute(text("""
            UPDATE rollout_stages SET 
                completed_at = NOW(),
                proceed_to_next = FALSE,
                notes = 'Rollout completed successfully'
            WHERE id = :stage_id
        """), {"stage_id": str(current_stage.id)})
        
        self.db.execute(text("""
            UPDATE shadow_tests SET status = 'deployed' WHERE id = :test_id
        """), {"test_id": str(test_id)})
        
        self.db.commit()
    
    # ==========================================
    # Regression Detection
    # ==========================================
    
    def check_regression(
        self,
        baseline_metrics: Dict[str, float],
        current_metrics: Dict[str, float],
        threshold: float = -0.05
    ) -> Dict[str, Any]:
        """
        Check if current metrics show regression from baseline.
        
        Returns:
            is_regression: bool
            reason: str
            degraded_metrics: List of metrics that degraded
        """
        degraded = []
        
        for metric, baseline_value in baseline_metrics.items():
            if metric in current_metrics and baseline_value > 0:
                change = (current_metrics[metric] - baseline_value) / baseline_value
                if change < threshold:
                    degraded.append({
                        "metric": metric,
                        "baseline": baseline_value,
                        "current": current_metrics[metric],
                        "change": change
                    })
        
        is_regression = len(degraded) > 0
        
        if is_regression:
            reason = f"Regression detected in {len(degraded)} metric(s): " + \
                     ", ".join([f"{d['metric']} ({d['change']:.1%})" for d in degraded])
        else:
            reason = "No regression detected"
        
        return {
            "is_regression": is_regression,
            "reason": reason,
            "degraded_metrics": degraded,
            "threshold": threshold
        }
    
    # ==========================================
    # Bias Detection
    # ==========================================
    
    def detect_bias(
        self,
        group_type: str = "specialty",
        period_days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Detect potential bias in adaptation effectiveness across user groups.
        
        Checks if certain groups (specialties, roles, etc.) benefit more
        or less from adaptations than others.
        """
        # Get adaptation improvements by group
        query = text("""
            WITH group_metrics AS (
                SELECT 
                    COALESCE(u.specialty, 'unknown') as group_value,
                    COUNT(*) as adaptation_count,
                    AVG(
                        CASE 
                            WHEN al.metrics_after IS NOT NULL AND al.metrics_before IS NOT NULL
                            THEN (al.metrics_after->>'efficiency')::float - (al.metrics_before->>'efficiency')::float
                            ELSE NULL
                        END
                    ) as avg_improvement
                FROM adaptation_logs al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE al.created_at > NOW() - INTERVAL '1 day' * :period_days
                GROUP BY COALESCE(u.specialty, 'unknown')
            ),
            overall AS (
                SELECT AVG(avg_improvement) as overall_avg
                FROM group_metrics
                WHERE avg_improvement IS NOT NULL
            )
            SELECT 
                gm.group_value,
                gm.adaptation_count,
                gm.avg_improvement,
                o.overall_avg,
                ABS(gm.avg_improvement - o.overall_avg) as deviation
            FROM group_metrics gm, overall o
            WHERE gm.avg_improvement IS NOT NULL
            ORDER BY deviation DESC
        """)
        
        try:
            result = self.db.execute(query, {"period_days": period_days})
            rows = result.fetchall()
        except Exception as e:
            logger.warning(f"Bias detection query failed: {e}")
            return []
        
        bias_findings = []
        for row in rows:
            is_bias = row.deviation > 0.1  # More than 10% deviation from average
            
            bias_findings.append({
                "group_type": group_type,
                "group_value": row.group_value,
                "adaptation_count": row.adaptation_count,
                "avg_improvement": row.avg_improvement,
                "overall_avg": row.overall_avg,
                "deviation": row.deviation,
                "is_potential_bias": is_bias,
                "direction": "advantaged" if row.avg_improvement > row.overall_avg else "disadvantaged"
            })
            
            # Store in bias_metrics table
            if is_bias:
                self._store_bias_metric(group_type, row, period_days)
        
        return bias_findings
    
    def _store_bias_metric(self, group_type: str, row, period_days: int):
        """Store bias metric finding."""
        try:
            self.db.execute(text("""
                INSERT INTO bias_metrics (
                    group_type, group_value, adaptation_count,
                    avg_improvement, overall_avg_improvement, deviation_from_overall,
                    is_potential_bias, period_start, period_end
                ) VALUES (
                    :group_type, :group_value, :count,
                    :avg, :overall, :deviation,
                    TRUE, NOW() - INTERVAL '1 day' * :period_days, NOW()
                )
            """), {
                "group_type": group_type,
                "group_value": row.group_value,
                "count": row.adaptation_count,
                "avg": row.avg_improvement,
                "overall": row.overall_avg,
                "deviation": row.deviation,
                "period_days": period_days
            })
            self.db.commit()
        except Exception as e:
            logger.warning(f"Failed to store bias metric: {e}")
    
    # ==========================================
    # Drift Detection
    # ==========================================
    
    def detect_drift(
        self,
        metric_name: str,
        baseline_period_days: int = 30,
        current_period_days: int = 7,
        drift_threshold: float = 2.0  # Standard deviations
    ) -> Dict[str, Any]:
        """
        Detect drift in a metric from its baseline.
        
        Uses statistical distance (z-score) to detect significant changes.
        """
        # Get baseline statistics
        baseline_query = text("""
            SELECT 
                AVG((metrics_after->>:metric)::float) as mean,
                STDDEV((metrics_after->>:metric)::float) as std,
                COUNT(*) as count
            FROM adaptation_logs
            WHERE metrics_after IS NOT NULL
            AND created_at BETWEEN 
                NOW() - INTERVAL '1 day' * :baseline_end 
                AND NOW() - INTERVAL '1 day' * :current_days
        """)
        
        current_query = text("""
            SELECT 
                AVG((metrics_after->>:metric)::float) as mean,
                STDDEV((metrics_after->>:metric)::float) as std,
                COUNT(*) as count
            FROM adaptation_logs
            WHERE metrics_after IS NOT NULL
            AND created_at > NOW() - INTERVAL '1 day' * :current_days
        """)
        
        try:
            baseline_result = self.db.execute(baseline_query, {
                "metric": metric_name,
                "baseline_end": baseline_period_days,
                "current_days": current_period_days
            }).fetchone()
            
            current_result = self.db.execute(current_query, {
                "metric": metric_name,
                "current_days": current_period_days
            }).fetchone()
        except Exception as e:
            logger.warning(f"Drift detection query failed: {e}")
            return {"drift_detected": False, "error": str(e)}
        
        if not baseline_result.mean or not current_result.mean:
            return {
                "metric": metric_name,
                "drift_detected": False,
                "reason": "Insufficient data for drift detection"
            }
        
        # Calculate drift score (z-score)
        baseline_std = baseline_result.std or 1.0
        drift_score = abs(current_result.mean - baseline_result.mean) / baseline_std
        drift_detected = drift_score > drift_threshold
        
        # Determine direction
        if current_result.mean > baseline_result.mean:
            direction = "improving"
        elif current_result.mean < baseline_result.mean:
            direction = "degrading"
        else:
            direction = "stable"
        
        result = {
            "metric": metric_name,
            "drift_detected": drift_detected,
            "drift_score": drift_score,
            "drift_threshold": drift_threshold,
            "direction": direction,
            "baseline": {
                "mean": baseline_result.mean,
                "std": baseline_std,
                "count": baseline_result.count
            },
            "current": {
                "mean": current_result.mean,
                "std": current_result.std or 0,
                "count": current_result.count
            }
        }
        
        # Store if drift detected
        if drift_detected:
            self._store_drift_metric(metric_name, result, baseline_period_days, current_period_days)
            logger.warning(f"Drift detected in {metric_name}: {direction} (score: {drift_score:.2f})")
        
        return result
    
    def _store_drift_metric(
        self,
        metric_name: str,
        result: Dict,
        baseline_days: int,
        current_days: int
    ):
        """Store drift detection finding."""
        try:
            self.db.execute(text("""
                INSERT INTO drift_metrics (
                    metric_name, baseline_mean, baseline_std,
                    baseline_period_start, baseline_period_end,
                    current_mean, current_std,
                    current_period_start, current_period_end,
                    drift_score, drift_detected, drift_direction
                ) VALUES (
                    :metric, :baseline_mean, :baseline_std,
                    NOW() - INTERVAL '1 day' * :baseline_days, 
                    NOW() - INTERVAL '1 day' * :current_days,
                    :current_mean, :current_std,
                    NOW() - INTERVAL '1 day' * :current_days, NOW(),
                    :drift_score, :drift_detected, :direction
                )
            """), {
                "metric": metric_name,
                "baseline_mean": result["baseline"]["mean"],
                "baseline_std": result["baseline"]["std"],
                "baseline_days": baseline_days,
                "current_days": current_days,
                "current_mean": result["current"]["mean"],
                "current_std": result["current"]["std"],
                "drift_score": result["drift_score"],
                "drift_detected": result["drift_detected"],
                "direction": result["direction"]
            })
            self.db.commit()
        except Exception as e:
            logger.warning(f"Failed to store drift metric: {e}")
    
    # ==========================================
    # Dashboard Data
    # ==========================================
    
    def get_assurance_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive data for the assurance dashboard."""
        return {
            "active_tests": self._get_active_tests(),
            "recent_rollouts": self._get_recent_rollouts(),
            "bias_alerts": self._get_bias_alerts(),
            "drift_alerts": self._get_drift_alerts(),
            "summary": self._get_summary_stats()
        }
    
    def _get_active_tests(self) -> List[Dict]:
        """Get currently running shadow/A/B tests."""
        try:
            result = self.db.execute(text("""
                SELECT id, name, policy_type, is_shadow_mode, 
                       test_group_percentage, started_at, scheduled_end_at, status
                FROM shadow_tests
                WHERE status = 'running'
                ORDER BY started_at DESC
            """))
            return [dict(row._mapping) for row in result.fetchall()]
        except Exception:
            return []
    
    def _get_recent_rollouts(self) -> List[Dict]:
        """Get recent rollout status."""
        try:
            result = self.db.execute(text("""
                SELECT st.id, st.name, st.policy_type, st.status,
                       rs.stage_number, rs.rollout_percentage, rs.regression_detected
                FROM shadow_tests st
                LEFT JOIN rollout_stages rs ON st.id = rs.shadow_test_id
                WHERE st.status IN ('rolling_out', 'deployed', 'rolled_back')
                ORDER BY st.started_at DESC
                LIMIT 10
            """))
            return [dict(row._mapping) for row in result.fetchall()]
        except Exception:
            return []
    
    def _get_bias_alerts(self) -> List[Dict]:
        """Get recent bias alerts."""
        try:
            result = self.db.execute(text("""
                SELECT group_type, group_value, deviation_from_overall, created_at
                FROM bias_metrics
                WHERE is_potential_bias = TRUE
                AND created_at > NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
                LIMIT 5
            """))
            return [dict(row._mapping) for row in result.fetchall()]
        except Exception:
            return []
    
    def _get_drift_alerts(self) -> List[Dict]:
        """Get recent drift alerts."""
        try:
            result = self.db.execute(text("""
                SELECT metric_name, drift_score, drift_direction, created_at
                FROM drift_metrics
                WHERE drift_detected = TRUE
                AND created_at > NOW() - INTERVAL '7 days'
                ORDER BY created_at DESC
                LIMIT 5
            """))
            return [dict(row._mapping) for row in result.fetchall()]
        except Exception:
            return []
    
    def _get_summary_stats(self) -> Dict:
        """Get summary statistics."""
        try:
            result = self.db.execute(text("""
                SELECT 
                    COUNT(*) FILTER (WHERE status = 'running') as active_tests,
                    COUNT(*) FILTER (WHERE status = 'deployed') as successful_deployments,
                    COUNT(*) FILTER (WHERE status = 'rolled_back') as rollbacks,
                    COUNT(*) as total_tests
                FROM shadow_tests
                WHERE created_at > NOW() - INTERVAL '30 days'
            """)).fetchone()
            
            return {
                "active_tests": result.active_tests or 0,
                "successful_deployments": result.successful_deployments or 0,
                "rollbacks": result.rollbacks or 0,
                "total_tests": result.total_tests or 0,
                "success_rate": (result.successful_deployments or 0) / max(result.total_tests or 1, 1)
            }
        except Exception:
            return {"active_tests": 0, "successful_deployments": 0, "rollbacks": 0, "total_tests": 0, "success_rate": 0}

