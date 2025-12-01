"""
MAPE-K Plan Component
Generates JSON layout plans based on analysis results

Supports two planning strategies:
1. Rule-based (original): Simple heuristic rules
2. Bandit-based (new): Thompson Sampling for intelligent exploration/exploitation
"""
from typing import Dict, Any, List, Optional
from uuid import UUID
import os
import random
from sqlalchemy.orm import Session
from services.adaptation_service import AdaptationService
from schemas.adaptation import AdaptationPlan, AnalyzeResponse
import logging

logger = logging.getLogger(__name__)


# Configuration for A/B testing and planning strategy
class PlanningConfig:
    """Configuration for MAPE-K planning strategy"""
    
    # Enable bandit-based planning (set via env var or default)
    ENABLE_BANDIT = os.getenv("MAPE_K_ENABLE_BANDIT", "true").lower() == "true"
    
    # A/B testing: percentage of users to use bandit planning (0.0 to 1.0)
    BANDIT_AB_RATIO = float(os.getenv("MAPE_K_BANDIT_RATIO", "0.5"))
    
    # Force bandit for specific users (comma-separated UUIDs)
    FORCE_BANDIT_USERS = set(
        uid.strip() for uid in os.getenv("MAPE_K_FORCE_BANDIT_USERS", "").split(",") if uid.strip()
    )
    
    # Force rule-based for specific users
    FORCE_RULE_USERS = set(
        uid.strip() for uid in os.getenv("MAPE_K_FORCE_RULE_USERS", "").split(",") if uid.strip()
    )


