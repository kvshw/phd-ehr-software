#!/usr/bin/env python3
"""
Add vitals and labs data to existing patients
Makes the patient data more realistic for testing
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import backend modules
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app" / "backend"))

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from core.database import SessionLocal
from services.vital_service import VitalService
from services.lab_service import LabService
from schemas.vital import VitalCreate
from schemas.lab import LabCreate
from models.patient import Patient
import random
from datetime import datetime, timedelta

# Lab types and their normal ranges
LAB_TYPES = {
    "Glucose": {"normal_range": "70-100", "unit": "mg/dL"},
    "Hemoglobin": {"normal_range": "12-16", "unit": "g/dL"},
    "Hematocrit": {"normal_range": "36-48", "unit": "%"},
    "White Blood Cell Count": {"normal_range": "4.5-11.0", "unit": "K/μL"},
    "Platelet Count": {"normal_range": "150-450", "unit": "K/μL"},
    "Creatinine": {"normal_range": "0.6-1.2", "unit": "mg/dL"},
    "BUN": {"normal_range": "7-20", "unit": "mg/dL"},
    "Sodium": {"normal_range": "136-145", "unit": "mEq/L"},
    "Potassium": {"normal_range": "3.5-5.0", "unit": "mEq/L"},
    "Chloride": {"normal_range": "98-107", "unit": "mEq/L"},
    "CO2": {"normal_range": "22-28", "unit": "mEq/L"},
    "ALT": {"normal_range": "7-56", "unit": "U/L"},
    "AST": {"normal_range": "10-40", "unit": "U/L"},
    "Total Cholesterol": {"normal_range": "<200", "unit": "mg/dL"},
    "LDL": {"normal_range": "<100", "unit": "mg/dL"},
    "HDL": {"normal_range": ">40", "unit": "mg/dL"},
    "Triglycerides": {"normal_range": "<150", "unit": "mg/dL"},
    "Troponin": {"normal_range": "<0.04", "unit": "ng/mL"},
    "BNP": {"normal_range": "<100", "unit": "pg/mL"},
    "D-Dimer": {"normal_range": "<0.5", "unit": "μg/mL"},
}


def generate_realistic_vitals(age: int, has_condition: bool = False):
    """Generate realistic vital signs based on age and condition"""
    # Base values vary by age
    if age < 30:
        hr_base = random.randint(60, 90)
        bp_sys_base = random.randint(100, 120)
        bp_dia_base = random.randint(60, 80)
    elif age < 50:
        hr_base = random.randint(65, 95)
        bp_sys_base = random.randint(110, 130)
        bp_dia_base = random.randint(65, 85)
    else:
        hr_base = random.randint(70, 100)
        bp_sys_base = random.randint(120, 140)
        bp_dia_base = random.randint(70, 90)
    
    # If patient has a condition, add some abnormalities
    if has_condition:
        hr = hr_base + random.randint(-10, 20)  # Can be elevated
        bp_sys = bp_sys_base + random.randint(0, 30)  # Can be high
        bp_dia = bp_dia_base + random.randint(0, 15)
        spo2 = random.uniform(92, 98)  # Can be low
        rr = random.randint(18, 28)  # Can be elevated
        temp = random.uniform(37.0, 39.5)  # Can have fever
        pain = random.randint(3, 8)  # Can have pain
    else:
        hr = hr_base + random.randint(-5, 10)
        bp_sys = bp_sys_base + random.randint(-5, 10)
        bp_dia = bp_dia_base + random.randint(-5, 5)
        spo2 = random.uniform(96, 100)
        rr = random.randint(12, 20)
        temp = random.uniform(36.1, 37.2)
        pain = random.randint(0, 3)
    
    return {
        "hr": max(40, min(150, hr)),  # Clamp to reasonable range
        "bp_sys": max(80, min(200, bp_sys)),
        "bp_dia": max(50, min(120, bp_dia)),
        "spo2": round(min(100, max(85, spo2)), 1),
        "rr": max(8, min(35, rr)),
        "temp": round(temp, 1),
        "pain": min(10, max(0, pain)),
    }


def generate_lab_value(lab_type: str, has_abnormality: bool = False):
    """Generate realistic lab value"""
    lab_info = LAB_TYPES[lab_type]
    normal_range = lab_info["normal_range"]
    
    # Parse normal range
    if "<" in normal_range:
        max_val = float(normal_range.replace("<", "").strip())
        if has_abnormality:
            value = random.uniform(max_val * 1.1, max_val * 2.0)  # Above normal
        else:
            value = random.uniform(max_val * 0.5, max_val * 0.95)  # Below max
    elif ">" in normal_range:
        min_val = float(normal_range.replace(">", "").strip())
        if has_abnormality:
            value = random.uniform(min_val * 0.3, min_val * 0.9)  # Below normal
        else:
            value = random.uniform(min_val * 1.05, min_val * 1.5)  # Above min
    else:
        # Range format like "70-100"
        parts = normal_range.split("-")
        min_val = float(parts[0].strip())
        max_val = float(parts[1].strip())
        if has_abnormality:
            # 50% chance high, 50% chance low
            if random.random() > 0.5:
                value = random.uniform(max_val * 1.1, max_val * 1.5)  # High
            else:
                value = random.uniform(min_val * 0.5, min_val * 0.9)  # Low
        else:
            value = random.uniform(min_val, max_val)
    
    return round(value, 2)


def add_vitals_to_patient(db: Session, patient: Patient, num_vitals: int = 5):
    """Add vitals data to a patient"""
    has_condition = patient.primary_diagnosis is not None
    
    # Generate vitals over the past 7 days
    now = datetime.utcnow()
    vitals_created = 0
    
    for i in range(num_vitals):
        # Spread vitals over past 7 days
        hours_ago = random.randint(0, 7 * 24)
        timestamp = now - timedelta(hours=hours_ago)
        
        vitals_data = generate_realistic_vitals(patient.age, has_condition)
        
        vital_data = VitalCreate(
            patient_id=patient.id,
            timestamp=timestamp,
            **vitals_data
        )
        
        try:
            VitalService.create_vital(db, vital_data)
            vitals_created += 1
        except Exception as e:
            print(f"    ⚠ Failed to create vital: {str(e)}")
    
    return vitals_created


def add_labs_to_patient(db: Session, patient: Patient, num_labs: int = 8):
    """Add lab data to a patient"""
    has_condition = patient.primary_diagnosis is not None
    
    # Select random lab types
    selected_labs = random.sample(list(LAB_TYPES.keys()), min(num_labs, len(LAB_TYPES)))
    
    # Generate labs over the past 14 days
    now = datetime.utcnow()
    labs_created = 0
    
    for lab_type in selected_labs:
        # Random timestamp in past 14 days
        days_ago = random.randint(0, 14)
        hours_ago = random.randint(0, 23)
        timestamp = now - timedelta(days=days_ago, hours=hours_ago)
        
        # 30% chance of abnormality if patient has condition
        has_abnormality = has_condition and random.random() < 0.3
        
        value = generate_lab_value(lab_type, has_abnormality)
        lab_info = LAB_TYPES[lab_type]
        
        lab_data = LabCreate(
            patient_id=patient.id,
            timestamp=timestamp,
            lab_type=lab_type,
            value=value,
            normal_range=lab_info["normal_range"],
        )
        
        try:
            LabService.create_lab(db, lab_data)
            labs_created += 1
        except Exception as e:
            print(f"    ⚠ Failed to create lab: {str(e)}")
    
    return labs_created


def add_data_to_all_patients(
    db: Session,
    vitals_per_patient: int = 5,
    labs_per_patient: int = 8,
    skip_existing: bool = True
):
    """Add vitals and labs to all patients"""
    # Get all patients
    stmt = select(Patient)
    result = db.execute(stmt)
    patients = result.scalars().all()
    
    if not patients:
        print("No patients found in database")
        return
    
    print(f"Found {len(patients)} patients")
    print("=" * 60)
    
    total_vitals = 0
    total_labs = 0
    
    for i, patient in enumerate(patients, 1):
        print(f"\n[{i}/{len(patients)}] Processing: {patient.name} (Age: {patient.age}, {patient.sex})")
        
        # Check if patient already has vitals/labs (if skip_existing)
        if skip_existing:
            from models.vital import Vital
            from models.lab import Lab
            existing_vitals = db.execute(
                select(func.count(Vital.id)).where(Vital.patient_id == patient.id)
            ).scalar_one()
            existing_labs = db.execute(
                select(func.count(Lab.id)).where(Lab.patient_id == patient.id)
            ).scalar_one()
            
            if existing_vitals > 0 or existing_labs > 0:
                print(f"  ⚠ Skipping (already has {existing_vitals} vitals, {existing_labs} labs)")
                continue
        
        # Add vitals
        vitals_count = add_vitals_to_patient(db, patient, vitals_per_patient)
        total_vitals += vitals_count
        print(f"  ✓ Added {vitals_count} vitals records")
        
        # Add labs
        labs_count = add_labs_to_patient(db, patient, labs_per_patient)
        total_labs += labs_count
        print(f"  ✓ Added {labs_count} lab records")
    
    db.commit()
    
    print("\n" + "=" * 60)
    print(f"✅ Complete!")
    print(f"   Total vitals added: {total_vitals}")
    print(f"   Total labs added: {total_labs}")
    print("=" * 60)


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Add vitals and labs data to patients")
    parser.add_argument(
        "--vitals",
        type=int,
        default=5,
        help="Number of vitals records per patient (default: 5)",
    )
    parser.add_argument(
        "--labs",
        type=int,
        default=8,
        help="Number of lab records per patient (default: 8)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Add data even if patient already has vitals/labs",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        print("=" * 60)
        print("Adding Vitals and Labs Data to Patients")
        print("=" * 60)
        add_data_to_all_patients(
            db,
            vitals_per_patient=args.vitals,
            labs_per_patient=args.labs,
            skip_existing=not args.force
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()

