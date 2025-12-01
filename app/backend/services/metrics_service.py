"""
Research Metrics Service

Comprehensive metrics collection for research evaluation:
- Time-to-target (dashboard open to feature activation)
- Click reduction (%)
- Suggestion acceptance/ignore rate
- Adaptation accuracy (top-N promoted features actually used)
- User satisfaction surveys
- System Usability Scale (SUS)
- NASA-TLX workload assessment

Part of Phase 8: Research Design & Metrics
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import logging
import math
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, text

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Service for collecting and analyzing research metrics.
    
    Metrics Categories:
    1. Efficiency Metrics - Time and clicks
    2. Effectiveness Metrics - Accuracy and relevance
    3. User Experience Metrics - Satisfaction and workload
    4. Adaptation Metrics - System performance
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # Efficiency Metrics
    # =========================================================================
    
    def measure_time_to_target(
        self,
        user_id: UUID,
        feature_key: str,
        session_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Measure time from dashboard open to feature activation.
        
        This is a key efficiency metric showing how quickly users
        can access the features they need.
        
        Args:
            user_id: User to measure
            feature_key: Target feature
            session_id: Optional specific session
            days: Days of data to analyze
        
        Returns:
            Time-to-target statistics
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        try:
            # Query for dashboard opens followed by feature activations
            query = text("""
                WITH dashboard_opens AS (
                    SELECT 
                        id,
                        session_id,
                        timestamp as open_time
                    FROM user_actions
                    WHERE user_id = :user_id
                      AND action_type = 'dashboard_open'
                      AND timestamp >= :cutoff
                ),
                feature_activations AS (
                    SELECT 
                        session_id,
                        timestamp as activation_time,
                        metadata->>'feature_id' as feature_id
                    FROM user_actions
                    WHERE user_id = :user_id
                      AND action_type IN ('feature_click', 'navigation', 'dashboard_feature_click')
                      AND metadata->>'feature_id' = :feature_key
                      AND timestamp >= :cutoff
                )
                SELECT 
                    do.session_id,
                    do.open_time,
                    fa.activation_time,
                    EXTRACT(EPOCH FROM (fa.activation_time - do.open_time)) as time_seconds
                FROM dashboard_opens do
                JOIN feature_activations fa ON do.session_id = fa.session_id
                WHERE fa.activation_time > do.open_time
                  AND fa.activation_time < do.open_time + INTERVAL '30 minutes'
                ORDER BY do.open_time DESC
            """)
            
            params = {
                "user_id": str(user_id),
                "feature_key": feature_key,
                "cutoff": cutoff
            }
            
            if session_id:
                # Add session filter if specified
                pass
            
            result = self.db.execute(query, params)
            rows = list(result)
            
            if not rows:
                return {
                    "feature_key": feature_key,
                    "measurements": 0,
                    "mean_seconds": None,
                    "median_seconds": None,
                    "min_seconds": None,
                    "max_seconds": None,
                    "std_seconds": None
                }
            
            times = [row.time_seconds for row in rows if row.time_seconds and row.time_seconds > 0]
            
            if not times:
                return {
                    "feature_key": feature_key,
                    "measurements": 0,
                    "mean_seconds": None,
                    "median_seconds": None
                }
            
            # Calculate statistics
            mean_time = sum(times) / len(times)
            sorted_times = sorted(times)
            median_time = sorted_times[len(times) // 2]
            min_time = min(times)
            max_time = max(times)
            
            # Standard deviation
            variance = sum((t - mean_time) ** 2 for t in times) / len(times)
            std_time = math.sqrt(variance)
            
            return {
                "feature_key": feature_key,
                "measurements": len(times),
                "mean_seconds": round(mean_time, 2),
                "median_seconds": round(median_time, 2),
                "min_seconds": round(min_time, 2),
                "max_seconds": round(max_time, 2),
                "std_seconds": round(std_time, 2),
                "percentile_25": round(sorted_times[len(times) // 4], 2) if len(times) >= 4 else None,
                "percentile_75": round(sorted_times[3 * len(times) // 4], 2) if len(times) >= 4 else None
            }
            
        except Exception as e:
            logger.error(f"Error measuring time-to-target: {e}")
            return {"error": str(e), "feature_key": feature_key}
    
    def calculate_click_reduction(
        self,
        user_id: UUID,
        baseline_period_days: int = 7,
        adaptive_period_days: int = 7
    ) -> Dict[str, Any]:
        """
        Calculate click reduction percentage between baseline and adaptive periods.
        
        Compares navigation efficiency before and after adaptation.
        
        Args:
            user_id: User to analyze
            baseline_period_days: Days in baseline period
            adaptive_period_days: Days in adaptive period
        
        Returns:
            Click reduction metrics
        """
        try:
            # Get user's first adaptation date
            adaptation_query = text("""
                SELECT MIN(timestamp) as first_adaptation
                FROM adaptations
                WHERE user_id = :user_id
            """)
            
            result = self.db.execute(adaptation_query, {"user_id": str(user_id)}).fetchone()
            
            if not result or not result.first_adaptation:
                return {
                    "status": "no_adaptation",
                    "message": "User has no adaptations yet"
                }
            
            first_adaptation = result.first_adaptation
            
            # Calculate baseline period (before first adaptation)
            baseline_start = first_adaptation - timedelta(days=baseline_period_days)
            baseline_end = first_adaptation
            
            # Calculate adaptive period (after first adaptation)
            adaptive_start = first_adaptation
            adaptive_end = first_adaptation + timedelta(days=adaptive_period_days)
            
            # Count clicks/navigations in baseline period
            baseline_query = text("""
                SELECT 
                    COUNT(*) as total_clicks,
                    COUNT(DISTINCT DATE(timestamp)) as active_days
                FROM user_actions
                WHERE user_id = :user_id
                  AND action_type IN ('navigation', 'feature_click', 'dashboard_feature_click')
                  AND timestamp BETWEEN :start_date AND :end_date
            """)
            
            baseline_result = self.db.execute(baseline_query, {
                "user_id": str(user_id),
                "start_date": baseline_start,
                "end_date": baseline_end
            }).fetchone()
            
            # Count clicks in adaptive period
            adaptive_result = self.db.execute(baseline_query, {
                "user_id": str(user_id),
                "start_date": adaptive_start,
                "end_date": adaptive_end
            }).fetchone()
            
            baseline_clicks = baseline_result.total_clicks if baseline_result else 0
            baseline_days = baseline_result.active_days if baseline_result else 1
            adaptive_clicks = adaptive_result.total_clicks if adaptive_result else 0
            adaptive_days = adaptive_result.active_days if adaptive_result else 1
            
            # Normalize to clicks per day
            baseline_clicks_per_day = baseline_clicks / max(baseline_days, 1)
            adaptive_clicks_per_day = adaptive_clicks / max(adaptive_days, 1)
            
            # Calculate reduction
            if baseline_clicks_per_day > 0:
                reduction_percent = ((baseline_clicks_per_day - adaptive_clicks_per_day) / baseline_clicks_per_day) * 100
            else:
                reduction_percent = 0
            
            return {
                "user_id": str(user_id),
                "baseline_period": {
                    "start": baseline_start.isoformat(),
                    "end": baseline_end.isoformat(),
                    "total_clicks": baseline_clicks,
                    "active_days": baseline_days,
                    "clicks_per_day": round(baseline_clicks_per_day, 2)
                },
                "adaptive_period": {
                    "start": adaptive_start.isoformat(),
                    "end": adaptive_end.isoformat(),
                    "total_clicks": adaptive_clicks,
                    "active_days": adaptive_days,
                    "clicks_per_day": round(adaptive_clicks_per_day, 2)
                },
                "click_reduction_percent": round(reduction_percent, 2),
                "improvement": reduction_percent > 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating click reduction: {e}")
            return {"error": str(e)}
    
    def measure_task_completion_time(
        self,
        user_id: UUID,
        task_type: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Measure time to complete specific clinical tasks.
        
        Task types: patient_review, medication_check, lab_review, etc.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        try:
            query = text("""
                WITH task_starts AS (
                    SELECT 
                        session_id,
                        patient_id,
                        timestamp as start_time
                    FROM user_actions
                    WHERE user_id = :user_id
                      AND action_type = 'task_start'
                      AND metadata->>'task_type' = :task_type
                      AND timestamp >= :cutoff
                ),
                task_ends AS (
                    SELECT 
                        session_id,
                        patient_id,
                        timestamp as end_time
                    FROM user_actions
                    WHERE user_id = :user_id
                      AND action_type = 'task_complete'
                      AND metadata->>'task_type' = :task_type
                      AND timestamp >= :cutoff
                )
                SELECT 
                    ts.session_id,
                    ts.patient_id,
                    EXTRACT(EPOCH FROM (te.end_time - ts.start_time)) as duration_seconds
                FROM task_starts ts
                JOIN task_ends te ON ts.session_id = te.session_id 
                                 AND ts.patient_id = te.patient_id
                WHERE te.end_time > ts.start_time
                  AND te.end_time < ts.start_time + INTERVAL '1 hour'
            """)
            
            result = self.db.execute(query, {
                "user_id": str(user_id),
                "task_type": task_type,
                "cutoff": cutoff
            })
            
            durations = [row.duration_seconds for row in result if row.duration_seconds]
            
            if not durations:
                return {"task_type": task_type, "measurements": 0}
            
            return {
                "task_type": task_type,
                "measurements": len(durations),
                "mean_seconds": round(sum(durations) / len(durations), 2),
                "median_seconds": round(sorted(durations)[len(durations) // 2], 2),
                "min_seconds": round(min(durations), 2),
                "max_seconds": round(max(durations), 2)
            }
            
        except Exception as e:
            logger.error(f"Error measuring task completion: {e}")
            return {"error": str(e), "task_type": task_type}
    
    # =========================================================================
    # Effectiveness Metrics
    # =========================================================================
    
    def calculate_suggestion_rates(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate suggestion acceptance, ignore, and rejection rates.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        try:
            query = text("""
                SELECT 
                    metadata->>'action' as response,
                    COUNT(*) as count
                FROM user_actions
                WHERE user_id = :user_id
                  AND action_type = 'suggestion_response'
                  AND timestamp >= :cutoff
                GROUP BY metadata->>'action'
            """)
            
            result = self.db.execute(query, {
                "user_id": str(user_id),
                "cutoff": cutoff
            })
            
            counts = {}
            total = 0
            for row in result:
                counts[row.response] = row.count
                total += row.count
            
            if total == 0:
                return {
                    "total_suggestions": 0,
                    "acceptance_rate": 0.0,
                    "ignore_rate": 0.0,
                    "rejection_rate": 0.0
                }
            
            return {
                "total_suggestions": total,
                "accepted": counts.get("accept", 0),
                "ignored": counts.get("ignore", 0),
                "rejected": counts.get("reject", 0) + counts.get("not_relevant", 0),
                "acceptance_rate": round(counts.get("accept", 0) / total, 3),
                "ignore_rate": round(counts.get("ignore", 0) / total, 3),
                "rejection_rate": round((counts.get("reject", 0) + counts.get("not_relevant", 0)) / total, 3),
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error calculating suggestion rates: {e}")
            return {"error": str(e)}
    
    def measure_adaptation_accuracy(
        self,
        user_id: UUID,
        top_n: int = 5,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Measure adaptation accuracy: are promoted features actually used?
        
        Calculates precision and recall for top-N promoted features.
        
        Args:
            user_id: User to analyze
            top_n: Number of top features to consider
            days: Days of data to analyze
        
        Returns:
            Precision, recall, and F1 score
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        try:
            # Get promoted features from latest adaptation
            adaptation_query = text("""
                SELECT plan_json
                FROM adaptations
                WHERE user_id = :user_id
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            adaptation_result = self.db.execute(
                adaptation_query, 
                {"user_id": str(user_id)}
            ).fetchone()
            
            if not adaptation_result or not adaptation_result.plan_json:
                return {
                    "status": "no_adaptation",
                    "message": "No adaptation found for user"
                }
            
            import json
            plan = adaptation_result.plan_json
            if isinstance(plan, str):
                plan = json.loads(plan)
            
            # Get promoted features (top-N from section_order or feature list)
            promoted_features = set()
            if "order" in plan:
                promoted_features = set(plan["order"][:top_n])
            elif "section_order" in plan:
                promoted_features = set(plan["section_order"][:top_n])
            elif "feature_priorities" in plan:
                sorted_features = sorted(
                    plan["feature_priorities"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                promoted_features = set([f[0] for f in sorted_features[:top_n]])
            
            if not promoted_features:
                return {
                    "status": "no_promoted_features",
                    "message": "Could not determine promoted features"
                }
            
            # Get actually used features
            usage_query = text("""
                SELECT 
                    COALESCE(
                        metadata->>'feature_id',
                        metadata->>'to_section'
                    ) as feature,
                    COUNT(*) as usage_count
                FROM user_actions
                WHERE user_id = :user_id
                  AND timestamp >= :cutoff
                  AND action_type IN ('navigation', 'feature_click', 'dashboard_feature_click')
                GROUP BY COALESCE(
                    metadata->>'feature_id',
                    metadata->>'to_section'
                )
                ORDER BY usage_count DESC
            """)
            
            usage_result = self.db.execute(usage_query, {
                "user_id": str(user_id),
                "cutoff": cutoff
            })
            
            # Get top-N actually used features
            actually_used = set()
            all_used = {}
            for i, row in enumerate(usage_result):
                if row.feature:
                    all_used[row.feature] = row.usage_count
                    if i < top_n:
                        actually_used.add(row.feature)
            
            # Calculate precision, recall, F1
            true_positives = len(promoted_features & actually_used)
            false_positives = len(promoted_features - actually_used)
            false_negatives = len(actually_used - promoted_features)
            
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            return {
                "top_n": top_n,
                "promoted_features": list(promoted_features),
                "actually_used_top_n": list(actually_used),
                "true_positives": true_positives,
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "precision": round(precision, 3),
                "recall": round(recall, 3),
                "f1_score": round(f1, 3),
                "period_days": days,
                "feature_usage_counts": all_used
            }
            
        except Exception as e:
            logger.error(f"Error measuring adaptation accuracy: {e}")
            return {"error": str(e)}
    
    # =========================================================================
    # User Experience Metrics
    # =========================================================================
    
    def record_satisfaction_survey(
        self,
        user_id: UUID,
        survey_type: str,
        responses: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Record user satisfaction survey response.
        
        Survey types:
        - quick_feedback: Single 1-5 rating
        - sus: System Usability Scale (10 questions)
        - nasa_tlx: NASA Task Load Index (6 dimensions)
        - custom: Custom survey
        """
        try:
            import json
            
            # Calculate scores based on survey type
            scores = self._calculate_survey_scores(survey_type, responses)
            
            query = text("""
                INSERT INTO user_surveys (
                    user_id, survey_type, responses, scores, context, created_at
                ) VALUES (
                    :user_id, :survey_type, :responses, :scores, :context, :created_at
                )
                RETURNING id
            """)
            
            result = self.db.execute(query, {
                "user_id": str(user_id),
                "survey_type": survey_type,
                "responses": json.dumps(responses),
                "scores": json.dumps(scores),
                "context": json.dumps(context or {}),
                "created_at": datetime.utcnow()
            })
            
            survey_id = result.fetchone()[0]
            self.db.commit()
            
            return {
                "survey_id": str(survey_id),
                "survey_type": survey_type,
                "scores": scores,
                "recorded_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recording survey: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def _calculate_survey_scores(
        self,
        survey_type: str,
        responses: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate scores based on survey type."""
        
        if survey_type == "quick_feedback":
            # Simple 1-5 rating
            return {"overall": float(responses.get("rating", 0))}
        
        elif survey_type == "sus":
            # System Usability Scale calculation
            # Questions 1,3,5,7,9 are positive (score - 1)
            # Questions 2,4,6,8,10 are negative (5 - score)
            positive_items = [1, 3, 5, 7, 9]
            negative_items = [2, 4, 6, 8, 10]
            
            total = 0
            for i in positive_items:
                score = responses.get(f"q{i}", 3)
                total += (score - 1)
            
            for i in negative_items:
                score = responses.get(f"q{i}", 3)
                total += (5 - score)
            
            sus_score = total * 2.5  # Scale to 0-100
            
            return {
                "sus_score": round(sus_score, 1),
                "interpretation": self._interpret_sus(sus_score)
            }
        
        elif survey_type == "nasa_tlx":
            # NASA Task Load Index
            dimensions = ["mental", "physical", "temporal", "performance", "effort", "frustration"]
            scores = {}
            total = 0
            
            for dim in dimensions:
                score = responses.get(dim, 50)  # 0-100 scale
                scores[dim] = score
                total += score
            
            scores["overall"] = round(total / len(dimensions), 1)
            scores["interpretation"] = self._interpret_tlx(scores["overall"])
            
            return scores
        
        else:
            # Custom survey - return raw scores
            return {k: float(v) if isinstance(v, (int, float)) else v for k, v in responses.items()}
    
    def _interpret_sus(self, score: float) -> str:
        """Interpret SUS score."""
        if score >= 85:
            return "excellent"
        elif score >= 72:
            return "good"
        elif score >= 52:
            return "ok"
        elif score >= 38:
            return "poor"
        else:
            return "awful"
    
    def _interpret_tlx(self, score: float) -> str:
        """Interpret NASA-TLX score (lower is better)."""
        if score <= 20:
            return "very_low_workload"
        elif score <= 40:
            return "low_workload"
        elif score <= 60:
            return "moderate_workload"
        elif score <= 80:
            return "high_workload"
        else:
            return "very_high_workload"
    
    def get_satisfaction_trends(
        self,
        user_id: Optional[UUID] = None,
        survey_type: str = "quick_feedback",
        days: int = 90
    ) -> Dict[str, Any]:
        """Get satisfaction score trends over time."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        try:
            if user_id:
                query = text("""
                    SELECT 
                        DATE(created_at) as date,
                        AVG((scores->>'overall')::float) as avg_score,
                        COUNT(*) as responses
                    FROM user_surveys
                    WHERE user_id = :user_id
                      AND survey_type = :survey_type
                      AND created_at >= :cutoff
                    GROUP BY DATE(created_at)
                    ORDER BY DATE(created_at)
                """)
                params = {"user_id": str(user_id), "survey_type": survey_type, "cutoff": cutoff}
            else:
                query = text("""
                    SELECT 
                        DATE(created_at) as date,
                        AVG((scores->>'overall')::float) as avg_score,
                        COUNT(*) as responses,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM user_surveys
                    WHERE survey_type = :survey_type
                      AND created_at >= :cutoff
                    GROUP BY DATE(created_at)
                    ORDER BY DATE(created_at)
                """)
                params = {"survey_type": survey_type, "cutoff": cutoff}
            
            result = self.db.execute(query, params)
            
            trends = []
            for row in result:
                trends.append({
                    "date": row.date.isoformat() if row.date else None,
                    "avg_score": round(row.avg_score, 2) if row.avg_score else None,
                    "responses": row.responses
                })
            
            return {
                "survey_type": survey_type,
                "period_days": days,
                "trends": trends,
                "total_responses": sum(t["responses"] for t in trends)
            }
            
        except Exception as e:
            logger.error(f"Error getting satisfaction trends: {e}")
            return {"error": str(e)}
    
    # =========================================================================
    # Adaptation Metrics
    # =========================================================================
    
    def measure_adaptation_stability(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Measure how stable adaptations are over time.
        
        High stability = fewer changes = system has converged
        Low stability = frequent changes = still learning
        """
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        try:
            query = text("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as adaptations
                FROM adaptations
                WHERE user_id = :user_id
                  AND timestamp >= :cutoff
                GROUP BY DATE(timestamp)
                ORDER BY DATE(timestamp)
            """)
            
            result = self.db.execute(query, {
                "user_id": str(user_id),
                "cutoff": cutoff
            })
            
            daily_counts = []
            total = 0
            for row in result:
                daily_counts.append(row.adaptations)
                total += row.adaptations
            
            if not daily_counts:
                return {
                    "total_adaptations": 0,
                    "stability_score": 1.0,
                    "status": "stable"
                }
            
            # Calculate stability (inverse of variance normalized)
            mean = total / len(daily_counts)
            variance = sum((c - mean) ** 2 for c in daily_counts) / len(daily_counts)
            std = math.sqrt(variance)
            
            # Stability score: 1 / (1 + coefficient of variation)
            cv = std / mean if mean > 0 else 0
            stability_score = 1 / (1 + cv)
            
            return {
                "total_adaptations": total,
                "days_with_adaptations": len(daily_counts),
                "adaptations_per_day": round(mean, 2),
                "stability_score": round(stability_score, 3),
                "coefficient_of_variation": round(cv, 3),
                "status": "stable" if stability_score > 0.7 else "converging" if stability_score > 0.4 else "learning"
            }
            
        except Exception as e:
            logger.error(f"Error measuring stability: {e}")
            return {"error": str(e)}
    
    def measure_bandit_convergence(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Measure Thompson Sampling bandit convergence.
        
        Uses confidence interval width as convergence indicator.
        """
        try:
            query = text("""
                SELECT 
                    feature_key,
                    alpha,
                    beta,
                    total_interactions
                FROM bandit_states
                WHERE user_id = :user_id
            """)
            
            result = self.db.execute(query, {"user_id": str(user_id)})
            
            features = []
            total_uncertainty = 0
            
            for row in result:
                # Calculate 95% CI width for Beta distribution
                # Approximation: width ≈ 4 * sqrt(alpha * beta / ((alpha + beta)^2 * (alpha + beta + 1)))
                a, b = row.alpha, row.beta
                if a > 0 and b > 0:
                    variance = (a * b) / ((a + b) ** 2 * (a + b + 1))
                    ci_width = 4 * math.sqrt(variance)
                else:
                    ci_width = 1.0
                
                features.append({
                    "feature_key": row.feature_key,
                    "alpha": round(row.alpha, 2),
                    "beta": round(row.beta, 2),
                    "expected_value": round(a / (a + b), 3) if (a + b) > 0 else 0.5,
                    "ci_width": round(ci_width, 3),
                    "interactions": row.total_interactions,
                    "converged": ci_width < 0.2
                })
                
                total_uncertainty += ci_width
            
            if not features:
                return {"status": "no_data"}
            
            avg_uncertainty = total_uncertainty / len(features)
            converged_count = sum(1 for f in features if f["converged"])
            
            return {
                "features": features,
                "total_features": len(features),
                "converged_features": converged_count,
                "convergence_rate": round(converged_count / len(features), 3),
                "average_uncertainty": round(avg_uncertainty, 3),
                "status": "converged" if avg_uncertainty < 0.15 else "converging" if avg_uncertainty < 0.3 else "exploring"
            }
            
        except Exception as e:
            logger.error(f"Error measuring bandit convergence: {e}")
            return {"error": str(e)}
    
    # =========================================================================
    # Aggregate Reports
    # =========================================================================
    
    def generate_user_metrics_report(
        self,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive metrics report for a user."""
        return {
            "user_id": str(user_id),
            "report_date": datetime.utcnow().isoformat(),
            "period_days": days,
            "efficiency": {
                "click_reduction": self.calculate_click_reduction(user_id),
                "suggestion_rates": self.calculate_suggestion_rates(user_id, days)
            },
            "effectiveness": {
                "adaptation_accuracy": self.measure_adaptation_accuracy(user_id, top_n=5, days=days)
            },
            "system": {
                "adaptation_stability": self.measure_adaptation_stability(user_id, days),
                "bandit_convergence": self.measure_bandit_convergence(user_id)
            },
            "satisfaction": self.get_satisfaction_trends(user_id, days=days)
        }
    
    def generate_study_metrics_report(
        self,
        study_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Generate aggregate metrics report for a study."""
        try:
            # Get all users in study
            query = text("""
                SELECT DISTINCT user_id, condition
                FROM study_assignments
                WHERE study_id = :study_id
            """)
            
            result = self.db.execute(query, {"study_id": study_id})
            
            users_by_condition = {"A": [], "B": []}
            for row in result:
                condition = row.condition
                if condition in users_by_condition:
                    users_by_condition[condition].append(UUID(row.user_id))
            
            # Calculate metrics for each condition
            metrics_by_condition = {}
            
            for condition, users in users_by_condition.items():
                if not users:
                    continue
                
                suggestion_rates = []
                adaptation_accuracies = []
                
                for user_id in users:
                    sr = self.calculate_suggestion_rates(user_id, days)
                    if "acceptance_rate" in sr:
                        suggestion_rates.append(sr["acceptance_rate"])
                    
                    aa = self.measure_adaptation_accuracy(user_id, days=days)
                    if "f1_score" in aa:
                        adaptation_accuracies.append(aa["f1_score"])
                
                metrics_by_condition[condition] = {
                    "user_count": len(users),
                    "avg_acceptance_rate": round(sum(suggestion_rates) / len(suggestion_rates), 3) if suggestion_rates else None,
                    "avg_adaptation_f1": round(sum(adaptation_accuracies) / len(adaptation_accuracies), 3) if adaptation_accuracies else None
                }
            
            return {
                "study_id": study_id,
                "report_date": datetime.utcnow().isoformat(),
                "period_days": days,
                "metrics_by_condition": metrics_by_condition
            }
            
        except Exception as e:
            logger.error(f"Error generating study report: {e}")
            return {"error": str(e)}


def get_metrics_service(db: Session) -> MetricsService:
    """Get metrics service instance."""
    return MetricsService(db)

