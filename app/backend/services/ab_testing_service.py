"""
A/B Testing Service

Support for rigorous research study designs:
- Random assignment to conditions
- Crossover support (A/B/BA within-subjects design)
- Counterbalancing
- Sequential analysis (stop early if large benefit)
- Mixed-effects model data export

Part of Phase 8: Research Design & Metrics
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import logging
import math
import random
import hashlib
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, text

logger = logging.getLogger(__name__)


class StudyDesign(str, Enum):
    """Study design types."""
    BETWEEN_SUBJECTS = "between_subjects"  # Different users in each condition
    WITHIN_SUBJECTS = "within_subjects"    # Same users experience both conditions (crossover)
    MIXED = "mixed"                         # Combination


class Condition(str, Enum):
    """Study conditions."""
    A = "A"  # Control (baseline/rule-based)
    B = "B"  # Treatment (adaptive/bandit)


class ABTestingService:
    """
    Service for managing A/B testing and research studies.
    
    Supports:
    - Randomized controlled trials
    - Crossover designs (ABA, BAB)
    - Sequential analysis
    - Data export for statistical analysis
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # Study Management
    # =========================================================================
    
    def create_study(
        self,
        study_id: str,
        name: str,
        description: str,
        design: StudyDesign,
        conditions: List[str] = None,
        config: Dict[str, Any] = None,
        created_by: UUID = None
    ) -> Dict[str, Any]:
        """
        Create a new research study.
        
        Args:
            study_id: Unique study identifier
            name: Study name
            description: Study description
            design: Study design type
            conditions: List of conditions (default: ["A", "B"])
            config: Study configuration
            created_by: User creating the study
        
        Returns:
            Created study details
        """
        try:
            import json
            
            if conditions is None:
                conditions = ["A", "B"]
            
            default_config = {
                "phase_duration_days": 14,
                "washout_days": 0,
                "min_participants_per_condition": 30,
                "sequential_analysis": True,
                "alpha": 0.05,
                "power": 0.80,
                "min_detectable_effect": 0.2
            }
            
            if config:
                default_config.update(config)
            
            query = text("""
                INSERT INTO studies (
                    id, name, description, design, conditions, config,
                    status, created_by, created_at
                ) VALUES (
                    :id, :name, :description, :design, :conditions, :config,
                    'draft', :created_by, :created_at
                )
            """)
            
            self.db.execute(query, {
                "id": study_id,
                "name": name,
                "description": description,
                "design": design.value,
                "conditions": json.dumps(conditions),
                "config": json.dumps(default_config),
                "created_by": str(created_by) if created_by else None,
                "created_at": datetime.utcnow()
            })
            self.db.commit()
            
            return {
                "study_id": study_id,
                "name": name,
                "design": design.value,
                "conditions": conditions,
                "config": default_config,
                "status": "draft"
            }
            
        except Exception as e:
            logger.error(f"Error creating study: {e}")
            self.db.rollback()
            raise
    
    def start_study(self, study_id: str) -> Dict[str, Any]:
        """Start a study (change status from draft to active)."""
        try:
            query = text("""
                UPDATE studies
                SET status = 'active', started_at = :started_at
                WHERE id = :study_id AND status = 'draft'
            """)
            
            self.db.execute(query, {
                "study_id": study_id,
                "started_at": datetime.utcnow()
            })
            self.db.commit()
            
            return {"study_id": study_id, "status": "active"}
            
        except Exception as e:
            logger.error(f"Error starting study: {e}")
            self.db.rollback()
            raise
    
    def end_study(self, study_id: str) -> Dict[str, Any]:
        """End a study."""
        try:
            query = text("""
                UPDATE studies
                SET status = 'completed', ended_at = :ended_at
                WHERE id = :study_id AND status = 'active'
            """)
            
            self.db.execute(query, {
                "study_id": study_id,
                "ended_at": datetime.utcnow()
            })
            self.db.commit()
            
            return {"study_id": study_id, "status": "completed"}
            
        except Exception as e:
            logger.error(f"Error ending study: {e}")
            self.db.rollback()
            raise
    
    def get_study(self, study_id: str) -> Optional[Dict[str, Any]]:
        """Get study details."""
        try:
            import json
            
            query = text("""
                SELECT * FROM studies WHERE id = :study_id
            """)
            
            result = self.db.execute(query, {"study_id": study_id}).fetchone()
            
            if not result:
                return None
            
            row = dict(result._mapping)
            
            # Parse JSON fields
            for field in ["conditions", "config"]:
                if field in row and row[field]:
                    if isinstance(row[field], str):
                        row[field] = json.loads(row[field])
            
            return row
            
        except Exception as e:
            logger.error(f"Error getting study: {e}")
            return None
    
    # =========================================================================
    # Condition Assignment
    # =========================================================================
    
    def assign_condition(
        self,
        user_id: UUID,
        study_id: str,
        force_condition: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assign user to a study condition.
        
        Uses stratified randomization to balance conditions.
        For within-subjects, assigns to initial condition.
        
        Args:
            user_id: User to assign
            study_id: Study ID
            force_condition: Force specific condition (for testing)
        
        Returns:
            Assignment details
        """
        try:
            import json
            
            # Check if already assigned
            existing_query = text("""
                SELECT condition, phase, assigned_at
                FROM study_assignments
                WHERE user_id = :user_id AND study_id = :study_id
                ORDER BY assigned_at DESC
                LIMIT 1
            """)
            
            existing = self.db.execute(existing_query, {
                "user_id": str(user_id),
                "study_id": study_id
            }).fetchone()
            
            if existing:
                return {
                    "status": "already_assigned",
                    "user_id": str(user_id),
                    "study_id": study_id,
                    "condition": existing.condition,
                    "phase": existing.phase,
                    "assigned_at": existing.assigned_at.isoformat() if existing.assigned_at else None
                }
            
            # Get study details
            study = self.get_study(study_id)
            if not study:
                raise ValueError(f"Study {study_id} not found")
            
            if study["status"] != "active":
                raise ValueError(f"Study {study_id} is not active")
            
            conditions = study.get("conditions", ["A", "B"])
            design = study.get("design", "between_subjects")
            
            # Determine condition
            if force_condition and force_condition in conditions:
                condition = force_condition
            else:
                condition = self._randomize_condition(study_id, conditions)
            
            # For within-subjects, determine order (ABA or BAB)
            order = None
            if design == StudyDesign.WITHIN_SUBJECTS.value:
                order = self._determine_crossover_order(study_id, conditions)
                condition = order[0]  # Start with first condition in order
            
            # Create assignment
            query = text("""
                INSERT INTO study_assignments (
                    user_id, study_id, condition, phase, crossover_order,
                    assigned_at
                ) VALUES (
                    :user_id, :study_id, :condition, 1, :crossover_order,
                    :assigned_at
                )
            """)
            
            self.db.execute(query, {
                "user_id": str(user_id),
                "study_id": study_id,
                "condition": condition,
                "crossover_order": json.dumps(order) if order else None,
                "assigned_at": datetime.utcnow()
            })
            self.db.commit()
            
            return {
                "status": "assigned",
                "user_id": str(user_id),
                "study_id": study_id,
                "condition": condition,
                "phase": 1,
                "crossover_order": order,
                "assigned_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error assigning condition: {e}")
            self.db.rollback()
            raise
    
    def _randomize_condition(
        self,
        study_id: str,
        conditions: List[str]
    ) -> str:
        """
        Randomize condition with stratified balancing.
        
        Assigns to the condition with fewer participants to maintain balance.
        """
        try:
            # Count current assignments per condition
            query = text("""
                SELECT condition, COUNT(*) as count
                FROM study_assignments
                WHERE study_id = :study_id
                GROUP BY condition
            """)
            
            result = self.db.execute(query, {"study_id": study_id})
            
            counts = {c: 0 for c in conditions}
            for row in result:
                if row.condition in counts:
                    counts[row.condition] = row.count
            
            # Find minimum count
            min_count = min(counts.values())
            
            # Conditions with minimum count
            min_conditions = [c for c, count in counts.items() if count == min_count]
            
            # Random selection among minimum conditions
            return random.choice(min_conditions)
            
        except Exception as e:
            logger.warning(f"Error in stratified randomization: {e}")
            return random.choice(conditions)
    
    def _determine_crossover_order(
        self,
        study_id: str,
        conditions: List[str]
    ) -> List[str]:
        """
        Determine crossover order for within-subjects design.
        
        Counterbalances AB and BA sequences.
        """
        try:
            # Count current orders
            query = text("""
                SELECT crossover_order, COUNT(*) as count
                FROM study_assignments
                WHERE study_id = :study_id
                  AND crossover_order IS NOT NULL
                GROUP BY crossover_order
            """)
            
            result = self.db.execute(query, {"study_id": study_id})
            
            # Define possible orders
            orders = [
                conditions,                          # [A, B]
                list(reversed(conditions))           # [B, A]
            ]
            
            order_counts = {str(o): 0 for o in orders}
            
            import json
            for row in result:
                order_str = row.crossover_order
                if order_str in order_counts:
                    order_counts[order_str] = row.count
            
            # Select order with fewer assignments
            min_count = min(order_counts.values())
            min_orders = [json.loads(o) for o, c in order_counts.items() if c == min_count]
            
            return random.choice(min_orders)
            
        except Exception as e:
            logger.warning(f"Error determining crossover order: {e}")
            return conditions if random.random() < 0.5 else list(reversed(conditions))
    
    # =========================================================================
    # Crossover Support
    # =========================================================================
    
    def crossover(
        self,
        user_id: UUID,
        study_id: str
    ) -> Dict[str, Any]:
        """
        Switch user to next condition in crossover design.
        
        Args:
            user_id: User to crossover
            study_id: Study ID
        
        Returns:
            New condition details
        """
        try:
            import json
            
            # Get current assignment
            query = text("""
                SELECT condition, phase, crossover_order, assigned_at
                FROM study_assignments
                WHERE user_id = :user_id AND study_id = :study_id
                ORDER BY assigned_at DESC
                LIMIT 1
            """)
            
            current = self.db.execute(query, {
                "user_id": str(user_id),
                "study_id": study_id
            }).fetchone()
            
            if not current:
                raise ValueError(f"User {user_id} not assigned to study {study_id}")
            
            current_condition = current.condition
            current_phase = current.phase
            crossover_order = current.crossover_order
            
            if crossover_order:
                if isinstance(crossover_order, str):
                    crossover_order = json.loads(crossover_order)
            else:
                # Get study conditions
                study = self.get_study(study_id)
                crossover_order = study.get("conditions", ["A", "B"])
            
            # Determine next condition
            if current_phase >= len(crossover_order):
                return {
                    "status": "completed",
                    "message": "User has completed all phases",
                    "user_id": str(user_id),
                    "study_id": study_id,
                    "final_phase": current_phase
                }
            
            new_condition = crossover_order[current_phase]  # phase is 1-indexed, list is 0-indexed
            new_phase = current_phase + 1
            
            # Record crossover
            insert_query = text("""
                INSERT INTO study_assignments (
                    user_id, study_id, condition, phase, crossover_order,
                    assigned_at, previous_condition, crossover_from_phase
                ) VALUES (
                    :user_id, :study_id, :condition, :phase, :crossover_order,
                    :assigned_at, :previous_condition, :crossover_from_phase
                )
            """)
            
            self.db.execute(insert_query, {
                "user_id": str(user_id),
                "study_id": study_id,
                "condition": new_condition,
                "phase": new_phase,
                "crossover_order": json.dumps(crossover_order),
                "assigned_at": datetime.utcnow(),
                "previous_condition": current_condition,
                "crossover_from_phase": current_phase
            })
            self.db.commit()
            
            return {
                "status": "crossed_over",
                "user_id": str(user_id),
                "study_id": study_id,
                "previous_condition": current_condition,
                "new_condition": new_condition,
                "phase": new_phase,
                "total_phases": len(crossover_order),
                "crossover_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in crossover: {e}")
            self.db.rollback()
            raise
    
    def get_user_condition(
        self,
        user_id: UUID,
        study_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get user's current condition in a study."""
        try:
            query = text("""
                SELECT condition, phase, crossover_order, assigned_at
                FROM study_assignments
                WHERE user_id = :user_id AND study_id = :study_id
                ORDER BY assigned_at DESC
                LIMIT 1
            """)
            
            result = self.db.execute(query, {
                "user_id": str(user_id),
                "study_id": study_id
            }).fetchone()
            
            if not result:
                return None
            
            import json
            return {
                "user_id": str(user_id),
                "study_id": study_id,
                "condition": result.condition,
                "phase": result.phase,
                "crossover_order": json.loads(result.crossover_order) if result.crossover_order else None,
                "assigned_at": result.assigned_at.isoformat() if result.assigned_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting user condition: {e}")
            return None
    
    def should_use_adaptive(
        self,
        user_id: UUID,
        study_id: str
    ) -> bool:
        """
        Check if user should receive adaptive treatment.
        
        Typically: Condition B = adaptive, Condition A = control
        """
        assignment = self.get_user_condition(user_id, study_id)
        
        if not assignment:
            return False
        
        # B is typically the treatment (adaptive) condition
        return assignment.get("condition") == "B"
    
    # =========================================================================
    # Sequential Analysis
    # =========================================================================
    
    def check_sequential_stopping(
        self,
        study_id: str,
        primary_outcome: str = "acceptance_rate"
    ) -> Dict[str, Any]:
        """
        Check if study can be stopped early based on sequential analysis.
        
        Uses O'Brien-Fleming spending function for alpha adjustment.
        
        Args:
            study_id: Study to check
            primary_outcome: Primary outcome metric
        
        Returns:
            Sequential analysis results
        """
        try:
            study = self.get_study(study_id)
            if not study:
                raise ValueError(f"Study {study_id} not found")
            
            config = study.get("config", {})
            alpha = config.get("alpha", 0.05)
            min_effect = config.get("min_detectable_effect", 0.2)
            
            # Get outcome data by condition
            query = text("""
                SELECT 
                    sa.condition,
                    COUNT(DISTINCT sa.user_id) as n,
                    AVG(CASE WHEN ua.metadata->>'action' = 'accept' THEN 1.0 ELSE 0.0 END) as outcome_mean
                FROM study_assignments sa
                LEFT JOIN user_actions ua ON sa.user_id = ua.user_id::text
                    AND ua.action_type = 'suggestion_response'
                    AND ua.timestamp >= sa.assigned_at
                WHERE sa.study_id = :study_id
                GROUP BY sa.condition
            """)
            
            result = self.db.execute(query, {"study_id": study_id})
            
            condition_data = {}
            for row in result:
                condition_data[row.condition] = {
                    "n": row.n,
                    "mean": float(row.outcome_mean) if row.outcome_mean else 0.5
                }
            
            if len(condition_data) < 2:
                return {
                    "can_stop": False,
                    "reason": "Insufficient conditions with data"
                }
            
            # Calculate effect size (Cohen's d approximation)
            cond_a = condition_data.get("A", {"n": 0, "mean": 0.5})
            cond_b = condition_data.get("B", {"n": 0, "mean": 0.5})
            
            n_a, n_b = cond_a["n"], cond_b["n"]
            mean_a, mean_b = cond_a["mean"], cond_b["mean"]
            
            if n_a < 10 or n_b < 10:
                return {
                    "can_stop": False,
                    "reason": "Insufficient sample size",
                    "n_a": n_a,
                    "n_b": n_b
                }
            
            # Simple effect size calculation
            effect_diff = mean_b - mean_a
            pooled_std = 0.5  # Approximate for proportions
            effect_size = effect_diff / pooled_std if pooled_std > 0 else 0
            
            # O'Brien-Fleming adjusted alpha (simplified)
            # At 50% information, adjusted alpha ≈ 0.003
            # At 75% information, adjusted alpha ≈ 0.019
            min_n = config.get("min_participants_per_condition", 30)
            information_fraction = min(n_a, n_b) / min_n
            
            if information_fraction < 0.5:
                adjusted_alpha = 0.001
            elif information_fraction < 0.75:
                adjusted_alpha = 0.01
            else:
                adjusted_alpha = alpha
            
            # Calculate Z-score
            se = math.sqrt((mean_a * (1 - mean_a) / n_a) + (mean_b * (1 - mean_b) / n_b))
            z_score = abs(effect_diff) / se if se > 0 else 0
            
            # Critical value for adjusted alpha
            # Using normal approximation
            critical_values = {0.001: 3.29, 0.01: 2.58, 0.05: 1.96}
            critical_z = critical_values.get(adjusted_alpha, 1.96)
            
            can_stop = z_score > critical_z
            
            # Determine recommendation
            if can_stop:
                if effect_diff > 0:
                    recommendation = "Stop: Treatment (B) significantly better"
                else:
                    recommendation = "Stop: Control (A) significantly better"
            else:
                recommendation = "Continue: No significant difference yet"
            
            return {
                "can_stop": can_stop,
                "recommendation": recommendation,
                "effect_size": round(effect_size, 3),
                "effect_difference": round(effect_diff, 3),
                "z_score": round(z_score, 3),
                "critical_z": critical_z,
                "adjusted_alpha": adjusted_alpha,
                "information_fraction": round(information_fraction, 2),
                "condition_a": {"n": n_a, "mean": round(mean_a, 3)},
                "condition_b": {"n": n_b, "mean": round(mean_b, 3)}
            }
            
        except Exception as e:
            logger.error(f"Error in sequential analysis: {e}")
            return {"error": str(e)}
    
    # =========================================================================
    # Data Export
    # =========================================================================
    
    def export_for_analysis(
        self,
        study_id: str,
        include_covariates: bool = True
    ) -> Dict[str, Any]:
        """
        Export study data for statistical analysis.
        
        Exports data suitable for mixed-effects models:
        - outcome, condition, user_id, day, phase, covariates
        
        Args:
            study_id: Study to export
            include_covariates: Include user covariates
        
        Returns:
            Data ready for analysis
        """
        try:
            # Build export query
            query = text("""
                SELECT 
                    sa.user_id,
                    sa.condition,
                    sa.phase,
                    sa.assigned_at,
                    DATE(ua.timestamp) as date,
                    DATE(ua.timestamp) - DATE(sa.assigned_at) as day_in_phase,
                    ua.action_type,
                    ua.metadata,
                    CASE WHEN ua.metadata->>'action' = 'accept' THEN 1 ELSE 0 END as accepted
                FROM study_assignments sa
                LEFT JOIN user_actions ua ON sa.user_id = ua.user_id::text
                    AND ua.timestamp >= sa.assigned_at
                    AND ua.action_type = 'suggestion_response'
                WHERE sa.study_id = :study_id
                ORDER BY sa.user_id, sa.phase, ua.timestamp
            """)
            
            result = self.db.execute(query, {"study_id": study_id})
            
            rows = []
            for row in result:
                row_dict = {
                    "user_id": row.user_id,
                    "condition": row.condition,
                    "phase": row.phase,
                    "day_in_phase": row.day_in_phase,
                    "date": row.date.isoformat() if row.date else None,
                    "accepted": row.accepted
                }
                rows.append(row_dict)
            
            # Get user covariates if requested
            covariates = {}
            if include_covariates:
                cov_query = text("""
                    SELECT DISTINCT sa.user_id, u.role, u.specialty
                    FROM study_assignments sa
                    JOIN users u ON sa.user_id = u.id::text
                    WHERE sa.study_id = :study_id
                """)
                
                cov_result = self.db.execute(cov_query, {"study_id": study_id})
                
                for row in cov_result:
                    covariates[row.user_id] = {
                        "role": row.role,
                        "specialty": row.specialty
                    }
            
            # Aggregate by user-day for mixed-effects
            aggregated = {}
            for row in rows:
                key = (row["user_id"], row["condition"], row["phase"], row["day_in_phase"])
                
                if key not in aggregated:
                    aggregated[key] = {
                        "user_id": row["user_id"],
                        "condition": row["condition"],
                        "phase": row["phase"],
                        "day": row["day_in_phase"],
                        "total": 0,
                        "accepted": 0
                    }
                    
                    if row["user_id"] in covariates:
                        aggregated[key].update(covariates[row["user_id"]])
                
                aggregated[key]["total"] += 1
                aggregated[key]["accepted"] += row["accepted"]
            
            # Calculate rates
            export_rows = []
            for key, data in aggregated.items():
                data["acceptance_rate"] = data["accepted"] / data["total"] if data["total"] > 0 else None
                export_rows.append(data)
            
            return {
                "study_id": study_id,
                "export_date": datetime.utcnow().isoformat(),
                "n_rows": len(export_rows),
                "n_users": len(set(r["user_id"] for r in export_rows)),
                "columns": ["user_id", "condition", "phase", "day", "total", "accepted", "acceptance_rate"] + (["role", "specialty"] if include_covariates else []),
                "data": export_rows
            }
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            return {"error": str(e)}
    
    def get_study_summary(self, study_id: str) -> Dict[str, Any]:
        """Get summary statistics for a study."""
        try:
            # Get assignment counts
            query = text("""
                SELECT 
                    condition,
                    phase,
                    COUNT(DISTINCT user_id) as users,
                    MIN(assigned_at) as first_assignment,
                    MAX(assigned_at) as last_assignment
                FROM study_assignments
                WHERE study_id = :study_id
                GROUP BY condition, phase
                ORDER BY condition, phase
            """)
            
            result = self.db.execute(query, {"study_id": study_id})
            
            assignments = []
            total_users = set()
            
            for row in result:
                assignments.append({
                    "condition": row.condition,
                    "phase": row.phase,
                    "users": row.users,
                    "first_assignment": row.first_assignment.isoformat() if row.first_assignment else None,
                    "last_assignment": row.last_assignment.isoformat() if row.last_assignment else None
                })
            
            # Get unique users
            user_query = text("""
                SELECT COUNT(DISTINCT user_id) as unique_users
                FROM study_assignments
                WHERE study_id = :study_id
            """)
            
            unique_users = self.db.execute(user_query, {"study_id": study_id}).scalar() or 0
            
            # Get study details
            study = self.get_study(study_id)
            
            return {
                "study_id": study_id,
                "name": study.get("name") if study else None,
                "status": study.get("status") if study else None,
                "design": study.get("design") if study else None,
                "unique_users": unique_users,
                "assignments_by_condition_phase": assignments,
                "sequential_analysis": self.check_sequential_stopping(study_id)
            }
            
        except Exception as e:
            logger.error(f"Error getting study summary: {e}")
            return {"error": str(e)}


def get_ab_testing_service(db: Session) -> ABTestingService:
    """Get A/B testing service instance."""
    return ABTestingService(db)

