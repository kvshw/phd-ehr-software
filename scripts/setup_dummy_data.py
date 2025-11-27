#!/usr/bin/env python3
"""
Setup dummy data for the EHR system
- Removes duplicate patients (same names)
- Generates diverse synthetic patient data
- Adds vitals, labs, and other data for realistic testing
"""
import sys
import os
from pathlib import Path
from collections import Counter

# Add parent directory to path to import backend modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app" / "backend"))

from sqlalchemy.orm import Session
from sqlalchemy import select, func, delete
from core.database import SessionLocal
from services.patient_service import PatientService
from schemas.patient import PatientCreate
from models.patient import Patient
import random
from datetime import datetime, timedelta

# Diverse unique patient names (no duplicates)
UNIQUE_PATIENT_NAMES = [
    "Alexandra Chen", "Benjamin Rodriguez", "Charlotte Kim", "David Thompson",
    "Emma Martinez", "Felix Anderson", "Grace Lee", "Henry Wilson",
    "Isabella Garcia", "James Park", "Katherine Brown", "Liam O'Connor",
    "Maya Patel", "Nathan Singh", "Olivia Taylor", "Patrick Murphy",
    "Quinn Johnson", "Rachel White", "Samuel Davis", "Tara Williams",
    "Uma Jackson", "Victor Lopez", "Wendy Harris", "Xavier Moore",
    "Yara Ali", "Zoe Mitchell", "Aaron Foster", "Bella Clark",
    "Caleb Young", "Diana King", "Ethan Wright", "Fiona Green",
    "Gabriel Adams", "Hannah Baker", "Isaac Hill", "Julia Scott",
    "Kai Turner", "Luna Phillips", "Mason Campbell", "Nora Parker",
    "Owen Evans", "Penelope Edwards", "Quinn Collins", "Riley Stewart",
    "Sophia Sanchez", "Tyler Morris", "Victoria Rogers", "William Reed",
    "Ximena Cook", "Yuki Morgan", "Zara Bell", "Aiden Murphy",
    "Brooke Bailey", "Carter Rivera", "Delilah Cooper", "Eli Richardson",
    "Freya Cox", "Grayson Howard", "Harper Ward", "Ivy Torres",
    "Jasper Peterson", "Kira Gray", "Leo Ramirez", "Mia James",
    "Noah Watson", "Opal Brooks", "Phoenix Kelly", "Quinn Sanders",
    "Ruby Price", "Sage Bennett", "Theo Wood", "Uma Barnes",
    "Violet Ross", "Wren Henderson", "Xander Coleman", "Yara Jenkins",
    "Zane Perry", "Aria Powell", "Blake Long", "Cora Patterson",
    "Dante Hughes", "Elena Flores", "Finn Washington", "Gia Butler",
    "Hugo Simmons", "Iris Foster", "Jade Alexander", "Kai Russell",
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
    "Hyperthyroidism",
    "Hypothyroidism",
    "Chronic pain",
    "Fibromyalgia",
    "Multiple sclerosis",
]

# Past Medical History templates
PMH_TEMPLATES = [
    "Hypertension, Type 2 Diabetes",
    "Asthma, Allergic rhinitis",
    "Obesity, Sleep apnea",
    "Chronic kidney disease stage 3",
    "Coronary artery disease, Hyperlipidemia",
    "Rheumatoid arthritis, Osteoporosis",
    "Depression, Anxiety",
    "COPD, Chronic bronchitis",
    "Atrial fibrillation, Hypertension",
    "Type 1 Diabetes, Diabetic neuropathy",
    "Hypothyroidism, Anemia",
    "Migraine, Tension headaches",
    "GERD, Hiatal hernia",
    "Chronic back pain, Degenerative disc disease",
    "None significant",
]

# Past Surgical History templates
PSH_TEMPLATES = [
    "Appendectomy (2010), Cholecystectomy (2015)",
    "Total knee replacement (2018)",
    "Cataract surgery bilateral (2020)",
    "Hernia repair (2012)",
    "Hip replacement (2019)",
    "Coronary artery bypass graft (2016)",
    "Hysterectomy (2014)",
    "Prostatectomy (2017)",
    "Laminectomy (2021)",
    "None",
]

# Family History templates
FAMILY_HISTORY_TEMPLATES = [
    "Father: Heart disease, Diabetes. Mother: Hypertension, Breast cancer",
    "Mother: Type 2 Diabetes, Obesity",
    "Father: Stroke, Hypertension. Maternal grandmother: Alzheimer's",
    "Paternal grandfather: Colon cancer. Father: Prostate cancer",
    "Mother: Rheumatoid arthritis. Sister: Lupus",
    "Both parents: Hypertension, Hyperlipidemia",
    "Maternal family: Strong history of diabetes",
    "Paternal grandfather: Heart attack at age 55",
    "Mother: Breast cancer (age 60). Sister: Ovarian cancer (age 45)",
    "No significant family history",
]

