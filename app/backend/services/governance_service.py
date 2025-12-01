"""
Governance Service - Assurance Cases & Ethics Compliance

Implements governance mechanisms for ethical AI adaptation:
- Goal definition (what adaptation aims to achieve)
- Evidence collection (A/B metrics, user feedback)
- Risk assessment (potential harms)
- Mitigation strategies
- Approval workflow

Part of Phase 7: Privacy, Security & Governance
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from uuid import UUID
import logging
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_

logger = logging.getLogger(__name__)


class ApprovalStatus(str, Enum):
    """Approval status for assurance cases."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_CHANGES = "requires_changes"


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GovernanceService:
    """
    Governance service for ethical AI compliance.
    
    Key Capabilities:
    1. Assurance Case Management - Document goals, evidence, risks
    2. Approval Workflow - Multi-level approval for high-risk adaptations
    3. Audit Trail - Complete history of decisions
    4. Compliance Reporting - Generate compliance reports
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # =========================================================================
    # Assurance Case Management
    # =========================================================================
    
    def create_assurance_case(
        self,
        adaptation_id: UUID,
        goal: str,
        goal_category: str,
        evidence: Dict[str, Any],
        risks: List[Dict[str, Any]],
        mitigations: List[Dict[str, Any]],
        created_by: UUID,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create an assurance case for an adaptation.
        
        An assurance case provides structured argumentation that an
        adaptation is ethical, safe, and beneficial.
        
        Args:
            adaptation_id: ID of the adaptation being documented
            goal: Primary goal statement
            goal_category: Category (efficiency, safety, usability, etc.)
            evidence: Supporting evidence (metrics, studies, feedback)
            risks: Identified risks with assessments
            mitigations: Mitigation strategies for each risk
            created_by: User creating the case
            metadata: Additional metadata
        
        Returns:
            Created assurance case
        """
        try:
            import json
            from sqlalchemy import text
            
            case_id = str(UUID(int=int(datetime.utcnow().timestamp() * 1000000)))
            
            # Calculate overall risk level
            risk_level = self._calculate_overall_risk(risks)
            
            # Determine required approval level based on risk
            required_approval = self._determine_approval_requirements(risk_level)
            
            query = text("""
                INSERT INTO assurance_cases (
                    id, adaptation_id, goal, goal_category, evidence, risks,
                    mitigations, risk_level, status, required_approvals,
                    created_by, created_at, metadata
                ) VALUES (
                    :id, :adaptation_id, :goal, :goal_category, :evidence, :risks,
                    :mitigations, :risk_level, :status, :required_approvals,
                    :created_by, :created_at, :metadata
                )
            """)
            
            self.db.execute(query, {
                "id": case_id,
                "adaptation_id": str(adaptation_id),
                "goal": goal,
                "goal_category": goal_category,
                "evidence": json.dumps(evidence),
                "risks": json.dumps(risks),
                "mitigations": json.dumps(mitigations),
                "risk_level": risk_level.value,
                "status": ApprovalStatus.DRAFT.value,
                "required_approvals": json.dumps(required_approval),
                "created_by": str(created_by),
                "created_at": datetime.utcnow(),
                "metadata": json.dumps(metadata or {})
            })
            self.db.commit()
            
            case = {
                "id": case_id,
                "adaptation_id": str(adaptation_id),
                "goal": goal,
                "goal_category": goal_category,
                "evidence": evidence,
                "risks": risks,
                "mitigations": mitigations,
                "risk_level": risk_level.value,
                "status": ApprovalStatus.DRAFT.value,
                "required_approvals": required_approval,
                "created_by": str(created_by),
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Created assurance case {case_id} for adaptation {adaptation_id}")
            
            return case
            
        except Exception as e:
            logger.error(f"Error creating assurance case: {e}")
            self.db.rollback()
            raise
    
    def _calculate_overall_risk(self, risks: List[Dict[str, Any]]) -> RiskLevel:
        """Calculate overall risk level from individual risks."""
        if not risks:
            return RiskLevel.LOW
        
        risk_scores = {
            RiskLevel.LOW.value: 1,
            RiskLevel.MEDIUM.value: 2,
            RiskLevel.HIGH.value: 3,
            RiskLevel.CRITICAL.value: 4
        }
        
        max_score = 0
        weighted_sum = 0
        
        for risk in risks:
            level = risk.get("level", "low")
            likelihood = risk.get("likelihood", 0.5)
            impact = risk.get("impact", 0.5)
            
            score = risk_scores.get(level, 1)
            weighted_score = score * likelihood * impact
            
            max_score = max(max_score, score)
            weighted_sum += weighted_score
        
        avg_score = weighted_sum / len(risks)
        
        # Use both max and average to determine overall level
        if max_score >= 4 or avg_score >= 3:
            return RiskLevel.CRITICAL
        elif max_score >= 3 or avg_score >= 2:
            return RiskLevel.HIGH
        elif max_score >= 2 or avg_score >= 1.5:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _determine_approval_requirements(
        self,
        risk_level: RiskLevel
    ) -> Dict[str, Any]:
        """Determine approval requirements based on risk level."""
        requirements = {
            RiskLevel.LOW: {
                "min_approvers": 1,
                "required_roles": ["researcher"],
                "auto_approve_after_days": 7,
                "requires_ethics_review": False
            },
            RiskLevel.MEDIUM: {
                "min_approvers": 2,
                "required_roles": ["researcher", "admin"],
                "auto_approve_after_days": None,
                "requires_ethics_review": False
            },
            RiskLevel.HIGH: {
                "min_approvers": 2,
                "required_roles": ["researcher", "admin"],
                "auto_approve_after_days": None,
                "requires_ethics_review": True
            },
            RiskLevel.CRITICAL: {
                "min_approvers": 3,
                "required_roles": ["researcher", "admin", "ethics_officer"],
                "auto_approve_after_days": None,
                "requires_ethics_review": True,
                "requires_irb_approval": True
            }
        }
        
        return requirements.get(risk_level, requirements[RiskLevel.LOW])
    
    def get_assurance_case(self, case_id: UUID) -> Optional[Dict[str, Any]]:
        """Get an assurance case by ID."""
        try:
            import json
            from sqlalchemy import text
            
            query = text("""
                SELECT * FROM assurance_cases WHERE id = :case_id
            """)
            
            result = self.db.execute(query, {"case_id": str(case_id)}).fetchone()
            
            if not result:
                return None
            
            row = dict(result._mapping)
            
            # Parse JSON fields
            for field in ["evidence", "risks", "mitigations", "required_approvals", "metadata", "approvals"]:
                if field in row and row[field]:
                    if isinstance(row[field], str):
                        row[field] = json.loads(row[field])
            
            return row
            
        except Exception as e:
            logger.error(f"Error getting assurance case: {e}")
            return None
    
    def update_assurance_case(
        self,
        case_id: UUID,
        updates: Dict[str, Any],
        updated_by: UUID
    ) -> Dict[str, Any]:
        """Update an assurance case."""
        try:
            import json
            from sqlalchemy import text
            
            # Get current case
            current = self.get_assurance_case(case_id)
            if not current:
                raise ValueError(f"Assurance case {case_id} not found")
            
            # Only allow updates in certain statuses
            if current["status"] not in [ApprovalStatus.DRAFT.value, ApprovalStatus.REQUIRES_CHANGES.value]:
                raise ValueError(f"Cannot update case in status: {current['status']}")
            
            # Build update query
            allowed_fields = ["goal", "goal_category", "evidence", "risks", "mitigations", "metadata"]
            update_parts = []
            params = {"case_id": str(case_id), "updated_at": datetime.utcnow(), "updated_by": str(updated_by)}
            
            for field in allowed_fields:
                if field in updates:
                    value = updates[field]
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value)
                    params[field] = value
                    update_parts.append(f"{field} = :{field}")
            
            if not update_parts:
                return current
            
            update_parts.append("updated_at = :updated_at")
            update_parts.append("updated_by = :updated_by")
            
            # Recalculate risk if risks updated
            if "risks" in updates:
                new_risk_level = self._calculate_overall_risk(updates["risks"])
                params["risk_level"] = new_risk_level.value
                update_parts.append("risk_level = :risk_level")
                
                # Update approval requirements
                new_requirements = self._determine_approval_requirements(new_risk_level)
                params["required_approvals"] = json.dumps(new_requirements)
                update_parts.append("required_approvals = :required_approvals")
            
            query = text(f"""
                UPDATE assurance_cases
                SET {', '.join(update_parts)}
                WHERE id = :case_id
            """)
            
            self.db.execute(query, params)
            self.db.commit()
            
            # Log update
            self._log_case_event(case_id, "updated", updated_by, {"fields": list(updates.keys())})
            
            return self.get_assurance_case(case_id)
            
        except Exception as e:
            logger.error(f"Error updating assurance case: {e}")
            self.db.rollback()
            raise
    
    # =========================================================================
    # Approval Workflow
    # =========================================================================
    
    def submit_for_review(
        self,
        case_id: UUID,
        submitted_by: UUID,
        notes: str = None
    ) -> Dict[str, Any]:
        """Submit assurance case for review."""
        try:
            from sqlalchemy import text
            
            current = self.get_assurance_case(case_id)
            if not current:
                raise ValueError(f"Assurance case {case_id} not found")
            
            if current["status"] not in [ApprovalStatus.DRAFT.value, ApprovalStatus.REQUIRES_CHANGES.value]:
                raise ValueError(f"Cannot submit case in status: {current['status']}")
            
            query = text("""
                UPDATE assurance_cases
                SET status = :status, submitted_at = :submitted_at, submitted_by = :submitted_by
                WHERE id = :case_id
            """)
            
            self.db.execute(query, {
                "case_id": str(case_id),
                "status": ApprovalStatus.PENDING_REVIEW.value,
                "submitted_at": datetime.utcnow(),
                "submitted_by": str(submitted_by)
            })
            self.db.commit()
            
            self._log_case_event(case_id, "submitted_for_review", submitted_by, {"notes": notes})
            
            return self.get_assurance_case(case_id)
            
        except Exception as e:
            logger.error(f"Error submitting for review: {e}")
            self.db.rollback()
            raise
    
    def add_approval(
        self,
        case_id: UUID,
        approver_id: UUID,
        approver_role: str,
        decision: str,  # "approve", "reject", "request_changes"
        comments: str = None,
        conditions: List[str] = None
    ) -> Dict[str, Any]:
        """Add an approval decision to the case."""
        try:
            import json
            from sqlalchemy import text
            
            current = self.get_assurance_case(case_id)
            if not current:
                raise ValueError(f"Assurance case {case_id} not found")
            
            if current["status"] not in [ApprovalStatus.PENDING_REVIEW.value, ApprovalStatus.UNDER_REVIEW.value]:
                raise ValueError(f"Cannot approve case in status: {current['status']}")
            
            # Check if approver's role is required
            required = current.get("required_approvals", {})
            required_roles = required.get("required_roles", [])
            
            if approver_role not in required_roles:
                logger.warning(f"Approver role {approver_role} not in required roles {required_roles}")
            
            # Add approval to list
            approvals = current.get("approvals", []) or []
            
            approval = {
                "approver_id": str(approver_id),
                "approver_role": approver_role,
                "decision": decision,
                "comments": comments,
                "conditions": conditions or [],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            approvals.append(approval)
            
            # Determine new status
            new_status = self._determine_status_after_approval(current, approvals, decision)
            
            query = text("""
                UPDATE assurance_cases
                SET status = :status, approvals = :approvals, updated_at = :updated_at
                WHERE id = :case_id
            """)
            
            self.db.execute(query, {
                "case_id": str(case_id),
                "status": new_status.value,
                "approvals": json.dumps(approvals),
                "updated_at": datetime.utcnow()
            })
            
            # If approved, record final approval timestamp
            if new_status == ApprovalStatus.APPROVED:
                approve_query = text("""
                    UPDATE assurance_cases
                    SET approved_at = :approved_at
                    WHERE id = :case_id
                """)
                self.db.execute(approve_query, {
                    "case_id": str(case_id),
                    "approved_at": datetime.utcnow()
                })
            
            self.db.commit()
            
            self._log_case_event(case_id, f"approval_{decision}", approver_id, {
                "role": approver_role,
                "comments": comments
            })
            
            return self.get_assurance_case(case_id)
            
        except Exception as e:
            logger.error(f"Error adding approval: {e}")
            self.db.rollback()
            raise
    
    def _determine_status_after_approval(
        self,
        case: Dict[str, Any],
        approvals: List[Dict],
        latest_decision: str
    ) -> ApprovalStatus:
        """Determine case status after an approval decision."""
        if latest_decision == "reject":
            return ApprovalStatus.REJECTED
        
        if latest_decision == "request_changes":
            return ApprovalStatus.REQUIRES_CHANGES
        
        # Count approvals
        required = case.get("required_approvals", {})
        min_approvers = required.get("min_approvers", 1)
        required_roles = set(required.get("required_roles", []))
        
        approve_count = sum(1 for a in approvals if a["decision"] == "approve")
        approved_roles = set(a["approver_role"] for a in approvals if a["decision"] == "approve")
        
        # Check if all requirements met
        if approve_count >= min_approvers and required_roles.issubset(approved_roles):
            return ApprovalStatus.APPROVED
        
        return ApprovalStatus.UNDER_REVIEW
    
    # =========================================================================
    # Evidence Collection
    # =========================================================================
    
    def add_evidence(
        self,
        case_id: UUID,
        evidence_type: str,
        evidence_data: Dict[str, Any],
        added_by: UUID
    ) -> Dict[str, Any]:
        """Add evidence to an assurance case."""
        try:
            import json
            
            current = self.get_assurance_case(case_id)
            if not current:
                raise ValueError(f"Assurance case {case_id} not found")
            
            evidence = current.get("evidence", {})
            
            if evidence_type not in evidence:
                evidence[evidence_type] = []
            
            evidence_entry = {
                **evidence_data,
                "added_by": str(added_by),
                "added_at": datetime.utcnow().isoformat()
            }
            
            evidence[evidence_type].append(evidence_entry)
            
            return self.update_assurance_case(case_id, {"evidence": evidence}, added_by)
            
        except Exception as e:
            logger.error(f"Error adding evidence: {e}")
            raise
    
    def collect_automated_evidence(
        self,
        case_id: UUID,
        adaptation_id: UUID
    ) -> Dict[str, Any]:
        """Automatically collect evidence for an adaptation."""
        try:
            from sqlalchemy import text
            
            evidence = {}
            
            # Get A/B test metrics if available
            ab_query = text("""
                SELECT * FROM shadow_tests
                WHERE policy_id = :adaptation_id
                AND status = 'completed'
                ORDER BY completed_at DESC
                LIMIT 1
            """)
            
            ab_result = self.db.execute(ab_query, {"adaptation_id": str(adaptation_id)}).fetchone()
            
            if ab_result:
                import json
                row = dict(ab_result._mapping)
                evidence["ab_test"] = [{
                    "test_id": row.get("id"),
                    "results": json.loads(row.get("results", "{}")) if isinstance(row.get("results"), str) else row.get("results"),
                    "recommendation": row.get("recommendation"),
                    "collected_at": datetime.utcnow().isoformat()
                }]
            
            # Get user feedback
            feedback_query = text("""
                SELECT 
                    COUNT(*) as total,
                    AVG(CASE WHEN sentiment = 'positive' THEN 1 WHEN sentiment = 'negative' THEN -1 ELSE 0 END) as sentiment_score
                FROM user_feedback
                WHERE context_id = :adaptation_id
                AND created_at > :cutoff
            """)
            
            cutoff = datetime.utcnow() - timedelta(days=30)
            feedback_result = self.db.execute(feedback_query, {
                "adaptation_id": str(adaptation_id),
                "cutoff": cutoff
            }).fetchone()
            
            if feedback_result:
                row = dict(feedback_result._mapping)
                evidence["user_feedback"] = [{
                    "total_feedback": row.get("total", 0),
                    "sentiment_score": round(float(row.get("sentiment_score") or 0), 2),
                    "period_days": 30,
                    "collected_at": datetime.utcnow().isoformat()
                }]
            
            # Get performance metrics
            metrics_query = text("""
                SELECT 
                    AVG(confidence_score) as avg_confidence,
                    COUNT(*) as adaptation_count
                FROM adaptation_logs
                WHERE new_state->>'adaptation_id' = :adaptation_id
                AND created_at > :cutoff
            """)
            
            metrics_result = self.db.execute(metrics_query, {
                "adaptation_id": str(adaptation_id),
                "cutoff": cutoff
            }).fetchone()
            
            if metrics_result:
                row = dict(metrics_result._mapping)
                evidence["performance_metrics"] = [{
                    "avg_confidence": round(float(row.get("avg_confidence") or 0), 3),
                    "adaptation_count": row.get("adaptation_count", 0),
                    "collected_at": datetime.utcnow().isoformat()
                }]
            
            return evidence
            
        except Exception as e:
            logger.warning(f"Error collecting automated evidence: {e}")
            return {}
    
    # =========================================================================
    # Risk Assessment
    # =========================================================================
    
    def assess_risk(
        self,
        risk_name: str,
        description: str,
        likelihood: float,  # 0-1
        impact: float,  # 0-1
        affected_groups: List[str] = None,
        existing_controls: List[str] = None
    ) -> Dict[str, Any]:
        """Create a structured risk assessment."""
        # Calculate risk score
        raw_score = likelihood * impact
        
        # Determine risk level
        if raw_score >= 0.7:
            level = RiskLevel.CRITICAL
        elif raw_score >= 0.4:
            level = RiskLevel.HIGH
        elif raw_score >= 0.2:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW
        
        # Adjust for existing controls
        control_effectiveness = len(existing_controls or []) * 0.1  # Each control reduces risk by 10%
        adjusted_score = max(0.05, raw_score * (1 - min(control_effectiveness, 0.5)))
        
        return {
            "name": risk_name,
            "description": description,
            "likelihood": likelihood,
            "impact": impact,
            "raw_score": round(raw_score, 3),
            "adjusted_score": round(adjusted_score, 3),
            "level": level.value,
            "affected_groups": affected_groups or [],
            "existing_controls": existing_controls or [],
            "requires_mitigation": level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        }
    
    def create_mitigation(
        self,
        risk_name: str,
        strategy: str,
        description: str,
        implementation_status: str,
        owner: str = None,
        effectiveness_estimate: float = 0.5
    ) -> Dict[str, Any]:
        """Create a mitigation strategy for a risk."""
        return {
            "risk_name": risk_name,
            "strategy": strategy,
            "description": description,
            "implementation_status": implementation_status,  # planned, in_progress, implemented, verified
            "owner": owner,
            "effectiveness_estimate": effectiveness_estimate,
            "created_at": datetime.utcnow().isoformat()
        }
    
    # =========================================================================
    # Audit Trail
    # =========================================================================
    
    def _log_case_event(
        self,
        case_id: UUID,
        event_type: str,
        actor_id: UUID,
        details: Dict[str, Any] = None
    ) -> None:
        """Log an event in the case audit trail."""
        try:
            import json
            from sqlalchemy import text
            
            query = text("""
                INSERT INTO assurance_case_audit (
                    case_id, event_type, actor_id, details, timestamp
                ) VALUES (
                    :case_id, :event_type, :actor_id, :details, :timestamp
                )
            """)
            
            self.db.execute(query, {
                "case_id": str(case_id),
                "event_type": event_type,
                "actor_id": str(actor_id),
                "details": json.dumps(details or {}),
                "timestamp": datetime.utcnow()
            })
            self.db.commit()
            
        except Exception as e:
            logger.warning(f"Error logging case event: {e}")
    
    def get_case_audit_trail(
        self,
        case_id: UUID,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get audit trail for a case."""
        try:
            import json
            from sqlalchemy import text
            
            query = text("""
                SELECT * FROM assurance_case_audit
                WHERE case_id = :case_id
                ORDER BY timestamp DESC
                LIMIT :limit
            """)
            
            result = self.db.execute(query, {"case_id": str(case_id), "limit": limit})
            
            events = []
            for row in result:
                event = dict(row._mapping)
                if "details" in event and isinstance(event["details"], str):
                    event["details"] = json.loads(event["details"])
                events.append(event)
            
            return events
            
        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return []
    
    # =========================================================================
    # Compliance Reporting
    # =========================================================================
    
    def generate_compliance_report(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Generate a compliance report for assurance cases."""
        try:
            from sqlalchemy import text
            
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get case statistics
            stats_query = text("""
                SELECT 
                    status,
                    risk_level,
                    COUNT(*) as count
                FROM assurance_cases
                WHERE created_at BETWEEN :start_date AND :end_date
                GROUP BY status, risk_level
            """)
            
            stats_result = self.db.execute(stats_query, {
                "start_date": start_date,
                "end_date": end_date
            })
            
            status_breakdown = {}
            risk_breakdown = {}
            total_cases = 0
            
            for row in stats_result:
                r = dict(row._mapping)
                status = r["status"]
                risk = r["risk_level"]
                count = r["count"]
                
                status_breakdown[status] = status_breakdown.get(status, 0) + count
                risk_breakdown[risk] = risk_breakdown.get(risk, 0) + count
                total_cases += count
            
            # Calculate approval metrics
            approval_query = text("""
                SELECT 
                    AVG(EXTRACT(EPOCH FROM (approved_at - submitted_at)) / 86400) as avg_approval_days,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved_count,
                    COUNT(*) FILTER (WHERE status = 'rejected') as rejected_count
                FROM assurance_cases
                WHERE created_at BETWEEN :start_date AND :end_date
                AND submitted_at IS NOT NULL
            """)
            
            approval_result = self.db.execute(approval_query, {
                "start_date": start_date,
                "end_date": end_date
            }).fetchone()
            
            approval_metrics = {}
            if approval_result:
                r = dict(approval_result._mapping)
                approval_metrics = {
                    "avg_approval_days": round(float(r.get("avg_approval_days") or 0), 1),
                    "approved_count": r.get("approved_count", 0),
                    "rejected_count": r.get("rejected_count", 0),
                    "approval_rate": round(
                        r.get("approved_count", 0) / max(1, r.get("approved_count", 0) + r.get("rejected_count", 0)),
                        3
                    )
                }
            
            return {
                "report_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "summary": {
                    "total_cases": total_cases,
                    "status_breakdown": status_breakdown,
                    "risk_breakdown": risk_breakdown
                },
                "approval_metrics": approval_metrics,
                "compliance_score": self._calculate_compliance_score(
                    status_breakdown, risk_breakdown, approval_metrics
                ),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            return {"error": str(e)}
    
    def _calculate_compliance_score(
        self,
        status_breakdown: Dict,
        risk_breakdown: Dict,
        approval_metrics: Dict
    ) -> Dict[str, Any]:
        """Calculate overall compliance score."""
        scores = {}
        
        # Documentation score - % of cases not in draft
        total = sum(status_breakdown.values())
        if total > 0:
            documented = total - status_breakdown.get("draft", 0)
            scores["documentation"] = round(documented / total, 3)
        else:
            scores["documentation"] = 1.0
        
        # Approval score - % of submitted cases approved
        submitted = sum(v for k, v in status_breakdown.items() if k != "draft")
        approved = status_breakdown.get("approved", 0)
        if submitted > 0:
            scores["approval"] = round(approved / submitted, 3)
        else:
            scores["approval"] = 1.0
        
        # Risk management score - inverse of high/critical risk ratio
        total_risk = sum(risk_breakdown.values())
        if total_risk > 0:
            high_risk = risk_breakdown.get("high", 0) + risk_breakdown.get("critical", 0)
            scores["risk_management"] = round(1 - (high_risk / total_risk), 3)
        else:
            scores["risk_management"] = 1.0
        
        # Timeliness score - based on avg approval days
        avg_days = approval_metrics.get("avg_approval_days", 0)
        if avg_days <= 7:
            scores["timeliness"] = 1.0
        elif avg_days <= 14:
            scores["timeliness"] = 0.8
        elif avg_days <= 30:
            scores["timeliness"] = 0.6
        else:
            scores["timeliness"] = 0.4
        
        # Overall score (weighted average)
        weights = {
            "documentation": 0.25,
            "approval": 0.30,
            "risk_management": 0.30,
            "timeliness": 0.15
        }
        
        overall = sum(scores[k] * weights[k] for k in scores)
        
        return {
            "overall": round(overall, 3),
            "components": scores,
            "rating": "excellent" if overall >= 0.9 else "good" if overall >= 0.7 else "fair" if overall >= 0.5 else "needs_improvement"
        }
    
    # =========================================================================
    # Queries
    # =========================================================================
    
    def get_pending_approvals(
        self,
        approver_role: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get cases pending approval."""
        try:
            import json
            from sqlalchemy import text
            
            query = text("""
                SELECT * FROM assurance_cases
                WHERE status IN ('pending_review', 'under_review')
                ORDER BY 
                    CASE risk_level 
                        WHEN 'critical' THEN 1 
                        WHEN 'high' THEN 2 
                        WHEN 'medium' THEN 3 
                        ELSE 4 
                    END,
                    submitted_at ASC
                LIMIT :limit
            """)
            
            result = self.db.execute(query, {"limit": limit})
            
            cases = []
            for row in result:
                case = dict(row._mapping)
                
                # Filter by role if specified
                if approver_role:
                    required = json.loads(case.get("required_approvals", "{}")) if isinstance(case.get("required_approvals"), str) else case.get("required_approvals", {})
                    required_roles = required.get("required_roles", [])
                    
                    if approver_role not in required_roles:
                        continue
                
                # Parse JSON fields
                for field in ["evidence", "risks", "mitigations", "required_approvals", "metadata", "approvals"]:
                    if field in case and case[field]:
                        if isinstance(case[field], str):
                            case[field] = json.loads(case[field])
                
                cases.append(case)
            
            return cases
            
        except Exception as e:
            logger.error(f"Error getting pending approvals: {e}")
            return []


def get_governance_service(db: Session) -> GovernanceService:
    """Get governance service instance."""
    return GovernanceService(db)