class MAPEKPlanService:
    """Service for generating adaptation plans"""
    
    # Default section order
    DEFAULT_ORDER = [
        "summary",
        "demographics",
        "diagnoses",
        "medications",
        "allergies",
        "vitals",
        "labs",
        "imaging",
        "suggestions",
        "safety"
    ]
    
    # Knowledge base: Rules and thresholds
    KNOWLEDGE_BASE = {
        "navigation_threshold": 5,  # Minimum visits to consider a section frequently visited
        "ignore_rate_threshold": 0.5,  # If ignore rate > 50%, reduce suggestion density
        "acceptance_rate_threshold": 0.7,  # If acceptance rate > 70%, maintain or increase density
        "risk_escalation_threshold": 1,  # If risk escalations > 1, prioritize monitoring sections
    }
    
    @staticmethod
    def should_use_bandit(user_id: UUID) -> bool:
        """
        Determine whether to use bandit-based planning for this user.
        Supports A/B testing and per-user overrides.
        """
        if not PlanningConfig.ENABLE_BANDIT:
            return False
        
        user_str = str(user_id)
        
        # Check force overrides
        if user_str in PlanningConfig.FORCE_BANDIT_USERS:
            return True
        if user_str in PlanningConfig.FORCE_RULE_USERS:
            return False
        
        # A/B testing: use deterministic assignment based on user_id
        # This ensures same user always gets same treatment
        import hashlib
        hash_val = int(hashlib.md5(user_str.encode()).hexdigest()[:8], 16)
        assignment = (hash_val % 100) / 100.0
        
        return assignment < PlanningConfig.BANDIT_AB_RATIO
    
    @staticmethod
    def generate_plan_with_bandit(
        db: Session,
        user_id: UUID,
        patient_id: Optional[UUID],
        specialty: Optional[str] = None,
        analysis_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate plan using Thompson Sampling bandit algorithm.
        Falls back to rule-based if bandit fails.
        """
        try:
            from services.mape_k_plan_bandit import BanditPlanService
            
            bandit_service = BanditPlanService(db)
            
            # Generate bandit-based plan
            bandit_result = bandit_service.generate_plan(
                user_id=user_id,
                specialty=specialty,
            )
            
            # Convert to standard AdaptationPlan format
            plan = AdaptationPlan(
                order=bandit_result["order"],
                suggestion_density=bandit_result["plan"]["suggestion_density"],
                flags={
                    **bandit_result["plan"]["flags"],
                    "algorithm": "thompson_sampling",
                    "sampled_values": bandit_result["sampled_values"],
                },
                explanation=bandit_result["explanation"]
            )
            
            # Store adaptation in database
            from schemas.adaptation import AdaptationCreate
            adaptation = AdaptationService.create_adaptation(
                db,
                AdaptationCreate(
                    user_id=user_id,
                    patient_id=patient_id,
                    plan_json=plan
                )
            )
            
            logger.info(f"Bandit plan generated for user {user_id}: {bandit_result['actions']}")
            
            return {
                "plan": plan,
                "adaptation_id": str(adaptation.id),
                "explanation": bandit_result["explanation"],
                "algorithm": "thompson_sampling",
                "bandit_details": {
                    "sampled_values": bandit_result["sampled_values"],
                    "actions": bandit_result["actions"],
                    "constraints_applied": bandit_result["constraints_applied"],
                }
            }
            
        except Exception as e:
            logger.error(f"Bandit planning failed, falling back to rule-based: {e}")
            # Fall back to rule-based planning
            return MAPEKPlanService.generate_plan(
                db, user_id, patient_id, analysis_data
            )

    @staticmethod
    def generate_plan(
        db: Session,
        user_id: UUID,
        patient_id: Optional[UUID],
        analysis_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate an adaptation plan based on analysis
        
        Args:
            db: Database session
            user_id: User ID
            patient_id: Optional patient ID
            analysis_data: Pre-computed analysis data (optional)
        
        Returns:
            Dictionary containing the plan and explanation
        """
        # If no analysis data provided, we'll use defaults
        if not analysis_data:
            analysis_data = {
                "navigation_patterns": {},
                "suggestion_actions": {},
                "risk_changes": None,
                "recommendations": []
            }
        
        nav_analysis = analysis_data.get("navigation_patterns", {})
        suggestion_analysis = analysis_data.get("suggestion_actions", {})
        risk_analysis = analysis_data.get("risk_changes")
        recommendations = analysis_data.get("recommendations", [])
        
        # Start with default order
        section_order = MAPEKPlanService.DEFAULT_ORDER.copy()
        
        # Apply navigation-based adaptations
        section_order = MAPEKPlanService._apply_navigation_rules(
            section_order, nav_analysis
        )
        
        # Apply suggestion-based adaptations
        suggestion_density = MAPEKPlanService._determine_suggestion_density(
            suggestion_analysis
        )
        
        # Apply risk-based adaptations
        section_order = MAPEKPlanService._apply_risk_rules(
            section_order, risk_analysis
        )
        
        # Build flags
        flags = MAPEKPlanService._build_flags(
            nav_analysis, suggestion_analysis, risk_analysis
        )
        
        # Generate explanation
        explanation = MAPEKPlanService._generate_explanation(
            section_order, suggestion_density, recommendations
        )
        
        # Create plan
        plan = AdaptationPlan(
            order=section_order,
            suggestion_density=suggestion_density,
            flags=flags,
            explanation=explanation
        )
        
        # Store adaptation in database
        from schemas.adaptation import AdaptationCreate
        adaptation = AdaptationService.create_adaptation(
            db,
            AdaptationCreate(
                user_id=user_id,
                patient_id=patient_id,
                plan_json=plan
            )
        )
        
        return {
            "plan": plan,
            "adaptation_id": str(adaptation.id),
            "explanation": explanation
        }

    @staticmethod
    def _apply_navigation_rules(
        section_order: List[str],
        nav_analysis: Dict[str, Any]
    ) -> List[str]:
        """Apply rules based on navigation patterns"""
        section_visits = nav_analysis.get("section_visits", {})
        most_visited = nav_analysis.get("most_visited")
        threshold = MAPEKPlanService.KNOWLEDGE_BASE["navigation_threshold"]
        
        # If a section is frequently visited, move it up
        if most_visited and most_visited in section_order:
            visits = section_visits.get(most_visited, 0)
            if visits >= threshold:
                # Remove from current position
                section_order.remove(most_visited)
                # Insert after summary (position 1) or at position 2
                insert_pos = min(2, len(section_order))
                section_order.insert(insert_pos, most_visited)
        
        return section_order

    @staticmethod
    def _determine_suggestion_density(
        suggestion_analysis: Dict[str, Any]
    ) -> str:
        """Determine suggestion density based on interaction patterns"""
        ignore_rate = suggestion_analysis.get("ignore_rate", 0.0)
        acceptance_rate = suggestion_analysis.get("acceptance_rate", 0.0)
        threshold = MAPEKPlanService.KNOWLEDGE_BASE["ignore_rate_threshold"]
        acceptance_threshold = MAPEKPlanService.KNOWLEDGE_BASE["acceptance_rate_threshold"]
        
        if ignore_rate > threshold:
            return "low"
        elif acceptance_rate > acceptance_threshold:
            return "high"
        else:
            return "medium"

    @staticmethod
    def _apply_risk_rules(
        section_order: List[str],
        risk_analysis: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Apply rules based on risk changes"""
        if not risk_analysis:
            return section_order
        
        escalations = risk_analysis.get("escalations", 0)
        threshold = MAPEKPlanService.KNOWLEDGE_BASE["risk_escalation_threshold"]
        
        if escalations >= threshold:
            # Prioritize vitals and imaging sections
            priority_sections = ["vitals", "imaging"]
            for section in priority_sections:
                if section in section_order:
                    section_order.remove(section)
                    # Insert after summary
                    insert_pos = min(2, len(section_order))
                    section_order.insert(insert_pos, section)
        
        return section_order

    @staticmethod
    def _build_flags(
        nav_analysis: Dict[str, Any],
        suggestion_analysis: Dict[str, Any],
        risk_analysis: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build flags for the adaptation plan"""
        flags = {}
        
        most_visited = nav_analysis.get("most_visited")
        if most_visited:
            flags["prioritized_section"] = most_visited
        
        ignore_rate = suggestion_analysis.get("ignore_rate", 0.0)
        if ignore_rate > 0.5:
            flags["high_ignore_rate"] = True
        
        if risk_analysis:
            escalations = risk_analysis.get("escalations", 0)
            if escalations > 0:
                flags["risk_escalated"] = True
                flags["escalation_count"] = escalations
        
        return flags

    @staticmethod
    def _generate_explanation(
        section_order: List[str],
        suggestion_density: str,
        recommendations: List[str]
    ) -> str:
        """Generate human-readable explanation of the adaptation"""
        parts = []
        
        # Explain section ordering
        if section_order != MAPEKPlanService.DEFAULT_ORDER:
            parts.append(f"Sections reordered based on usage patterns: {', '.join(section_order[:3])} prioritized")
        
        # Explain suggestion density
        if suggestion_density == "low":
            parts.append("Suggestion frequency reduced due to high ignore rate")
        elif suggestion_density == "high":
            parts.append("Suggestion frequency maintained/increased due to high acceptance rate")
        
        # Add recommendations
        if recommendations:
            parts.append("Recommendations: " + "; ".join(recommendations))
        
        return ". ".join(parts) if parts else "Standard layout maintained"

    @staticmethod
    def generate_dashboard_plan(
        db: Session,
        user_id: UUID,
        dashboard_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate dashboard layout plan based on usage analysis
        
        Returns JSON plan for dashboard adaptation
        """
        from services.mape_k_analyze import MAPEKAnalyzeService
        from models.user import User
        
        if not dashboard_analysis:
            dashboard_analysis = MAPEKAnalyzeService.analyze_dashboard_usage(db, user_id)
        
        feature_freqs = dashboard_analysis.get("feature_frequencies", {})
        feature_daily_avgs = dashboard_analysis.get("feature_daily_averages", {})
        most_used = dashboard_analysis.get("most_used_features", [])
        least_used = dashboard_analysis.get("least_used_features", [])
        
        # Get user specialty for defaults
        user = db.query(User).filter(User.id == user_id).first()
        specialty = user.specialty if user else None
        
        # Build feature priority list
        feature_priority = []
        position = 1
        
        # Add most used features first
        for feature_id in most_used:
            frequency = feature_freqs.get(feature_id, 0)
            daily_avg = feature_daily_avgs.get(feature_id, 0)
            
            # Determine size based on daily average
            if daily_avg > 15:  # Used >15 times per day
                size = "large"
            elif daily_avg > 8:
                size = "medium"
            elif daily_avg > 3:
                size = "small"
            else:
                size = "small"
            
            feature_priority.append({
                "id": feature_id,
                "position": position,
                "size": size,
                "usage_count": frequency,
                "daily_average": round(daily_avg, 1)
            })
            position += 1
        
        # Add specialty defaults for features not yet used (if we have < 4 features)
        if len(feature_priority) < 4:
            specialty_defaults = MAPEKPlanService._get_specialty_default_features(specialty)
            for feature_id in specialty_defaults:
                if feature_id not in [f["id"] for f in feature_priority]:
                    feature_priority.append({
                        "id": feature_id,
                        "position": position,
                        "size": "medium",
                        "usage_count": 0,
                        "daily_average": 0,
                        "source": "specialty_default"
                    })
                    position += 1
                    if len(feature_priority) >= 4:
                        break
        
        # Build quick stats based on specialty and usage
        quick_stats = MAPEKPlanService._determine_relevant_stats(specialty, feature_freqs)
        
        # Patient list adaptations
        patient_list_config = {
            "sort_by": "relevance",  # relevance, recent, name
            "default_filters": MAPEKPlanService._get_specialty_filters(specialty),
            "items_per_page": 10
        }
        
        # Generate explanation
        explanation = MAPEKPlanService._generate_dashboard_explanation(
            feature_freqs, feature_daily_avgs, specialty
        )
        
        return {
            "plan_type": "dashboard",
            "version": "1.0",
            "feature_priority": feature_priority,
            "hidden_features": least_used[:3] if least_used else [],  # Hide bottom 3
            "quick_stats": quick_stats,
            "patient_list": patient_list_config,
            "explanation": explanation
        }

    @staticmethod
    def _get_specialty_default_features(specialty: Optional[str]) -> List[str]:
        """Get default features for a specialty (includes navigation items)"""
        defaults = {
            "cardiology": [
                "ecg_review", "bp_trends", "cv_risk", "patient_search",
                "dashboard_overview", "lab_results", "clinical_notes", "medications"
            ],
            "neurology": [
                "mri_review", "neuro_exam", "cognitive_tests", "patient_history",
                "dashboard_overview", "imaging_documents", "clinical_notes", "lab_results"
            ],
            "psychiatry": [
                "mse", "phq9", "gad7", "medications",
                "dashboard_overview", "clinical_notes", "medications", "appointments_schedule"
            ],
            "pediatrics": [
                "growth_chart", "vaccines", "development", "nutrition",
                "dashboard_overview", "clinical_notes", "lab_results", "appointments_schedule"
            ],
            "emergency": [
                "triage", "vitals", "safety_alerts", "patient_search",
                "dashboard_overview", "clinical_notes", "lab_results", "imaging_documents"
            ],
            "internal": [
                "history", "labs", "imaging", "consults",
                "dashboard_overview", "lab_results", "imaging_documents", "clinical_notes"
            ],
            "general": [
                "checkup", "vitals", "labs", "referral",
                "dashboard_overview", "clinical_notes", "lab_results", "medications"
            ],
        }
        return defaults.get(specialty or "general", defaults["general"])

    @staticmethod
    def _determine_relevant_stats(specialty: Optional[str], feature_freqs: Dict[str, int]) -> List[str]:
        """Determine relevant quick stats based on specialty and usage"""
        specialty_stats = {
            "cardiology": ["cardiac_patients", "pending_ecgs", "high_bp_alerts"],
            "neurology": ["neurological_patients", "pending_mris", "cognitive_assessments"],
            "psychiatry": ["psychiatric_patients", "pending_assessments", "medication_reviews"],
            "pediatrics": ["pediatric_patients", "vaccination_due", "growth_checks"],
            "emergency": ["triage_queue", "critical_alerts", "active_cases"],
            "internal": ["internal_patients", "pending_labs", "consult_requests"],
            "general": ["total_patients", "today_appointments", "pending_tasks"],
        }
        
        # Start with specialty defaults
        stats = specialty_stats.get(specialty or "general", specialty_stats["general"])
        
        # Adjust based on actual usage
        if "ecg_review" in feature_freqs and feature_freqs["ecg_review"] > 10:
            if "pending_ecgs" not in stats:
                stats.insert(0, "pending_ecgs")
        
        return stats[:3]  # Return top 3

    @staticmethod
    def _get_specialty_filters(specialty: Optional[str]) -> List[str]:
        """Get default filters for a specialty"""
        filters = {
            "cardiology": ["cardiac_conditions", "high_bp", "heart_failure"],
            "neurology": ["neurological_conditions", "stroke", "headache"],
            "psychiatry": ["psychiatric_conditions", "depression", "anxiety"],
            "pediatrics": ["pediatric_age", "vaccination_status"],
            "emergency": ["triage_level", "critical"],
            "internal": ["internal_medicine", "chronic_disease"],
            "general": [],
        }
        return filters.get(specialty or "general", [])

    @staticmethod
    def _generate_dashboard_explanation(
        feature_freqs: Dict[str, int],
        feature_daily_avgs: Dict[str, float],
        specialty: Optional[str]
    ) -> str:
        """Generate human-readable explanation of dashboard adaptation"""
        if not feature_freqs:
            if specialty:
                return f"Dashboard configured for {specialty} specialty. Start using features to personalize further."
            return "Dashboard using default layout. Use features to enable personalization."
        
        # Find top feature
        top_feature = max(feature_freqs.items(), key=lambda x: x[1])
        top_daily_avg = feature_daily_avgs.get(top_feature[0], 0)
        
        parts = []
        parts.append(f"Dashboard optimized based on your workflow")
        
        if top_daily_avg > 10:
            parts.append(f"{top_feature[0].replace('_', ' ').title()} promoted (used {round(top_daily_avg)}x/day)")
        
        if len(feature_freqs) > 3:
            parts.append(f"Top {min(3, len(feature_freqs))} features prioritized")
        
        if specialty:
            parts.append(f"Specialty: {specialty}")
        
        return ". ".join(parts)

