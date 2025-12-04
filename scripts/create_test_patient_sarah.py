"""
Create test patient "Sarah Chen" for brain health user story testing
This patient has complex brain health case with all required data for testing
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
from uuid import uuid4

# Add backend directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "app" / "backend"))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.patient import Patient
from models.vital import Vital
from models.lab import Lab
from models.clinical_note import ClinicalNote
from models.problem import Problem
from models.medication import Medication
from models.allergy import Allergy
from models.conversation import ConversationSession, ConversationTranscript, ConversationAnalysis

def create_sarah_chen(db: Session):
    """Create Sarah Chen patient with complete brain health data"""
    
    print("Creating patient: Sarah Chen...")
    
    # Create patient
    patient = Patient(
        id=uuid4(),
        name="Sarah Chen",
        age=68,
        sex="F",
        primary_diagnosis="Mild Cognitive Impairment (MCI) with suspected progression to early-stage Alzheimer's Disease",
        past_medical_history="Hypertension (diagnosed 2010), Type 2 Diabetes (diagnosed 2015), Osteoarthritis (knees, diagnosed 2018)",
        past_surgical_history="Cholecystectomy (2012), Cataract surgery - right eye (2019)",
        family_history="Mother: Alzheimer's Disease (diagnosed age 75, deceased at 82). Father: Hypertension, Type 2 Diabetes. Sister: Breast cancer (age 60, in remission).",
        social_history="Widowed (husband passed 5 years ago). Lives alone in 2-bedroom apartment. Two adult children visit weekly. Former elementary school teacher (retired 10 years ago). Non-smoker, occasional alcohol (1-2 glasses wine/week). Limited exercise due to knee pain.",
        created_at=datetime.now(timezone.utc) - timedelta(days=180),
        updated_at=datetime.now(timezone.utc)
    )
    db.add(patient)
    db.commit()  # Commit patient first so foreign keys work
    db.refresh(patient)
    
    print(f"  ✓ Patient created: {patient.id}")
    
    # Create vitals (last 6 months, showing some concerning trends)
    # Note: Temperature in Celsius, convert from Fahrenheit: (F - 32) * 5/9
    vitals_data = [
        # 6 months ago
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=180), "bp_sys": 142, "bp_dia": 88, "hr": 78, "temp": 36.8, "rr": 16, "spo2": 98.0},
        # 4 months ago
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=120), "bp_sys": 145, "bp_dia": 90, "hr": 82, "temp": 36.7, "rr": 17, "spo2": 97.0},
        # 3 months ago
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=90), "bp_sys": 148, "bp_dia": 92, "hr": 85, "temp": 36.8, "rr": 16, "spo2": 98.0},
        # 2 months ago
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=60), "bp_sys": 150, "bp_dia": 94, "hr": 88, "temp": 36.9, "rr": 18, "spo2": 97.0},
        # 1 month ago
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=30), "bp_sys": 152, "bp_dia": 95, "hr": 90, "temp": 36.8, "rr": 17, "spo2": 96.0},
        # 2 weeks ago
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=14), "bp_sys": 155, "bp_dia": 96, "hr": 92, "temp": 36.9, "rr": 18, "spo2": 97.0},
        # Today
        {"timestamp": datetime.now(timezone.utc), "bp_sys": 158, "bp_dia": 98, "hr": 95, "temp": 36.8, "rr": 19, "spo2": 96.0},
    ]
    
    for vital_data in vitals_data:
        vital = Vital(
            id=uuid4(),
            patient_id=patient.id,
            **vital_data
        )
        db.add(vital)
    
    print(f"  ✓ Created {len(vitals_data)} vital records")
    
    # Create labs (mix of normal and abnormal, relevant to brain health)
    # Note: Lab model uses: lab_type, value, normal_range (no unit or status fields)
    labs_data = [
        # 6 months ago
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=180), "lab_type": "B12", "value": 350.0, "normal_range": "200-900"},
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=180), "lab_type": "Folate", "value": 12.5, "normal_range": ">3.0"},
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=180), "lab_type": "TSH", "value": 2.5, "normal_range": "0.4-4.0"},
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=180), "lab_type": "Glucose", "value": 105.0, "normal_range": "70-100"},
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=180), "lab_type": "HbA1c", "value": 6.8, "normal_range": "<5.7"},
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=180), "lab_type": "Creatinine", "value": 0.9, "normal_range": "0.6-1.2"},
        
        # 3 months ago
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=90), "lab_type": "B12", "value": 280.0, "normal_range": "200-900"},
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=90), "lab_type": "TSH", "value": 3.2, "normal_range": "0.4-4.0"},
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=90), "lab_type": "Glucose", "value": 112.0, "normal_range": "70-100"},
        {"timestamp": datetime.now(timezone.utc) - timedelta(days=90), "lab_type": "HbA1c", "value": 7.0, "normal_range": "<5.7"},
        
        # Today (concerning values)
        {"timestamp": datetime.now(timezone.utc), "lab_type": "B12", "value": 180.0, "normal_range": "200-900"},  # LOW - concerning
        {"timestamp": datetime.now(timezone.utc), "lab_type": "Folate", "value": 2.8, "normal_range": ">3.0"},  # LOW - concerning
        {"timestamp": datetime.now(timezone.utc), "lab_type": "TSH", "value": 4.8, "normal_range": "0.4-4.0"},  # ELEVATED - concerning
        {"timestamp": datetime.now(timezone.utc), "lab_type": "Glucose", "value": 118.0, "normal_range": "70-100"},
        {"timestamp": datetime.now(timezone.utc), "lab_type": "HbA1c", "value": 7.2, "normal_range": "<5.7"},
        {"timestamp": datetime.now(timezone.utc), "lab_type": "Creatinine", "value": 1.0, "normal_range": "0.6-1.2"},
    ]
    
    for lab_data in labs_data:
        lab = Lab(
            id=uuid4(),
            patient_id=patient.id,
            **lab_data
        )
        db.add(lab)
    
    print(f"  ✓ Created {len(labs_data)} lab records")
    
    # Get a clinician user ID (use first admin/clinician user)
    from models.user import User
    clinician = db.query(User).filter(User.role.in_(["clinician", "admin"])).first()
    if not clinician:
        print("  [WARNING]  Warning: No clinician user found. Creating note with placeholder ID.")
        clinician_id = uuid4()
    else:
        clinician_id = clinician.id
    
    # Create clinical notes (SOAP format)
    # Note: ClinicalNote uses: chief_complaint, history_of_present_illness, review_of_systems, 
    # physical_exam, assessment, plan (not subjective/objective)
    notes_data = [
        {
            "note_type": "progress",
            "chief_complaint": "Progressive memory loss over 18 months",
            "history_of_present_illness": "Patient reports progressive memory loss over past 18 months. Family notes difficulty with daily tasks (cooking, medication management). Recent fall (no injury). Sleep disturbances reported.",
            "physical_exam": "BP elevated: 158/98. Neurological exam: mild cognitive deficits noted. Physical exam otherwise unremarkable.",
            "assessment": "Mild Cognitive Impairment (MCI) with suspected progression. Rule out reversible causes: B12/folate deficiency, hypothyroidism. Diabetes control suboptimal.",
            "plan": "1) Supplement B12 and folate. 2) Refer to endocrinology for TSH elevation. 3) Optimize diabetes management. 4) Repeat MoCA in 3 months. 5) Consider neurology referral if progression continues.",
            "encounter_date": datetime.now(timezone.utc) - timedelta(days=14)
        },
        {
            "note_type": "progress",
            "chief_complaint": "Follow-up for cognitive decline",
            "history_of_present_illness": "Follow-up visit. Patient reports some improvement in energy after B12 supplementation. Family notes memory still declining. No further falls.",
            "physical_exam": "BP: 152/95. Neurological exam: stable cognitive deficits.",
            "assessment": "MCI stable. B12 deficiency responding to treatment. TSH still elevated. Continue monitoring.",
            "plan": "1) Continue B12/folate supplementation. 2) Endocrinology appointment scheduled. 3) Family education on safety measures. 4) Follow-up in 6 weeks.",
            "encounter_date": datetime.now(timezone.utc) - timedelta(days=7)
        },
        {
            "note_type": "progress",
            "chief_complaint": "Ongoing memory concerns",
            "history_of_present_illness": "Routine follow-up. Patient and family report ongoing concerns about memory. Patient seems more confused about recent events.",
            "physical_exam": "BP: 158/98. Physical exam: unremarkable. Neurological exam: mild cognitive deficits noted.",
            "assessment": "MCI with possible progression. Awaiting lab results. Consider neuropsychology evaluation.",
            "plan": "1) Review labs when available. 2) Refer to neuropsychology for detailed cognitive assessment. 3) Consider neurology referral. 4) Safety assessment for living alone.",
            "encounter_date": datetime.now(timezone.utc)
        }
    ]
    
    for note_data in notes_data:
        note = ClinicalNote(
            id=uuid4(),
            patient_id=patient.id,
            user_id=clinician_id,
            **note_data
        )
        db.add(note)
    
    print(f"  ✓ Created {len(notes_data)} clinical notes")
    
    # Create problems
    problems_data = [
        {"problem_name": "Mild Cognitive Impairment", "icd_code": "G31.84", "status": "active", "notes": "Progressive over 18 months. MoCA declining."},
        {"problem_name": "Hypertension", "icd_code": "I10", "status": "active", "notes": "Poorly controlled. BP trending upward."},
        {"problem_name": "Type 2 Diabetes", "icd_code": "E11.9", "status": "active", "notes": "HbA1c 7.2%, needs optimization."},
        {"problem_name": "B12 Deficiency", "icd_code": "D51.9", "status": "active", "notes": "Responding to supplementation."},
        {"problem_name": "Hypothyroidism", "icd_code": "E03.9", "status": "active", "notes": "TSH elevated, pending endocrinology referral."},
    ]
    
    for problem_data in problems_data:
        problem = Problem(
            id=uuid4(),
            patient_id=patient.id,
            **problem_data
        )
        db.add(problem)
    
    print(f"  ✓ Created {len(problems_data)} problems")
    
    # Create medications (some with cognitive side effects)
    medications_data = [
        {"medication_name": "Lisinopril", "dosage": "10mg", "frequency": "Once daily", "route": "Oral", "status": "active", "notes": "For hypertension"},
        {"medication_name": "Metformin", "dosage": "1000mg", "frequency": "Twice daily", "route": "Oral", "status": "active", "notes": "For diabetes"},
        {"medication_name": "Vitamin B12", "dosage": "1000mcg", "frequency": "Once daily", "route": "Oral", "status": "active", "notes": "Supplementation for deficiency"},
        {"medication_name": "Folic Acid", "dosage": "1mg", "frequency": "Once daily", "route": "Oral", "status": "active", "notes": "Supplementation"},
        {"medication_name": "Lorazepam", "dosage": "0.5mg", "frequency": "As needed for anxiety", "route": "Oral", "status": "active", "notes": "CAUTION: May affect cognition. Review necessity."},  # Cognitive side effect
    ]
    
    for med_data in medications_data:
        medication = Medication(
            id=uuid4(),
            patient_id=patient.id,
            **med_data
        )
        db.add(medication)
    
    print(f"  ✓ Created {len(medications_data)} medications")
    
    # Create allergies
    allergies_data = [
        {"allergen": "Penicillin", "allergen_type": "Medication", "severity": "Moderate", "reaction": "Rash", "status": "active"},
        {"allergen": "Sulfa drugs", "allergen_type": "Medication", "severity": "Mild", "reaction": "Hives", "status": "active"},
    ]
    
    for allergy_data in allergies_data:
        allergy = Allergy(
            id=uuid4(),
            patient_id=patient.id,
            **allergy_data
        )
        db.add(allergy)
    
    print(f"  ✓ Created {len(allergies_data)} allergies")
    
    # Commit all core data first
    db.commit()
    print(f"  ✓ All core data committed to database")
    
    # Create conversation session (doctor-patient conversation) - optional
    # Note: ConversationSession uses: session_date, duration_seconds (not start_time/end_time/duration_minutes)
    try:
        session_date = datetime.now(timezone.utc) - timedelta(days=7)
        session = ConversationSession(
            id=uuid4(),
            patient_id=patient.id,
            clinician_id=clinician_id,
            session_date=session_date,
            duration_seconds=25 * 60,  # 25 minutes in seconds
            status="completed"
        )
        db.add(session)
        db.flush()
        
        # Create conversation transcript
        # Note: ConversationTranscript uses: timestamp_seconds (not timestamp)
        transcript_data = [
            {"speaker": "doctor", "text": "Good morning, Sarah. How have you been feeling since our last visit?", "timestamp_seconds": 10},
            {"speaker": "patient", "text": "Oh, I'm okay I guess. My daughter says I'm forgetting things more. I don't really notice it myself.", "timestamp_seconds": 25},
            {"speaker": "doctor", "text": "I understand. Can you tell me about any specific things you've been forgetting?", "timestamp_seconds": 45},
            {"speaker": "patient", "text": "Well, sometimes I forget if I took my pills. And I burned something on the stove last week because I forgot I was cooking.", "timestamp_seconds": 70},
            {"speaker": "doctor", "text": "I see. That's concerning for safety. Have you had any falls recently?", "timestamp_seconds": 95},
            {"speaker": "patient", "text": "Yes, I fell in the kitchen about two weeks ago. I'm fine though, no broken bones.", "timestamp_seconds": 120},
            {"speaker": "doctor", "text": "I'm glad you're okay. Let's do a quick memory test today, and I'll also check your recent lab results.", "timestamp_seconds": 150},
        ]
        
        full_transcript_text = "\n".join([f"{t['speaker'].title()}: {t['text']}" for t in transcript_data])
        
        for trans_data in transcript_data:
            transcript = ConversationTranscript(
                id=uuid4(),
                session_id=session.id,
                **trans_data
            )
            db.add(transcript)
        
        # Create conversation analysis
        # Note: ConversationAnalysis uses JSONB for arrays
        import json
        analysis = ConversationAnalysis(
            id=uuid4(),
            session_id=session.id,
            full_transcript=full_transcript_text,
            key_points=json.dumps([
                "Patient reports progressive memory loss",
                "Family notes difficulty with daily tasks",
                "Recent fall in kitchen (no injury)",
                "Patient minimizes symptoms",
                "Safety concerns identified"
            ]),
            summary="Patient presents with progressive cognitive decline. Family reports more significant issues than patient acknowledges. Safety concerns identified (falls, cooking incidents). Requires comprehensive assessment and safety planning.",
            medical_terms=json.dumps(["cognitive decline", "memory loss", "falls", "safety assessment"]),
            concerns_identified=json.dumps(["Safety at home", "Medication adherence", "Progressive cognitive decline"]),
            recommendations="1) Comprehensive cognitive assessment\n2) Safety evaluation for living alone\n3) Medication review for cognitive side effects\n4) Family involvement in care planning"
        )
        db.add(analysis)
        db.commit()
        
        print(f"  ✓ Created conversation session with transcript and analysis")
    except Exception as e:
        # Rollback the failed conversation transaction, but patient data is already committed
        db.rollback()
        print(f"  [WARNING]  Warning: Could not create conversation data: {str(e)[:100]}")
        print(f"     Run 'scripts/create_conversation_tables.sql' in Supabase SQL Editor to enable conversation features")
        print(f"     Patient and other core data were created successfully")
    print(f"\n[SUCCESS] Successfully created patient 'Sarah Chen' with ID: {patient.id}")
    print(f"\n[STANDARD] Patient Summary:")
    print(f"   - Name: {patient.name}")
    print(f"   - Age: {patient.age}")
    print(f"   - Diagnosis: {patient.primary_diagnosis}")
    print(f"   - Vitals: {len(vitals_data)} records")
    print(f"   - Labs: {len(labs_data)} records")
    print(f"   - Clinical Notes: {len(notes_data)}")
    print(f"   - Problems: {len(problems_data)}")
    print(f"   - Medications: {len(medications_data)}")
    print(f"   - Allergies: {len(allergies_data)}")
    print(f"   - Conversations: 1 session")
    
    return patient.id

if __name__ == "__main__":
    db = SessionLocal()
    try:
        patient_id = create_sarah_chen(db)
        print(f"\n[ACTION] Test patient ready for user story testing!")
        print(f"   Use patient ID: {patient_id}")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error creating patient: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

