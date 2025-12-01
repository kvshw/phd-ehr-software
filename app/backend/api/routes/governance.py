"""
Governance API Endpoints
Privacy, Security & Assurance Case Management

Part of Phase 7: Privacy, Security & Governance
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import logging

from core.database import get_db
from core.dependencies import get_current_user, require_role
from services.privacy_service import PrivacyService
from services.security_service import SecurityService
from services.governance_service import GovernanceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/governance", tags=["Governance"])


# ============================================================================
# Privacy Endpoints
# ============================================================================

@router.get("/privacy/consent")
async def get_my_consents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get current user's consent status for all purposes.
    """
    try:
        from sqlalchemy import text
        
        query = text("""
            SELECT purpose, consented, created_at, updated_at
            FROM user_consents
            WHERE user_id = :user_id
        """)
        
        result = db.execute(query, {"user_id": current_user.user_id})
        
        consents = {}
        for row in result:
            r = dict(row._mapping)
            consents[r["purpose"]] = {
                "consented": r["consented"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
                "updated_at": r["updated_at"].isoformat() if r["updated_at"] else None
            }
        
        return {
            "user_id": str(current_user.user_id),
            "consents": consents
        }
        
    except Exception as e:
        logger.error(f"Error getting consents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/privacy/consent")
async def update_consent(
    purpose: str,
    consented: bool,
    consent_text: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Update consent for a specific purpose.
    
    **Purposes:**
    - `analytics`: Usage analytics for UI adaptation
    - `research`: Data use for research purposes
    - `adaptation`: AI-powered UI personalization
    """
    privacy_service = PrivacyService(db)
    
    success = privacy_service.record_consent(
        user_id=current_user.user_id,
        purpose=purpose,
        consented=consented,
        consent_text=consent_text
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record consent"
        )
    
    return {
        "status": "updated",
        "purpose": purpose,
        "consented": consented
    }


@router.get("/privacy/retention-status")
async def get_retention_status(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Get data retention status across tables.
    
    **Admin/Researcher Only**
    """
    privacy_service = PrivacyService(db)
    return privacy_service.get_retention_status()


@router.post("/privacy/enforce-retention")
async def enforce_retention(
    table_name: str,
    retention_days: int = 90,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    """
    Enforce data retention policy on a table.
    
    **Admin Only**
    
    Deletes data older than retention_days.
    """
    privacy_service = PrivacyService(db)
    
    # Validate table name to prevent SQL injection
    allowed_tables = [
        "user_actions", "adaptation_logs", "bandit_adaptation_logs",
        "shadow_tests", "rate_limit_log"
    ]
    
    if table_name not in allowed_tables:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Table not allowed. Allowed tables: {allowed_tables}"
        )
    
    deleted = privacy_service.enforce_retention_policy(
        table_name=table_name,
        retention_days=retention_days
    )
    
    return {
        "table": table_name,
        "retention_days": retention_days,
        "records_deleted": deleted
    }


# ============================================================================
# Security Endpoints
# ============================================================================

@router.get("/security/alerts")
async def get_security_alerts(
    severity: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Get open security alerts.
    
    **Admin/Researcher Only**
    """
    security_service = SecurityService(db)
    alerts = security_service.get_open_alerts(severity=severity, limit=limit)
    
    return {
        "alerts": alerts,
        "count": len(alerts),
        "filter": {"severity": severity}
    }


@router.post("/security/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: UUID,
    resolution_notes: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin"])),
):
    """
    Resolve a security alert.
    
    **Admin Only**
    """
    try:
        from sqlalchemy import text
        
        query = text("""
            UPDATE security_alerts
            SET status = 'resolved',
                resolved_by = :resolved_by,
                resolved_at = :resolved_at,
                resolution_notes = :resolution_notes
            WHERE id = :alert_id
        """)
        
        db.execute(query, {
            "alert_id": str(alert_id),
            "resolved_by": str(current_user.user_id),
            "resolved_at": datetime.utcnow(),
            "resolution_notes": resolution_notes
        })
        db.commit()
        
        return {"status": "resolved", "alert_id": str(alert_id)}
        
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/security/check-fl-poisoning")
async def check_fl_poisoning(
    client_updates: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Check FL client updates for poisoning attacks.
    
    **Admin/Researcher Only**
    
    **Request Body:**
    ```json
    [
        {
            "client_id": "site_1",
            "weight_updates": {"layer1": [0.1, 0.2, ...], ...}
        },
        ...
    ]
    ```
    """
    security_service = SecurityService(db)
    result = security_service.detect_poisoning(client_updates)
    
    # Create alert if poisoning detected
    if result["poisoning_detected"]:
        security_service.create_security_alert(
            alert_type="fl_poisoning",
            severity="high",
            description=f"Potential FL poisoning detected: {len(result['flagged_clients'])} client(s) flagged",
            details=result,
            affected_entity=",".join([c["client_id"] for c in result["flagged_clients"]])
        )
    
    return result


@router.post("/security/clip-gradients")
async def clip_gradients(
    gradients: Dict[str, Any],
    max_norm: float = 1.0,
    add_noise: bool = False,
    noise_multiplier: float = 0.1,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Clip gradients for differential privacy.
    
    **Admin/Researcher Only**
    """
    security_service = SecurityService(db)
    
    if add_noise:
        clipped = security_service.clip_and_add_noise(
            gradients=gradients,
            max_norm=max_norm,
            noise_multiplier=noise_multiplier
        )
        return {"gradients": clipped, "clipped": True, "noise_added": True}
    else:
        clipped, was_clipped = security_service.clip_gradients(
            gradients=gradients,
            max_norm=max_norm
        )
        return {"gradients": clipped, "clipped": was_clipped, "noise_added": False}


# ============================================================================
# Assurance Case Endpoints
# ============================================================================

@router.post("/assurance-cases")
async def create_assurance_case(
    adaptation_id: UUID,
    goal: str,
    goal_category: str,
    evidence: Dict[str, Any] = None,
    risks: List[Dict[str, Any]] = None,
    mitigations: List[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Create a new assurance case for an adaptation.
    
    **Request Body:**
    ```json
    {
        "adaptation_id": "uuid",
        "goal": "Improve workflow efficiency by 15%",
        "goal_category": "efficiency",
        "evidence": {
            "ab_test": [{"test_id": "...", "results": {...}}],
            "user_feedback": [{"score": 4.2, "comments": "..."}]
        },
        "risks": [
            {
                "name": "Workflow disruption",
                "description": "Users may initially be confused",
                "level": "medium",
                "likelihood": 0.3,
                "impact": 0.4
            }
        ],
        "mitigations": [
            {
                "risk_name": "Workflow disruption",
                "strategy": "Gradual rollout",
                "description": "Deploy to 10% of users first",
                "implementation_status": "planned"
            }
        ]
    }
    ```
    """
    governance_service = GovernanceService(db)
    
    case = governance_service.create_assurance_case(
        adaptation_id=adaptation_id,
        goal=goal,
        goal_category=goal_category,
        evidence=evidence or {},
        risks=risks or [],
        mitigations=mitigations or [],
        created_by=current_user.user_id
    )
    
    return case


@router.get("/assurance-cases/{case_id}")
async def get_assurance_case(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get an assurance case by ID.
    """
    governance_service = GovernanceService(db)
    case = governance_service.get_assurance_case(case_id)
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assurance case not found"
        )
    
    return case


@router.patch("/assurance-cases/{case_id}")
async def update_assurance_case(
    case_id: UUID,
    updates: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Update an assurance case.
    
    Only allowed for cases in 'draft' or 'requires_changes' status.
    """
    governance_service = GovernanceService(db)
    
    try:
        case = governance_service.update_assurance_case(
            case_id=case_id,
            updates=updates,
            updated_by=current_user.user_id
        )
        return case
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/assurance-cases/{case_id}/submit")
async def submit_for_review(
    case_id: UUID,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Submit an assurance case for review.
    """
    governance_service = GovernanceService(db)
    
    try:
        case = governance_service.submit_for_review(
            case_id=case_id,
            submitted_by=current_user.user_id,
            notes=notes
        )
        return case
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/assurance-cases/{case_id}/approve")
async def add_approval(
    case_id: UUID,
    decision: str,  # approve, reject, request_changes
    comments: Optional[str] = None,
    conditions: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Add an approval decision to an assurance case.
    
    **Researcher/Admin Only**
    
    **Parameters:**
    - `decision`: "approve", "reject", or "request_changes"
    - `comments`: Optional comments
    - `conditions`: Optional list of conditions (for conditional approval)
    """
    if decision not in ["approve", "reject", "request_changes"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision must be: approve, reject, or request_changes"
        )
    
    governance_service = GovernanceService(db)
    
    try:
        case = governance_service.add_approval(
            case_id=case_id,
            approver_id=current_user.user_id,
            approver_role=current_user.role,
            decision=decision,
            comments=comments,
            conditions=conditions
        )
        return case
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/assurance-cases/{case_id}/evidence")
async def add_evidence(
    case_id: UUID,
    evidence_type: str,
    evidence_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["clinician", "researcher", "admin"])),
):
    """
    Add evidence to an assurance case.
    
    **Evidence Types:**
    - `ab_test`: A/B test results
    - `user_feedback`: User feedback and surveys
    - `performance_metrics`: System performance data
    - `expert_review`: Expert evaluation
    """
    governance_service = GovernanceService(db)
    
    case = governance_service.add_evidence(
        case_id=case_id,
        evidence_type=evidence_type,
        evidence_data=evidence_data,
        added_by=current_user.user_id
    )
    
    return case


@router.post("/assurance-cases/{case_id}/collect-evidence")
async def collect_automated_evidence(
    case_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Automatically collect evidence for an assurance case.
    
    Gathers:
    - A/B test results
    - User feedback metrics
    - Performance metrics
    
    **Researcher/Admin Only**
    """
    governance_service = GovernanceService(db)
    
    case = governance_service.get_assurance_case(case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assurance case not found"
        )
    
    adaptation_id = case.get("adaptation_id")
    if not adaptation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Case has no linked adaptation"
        )
    
    evidence = governance_service.collect_automated_evidence(
        case_id=case_id,
        adaptation_id=UUID(adaptation_id)
    )
    
    # Add collected evidence to case
    for evidence_type, evidence_data in evidence.items():
        if evidence_data:
            governance_service.add_evidence(
                case_id=case_id,
                evidence_type=evidence_type,
                evidence_data=evidence_data[0],  # First entry
                added_by=current_user.user_id
            )
    
    return {
        "case_id": str(case_id),
        "evidence_collected": list(evidence.keys()),
        "evidence": evidence
    }


@router.get("/assurance-cases/{case_id}/audit")
async def get_audit_trail(
    case_id: UUID,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Get audit trail for an assurance case.
    """
    governance_service = GovernanceService(db)
    events = governance_service.get_case_audit_trail(case_id, limit=limit)
    
    return {
        "case_id": str(case_id),
        "events": events
    }


@router.get("/assurance-cases/pending")
async def get_pending_approvals(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["researcher", "admin"])),
):
    """
    Get assurance cases pending approval.
    
    **Researcher/Admin Only**
    
    Returns cases sorted by risk level (critical first).
    """
    governance_service = GovernanceService(db)
    cases = governance_service.get_pending_approvals(
        approver_role=current_user.role,
        limit=limit
    )
    
    return {
        "cases": cases,
        "count": len(cases)
    }


# ============================================================================
# Risk Assessment Helpers
# ============================================================================

@router.post("/governance/assess-risk")
async def assess_risk(
    risk_name: str,
    description: str,
    likelihood: float,
    impact: float,
    affected_groups: Optional[List[str]] = None,
    existing_controls: Optional[List[str]] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a structured risk assessment.
    
    **Parameters:**
    - `likelihood`: 0-1 (probability of occurrence)
    - `impact`: 0-1 (severity if it occurs)
    - `affected_groups`: Groups potentially affected
    - `existing_controls`: Controls already in place
    """
    governance_service = GovernanceService(db)
    
    assessment = governance_service.assess_risk(
        risk_name=risk_name,
        description=description,
        likelihood=likelihood,
        impact=impact,
        affected_groups=affected_groups,
        existing_controls=existing_controls
    )
    
    return assessment


@router.post("/governance/create-mitigation")
async def create_mitigation(
    risk_name: str,
    strategy: str,
    description: str,
    implementation_status: str,
    owner: Optional[str] = None,
    effectiveness_estimate: float = 0.5,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create a mitigation strategy.
    
    **Implementation Status:**
    - `planned`: Not yet started
    - `in_progress`: Currently being implemented
    - `implemented`: Deployed but not verified
    - `verified`: Tested and confirmed effective
    """
    governance_service = GovernanceService(db)
    
    mitigation = governance_service.create_mitigation(
        risk_name=risk_name,
        strategy=strategy,
        description=description,
        implementation_status=implementation_status,
        owner=owner,
        effectiveness_estimate=effectiveness_estimate
    )
    
    return mitigation


# ============================================================================
# Compliance Reporting
# ============================================================================

@router.get("/governance/compliance-report")
async def get_compliance_report(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Generate compliance report for assurance cases.
    
    **Admin/Researcher Only**
    
    Returns:
    - Case statistics by status and risk level
    - Approval metrics
    - Compliance score breakdown
    """
    governance_service = GovernanceService(db)
    
    from datetime import timedelta
    start_date = datetime.utcnow() - timedelta(days=days)
    
    report = governance_service.generate_compliance_report(
        start_date=start_date,
        end_date=datetime.utcnow()
    )
    
    return report


@router.get("/governance/dashboard")
async def get_governance_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["admin", "researcher"])),
):
    """
    Get governance dashboard summary.
    
    **Admin/Researcher Only**
    """
    governance_service = GovernanceService(db)
    security_service = SecurityService(db)
    privacy_service = PrivacyService(db)
    
    # Get pending approvals
    pending = governance_service.get_pending_approvals(limit=5)
    
    # Get open security alerts
    alerts = security_service.get_open_alerts(limit=5)
    
    # Get retention status
    retention = privacy_service.get_retention_status()
    
    # Get compliance score
    report = governance_service.generate_compliance_report()
    
    return {
        "pending_approvals": {
            "count": len(pending),
            "critical_risk": sum(1 for c in pending if c.get("risk_level") == "critical"),
            "high_risk": sum(1 for c in pending if c.get("risk_level") == "high")
        },
        "security_alerts": {
            "count": len(alerts),
            "critical": sum(1 for a in alerts if a.get("severity") == "critical"),
            "high": sum(1 for a in alerts if a.get("severity") == "high")
        },
        "compliance": report.get("compliance_score", {}),
        "data_retention": {
            table: status.get("expired_records", 0) 
            for table, status in retention.items() 
            if isinstance(status, dict) and "expired_records" in status
        }
    }

