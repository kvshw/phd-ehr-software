#!/usr/bin/env python3
"""
Generate Test Feedback Data
Creates realistic clinician feedback for testing the analytics dashboard.

Usage:
    python3 scripts/generate_test_feedback.py --count 50 --days 30
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

# Actions and their probabilities (realistic distribution)
ACTIONS = {
    "accept": 0.55,      # 55% accepted
    "ignore": 0.30,     # 30% ignored
    "not_relevant": 0.15,  # 15% not relevant
}

# Suggestion sources
SOURCES = ["rules", "ai_model", "hybrid", "vital_risk", "image_analysis"]

# Realistic suggestion types
SUGGESTION_TYPES = [
    "diagnosis",
    "vital_risk",
    "lab_analysis",
    "image_analysis",
    "medication_review",
    "follow_up",
]


def weighted_choice(choices):
    """Choose an action based on weighted probabilities"""
    r = random.random()
    cumulative = 0
    for action, weight in choices.items():
        cumulative += weight
        if r <= cumulative:
            return action
    return list(choices.keys())[0]


def generate_feedback(
    db: Session,
    count: int = 50,
    days_back: int = 30,
    clinician_id: uuid.UUID = None,
    patient_id: uuid.UUID = None,
):
    """
    Generate test feedback data
    
    Args:
        db: Database session
        count: Number of feedback items to create
        days_back: How many days back to spread the feedback
        clinician_id: Optional specific clinician (otherwise picks random)
        patient_id: Optional specific patient (otherwise picks random)
    """
    # Get available users (clinicians)
    clinicians = db.query(User).filter(User.role.in_(["clinician", "admin"])).all()
    if not clinicians:
        print("❌ No clinicians found in database. Please create at least one clinician user.")
        return
    
    # Get available patients
    patients = db.query(Patient).all()
    if not patients:
        print("❌ No patients found in database. Please create at least one patient.")
        return
    
    # Get available suggestions (or create some if none exist)
    suggestions = db.query(Suggestion).limit(100).all()
    
    if not suggestions:
        print("⚠️  No suggestions found. Creating sample suggestions first...")
        # Create some sample suggestions
        for i in range(10):
            patient = random.choice(patients)
            suggestion = Suggestion(
                id=uuid.uuid4(),
                patient_id=patient.id,
                type=random.choice(SUGGESTION_TYPES),
                text=f"Sample suggestion {i+1}: Consider monitoring patient vitals",
                source=random.choice(SOURCES),
                explanation=f"This is a test suggestion for feedback generation",
                confidence=round(random.uniform(0.5, 0.9), 2),
            )
            db.add(suggestion)
        db.commit()
        suggestions = db.query(Suggestion).all()
        print(f"✅ Created {len(suggestions)} sample suggestions")
    
    print(f"\n📊 Generating {count} feedback items over the last {days_back} days...")
    print(f"   Using {len(clinicians)} clinicians and {len(patients)} patients")
    print(f"   Using {len(suggestions)} suggestions\n")
    
    created = 0
    start_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    for i in range(count):
        # Pick random clinician (or use provided)
        clinician = clinician_id and db.query(User).filter(User.id == clinician_id).first() or random.choice(clinicians)
        
        # Pick random suggestion
        suggestion = random.choice(suggestions)
        
        # Get patient from suggestion
        patient = db.query(Patient).filter(Patient.id == suggestion.patient_id).first()
        
        # Pick action based on weighted probabilities
        action = weighted_choice(ACTIONS)
        
        # Generate timestamp (spread over the time period)
        days_ago = random.randint(0, days_back)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        created_at = datetime.now(timezone.utc) - timedelta(
            days=days_ago,
            hours=hours_ago,
            minutes=minutes_ago
        )
        
        # Generate ratings (only for some feedback - more realistic)
        has_ratings = random.random() < 0.4  # 40% have detailed ratings
        
        clinical_relevance = None
        agreement_rating = None
        explanation_quality = None
        would_act_on = None
        
        if has_ratings:
            # Ratings tend to be higher for accepted suggestions
            if action == "accept":
                clinical_relevance = random.randint(4, 5)
                agreement_rating = random.randint(4, 5)
                explanation_quality = random.randint(3, 5)
                would_act_on = random.randint(4, 5)
            elif action == "ignore":
                clinical_relevance = random.randint(2, 4)
                agreement_rating = random.randint(2, 4)
                explanation_quality = random.randint(2, 4)
                would_act_on = random.randint(1, 3)
            else:  # not_relevant
                clinical_relevance = random.randint(1, 3)
                agreement_rating = random.randint(1, 3)
                explanation_quality = random.randint(1, 3)
                would_act_on = random.randint(1, 2)
        
        # Generate comments (only for some feedback)
        comment = None
        improvement = None
        if random.random() < 0.2:  # 20% have comments
            comments_pool = [
                "Helpful suggestion, aligned with clinical judgment",
                "Good catch on the lab values",
                "Would like more context on this recommendation",
                "Not applicable to this patient's condition",
                "Timing of suggestion was good",
                "Could use more explanation",
            ]
            comment = random.choice(comments_pool)
        
        if random.random() < 0.1:  # 10% have improvement suggestions
            improvements_pool = [
                "Consider adding more context about patient history",
                "Would be helpful to see similar cases",
                "Suggestion came too late in the workflow",
                "Good suggestion but needs better timing",
            ]
            improvement = random.choice(improvements_pool)
        
        # Create feedback
        feedback = SuggestionFeedback(
            suggestion_id=suggestion.id,
            patient_id=patient.id,
            clinician_id=clinician.id,
            action=action,
            suggestion_text=suggestion.text,
            suggestion_source=suggestion.source,
            suggestion_confidence=suggestion.confidence,
            suggestion_type=suggestion.type,
            clinical_relevance=clinical_relevance,
            agreement_rating=agreement_rating,
            explanation_quality=explanation_quality,
            would_act_on=would_act_on,
            clinician_comment=comment,
            improvement_suggestion=improvement,
            was_helpful=(action == "accept"),
            patient_age=patient.age,
            patient_sex=patient.sex,
            patient_diagnosis=patient.primary_diagnosis,
            created_at=created_at,
        )
        
        db.add(feedback)
        created += 1
        
        if (i + 1) % 10 == 0:
            print(f"   Created {i + 1}/{count} feedback items...")
    
    db.commit()
    
    print(f"\n✅ Successfully created {created} feedback items!")
    print(f"\n📈 Expected distribution:")
    for action, weight in ACTIONS.items():
        expected = int(count * weight)
        print(f"   {action}: ~{expected} items ({weight*100:.0f}%)")
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Go to http://localhost:3000/feedback/analytics")
    print(f"   2. You should now see data in the dashboard!")
    print(f"   3. Try different time periods (7, 14, 30, 90 days)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test feedback data")
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of feedback items to create (default: 50)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Spread feedback over this many days (default: 30)"
    )
    parser.add_argument(
        "--clinician-id",
        type=str,
        help="Specific clinician ID to use (optional)"
    )
    parser.add_argument(
        "--patient-id",
        type=str,
        help="Specific patient ID to use (optional)"
    )
    
    args = parser.parse_args()
    
    # Get database session
    db = next(get_db())
    
    try:
        clinician_uuid = uuid.UUID(args.clinician_id) if args.clinician_id else None
        patient_uuid = uuid.UUID(args.patient_id) if args.patient_id else None
        
        generate_feedback(
            db=db,
            count=args.count,
            days_back=args.days,
            clinician_id=clinician_uuid,
            patient_id=patient_uuid,
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

