"""
MAPE-K Analyze Component
Analyzes collected monitoring data to determine what adaptations are needed
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from services.user_action_service import UserActionService


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

