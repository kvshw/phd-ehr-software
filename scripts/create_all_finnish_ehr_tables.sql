-- Complete Finnish EHR Migration Script
-- This script creates all necessary tables and adds Finnish-specific fields
-- Run this in Supabase SQL Editor

-- ============================================
-- STEP 1: Ensure Basic Tables Exist
-- ============================================
-- These should already exist, but we'll check and create if needed

-- Ensure update_updated_at_column function exists
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- STEP 2: Create Visits Table (if not exists)
-- ============================================
CREATE TABLE IF NOT EXISTS visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    visit_type VARCHAR(50) NOT NULL,
    visit_status VARCHAR(50) NOT NULL DEFAULT 'scheduled',
    chief_complaint TEXT,
    visit_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    discharge_date TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for visits
CREATE INDEX IF NOT EXISTS idx_visits_patient_id ON visits(patient_id);
CREATE INDEX IF NOT EXISTS idx_visits_user_id ON visits(user_id);
CREATE INDEX IF NOT EXISTS idx_visits_visit_date ON visits(visit_date);
CREATE INDEX IF NOT EXISTS idx_visits_status ON visits(visit_status);

-- Add constraints if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'valid_visit_type' 
        AND conrelid = 'visits'::regclass
    ) THEN
        ALTER TABLE visits ADD CONSTRAINT valid_visit_type CHECK (
            visit_type IN ('outpatient', 'inpatient', 'emergency', 'follow_up', 'consult', 'procedure')
        );
    END IF;
    
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'valid_visit_status' 
        AND conrelid = 'visits'::regclass
    ) THEN
        ALTER TABLE visits ADD CONSTRAINT valid_visit_status CHECK (
            visit_status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show')
        );
    END IF;
END $$;

-- Add trigger for updated_at
DROP TRIGGER IF EXISTS update_visits_updated_at ON visits;
CREATE TRIGGER update_visits_updated_at 
    BEFORE UPDATE ON visits
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- STEP 3: Add Finnish Fields to Patients
-- ============================================
ALTER TABLE patients
-- Finnish identification
ADD COLUMN IF NOT EXISTS henkilotunnus VARCHAR(11),
ADD COLUMN IF NOT EXISTS kela_card_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS date_of_birth DATE,

-- Healthcare eligibility
ADD COLUMN IF NOT EXISTS kela_eligible BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS municipality_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS municipality_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS primary_care_center VARCHAR(255),

-- International patients
ADD COLUMN IF NOT EXISTS ehic_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS ehic_country_code VARCHAR(3),
ADD COLUMN IF NOT EXISTS ehic_expiry_date DATE,
ADD COLUMN IF NOT EXISTS is_temporary_visitor BOOLEAN DEFAULT FALSE,

-- Contact information
ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS postal_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS city VARCHAR(100);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_patients_henkilotunnus ON patients(henkilotunnus);
CREATE INDEX IF NOT EXISTS idx_patients_kela_card ON patients(kela_card_number);
CREATE INDEX IF NOT EXISTS idx_patients_municipality ON patients(municipality_code);

-- ============================================
-- STEP 4: Add Finnish Fields to Visits
-- ============================================
ALTER TABLE visits
ADD COLUMN IF NOT EXISTS service_type VARCHAR(20) DEFAULT 'public',
ADD COLUMN IF NOT EXISTS visit_type_fi VARCHAR(50),
ADD COLUMN IF NOT EXISTS municipality_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS kela_reimbursement_amount DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS referral_from VARCHAR(255),
ADD COLUMN IF NOT EXISTS referral_to VARCHAR(255),
ADD COLUMN IF NOT EXISTS heti_number VARCHAR(20);

-- Add constraint for Finnish visit types
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'valid_visit_type_fi' 
        AND conrelid = 'visits'::regclass
    ) THEN
        ALTER TABLE visits ADD CONSTRAINT valid_visit_type_fi CHECK (
            visit_type_fi IS NULL OR visit_type_fi IN ('terveyskeskus', 'erikoislääkäri', 'päivystys', 'kotikäynti', 'etäkonsultaatio', 'toimenpide')
        );
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_visits_service_type ON visits(service_type);
CREATE INDEX IF NOT EXISTS idx_visits_municipality ON visits(municipality_code);

