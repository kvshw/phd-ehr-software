"""
Change Log Service
Phase 4: Ethics, Safety, and Transparency

Provides:
- Full provenance logging for all adaptations
- Who/what/why/when tracking
- User-visible change history
- Explanation generation
"""

from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import logging

logger = logging.getLogger(__name__)


class ChangeLogService:
    """
    Service for logging and retrieving adaptation changes.
    Provides full transparency and audit trail for MAPE-K adaptations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ==========================================
    # Logging Adaptations
    # ==========================================
    
    def log_adaptation(
        self,
        user_id: UUID,
        adaptation_type: str,
        old_state: Dict,
        new_state: Dict,
        explanation: str,
        trigger_reason: str = "automatic",
        confidence_score: float = 1.0,
        metrics_before: Optional[Dict] = None,
        feature_name: Optional[str] = None,
        auto_approved: bool = True,
        expires_at: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Log an adaptation with full provenance.
        
        This is called whenever MAPE-K makes an adaptation decision.
        Stores the complete context for transparency and audit.
        """
        query = text("""
            INSERT INTO adaptation_logs (
                user_id, adaptation_type, feature_name,
                old_state, new_state, explanation,
                trigger_reason, confidence_score,
                metrics_before, auto_approved,
                applied_at, expires_at
            ) VALUES (
                :user_id, :type, :feature,
                :old_state::jsonb, :new_state::jsonb, :explanation,
                :trigger, :confidence,
                :metrics::jsonb, :auto_approved,
                NOW(), :expires
            )
            RETURNING id, created_at, applied_at
        """)
        
        try:
            result = self.db.execute(query, {
                "user_id": str(user_id),
                "type": adaptation_type,
                "feature": feature_name,
                "old_state": json.dumps(old_state),
                "new_state": json.dumps(new_state),
                "explanation": explanation,
                "trigger": trigger_reason,
                "confidence": confidence_score,
                "metrics": json.dumps(metrics_before) if metrics_before else None,
                "auto_approved": auto_approved,
                "expires": expires_at
            })
            
            row = result.fetchone()
            self.db.commit()
            
            logger.info(f"Logged adaptation for user {user_id}: {adaptation_type}")
            
            return {
                "log_id": str(row.id),
                "user_id": str(user_id),
                "adaptation_type": adaptation_type,
                "feature_name": feature_name,
                "explanation": explanation,
                "created_at": row.created_at.isoformat(),
                "applied_at": row.applied_at.isoformat() if row.applied_at else None
            }
            
        except Exception as e:
            logger.error(f"Failed to log adaptation: {e}")
            self.db.rollback()
            raise
    
    def update_metrics_after(
        self,
        log_id: UUID,
        metrics_after: Dict[str, float]
    ) -> bool:
        """
        Update an adaptation log with post-adaptation metrics.
        Called after the adaptation has been applied and measured.
        """
        query = text("""
            UPDATE adaptation_logs
            SET metrics_after = :metrics::jsonb
            WHERE id = :log_id
        """)
        
        try:
            self.db.execute(query, {
                "log_id": str(log_id),
                "metrics": json.dumps(metrics_after)
            })
            self.db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
            return False
    
    def log_rollback(
        self,
        original_log_id: UUID,
        reason: str
    ) -> Dict[str, Any]:
        """
        Log a rollback of a previous adaptation.
        """
        # Get original adaptation
        original = self.get_adaptation_log(original_log_id)
        if not original:
            raise ValueError(f"Original adaptation {original_log_id} not found")
        
        # Create rollback log
        rollback_log = self.log_adaptation(
            user_id=UUID(original["user_id"]),
            adaptation_type=f"rollback_{original['adaptation_type']}",
            old_state=original["new_state"],
            new_state=original["old_state"],
            explanation=f"Rollback: {reason}",
            trigger_reason="rollback",
            confidence_score=1.0,
            feature_name=original.get("feature_name")
        )
        
        # Mark original as rolled back
        self.db.execute(text("""
            UPDATE adaptation_logs
            SET rolled_back_at = NOW(), rollback_reason = :reason
            WHERE id = :log_id
        """), {"log_id": str(original_log_id), "reason": reason})
        
        # Link rollback to original
        self.db.execute(text("""
            UPDATE adaptation_logs
            SET rollback_of = :original_id
            WHERE id = :rollback_id
        """), {
            "original_id": str(original_log_id),
            "rollback_id": rollback_log["log_id"]
        })
        
        self.db.commit()
        
        logger.info(f"Logged rollback of adaptation {original_log_id}")
        
        return rollback_log
    
    # ==========================================
    # Retrieving Logs
    # ==========================================
    
    def get_adaptation_log(self, log_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a specific adaptation log by ID."""
        query = text("""
            SELECT * FROM adaptation_logs WHERE id = :log_id
        """)
        
        result = self.db.execute(query, {"log_id": str(log_id)})
        row = result.fetchone()
        
        if not row:
            return None
        
        return self._row_to_dict(row)
    
    def get_user_adaptations(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
        adaptation_type: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get adaptation history for a user.
        Used for the change log drawer in the UI.
        """
        filters = ["user_id = :user_id"]
        params = {"user_id": str(user_id), "limit": limit, "offset": offset}
        
        if adaptation_type:
            filters.append("adaptation_type = :type")
            params["type"] = adaptation_type
        
        if since:
            filters.append("created_at >= :since")
            params["since"] = since
        
        query = text(f"""
            SELECT * FROM adaptation_logs
            WHERE {' AND '.join(filters)}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = self.db.execute(query, params)
        return [self._row_to_dict(row) for row in result.fetchall()]
    
    def get_recent_adaptations(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get recent adaptations across all users."""
        query = text("""
            SELECT al.*, u.email as user_email, u.role as user_role
            FROM adaptation_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE al.created_at > NOW() - INTERVAL '1 hour' * :hours
            ORDER BY al.created_at DESC
            LIMIT :limit
        """)
        
        result = self.db.execute(query, {"hours": hours, "limit": limit})
        return [self._row_to_dict(row) for row in result.fetchall()]
    
    def get_adaptation_statistics(
        self,
        user_id: Optional[UUID] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get adaptation statistics for a user or system-wide."""
        user_filter = "AND user_id = :user_id" if user_id else ""
        params = {"days": days}
        if user_id:
            params["user_id"] = str(user_id)
        
        query = text(f"""
            SELECT 
                adaptation_type,
                COUNT(*) as count,
                AVG(confidence_score) as avg_confidence,
                COUNT(*) FILTER (WHERE rolled_back_at IS NOT NULL) as rollback_count
            FROM adaptation_logs
            WHERE created_at > NOW() - INTERVAL '1 day' * :days
            {user_filter}
            GROUP BY adaptation_type
            ORDER BY count DESC
        """)
        
        result = self.db.execute(query, params)
        
        by_type = {}
        total_count = 0
        total_rollbacks = 0
        
        for row in result.fetchall():
            by_type[row.adaptation_type] = {
                "count": row.count,
                "avg_confidence": round(row.avg_confidence or 0, 2),
                "rollback_count": row.rollback_count
            }
            total_count += row.count
            total_rollbacks += row.rollback_count
        
        return {
            "period_days": days,
            "total_adaptations": total_count,
            "total_rollbacks": total_rollbacks,
            "rollback_rate": round(total_rollbacks / max(total_count, 1), 3),
            "by_type": by_type
        }
    
    # ==========================================
    # Explanation Generation
    # ==========================================
    
    def generate_explanation(
        self,
        adaptation_type: str,
        old_state: Dict,
        new_state: Dict,
        trigger_reason: str,
        metrics: Optional[Dict] = None
    ) -> str:
        """
        Generate a human-readable explanation for an adaptation.
        Used for transparency in the UI.
        """
        # Map adaptation types to explanation templates
        templates = {
            "dashboard_layout": self._explain_layout_change,
            "feature_promotion": self._explain_feature_promotion,
            "suggestion_density": self._explain_density_change,
            "alert_threshold": self._explain_threshold_change,
            "section_order": self._explain_section_reorder
        }
        
        if adaptation_type in templates:
            return templates[adaptation_type](old_state, new_state, metrics)
        
        # Generic explanation
        return f"The system adjusted your {adaptation_type.replace('_', ' ')} based on your usage patterns."
    
    def _explain_layout_change(
        self,
        old_state: Dict,
        new_state: Dict,
        metrics: Optional[Dict]
    ) -> str:
        """Explain dashboard layout changes."""
        changes = []
        
        if "sections" in old_state and "sections" in new_state:
            old_sections = old_state.get("sections", [])
            new_sections = new_state.get("sections", [])
            
            # Find promoted sections
            for i, section in enumerate(new_sections):
                if section in old_sections:
                    old_pos = old_sections.index(section)
                    if i < old_pos:
                        changes.append(f"'{section}' was moved up")
        
        if not changes:
            return "Your dashboard layout was optimized based on your usage patterns."
        
        return f"Layout adjusted: {', '.join(changes)}. This reflects your most frequently used features."
    
    def _explain_feature_promotion(
        self,
        old_state: Dict,
        new_state: Dict,
        metrics: Optional[Dict]
    ) -> str:
        """Explain feature promotion."""
        feature = new_state.get("feature_name", "this feature")
        usage_count = metrics.get("usage_count", 0) if metrics else 0
        daily_avg = metrics.get("daily_average", 0) if metrics else 0
        
        if usage_count > 0:
            return f"'{feature}' was promoted because you use it frequently ({usage_count} times, ~{daily_avg:.1f}/day on average)."
        
        return f"'{feature}' was promoted based on your usage patterns."
    
    def _explain_density_change(
        self,
        old_state: Dict,
        new_state: Dict,
        metrics: Optional[Dict]
    ) -> str:
        """Explain suggestion density changes."""
        old_density = old_state.get("density", "normal")
        new_density = new_state.get("density", "normal")
        
        density_names = {
            "low": "fewer",
            "normal": "a balanced number of",
            "high": "more"
        }
        
        return f"AI suggestions adjusted to show {density_names.get(new_density, new_density)} recommendations based on your interaction history."
    
    def _explain_threshold_change(
        self,
        old_state: Dict,
        new_state: Dict,
        metrics: Optional[Dict]
    ) -> str:
        """Explain alert threshold changes."""
        old_threshold = old_state.get("threshold", 0)
        new_threshold = new_state.get("threshold", 0)
        alert_type = new_state.get("alert_type", "alert")
        
        if new_threshold > old_threshold:
            direction = "raised"
            reason = "to reduce notification fatigue"
        else:
            direction = "lowered"
            reason = "to catch more important items"
        
        return f"The {alert_type} threshold was {direction} {reason}, based on your response patterns."
    
    def _explain_section_reorder(
        self,
        old_state: Dict,
        new_state: Dict,
        metrics: Optional[Dict]
    ) -> str:
        """Explain section reordering."""
        promoted = new_state.get("promoted_sections", [])
        
        if promoted:
            return f"Sections reordered: {', '.join(promoted)} moved to top based on your frequent access patterns."
        
        return "Dashboard sections were reordered to match your workflow."
    
    # ==========================================
    # User-Facing History
    # ==========================================
    
    def get_user_change_log(
        self,
        user_id: UUID,
        days: int = 30,
        include_explanations: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get a user-friendly change log for display in the UI.
        Groups changes by date and adds explanations.
        """
        adaptations = self.get_user_adaptations(
            user_id=user_id,
            limit=100,
            since=datetime.utcnow() - timedelta(days=days)
        )
        
        # Group by date
        by_date = {}
        for adapt in adaptations:
            date = adapt["created_at"][:10]  # YYYY-MM-DD
            if date not in by_date:
                by_date[date] = []
            
            entry = {
                "id": adapt["log_id"],
                "type": adapt["adaptation_type"],
                "feature": adapt.get("feature_name"),
                "time": adapt["created_at"],
                "confidence": adapt.get("confidence_score", 1.0),
                "was_rolled_back": adapt.get("rolled_back_at") is not None
            }
            
            if include_explanations:
                entry["explanation"] = adapt.get("explanation") or self.generate_explanation(
                    adapt["adaptation_type"],
                    adapt.get("old_state", {}),
                    adapt.get("new_state", {}),
                    adapt.get("trigger_reason", "automatic"),
                    adapt.get("metrics_before")
                )
            
            by_date[date].append(entry)
        
        # Convert to list format
        return [
            {"date": date, "changes": changes}
            for date, changes in sorted(by_date.items(), reverse=True)
        ]
    
    # ==========================================
    # Helper Methods
    # ==========================================
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        d = dict(row._mapping)
        
        # Convert UUIDs to strings
        for key in ["id", "user_id", "approved_by", "rollback_of"]:
            if key in d and d[key] is not None:
                d[key] = str(d[key])
        
        # Convert timestamps to ISO format
        for key in ["created_at", "applied_at", "expires_at", "rolled_back_at"]:
            if key in d and d[key] is not None:
                d[key] = d[key].isoformat()
        
        # Rename id to log_id for clarity
        if "id" in d:
            d["log_id"] = d.pop("id")
        
        return d

