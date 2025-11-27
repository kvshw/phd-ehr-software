"""
Learning Adaptation Engine
Learns from user feedback to improve AI suggestions and UI adaptations

This is a core component for the PhD research on self-adaptive AI-assisted EHR systems.
It implements a feedback loop that continuously improves the system based on clinician behavior.
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

class LearningEngine:
    """
    Learning engine that adapts AI suggestions based on user feedback patterns.
    
    Key capabilities:
    1. Track suggestion acceptance/rejection patterns
    2. Learn user preferences per specialty/role
    3. Adjust confidence thresholds based on historical accuracy
    4. Generate personalized suggestion rankings
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.learning_rate = 0.1  # How quickly to adapt (0-1)
        self.min_samples = 5  # Minimum feedback samples before learning
        
    def learn_from_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process new feedback and update learning model.
        
        Args:
            feedback_data: Contains suggestion_id, action, user_id, specialty, etc.
            
        Returns:
            Learning result with insights and adjustments
        """
        try:
            suggestion_id = feedback_data.get('suggestion_id')
            action = feedback_data.get('action')  # accept, ignore, not_relevant
            user_id = feedback_data.get('user_id')
            suggestion_type = feedback_data.get('suggestion_type')
            source = feedback_data.get('source')  # rules, ai_model, hybrid
            
            # Get user context (role, specialty)
            user_context = self._get_user_context(user_id)
            
            # Calculate learning signal
            learning_signal = self._calculate_learning_signal(action)
            
            # Update pattern database
            update_result = self._update_patterns(
                suggestion_type=suggestion_type,
                source=source,
                learning_signal=learning_signal,
                user_context=user_context
            )
            
            # Check if adaptation should be triggered
            adaptation_triggered = self._check_adaptation_threshold(user_id)
            
            result = {
                "processed": True,
                "learning_signal": learning_signal,
                "patterns_updated": update_result.get("patterns_updated", 0),
                "adaptation_triggered": adaptation_triggered,
                "insights": self._generate_insights(user_id)
            }
            
            logger.info(f"Learning engine processed feedback: {action} for suggestion {suggestion_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in learning engine: {str(e)}", exc_info=True)
            return {"processed": False, "error": str(e)}
    
    def _get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's role, specialty, and preferences from database"""
        try:
            result = self.db.execute(text("""
                SELECT role, specialty, preferences
                FROM users
                WHERE id = :user_id
            """), {"user_id": user_id})
            
            row = result.fetchone()
            if row:
                return {
                    "role": row[0],
                    "specialty": row[1],
                    "preferences": row[2] if row[2] else {}
                }
        except Exception:
            pass
        
        return {"role": "doctor", "specialty": None, "preferences": {}}
    
    def _calculate_learning_signal(self, action: str) -> float:
        """
        Convert user action to learning signal.
        
        accept -> +1.0 (positive reinforcement)
        ignore -> 0.0 (neutral)
        not_relevant -> -1.0 (negative reinforcement)
        """
        signals = {
            "accept": 1.0,
            "ignore": 0.0,
            "not_relevant": -1.0
        }
        return signals.get(action, 0.0)
    
    def _update_patterns(
        self,
        suggestion_type: Optional[str],
        source: Optional[str],
        learning_signal: float,
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update pattern database with new learning signal"""
        try:
            # Store learning event
            self.db.execute(text("""
                INSERT INTO learning_events 
                (suggestion_type, source, learning_signal, user_role, user_specialty, created_at)
                VALUES (:suggestion_type, :source, :learning_signal, :user_role, :user_specialty, NOW())
            """), {
                "suggestion_type": suggestion_type,
                "source": source,
                "learning_signal": learning_signal,
                "user_role": user_context.get("role"),
                "user_specialty": user_context.get("specialty")
            })
            self.db.commit()
            
            return {"patterns_updated": 1}
        except Exception as e:
            logger.warning(f"Could not store learning event: {str(e)}")
            return {"patterns_updated": 0}
    
    def _check_adaptation_threshold(self, user_id: str) -> bool:
        """
        Check if accumulated learning signals should trigger UI adaptation.
        
        Triggers adaptation when:
        - Accumulated negative signals exceed threshold
        - Usage pattern changes significantly
        - Preference drift detected
        """
        try:
            # Check recent feedback pattern
            result = self.db.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN action = 'not_relevant' THEN 1 ELSE 0 END) as not_relevant_count
                FROM feedback
                WHERE created_at > NOW() - INTERVAL '24 HOURS'
            """))
            
            row = result.fetchone()
            if row and row[0] > 10:  # Minimum feedback count
                not_relevant_ratio = row[1] / row[0] if row[0] > 0 else 0
                # Trigger adaptation if more than 30% suggestions marked as not relevant
                return not_relevant_ratio > 0.3
                
        except Exception:
            pass
        
        return False
    
    def _generate_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate actionable insights from learning data"""
        insights = []
        
        try:
            # Insight 1: Source preference
            result = self.db.execute(text("""
                SELECT 
                    s.source,
                    COUNT(*) as total,
                    SUM(CASE WHEN f.action = 'accept' THEN 1 ELSE 0 END) as accepted
                FROM feedback f
                JOIN suggestions s ON s.id = f.suggestion_id
                WHERE f.created_at > NOW() - INTERVAL '7 DAYS'
                GROUP BY s.source
            """))
            
            source_prefs = {}
            for row in result:
                if row[1] > 0:
                    acceptance_rate = row[2] / row[1]
                    source_prefs[row[0]] = acceptance_rate
            
            if source_prefs:
                best_source = max(source_prefs.items(), key=lambda x: x[1])
                insights.append({
                    "type": "source_preference",
                    "message": f"Users prefer {best_source[0]} suggestions ({best_source[1]*100:.0f}% acceptance)",
                    "recommendation": f"Prioritize {best_source[0]} in suggestion ranking"
                })
                
        except Exception as e:
            logger.warning(f"Could not generate insights: {str(e)}")
        
        return insights
    
    def get_personalized_ranking(
        self,
        user_id: str,
        suggestions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Rank suggestions based on learned user preferences.
        
        This is the core of the adaptive AI - suggestions are re-ranked
        based on what similar users/roles have accepted in the past.
        """
        user_context = self._get_user_context(user_id)
        
        # Get historical acceptance rates for this user's role/specialty
        acceptance_rates = self._get_acceptance_rates(
            role=user_context.get("role"),
            specialty=user_context.get("specialty")
        )
        
        # Adjust suggestion scores based on learned preferences
        for suggestion in suggestions:
            source = suggestion.get("source", "unknown")
            base_confidence = suggestion.get("confidence", 0.5)
            
            # Apply learned adjustment
            learned_boost = acceptance_rates.get(source, 0.0) * self.learning_rate
            adjusted_confidence = min(1.0, base_confidence + learned_boost)
            
            suggestion["adjusted_confidence"] = adjusted_confidence
            suggestion["learning_boost"] = learned_boost
        
        # Re-rank by adjusted confidence
        suggestions.sort(key=lambda x: x.get("adjusted_confidence", 0), reverse=True)
        
        return suggestions
    
    def _get_acceptance_rates(
        self,
        role: Optional[str],
        specialty: Optional[str]
    ) -> Dict[str, float]:
        """Get historical acceptance rates by source for given role/specialty"""
        rates = defaultdict(float)
        
        try:
            result = self.db.execute(text("""
                SELECT 
                    s.source,
                    COUNT(*) as total,
                    SUM(CASE WHEN f.action = 'accept' THEN 1 ELSE 0 END) as accepted
                FROM feedback f
                JOIN suggestions s ON s.id = f.suggestion_id
                JOIN users u ON u.id = f.user_id
                WHERE 
                    (u.role = :role OR :role IS NULL)
                    AND (u.specialty = :specialty OR :specialty IS NULL)
                    AND f.created_at > NOW() - INTERVAL '30 DAYS'
                GROUP BY s.source
                HAVING COUNT(*) >= :min_samples
            """), {
                "role": role,
                "specialty": specialty,
                "min_samples": self.min_samples
            })
            
            for row in result:
                if row[1] > 0:
                    rates[row[0]] = (row[2] / row[1]) - 0.5  # Center around 0
                    
        except Exception as e:
            logger.warning(f"Could not get acceptance rates: {str(e)}")
        
        return rates
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """
        Get overall learning metrics for research analysis.
        
        Returns metrics suitable for PhD thesis analysis.
        """
        metrics = {
            "total_feedback_processed": 0,
            "learning_events": 0,
            "acceptance_rate_by_source": {},
            "acceptance_rate_by_role": {},
            "adaptation_triggers": 0,
            "confidence_calibration": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Total feedback
            result = self.db.execute(text("SELECT COUNT(*) FROM feedback"))
            row = result.fetchone()
            metrics["total_feedback_processed"] = row[0] if row else 0
            
            # By source
            result = self.db.execute(text("""
                SELECT 
                    s.source,
                    COUNT(*) as total,
                    SUM(CASE WHEN f.action = 'accept' THEN 1 ELSE 0 END) as accepted,
                    AVG(CASE WHEN f.action = 'accept' THEN 1.0 ELSE 0.0 END) as rate
                FROM feedback f
                JOIN suggestions s ON s.id = f.suggestion_id
                GROUP BY s.source
            """))
            
            for row in result:
                metrics["acceptance_rate_by_source"][row[0]] = {
                    "total": row[1],
                    "accepted": row[2],
                    "rate": float(row[3]) if row[3] else 0.0
                }
                
            # Confidence calibration (are high-confidence suggestions actually accepted more?)
            result = self.db.execute(text("""
                SELECT 
                    CASE 
                        WHEN s.confidence >= 0.7 THEN 'high'
                        WHEN s.confidence >= 0.4 THEN 'medium'
                        ELSE 'low'
                    END as confidence_band,
                    AVG(CASE WHEN f.action = 'accept' THEN 1.0 ELSE 0.0 END) as acceptance_rate
                FROM feedback f
                JOIN suggestions s ON s.id = f.suggestion_id
                GROUP BY confidence_band
            """))
            
            for row in result:
                metrics["confidence_calibration"][row[0]] = float(row[1]) if row[1] else 0.0
                
        except Exception as e:
            logger.warning(f"Could not get learning metrics: {str(e)}")
        
        return metrics


# Singleton instance factory
def get_learning_engine(db: Session) -> LearningEngine:
    """Get a learning engine instance for the given database session"""
    return LearningEngine(db)

