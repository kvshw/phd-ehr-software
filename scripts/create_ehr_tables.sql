-- Migration script to add EHR features to existing database
-- Run this in Supabase SQL Editor

-- Add new columns to patients table
ALTER TABLE patients 
ADD COLUMN IF NOT EXISTS past_medical_history TEXT,
ADD COLUMN IF NOT EXISTS past_surgical_history TEXT,
ADD COLUMN IF NOT EXISTS family_history TEXT,
ADD COLUMN IF NOT EXISTS social_history TEXT;

-- Create clinical_notes table
CREATE TABLE IF NOT EXISTS clinical_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    note_type VARCHAR(50) NOT NULL DEFAULT 'progress',
    encounter_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    chief_complaint TEXT,
    history_of_present_illness TEXT,
    review_of_systems TEXT,
    physical_exam TEXT,
    assessment TEXT,
    plan TEXT,
    note_text TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create problems table
CREATE TABLE IF NOT EXISTS problems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    problem_name VARCHAR(500) NOT NULL,
    icd_code VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    onset_date TIMESTAMPTZ,
    resolved_date TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create medications table
CREATE TABLE IF NOT EXISTS medications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    prescriber_id UUID REFERENCES users(id) ON DELETE SET NULL,
    medication_name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    route VARCHAR(50),
    quantity VARCHAR(50),
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    indication VARCHAR(500),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create allergies table
CREATE TABLE IF NOT EXISTS allergies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    allergen VARCHAR(255) NOT NULL,
    allergen_type VARCHAR(50),
    severity VARCHAR(20),
    reaction TEXT,
    onset_date TIMESTAMPTZ,
    notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_clinical_notes_patient_id ON clinical_notes(patient_id);
CREATE INDEX IF NOT EXISTS idx_clinical_notes_user_id ON clinical_notes(user_id);
CREATE INDEX IF NOT EXISTS idx_clinical_notes_encounter_date ON clinical_notes(encounter_date DESC);

CREATE INDEX IF NOT EXISTS idx_problems_patient_id ON problems(patient_id);
CREATE INDEX IF NOT EXISTS idx_problems_status ON problems(status);

CREATE INDEX IF NOT EXISTS idx_medications_patient_id ON medications(patient_id);
CREATE INDEX IF NOT EXISTS idx_medications_status ON medications(status);

CREATE INDEX IF NOT EXISTS idx_allergies_patient_id ON allergies(patient_id);
CREATE INDEX IF NOT EXISTS idx_allergies_status ON allergies(status);

-- Add updated_at trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for updated_at
DROP TRIGGER IF EXISTS update_clinical_notes_updated_at ON clinical_notes;
CREATE TRIGGER update_clinical_notes_updated_at
    BEFORE UPDATE ON clinical_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_problems_updated_at ON problems;
CREATE TRIGGER update_problems_updated_at
    BEFORE UPDATE ON problems
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_medications_updated_at ON medications;
CREATE TRIGGER update_medications_updated_at
    BEFORE UPDATE ON medications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_allergies_updated_at ON allergies;
CREATE TRIGGER update_allergies_updated_at
    BEFORE UPDATE ON allergies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

