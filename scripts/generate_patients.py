#!/usr/bin/env python3
"""
Generate synthetic patients for testing
Run this script to populate the database with test patients
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import backend modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app" / "backend"))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from services.patient_service import PatientService
from schemas.patient import PatientCreate
import random

# Synthetic patient data
PATIENT_NAMES = [
    "John Smith", "Jane Doe", "Robert Johnson", "Emily Davis", "Michael Brown",
    "Sarah Wilson", "David Martinez", "Jessica Anderson", "Christopher Taylor",
    "Amanda Thomas", "Daniel Jackson", "Melissa White", "Matthew Harris",
    "Michelle Martin", "Andrew Thompson", "Laura Garcia", "James Martinez",
    "Ashley Robinson", "Joshua Clark", "Stephanie Rodriguez", "Ryan Lewis",
    "Nicole Lee", "Kevin Walker", "Rebecca Hall", "Brian Allen", "Kimberly Young",
    "Jason King", "Angela Wright", "Eric Lopez", "Samantha Hill", "Justin Scott",
    "Megan Green", "Brandon Adams", "Rachel Baker", "Tyler Gonzalez", "Lauren Nelson",
    "Jacob Carter", "Brittany Mitchell", "Nathan Perez", "Amber Roberts",
    "Zachary Turner", "Heather Phillips", "Kyle Campbell", "Crystal Parker",
    "Aaron Evans", "Tiffany Edwards", "Sean Collins", "Monica Stewart",
    "Travis Sanchez", "Danielle Morris", "Derek Rogers", "Jasmine Reed",
    "Cody Cook", "Katherine Morgan", "Blake Bell", "Stephanie Murphy",
    "Adam Bailey", "Christina Rivera", "Jordan Cooper", "Vanessa Richardson",
    "Austin Cox", "Maria Howard", "Ethan Ward", "Lisa Torres", "Connor Peterson",
    "Nicole Gray", "Lucas Ramirez", "Amanda James", "Noah Watson", "Rachel Brooks",
    "Mason Kelly", "Samantha Sanders", "Logan Price", "Michelle Bennett",
    "Aiden Wood", "Lauren Barnes", "Carter Ross", "Brittany Henderson",
    "Owen Coleman", "Jessica Jenkins", "Lucas Perry", "Amanda Powell",
    "Mason Long", "Stephanie Patterson", "Ethan Hughes", "Melissa Flores",
    "Aiden Washington", "Rachel Butler", "Carter Simmons", "Michelle Foster",
    "Owen Gonzales", "Jessica Bryant", "Lucas Alexander", "Amanda Russell",
]

DIAGNOSES = [
    "Post-operative recovery",
    "Pneumonia",
    "Hypertension",
    "Type 2 Diabetes",
    "Acute kidney injury",
    "Sepsis",
    "Dehydration",
    "Anemia",
    "Hypoxia",
    "Fever of unknown origin",
    "Chronic obstructive pulmonary disease",
    "Congestive heart failure",
    "Atrial fibrillation",
    "Deep vein thrombosis",
    "Pulmonary embolism",
    "Acute myocardial infarction",
    "Stroke",
    "Gastroenteritis",
    "Urinary tract infection",
    "Cellulitis",
    "Osteoarthritis",
    "Rheumatoid arthritis",
    "Asthma",
    "Bronchitis",
    "Sinusitis",
    "Migraine",
    "Depression",
    "Anxiety disorder",
    "Sleep apnea",
    "Obesity",
]


def generate_patients(num_patients: int = 20, db: Session = None):
    """Generate synthetic patients"""
    if db is None:
        db = SessionLocal()
        try:
            return generate_patients(num_patients, db)
        finally:
            db.close()

    created = 0
    for i in range(num_patients):
        # Random selection
        name = random.choice(PATIENT_NAMES)
        age = random.randint(18, 85)
        sex = random.choice(['M', 'F', 'Other'])
        diagnosis = random.choice(DIAGNOSES) if random.random() > 0.2 else None  # 80% have diagnosis

        patient_data = PatientCreate(
            name=name,
            age=age,
            sex=sex,
            primary_diagnosis=diagnosis,
        )

        try:
            patient = PatientService.create_patient(db, patient_data)
            created += 1
            print(f"✓ Created patient {i+1}/{num_patients}: {patient.name} (ID: {patient.id})")
        except Exception as e:
            print(f"✗ Failed to create patient {i+1}: {str(e)}")

    db.commit()
    print(f"\n✅ Successfully created {created} out of {num_patients} patients")
    return created


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate synthetic patients")
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="Number of patients to generate (default: 20)",
    )
    args = parser.parse_args()

    print(f"Generating {args.count} synthetic patients...")
    print("-" * 50)
    generate_patients(args.count)

