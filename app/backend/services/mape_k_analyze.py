"""
MAPE-K Analyze Component
Analyzes collected monitoring data to determine what adaptations are needed

Enhanced with:
- Multi-window analysis (7/30/90 days)
- Exponential decay for recency weighting
- Drift detection for non-stationarity
- Context-aware windows
"""
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func
import math
import logging

from services.user_action_service import UserActionService

logger = logging.getLogger(__name__)


# Default window configurations
DEFAULT_WINDOWS = [7, 30, 90]  # days

# Exponential decay weights (sum to 1.0)
DECAY_WEIGHTS = {
    7: 0.5,    # 50% weight for recent 7 days
    30: 0.3,   # 30% weight for 30 days
    90: 0.2,   # 20% weight for 90 days
}

# Drift detection thresholds
DRIFT_THRESHOLD = 0.3  # 30% change between windows indicates drift


class MAPEKAnalyzeService:
    """Service for analyzing monitoring data and generating insights"""

    @staticmethod
    def analyze(
        db: Session,
        user_id: UUID,
        patient_id: Optional[UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze user behavior and system data to generate insights
        
        Returns:
            Dictionary containing analysis results with insights and recommendations
        """
        # Get navigation patterns
        navigation_patterns = UserActionService.get_navigation_patterns(
            db, user_id, patient_id=patient_id, days=days
        )
        
        # Get suggestion actions
        suggestion_actions = UserActionService.get_suggestion_actions(
            db, user_id=user_id, patient_id=patient_id, days=days
        )
        
        # Get risk changes (if patient-specific)
        risk_changes = None
        if patient_id:
            risk_changes = UserActionService.get_risk_changes(
                db, patient_id, days=days
            )
        
        # Analyze navigation patterns
        nav_analysis = MAPEKAnalyzeService._analyze_navigation(navigation_patterns)
        
        # Analyze suggestion interactions
        suggestion_analysis = MAPEKAnalyzeService._analyze_suggestions(suggestion_actions)
        
        # Analyze risk changes
        risk_analysis = None
        if risk_changes:
            risk_analysis = MAPEKAnalyzeService._analyze_risk_changes(risk_changes)
        
        # Generate insights
        insights = MAPEKAnalyzeService._generate_insights(
            nav_analysis, suggestion_analysis, risk_analysis
        )
        
        # Generate recommendations
        recommendations = MAPEKAnalyzeService._generate_recommendations(
            nav_analysis, suggestion_analysis, risk_analysis
        )
        
        return {
            "user_id": str(user_id),
            "patient_id": str(patient_id) if patient_id else None,
            "navigation_patterns": nav_analysis,
            "suggestion_actions": suggestion_analysis,
            "risk_changes": risk_changes,
            "insights": insights,
            "recommendations": recommendations
        }

    @staticmethod
    def _analyze_navigation(patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze navigation patterns"""
        if not patterns:
            return {
                "total_navigations": 0,
                "section_visits": {},
                "common_paths": [],
                "most_visited": None
            }
        
        # Count section visits
        section_visits = {}
        for pattern in patterns:
            to_section = pattern.get("to_section")
            if to_section:
                section_visits[to_section] = section_visits.get(to_section, 0) + 1
        
        # Find most visited section
        most_visited = max(section_visits.items(), key=lambda x: x[1])[0] if section_visits else None
        
        # Find common navigation paths
        paths = {}
        for pattern in patterns:
            from_section = pattern.get("from_section", "start")
            to_section = pattern.get("to_section")
            if to_section:
                path_key = f"{from_section} -> {to_section}"
                paths[path_key] = paths.get(path_key, 0) + 1
        
        common_paths = sorted(paths.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_navigations": len(patterns),
            "section_visits": section_visits,
            "common_paths": [{"path": k, "count": v} for k, v in common_paths],
            "most_visited": most_visited
        }

    @staticmethod
    def _analyze_suggestions(actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze suggestion interaction patterns"""
        if not actions:
            return {
                "total_actions": 0,
                "accept_count": 0,
                "ignore_count": 0,
                "not_relevant_count": 0,
                "acceptance_rate": 0.0,
                "ignore_rate": 0.0
            }
        
        accept_count = sum(1 for a in actions if a.get("action") == "accept")
        ignore_count = sum(1 for a in actions if a.get("action") == "ignore")
        not_relevant_count = sum(1 for a in actions if a.get("action") == "not_relevant")
        total = len(actions)
        
        return {
            "total_actions": total,
            "accept_count": accept_count,
            "ignore_count": ignore_count,
            "not_relevant_count": not_relevant_count,
            "acceptance_rate": accept_count / total if total > 0 else 0.0,
            "ignore_rate": ignore_count / total if total > 0 else 0.0
        }

    @staticmethod
    def _analyze_risk_changes(changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze risk change patterns"""
        if not changes:
            return {
                "total_changes": 0,
                "escalations": 0,
                "deescalations": 0
            }
        
        escalations = 0
        deescalations = 0
        
        risk_levels = {"routine": 1, "needs_attention": 2, "high_concern": 3}
        
        for change in changes:
            prev = change.get("previous_risk_level", "routine")
            new = change.get("new_risk_level", "routine")
            
            prev_level = risk_levels.get(prev, 1)
            new_level = risk_levels.get(new, 1)
            
            if new_level > prev_level:
                escalations += 1
            elif new_level < prev_level:
                deescalations += 1
        
        return {
            "total_changes": len(changes),
            "escalations": escalations,
            "deescalations": deescalations
        }

    @staticmethod
    def _generate_insights(
        nav_analysis: Dict[str, Any],
        suggestion_analysis: Dict[str, Any],
        risk_analysis: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate insights from analysis"""
        insights = []
        
        # Navigation insights
        most_visited = nav_analysis.get("most_visited")
        if most_visited:
            insights.append(f"User frequently navigates to '{most_visited}' section")
        
        total_navs = nav_analysis.get("total_navigations", 0)
        if total_navs > 50:
            insights.append(f"High navigation activity ({total_navs} navigations in analyzed period)")
        
        # Suggestion insights
        ignore_rate = suggestion_analysis.get("ignore_rate", 0.0)
        if ignore_rate > 0.5:
            insights.append(f"High suggestion ignore rate ({ignore_rate:.1%}) - suggestions may not be relevant")
        
        acceptance_rate = suggestion_analysis.get("acceptance_rate", 0.0)
        if acceptance_rate > 0.7:
            insights.append(f"High suggestion acceptance rate ({acceptance_rate:.1%}) - suggestions are valuable")
        
        # Risk insights
        if risk_analysis:
            escalations = risk_analysis.get("escalations", 0)
            if escalations > 0:
                insights.append(f"Patient risk has escalated {escalations} time(s) - increased monitoring may be needed")
        
        return insights

    @staticmethod
    def _generate_recommendations(
        nav_analysis: Dict[str, Any],
        suggestion_analysis: Dict[str, Any],
        risk_analysis: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate adaptation recommendations"""
        recommendations = []
        
        # Navigation-based recommendations
        most_visited = nav_analysis.get("most_visited")
        if most_visited:
            recommendations.append(f"Move '{most_visited}' section higher in the layout")
        
        # Suggestion-based recommendations
        ignore_rate = suggestion_analysis.get("ignore_rate", 0.0)
        if ignore_rate > 0.5:
            recommendations.append("Reduce suggestion frequency - many suggestions are being ignored")
        elif ignore_rate < 0.2:
            recommendations.append("Maintain or increase suggestion frequency - low ignore rate")
        
        # Risk-based recommendations
        if risk_analysis:
            escalations = risk_analysis.get("escalations", 0)
            if escalations > 0:
                recommendations.append("Prioritize vitals and risk monitoring sections")
        
        return recommendations

    @staticmethod
    def analyze_dashboard_usage(
        db: Session,
        user_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze dashboard usage patterns to identify:
        - Most frequently used features
        - Feature access patterns (time of day, day of week)
        - Workflow sequences (which features used together)
        - Rarely used features
        """
        from datetime import datetime, timedelta
        from sqlalchemy import select, and_
        from models.user_action import UserAction
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get dashboard-specific actions
        query = select(UserAction).where(
            and_(
                UserAction.user_id == user_id,
                UserAction.action_type.like('dashboard_%'),
                UserAction.timestamp >= cutoff_date
            )
        ).order_by(UserAction.timestamp.asc())
        
        result = db.execute(query)
        dashboard_actions = list(result.scalars().all())
        
        # Calculate feature frequencies
        feature_counts = {}
        feature_sequences = []
        time_of_day_counts = {}
        
        for action in dashboard_actions:
            action_data = action.action_metadata or {}
            feature_id = action_data.get('feature_id')
            
            if feature_id:
                feature_counts[feature_id] = feature_counts.get(feature_id, 0) + 1
                
                # Track sequences
                feature_sequences.append({
                    'feature': feature_id,
                    'timestamp': action.timestamp,
                    'context': action_data.get('metadata', {})
                })
                
                # Track time of day patterns
                hour = action.timestamp.hour
                time_slot = 'morning' if 6 <= hour < 12 else 'afternoon' if 12 <= hour < 18 else 'evening'
                if feature_id not in time_of_day_counts:
                    time_of_day_counts[feature_id] = {'morning': 0, 'afternoon': 0, 'evening': 0}
                time_of_day_counts[feature_id][time_slot] = time_of_day_counts[feature_id].get(time_slot, 0) + 1
        
        # Calculate daily averages
        feature_daily_averages = {
            feature_id: count / days
            for feature_id, count in feature_counts.items()
        }
        
        # Identify most/least used
        sorted_features = sorted(
            feature_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        most_used = [f[0] for f in sorted_features[:5]]  # Top 5
        least_used = [f[0] for f in sorted_features[-3:]] if len(sorted_features) >= 3 else []  # Bottom 3
        
        # Analyze workflow patterns (which features used together)
        workflow_patterns = MAPEKAnalyzeService._analyze_feature_sequences(feature_sequences)
        
        return {
            "feature_frequencies": feature_counts,
            "feature_daily_averages": feature_daily_averages,
            "most_used_features": most_used,
            "least_used_features": least_used,
            "workflow_patterns": workflow_patterns,
            "time_of_day_patterns": time_of_day_counts,
            "total_actions": len(dashboard_actions),
            "analysis_period_days": days
        }

    @staticmethod
    def _analyze_feature_sequences(sequences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sequences of feature usage to identify workflow patterns"""
        if len(sequences) < 2:
            return {"common_sequences": [], "workflow_patterns": []}
        
        # Group sequences by time windows (within 5 minutes = same workflow)
        workflows = []
        current_workflow = []
        last_timestamp = None
        
        for seq in sequences:
            timestamp = seq['timestamp']
            if isinstance(timestamp, str):
                from datetime import datetime
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            if last_timestamp:
                time_diff = (timestamp - last_timestamp).total_seconds() / 60  # minutes
                if time_diff > 5:  # New workflow if >5 minutes gap
                    if current_workflow:
                        workflows.append(current_workflow)
                    current_workflow = [seq['feature']]
                else:
                    current_workflow.append(seq['feature'])
            else:
                current_workflow = [seq['feature']]
            
            last_timestamp = timestamp
        
        if current_workflow:
            workflows.append(current_workflow)
        
        # Find common workflow patterns
        workflow_counts = {}
        for workflow in workflows:
            if len(workflow) >= 2:
                # Look for 2-3 feature sequences
                for i in range(len(workflow) - 1):
                    sequence_key = ' → '.join(workflow[i:i+2])
                    workflow_counts[sequence_key] = workflow_counts.get(sequence_key, 0) + 1
        
        common_sequences = sorted(
            workflow_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "common_sequences": [{"sequence": k, "count": v} for k, v in common_sequences],
            "workflow_patterns": workflows[:10]  # Top 10 workflows
        }

    # ============================================================================
    # Phase 6: Multi-Window Analysis with Exponential Decay
    # ============================================================================

    @staticmethod
    def analyze_with_windows(
        db: Session,
        user_id: UUID,
        patient_id: Optional[UUID] = None,
        windows: List[int] = None,
        decay_weights: Dict[int, float] = None
    ) -> Dict[str, Any]:
        """
        Analyze user behavior across multiple time windows.
        
        Provides a more nuanced understanding by:
        1. Analyzing short-term (7 days), medium-term (30 days), and long-term (90 days) patterns
        2. Applying exponential decay to weight recent data more heavily
        3. Detecting drift between windows (behavioral changes)
        4. Generating window-aware insights
        
        Args:
            db: Database session
            user_id: User to analyze
            patient_id: Optional patient context
            windows: List of window sizes in days (default: [7, 30, 90])
            decay_weights: Custom weights for each window (must sum to 1.0)
        
        Returns:
            Combined analysis with window-specific and weighted results
        """
        if windows is None:
            windows = DEFAULT_WINDOWS
        if decay_weights is None:
            decay_weights = DECAY_WEIGHTS
        
        # Validate weights sum to 1.0
        if windows and decay_weights:
            total_weight = sum(decay_weights.get(w, 0) for w in windows)
            if abs(total_weight - 1.0) > 0.01:
                logger.warning(f"Decay weights sum to {total_weight}, normalizing...")
                decay_weights = {
                    w: decay_weights.get(w, 0) / total_weight
                    for w in windows
                }
        
        # Analyze each window
        window_results = {}
        for window in sorted(windows):
            window_results[window] = MAPEKAnalyzeService._analyze_window(
                db, user_id, patient_id, window
            )
        
        # Combine with exponential decay
        combined = MAPEKAnalyzeService._combine_with_decay(
            window_results, decay_weights
        )
        
        # Detect drift between windows
        drift_analysis = MAPEKAnalyzeService._detect_drift(window_results)
        
        # Generate multi-window insights
        insights = MAPEKAnalyzeService._generate_window_insights(
            window_results, drift_analysis
        )
        
        # Calculate confidence based on data availability
        confidence = MAPEKAnalyzeService._calculate_analysis_confidence(
            window_results
        )
        
        return {
            "user_id": str(user_id),
            "patient_id": str(patient_id) if patient_id else None,
            "windows_analyzed": windows,
            "window_results": {
                f"{w}_day": r for w, r in window_results.items()
            },
            "combined_analysis": combined,
            "drift_analysis": drift_analysis,
            "insights": insights,
            "confidence": confidence,
            "methodology": "multi_window_exponential_decay"
        }

    @staticmethod
    def _analyze_window(
        db: Session,
        user_id: UUID,
        patient_id: Optional[UUID],
        days: int
    ) -> Dict[str, Any]:
        """Analyze data for a specific time window."""
        from models.user_action import UserAction
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get navigation patterns for this window
        navigation_patterns = UserActionService.get_navigation_patterns(
            db, user_id, patient_id=patient_id, days=days
        )
        
        # Get suggestion actions for this window
        suggestion_actions = UserActionService.get_suggestion_actions(
            db, user_id=user_id, patient_id=patient_id, days=days
        )
        
        # Analyze navigation
        nav_analysis = MAPEKAnalyzeService._analyze_navigation(navigation_patterns)
        
        # Analyze suggestions
        suggestion_analysis = MAPEKAnalyzeService._analyze_suggestions(suggestion_actions)
        
        # Get feature frequencies
        feature_counts = {}
        section_time_spent = {}
        
        try:
            query = select(UserAction).where(
                and_(
                    UserAction.user_id == user_id,
                    UserAction.timestamp >= cutoff_date
                )
            )
            
            result = db.execute(query)
            actions = list(result.scalars().all())
            
            for action in actions:
                action_data = action.action_metadata or {}
                feature_id = action_data.get('feature_id') or action_data.get('to_section')
                
                if feature_id:
                    feature_counts[feature_id] = feature_counts.get(feature_id, 0) + 1
                    
                    # Estimate time spent (using action frequency as proxy)
                    time_spent = action_data.get('time_spent', 1)  # default 1 second
                    section_time_spent[feature_id] = section_time_spent.get(feature_id, 0) + time_spent
        
        except Exception as e:
            logger.warning(f"Error analyzing window {days}: {e}")
        
        # Calculate daily averages
        daily_avg = {
            feature: count / days
            for feature, count in feature_counts.items()
        }
        
        return {
            "window_days": days,
            "navigation": nav_analysis,
            "suggestions": suggestion_analysis,
            "feature_counts": feature_counts,
            "feature_daily_averages": daily_avg,
            "section_time_spent": section_time_spent,
            "total_actions": nav_analysis.get("total_navigations", 0) + suggestion_analysis.get("total_actions", 0),
            "data_points": len(navigation_patterns) + len(suggestion_actions)
        }

    @staticmethod
    def _combine_with_decay(
        window_results: Dict[int, Dict],
        decay_weights: Dict[int, float]
    ) -> Dict[str, Any]:
        """
        Combine window results using exponential decay weighting.
        
        Recent data (7 days) gets higher weight than older data (90 days).
        This balances recency with stability.
        """
        # Combine feature scores
        combined_features = {}
        combined_acceptance_rate = 0.0
        combined_ignore_rate = 0.0
        total_weight = 0.0
        
        for window, result in window_results.items():
            weight = decay_weights.get(window, 0)
            if weight <= 0:
                continue
            
            total_weight += weight
            
            # Weighted feature counts
            daily_avgs = result.get("feature_daily_averages", {})
            for feature, avg in daily_avgs.items():
                if feature not in combined_features:
                    combined_features[feature] = 0.0
                combined_features[feature] += avg * weight
            
            # Weighted suggestion rates
            suggestions = result.get("suggestions", {})
            combined_acceptance_rate += suggestions.get("acceptance_rate", 0) * weight
            combined_ignore_rate += suggestions.get("ignore_rate", 0) * weight
        
        # Normalize if weights don't sum to 1
        if total_weight > 0 and abs(total_weight - 1.0) > 0.01:
            combined_features = {
                k: v / total_weight for k, v in combined_features.items()
            }
            combined_acceptance_rate /= total_weight
            combined_ignore_rate /= total_weight
        
        # Rank features by weighted score
        ranked_features = sorted(
            combined_features.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "weighted_feature_scores": dict(ranked_features),
            "top_features": [f[0] for f in ranked_features[:5]],
            "weighted_acceptance_rate": round(combined_acceptance_rate, 3),
            "weighted_ignore_rate": round(combined_ignore_rate, 3),
            "decay_weights_used": decay_weights
        }

    @staticmethod
    def _detect_drift(
        window_results: Dict[int, Dict]
    ) -> Dict[str, Any]:
        """
        Detect drift (non-stationarity) in user behavior across windows.
        
        Compares short-term vs long-term patterns to identify:
        - Emerging features (rising usage)
        - Declining features (falling usage)
        - Stable features (consistent usage)
        - Changed preferences (sudden shifts)
        """
        windows = sorted(window_results.keys())
        
        if len(windows) < 2:
            return {"drift_detected": False, "reason": "Insufficient windows for comparison"}
        
        short_term = window_results.get(windows[0], {})  # 7 days
        long_term = window_results.get(windows[-1], {})  # 90 days
        
        short_avgs = short_term.get("feature_daily_averages", {})
        long_avgs = long_term.get("feature_daily_averages", {})
        
        # Compare features
        emerging = []
        declining = []
        stable = []
        
        all_features = set(short_avgs.keys()) | set(long_avgs.keys())
        
        for feature in all_features:
            short_val = short_avgs.get(feature, 0)
            long_val = long_avgs.get(feature, 0)
            
            if long_val > 0:
                change_ratio = (short_val - long_val) / long_val
            elif short_val > 0:
                change_ratio = 1.0  # New feature
            else:
                continue
            
            feature_drift = {
                "feature": feature,
                "short_term_avg": round(short_val, 3),
                "long_term_avg": round(long_val, 3),
                "change_ratio": round(change_ratio, 3)
            }
            
            if change_ratio > DRIFT_THRESHOLD:
                emerging.append(feature_drift)
            elif change_ratio < -DRIFT_THRESHOLD:
                declining.append(feature_drift)
            else:
                stable.append(feature)
        
        # Detect suggestion preference drift
        short_accept = short_term.get("suggestions", {}).get("acceptance_rate", 0)
        long_accept = long_term.get("suggestions", {}).get("acceptance_rate", 0)
        
        suggestion_drift = None
        if long_accept > 0:
            accept_change = (short_accept - long_accept) / long_accept
            if abs(accept_change) > DRIFT_THRESHOLD:
                suggestion_drift = {
                    "short_term_rate": round(short_accept, 3),
                    "long_term_rate": round(long_accept, 3),
                    "change_ratio": round(accept_change, 3),
                    "direction": "increasing" if accept_change > 0 else "decreasing"
                }
        
        overall_drift = len(emerging) > 0 or len(declining) > 0 or suggestion_drift is not None
        
        return {
            "drift_detected": overall_drift,
            "emerging_features": emerging,
            "declining_features": declining,
            "stable_features": stable,
            "suggestion_preference_drift": suggestion_drift,
            "comparison": {
                "short_window": windows[0],
                "long_window": windows[-1]
            }
        }

    @staticmethod
    def _generate_window_insights(
        window_results: Dict[int, Dict],
        drift_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate insights from multi-window analysis."""
        insights = []
        
        # Drift-based insights
        if drift_analysis.get("drift_detected"):
            emerging = drift_analysis.get("emerging_features", [])
            declining = drift_analysis.get("declining_features", [])
            
            if emerging:
                top_emerging = emerging[0]
                insights.append({
                    "type": "emerging_pattern",
                    "severity": "info",
                    "message": f"'{top_emerging['feature']}' usage is increasing ({top_emerging['change_ratio']:.0%} vs long-term)",
                    "recommendation": f"Consider promoting '{top_emerging['feature']}' in the UI layout"
                })
            
            if declining:
                top_declining = declining[0]
                insights.append({
                    "type": "declining_pattern",
                    "severity": "info",
                    "message": f"'{top_declining['feature']}' usage is decreasing ({top_declining['change_ratio']:.0%} vs long-term)",
                    "recommendation": f"Consider demoting '{top_declining['feature']}' or investigating why usage dropped"
                })
            
            suggestion_drift = drift_analysis.get("suggestion_preference_drift")
            if suggestion_drift:
                direction = suggestion_drift["direction"]
                insights.append({
                    "type": "suggestion_drift",
                    "severity": "warning" if direction == "decreasing" else "info",
                    "message": f"AI suggestion acceptance is {direction} ({suggestion_drift['change_ratio']:.0%} change)",
                    "recommendation": "Review suggestion relevance and adjust density" if direction == "decreasing" else "Maintain current suggestion strategy"
                })
        else:
            insights.append({
                "type": "stable_patterns",
                "severity": "info",
                "message": "User behavior is stable across time windows",
                "recommendation": "Continue with current adaptation strategy"
            })
        
        # Data availability insights
        windows = sorted(window_results.keys())
        if len(windows) >= 2:
            short_data = window_results[windows[0]].get("data_points", 0)
            long_data = window_results[windows[-1]].get("data_points", 0)
            
            if short_data < 10:
                insights.append({
                    "type": "low_data",
                    "severity": "warning",
                    "message": f"Only {short_data} data points in recent {windows[0]} days",
                    "recommendation": "Analysis confidence is low - consider waiting for more data"
                })
        
        return insights

    @staticmethod
    def _calculate_analysis_confidence(
        window_results: Dict[int, Dict]
    ) -> Dict[str, Any]:
        """
        Calculate confidence in the analysis based on data availability.
        
        Higher confidence when:
        - More data points available
        - Data consistent across windows
        - No unusual patterns
        """
        total_data_points = 0
        window_scores = []
        
        for window, result in window_results.items():
            data_points = result.get("data_points", 0)
            total_data_points += data_points
            
            # Score based on data sufficiency for this window
            # Expect at least 5 actions per day for good confidence
            expected_min = window * 5
            window_score = min(data_points / expected_min, 1.0) if expected_min > 0 else 0
            window_scores.append(window_score)
        
        # Overall confidence
        avg_window_score = sum(window_scores) / len(window_scores) if window_scores else 0
        
        # Adjust for consistency
        if len(window_scores) >= 2:
            score_variance = sum((s - avg_window_score) ** 2 for s in window_scores) / len(window_scores)
            consistency_penalty = min(score_variance, 0.2)  # Max 20% penalty
            avg_window_score = max(0, avg_window_score - consistency_penalty)
        
        confidence_level = "high" if avg_window_score > 0.7 else "medium" if avg_window_score > 0.4 else "low"
        
        return {
            "overall_score": round(avg_window_score, 3),
            "level": confidence_level,
            "total_data_points": total_data_points,
            "window_scores": {
                w: round(s, 3) for w, s in zip(sorted(window_results.keys()), window_scores)
            }
        }

    @staticmethod
    def analyze_with_context(
        db: Session,
        user_id: UUID,
        context: Dict[str, Any],
        windows: List[int] = None
    ) -> Dict[str, Any]:
        """
        Context-aware multi-window analysis.
        
        Adjusts window sizes and weights based on context:
        - Role: Different windows for nurses vs doctors
        - Specialty: Specialty-specific patterns
        - Time of day: Morning vs evening patterns
        - Workload: High vs low activity periods
        """
        if windows is None:
            windows = DEFAULT_WINDOWS
        
        # Adjust weights based on context
        role = context.get("role", "clinician")
        specialty = context.get("specialty")
        
        # Custom weights based on role
        if role == "nurse":
            # Nurses may have more consistent daily patterns
            decay_weights = {7: 0.4, 30: 0.4, 90: 0.2}
        elif role == "researcher":
            # Researchers may need longer-term patterns
            decay_weights = {7: 0.3, 30: 0.3, 90: 0.4}
        else:
            decay_weights = DECAY_WEIGHTS
        
        # Run analysis
        analysis = MAPEKAnalyzeService.analyze_with_windows(
            db, user_id, patient_id=None, windows=windows, decay_weights=decay_weights
        )
        
        # Add context-specific insights
        analysis["context"] = context
        analysis["methodology"] = "context_aware_multi_window"
        
        return analysis