# Social History templates
SOCIAL_HISTORY_TEMPLATES = [
    "Non-smoker, Occasional alcohol (1-2 drinks/week), Works as teacher",
    "Former smoker (quit 5 years ago), No alcohol, Retired",
    "Current smoker (1 pack/day, 20 years), Social drinker, Construction worker",
    "Never smoked, Non-drinker, Office worker, Sedentary lifestyle",
    "Former smoker (quit 10 years ago), Occasional wine, Exercise 3x/week",
    "Non-smoker, No alcohol, Works from home, Minimal exercise",
    "Social smoker (occasional), Moderate alcohol (3-4 drinks/week), Active lifestyle",
    "Non-smoker, Non-drinker, Retired, Daily walks",
    "Former smoker (quit 2 years ago), No alcohol, Gym 4x/week",
    "Non-smoker, Occasional alcohol, Sedentary job, No regular exercise",
]


def remove_duplicate_patients(db: Session):
    """Remove patients with duplicate names, keeping the most recent one"""
    print("Checking for duplicate patients...")
    
    # Find duplicate names
    stmt = select(Patient.name, func.count(Patient.id).label('count')).group_by(Patient.name).having(func.count(Patient.id) > 1)
    result = db.execute(stmt)
    duplicates = result.all()
    
    if not duplicates:
        print("✓ No duplicate patients found")
        return 0
    
    removed_count = 0
    for name, count in duplicates:
        print(f"  Found {count} patients named '{name}'")
        
        # Get all patients with this name, ordered by created_at (oldest first)
        stmt = select(Patient).where(Patient.name == name).order_by(Patient.created_at.asc())
        result = db.execute(stmt)
        patients = result.scalars().all()
        
        # Keep the most recent one, delete the rest
        patients_to_delete = patients[:-1]  # All except the last one
        
        for patient in patients_to_delete:
            db.delete(patient)
            removed_count += 1
            print(f"    ✗ Deleted duplicate: {patient.name} (ID: {patient.id}, Created: {patient.created_at})")
    
    db.commit()
    print(f"\n✓ Removed {removed_count} duplicate patient(s)")
    return removed_count


def generate_diverse_patients(num_patients: int = 30, db: Session = None):
    """Generate diverse synthetic patients with unique names"""
    if db is None:
        db = SessionLocal()
        try:
            return generate_diverse_patients(num_patients, db)
        finally:
            db.close()

    # Shuffle names to get random selection
    available_names = UNIQUE_PATIENT_NAMES.copy()
    random.shuffle(available_names)
    
    # Check existing patients to avoid duplicates
    existing_patients = db.execute(select(Patient.name)).scalars().all()
    existing_names = set(existing_patients)
    
    created = 0
    skipped = 0
    
    for i in range(min(num_patients, len(available_names))):
        name = available_names[i]
        
        # Skip if name already exists
        if name in existing_names:
            print(f"⚠ Skipping '{name}' - already exists")
            skipped += 1
            continue
        
        # Generate diverse patient data
        age = random.randint(18, 85)
        sex = random.choice(['M', 'F', 'Other'])
        
        # 75% have diagnosis
        diagnosis = random.choice(DIAGNOSES) if random.random() > 0.25 else None
        
        # Add history data for more realistic patients
        pmh = random.choice(PMH_TEMPLATES) if random.random() > 0.3 else None
        psh = random.choice(PSH_TEMPLATES) if random.random() > 0.4 else None
        family_history = random.choice(FAMILY_HISTORY_TEMPLATES) if random.random() > 0.3 else None
        social_history = random.choice(SOCIAL_HISTORY_TEMPLATES) if random.random() > 0.2 else None
        
        patient_data = PatientCreate(
            name=name,
            age=age,
            sex=sex,
            primary_diagnosis=diagnosis,
            past_medical_history=pmh,
            past_surgical_history=psh,
            family_history=family_history,
            social_history=social_history,
        )

        try:
            patient = PatientService.create_patient(db, patient_data)
            existing_names.add(name)  # Track created name
            created += 1
            print(f"✓ Created patient {created}/{num_patients}: {patient.name} (Age: {age}, {sex})")
        except Exception as e:
            print(f"✗ Failed to create patient {i+1}: {str(e)}")

    db.commit()
    print(f"\n✅ Successfully created {created} new patients")
    if skipped > 0:
        print(f"⚠ Skipped {skipped} patients (duplicates)")
    return created


def main():
    """Main function to setup dummy data"""
    import argparse

    parser = argparse.ArgumentParser(description="Setup dummy data for EHR system")
    parser.add_argument(
        "--count",
        type=int,
        default=30,
        help="Number of new patients to generate (default: 30)",
    )
    parser.add_argument(
        "--remove-duplicates",
        action="store_true",
        help="Remove duplicate patients before generating new ones",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        print("=" * 60)
        print("EHR Dummy Data Setup")
        print("=" * 60)
        
        if args.remove_duplicates:
            print("\n1. Removing duplicate patients...")
            remove_duplicate_patients(db)
        
        print(f"\n2. Generating {args.count} diverse synthetic patients...")
        print("-" * 60)
        generate_diverse_patients(args.count, db)
        
        # Show final count
        total = db.execute(select(func.count(Patient.id))).scalar_one()
        print(f"\n" + "=" * 60)
        print(f"✅ Setup complete! Total patients in database: {total}")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()

