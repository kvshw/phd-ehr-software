#!/usr/bin/env python3
"""
Generate Feedback to Trigger Learning Events
Creates feedback with very high or very low acceptance rates to demonstrate self-adaptive learning.

Usage:
    python3 scripts/generate_learning_trigger_feedback.py --scenario high
    python3 scripts/generate_learning_trigger_feedback.py --scenario low
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
import random
import uuid

# Add backend to path
backend_path = Path(__file__).parent.parent / "app" / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from core.database import get_db
from models.suggestion_feedback import SuggestionFeedback
from models.suggestion import Suggestion
from models.user import User
from models.patient import Patient


def generate_learning_feedback(
    db: Session,
    scenario: str = "high",  # "high" or "low"
    count: int = 15,
    source: str = "ai_model",
):
    """
    Generate feedback that will trigger learning events
    
    Args:
        db: Database session
        scenario: "high" (80%+ acceptance) or "low" (20%- acceptance)
        count: Number of feedback items (need at least 10)
        source: Suggestion source to target
    """
    # Get available users and patients
    clinicians = db.query(User).filter(User.role.in_(["clinician", "admin"])).all()
    if not clinicians:
        print("[ERROR] No clinicians found.")
        return
    
    patients = db.query(Patient).all()
    if not patients:
        print("[ERROR] No patients found.")
        return
    
    # Get suggestions for the specified source
    suggestions = db.query(Suggestion).filter(Suggestion.source == source).limit(20).all()
    
    if not suggestions:
        print(f"[WARNING]  No suggestions found for source '{source}'. Creating sample suggestions...")
        for i in range(10):
            patient = random.choice(patients)
            suggestion = Suggestion(
                id=uuid.uuid4(),
                patient_id=patient.id,
                type="diagnosis",
                text=f"Sample {source} suggestion {i+1}",
                source=source,
                explanation=f"Test suggestion for {source}",
                confidence=round(random.uniform(0.5, 0.9), 2),
            )
            db.add(suggestion)
        db.commit()
        suggestions = db.query(Suggestion).filter(Suggestion.source == source).all()
    
    print(f"\n[DATA] Generating {count} feedback items for '{source}' source...")
    print(f"   Scenario: {scenario.upper()} acceptance rate")
    print(f"   Target: {'>80% accept' if scenario == 'high' else '<20% accept'}\n")
    
    created = 0
    start_date = datetime.now(timezone.utc) - timedelta(days=7)
    
    for i in range(count):
        clinician = random.choice(clinicians)
        suggestion = random.choice(suggestions)
        patient = db.query(Patient).filter(Patient.id == suggestion.patient_id).first()
        
        # Determine action based on scenario
        if scenario == "high":
            # 80% accept, 15% ignore, 5% not_relevant
            r = random.random()
            if r < 0.80:
                action = "accept"
            elif r < 0.95:
                action = "ignore"
            else:
                action = "not_relevant"
        else:  # low
            # 15% accept, 20% ignore, 65% not_relevant
            r = random.random()
            if r < 0.15:
                action = "accept"
            elif r < 0.35:
                action = "ignore"
            else:
                action = "not_relevant"
        
        # Generate timestamp (within last 7 days)
        days_ago = random.randint(0, 6)
        hours_ago = random.randint(0, 23)
        created_at = datetime.now(timezone.utc) - timedelta(
            days=days_ago,
            hours=hours_ago
        )
        
        # Generate ratings (correlated with action)
        if action == "accept":
            clinical_relevance = random.randint(4, 5)
            agreement_rating = random.randint(4, 5)
            explanation_quality = random.randint(4, 5)
            would_act_on = random.randint(4, 5)
        elif action == "ignore":
            clinical_relevance = random.randint(2, 4)
            agreement_rating = random.randint(2, 4)
            explanation_quality = random.randint(2, 4)
            would_act_on = random.randint(1, 3)
        else:  # not_relevant
            clinical_relevance = random.randint(1, 2)
            agreement_rating = random.randint(1, 2)
            explanation_quality = random.randint(1, 3)
            would_act_on = random.randint(1, 2)
        
        feedback = SuggestionFeedback(
            suggestion_id=suggestion.id,
            patient_id=patient.id,
            clinician_id=clinician.id,
            action=action,
            suggestion_text=suggestion.text,
            suggestion_source=source,
            suggestion_confidence=suggestion.confidence,
            suggestion_type=suggestion.type,
            clinical_relevance=clinical_relevance,
            agreement_rating=agreement_rating,
            explanation_quality=explanation_quality,
            would_act_on=would_act_on,
            was_helpful=(action == "accept"),
            patient_age=patient.age,
            patient_sex=patient.sex,
            patient_diagnosis=patient.primary_diagnosis,
            created_at=created_at,
        )
        
        db.add(feedback)
        created += 1
    
    db.commit()
    
    print(f"[SUCCESS] Created {created} feedback items")
    print(f"\n[ACTION] Expected acceptance rate: {'~80%' if scenario == 'high' else '~15%'}")
    print(f"\n[METRICS] Next steps:")
    print(f"   1. Wait a few seconds for learning to trigger")
    print(f"   2. Go to http://localhost:3000/feedback/analytics")
    print(f"   3. Check 'Learning Events History' section")
    print(f"   4. Check 'Confidence Adjustments' section")
    print(f"   5. You should see: {'+5%' if scenario == 'high' else '-5%'} adjustment for {source}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate feedback to trigger learning")
    parser.add_argument(
        "--scenario",
        choices=["high", "low"],
        default="high",
        help="High acceptance (80%+) or low acceptance (15%-)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=15,
        help="Number of feedback items (default: 15, need at least 10)"
    )
    parser.add_argument(
        "--source",
        default="ai_model",
        choices=["rules", "ai_model", "hybrid", "vital_risk", "image_analysis"],
        help="Suggestion source to target"
    )
    
    args = parser.parse_args()
    
    if args.count < 10:
        print("[WARNING]  Warning: Need at least 10 feedback items to trigger learning")
        print("   Increasing count to 10...")
        args.count = 10
    
    db = next(get_db())
    
    try:
        generate_learning_feedback(
            db=db,
            scenario=args.scenario,
            count=args.count,
            source=args.source,
        )
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