-- ============================================
-- STEP 5: Add Finnish Fields to Medications
-- ============================================
-- Ensure medications table exists (should from create_ehr_tables.sql)
-- Add Finnish-specific fields
ALTER TABLE medications
ADD COLUMN IF NOT EXISTS prescription_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS heti_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS refill_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS refill_authorized BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS atc_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS kela_reimbursement_percentage INTEGER;

CREATE INDEX IF NOT EXISTS idx_medications_prescription_id ON medications(prescription_id);
CREATE INDEX IF NOT EXISTS idx_medications_heti ON medications(heti_number);

-- ============================================
-- STEP 6: Add Finnish Fields to Users
-- ============================================
ALTER TABLE users
ADD COLUMN IF NOT EXISTS specialty VARCHAR(100),
ADD COLUMN IF NOT EXISTS first_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS title VARCHAR(50),
ADD COLUMN IF NOT EXISTS department VARCHAR(100),
ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}'::jsonb,
ADD COLUMN IF NOT EXISTS heti_number VARCHAR(20),
ADD COLUMN IF NOT EXISTS license_number VARCHAR(50),
ADD COLUMN IF NOT EXISTS workplace_municipality VARCHAR(10),
ADD COLUMN IF NOT EXISTS primary_workplace VARCHAR(255);

CREATE INDEX IF NOT EXISTS idx_users_specialty ON users(specialty);
CREATE INDEX IF NOT EXISTS idx_users_heti ON users(heti_number);

-- ============================================
-- STEP 7: Create Kela Reimbursements Table
-- ============================================
CREATE TABLE IF NOT EXISTS kela_reimbursements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    visit_id UUID REFERENCES visits(id) ON DELETE SET NULL,
    medication_id UUID REFERENCES medications(id) ON DELETE SET NULL,
    service_type VARCHAR(50) NOT NULL,
    service_description TEXT,
    total_cost DECIMAL(10,2) NOT NULL,
    kela_reimbursement DECIMAL(10,2) NOT NULL,
    patient_payment DECIMAL(10,2) NOT NULL,
    reimbursement_percentage INTEGER,
    kela_card_number VARCHAR(20),
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_kela_reimbursements_patient_id ON kela_reimbursements(patient_id);
CREATE INDEX IF NOT EXISTS idx_kela_reimbursements_visit_id ON kela_reimbursements(visit_id);

DROP TRIGGER IF EXISTS update_kela_reimbursements_updated_at ON kela_reimbursements;
CREATE TRIGGER update_kela_reimbursements_updated_at 
    BEFORE UPDATE ON kela_reimbursements
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- STEP 8: Create Municipalities Table
-- ============================================
CREATE TABLE IF NOT EXISTS municipalities (
    code VARCHAR(10) PRIMARY KEY,
    name_fi VARCHAR(255) NOT NULL,
    name_sv VARCHAR(255),
    region VARCHAR(100),
    primary_care_center VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_municipalities_name ON municipalities(name_fi);

-- Insert example municipalities
INSERT INTO municipalities (code, name_fi, name_sv, region) VALUES
    ('091', 'Helsinki', 'Helsingfors', 'Uusimaa'),
    ('049', 'Espoo', 'Esbo', 'Uusimaa'),
    ('235', 'Tampere', 'Tammerfors', 'Pirkanmaa'),
    ('837', 'Oulu', 'Uleåborg', 'Pohjois-Pohjanmaa')
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- STEP 9: Create Language Preferences Table
-- ============================================
CREATE TABLE IF NOT EXISTS user_language_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    interface_language VARCHAR(10) DEFAULT 'fi',
    document_language VARCHAR(10) DEFAULT 'fi',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_language_preferences_user_id ON user_language_preferences(user_id);

DROP TRIGGER IF EXISTS update_user_language_preferences_updated_at ON user_language_preferences;
CREATE TRIGGER update_user_language_preferences_updated_at 
    BEFORE UPDATE ON user_language_preferences
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Migration Complete!
-- ============================================
-- All Finnish EHR tables and fields have been created
-- You can now use Finnish-specific features in the application

