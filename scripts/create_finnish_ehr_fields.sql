-- Finnish EHR System Database Migration
-- Adds Finnish healthcare-specific fields and features
-- 
-- IMPORTANT: This script creates tables if they don't exist, then adds Finnish-specific fields
-- Run this AFTER the basic EHR tables are created (create_ehr_tables.sql)
-- If you get errors about missing tables, run create_ehr_tables.sql first

-- ============================================
-- 1. Enhance Patients Table (Finnish Fields)
-- ============================================
ALTER TABLE patients
-- Finnish identification
ADD COLUMN IF NOT EXISTS henkilotunnus VARCHAR(11) UNIQUE, -- Finnish personal ID (YYMMDD-XXXX)
ADD COLUMN IF NOT EXISTS kela_card_number VARCHAR(20), -- Kela health insurance card number
ADD COLUMN IF NOT EXISTS date_of_birth DATE, -- Can be derived from henkilötunnus

-- Healthcare eligibility (Finnish system)
ADD COLUMN IF NOT EXISTS kela_eligible BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS municipality_code VARCHAR(10), -- Municipality code for public healthcare
ADD COLUMN IF NOT EXISTS municipality_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS primary_care_center VARCHAR(255), -- Terveyskeskus assignment

-- International patients (EU/EEA)
ADD COLUMN IF NOT EXISTS ehic_number VARCHAR(20), -- European Health Insurance Card
ADD COLUMN IF NOT EXISTS ehic_country_code VARCHAR(3), -- ISO country code
ADD COLUMN IF NOT EXISTS ehic_expiry_date DATE,
ADD COLUMN IF NOT EXISTS is_temporary_visitor BOOLEAN DEFAULT FALSE,

-- Contact information (Finnish format)
ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS postal_code VARCHAR(10), -- Finnish postal code format
ADD COLUMN IF NOT EXISTS city VARCHAR(100);

-- Create indexes for Finnish-specific queries
CREATE INDEX IF NOT EXISTS idx_patients_henkilotunnus ON patients(henkilotunnus);
CREATE INDEX IF NOT EXISTS idx_patients_kela_card ON patients(kela_card_number);
CREATE INDEX IF NOT EXISTS idx_patients_municipality ON patients(municipality_code);
CREATE INDEX IF NOT EXISTS idx_patients_ehic ON patients(ehic_number);

-- ============================================
-- 2. Create Visits Table (if not exists) and Enhance with Finnish Context
-- ============================================
-- First, create the visits table if it doesn't exist
CREATE TABLE IF NOT EXISTS visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id), -- Primary provider
    visit_type VARCHAR(50) NOT NULL, -- outpatient, inpatient, emergency, follow_up, consult, procedure
    visit_status VARCHAR(50) NOT NULL DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    chief_complaint TEXT,
    visit_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    discharge_date TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255), -- Room, department, etc.
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create basic indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_visits_patient_id ON visits(patient_id);
CREATE INDEX IF NOT EXISTS idx_visits_user_id ON visits(user_id);
CREATE INDEX IF NOT EXISTS idx_visits_visit_date ON visits(visit_date);
CREATE INDEX IF NOT EXISTS idx_visits_status ON visits(visit_status);

-- Now add Finnish-specific columns
ALTER TABLE visits
ADD COLUMN IF NOT EXISTS service_type VARCHAR(20) DEFAULT 'public', -- public, private
ADD COLUMN IF NOT EXISTS visit_type_fi VARCHAR(50), -- terveyskeskus, erikoislääkäri, päivystys, kotikäynti, etc.
ADD COLUMN IF NOT EXISTS municipality_code VARCHAR(10),
ADD COLUMN IF NOT EXISTS kela_reimbursement_amount DECIMAL(10,2),
ADD COLUMN IF NOT EXISTS referral_from VARCHAR(255), -- Referring unit/physician
ADD COLUMN IF NOT EXISTS referral_to VARCHAR(255), -- Referred to unit/physician
ADD COLUMN IF NOT EXISTS heti_number VARCHAR(20); -- Healthcare professional HETI number

-- Update visit_type constraint to include Finnish types
-- Drop existing constraint if it exists (may have different name)
DO $$ 
BEGIN
    -- Drop constraint if it exists with any name
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'valid_visit_type') THEN
        ALTER TABLE visits DROP CONSTRAINT valid_visit_type;
    END IF;
    
    -- Drop constraint if it exists with different name
    IF EXISTS (SELECT 1 FROM information_schema.table_constraints 
               WHERE table_name = 'visits' 
               AND constraint_type = 'CHECK' 
               AND constraint_name LIKE '%visit_type%') THEN
        -- Find and drop the constraint
        EXECUTE (
            SELECT 'ALTER TABLE visits DROP CONSTRAINT ' || constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'visits' 
            AND constraint_type = 'CHECK' 
            AND constraint_name LIKE '%visit_type%'
            LIMIT 1
        );
    END IF;
END $$;

-- Add updated constraint that includes both standard and Finnish types
ALTER TABLE visits ADD CONSTRAINT valid_visit_type CHECK (
    visit_type IN ('outpatient', 'inpatient', 'emergency', 'follow_up', 'consult', 'procedure')
);

-- Add constraint for Finnish visit types
ALTER TABLE visits ADD CONSTRAINT valid_visit_type_fi CHECK (
    visit_type_fi IS NULL OR visit_type_fi IN ('terveyskeskus', 'erikoislääkäri', 'päivystys', 'kotikäynti', 'etäkonsultaatio', 'toimenpide')
);

-- Add visit_status constraint if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'valid_visit_status') THEN
        ALTER TABLE visits ADD CONSTRAINT valid_visit_status CHECK (
            visit_status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show')
        );
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_visits_service_type ON visits(service_type);
CREATE INDEX IF NOT EXISTS idx_visits_municipality ON visits(municipality_code);

-- ============================================
-- 3. Enhance Medications Table (ePrescription)
-- ============================================
-- Check if medications table exists, if not create basic structure
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'medications') THEN
        -- Create basic medications table if it doesn't exist
        CREATE TABLE medications (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            generic_name VARCHAR(255),
            dosage VARCHAR(100),
            frequency VARCHAR(100),
            route VARCHAR(50),
            quantity VARCHAR(100),
            start_date DATE,
            end_date DATE,
            status VARCHAR(50) DEFAULT 'active',
            indication TEXT,
            prescriber_id UUID REFERENCES users(id),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        
        CREATE INDEX idx_medications_patient_id ON medications(patient_id);
        CREATE INDEX idx_medications_status ON medications(status);
    END IF;
END $$;

-- Now add Finnish-specific columns
ALTER TABLE medications
ADD COLUMN IF NOT EXISTS prescription_id VARCHAR(100), -- ePrescription ID from Kanta
ADD COLUMN IF NOT EXISTS heti_number VARCHAR(20), -- Prescriber HETI number
ADD COLUMN IF NOT EXISTS refill_count INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS refill_authorized BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS atc_code VARCHAR(10), -- ATC code (already common, ensure it exists)
ADD COLUMN IF NOT EXISTS kela_reimbursement_percentage INTEGER; -- Kela reimbursement percentage

CREATE INDEX IF NOT EXISTS idx_medications_prescription_id ON medications(prescription_id);
CREATE INDEX IF NOT EXISTS idx_medications_heti ON medications(heti_number);

-- ============================================
-- 4. Enhance Users Table (Finnish Healthcare)
-- ============================================
ALTER TABLE users
ADD COLUMN IF NOT EXISTS heti_number VARCHAR(20) UNIQUE, -- Healthcare professional HETI number
ADD COLUMN IF NOT EXISTS license_number VARCHAR(50), -- Professional license number
ADD COLUMN IF NOT EXISTS workplace_municipality VARCHAR(10), -- Municipality of workplace
ADD COLUMN IF NOT EXISTS primary_workplace VARCHAR(255); -- Primary workplace name

CREATE INDEX IF NOT EXISTS idx_users_heti ON users(heti_number);

-- ============================================
-- 5. Kela Reimbursements Table
-- ============================================
CREATE TABLE IF NOT EXISTS kela_reimbursements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    visit_id UUID REFERENCES visits(id) ON DELETE SET NULL,
    medication_id UUID REFERENCES medications(id) ON DELETE SET NULL,
    service_type VARCHAR(50) NOT NULL, -- visit, medication, procedure, etc.
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

CREATE INDEX idx_kela_reimbursements_patient_id ON kela_reimbursements(patient_id);
CREATE INDEX idx_kela_reimbursements_visit_id ON kela_reimbursements(visit_id);
CREATE INDEX idx_kela_reimbursements_processed_at ON kela_reimbursements(processed_at);

-- ============================================
-- 6. Municipality Reference Table (Optional)
-- ============================================
-- This can be populated with Finnish municipality data
CREATE TABLE IF NOT EXISTS municipalities (
    code VARCHAR(10) PRIMARY KEY,
    name_fi VARCHAR(255) NOT NULL,
    name_sv VARCHAR(255), -- Swedish name
    region VARCHAR(100),
    primary_care_center VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_municipalities_name ON municipalities(name_fi);

-- Insert some example municipalities (can be expanded)
INSERT INTO municipalities (code, name_fi, name_sv, region) VALUES
    ('091', 'Helsinki', 'Helsingfors', 'Uusimaa'),
    ('049', 'Espoo', 'Esbo', 'Uusimaa'),
    ('235', 'Tampere', 'Tammerfors', 'Pirkanmaa'),
    ('837', 'Oulu', 'Uleåborg', 'Pohjois-Pohjanmaa')
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- 7. Language Preferences Table
-- ============================================
CREATE TABLE IF NOT EXISTS user_language_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    interface_language VARCHAR(10) DEFAULT 'fi', -- fi, sv, en
    document_language VARCHAR(10) DEFAULT 'fi',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_language_preferences_user_id ON user_language_preferences(user_id);

-- ============================================
-- 8. Update Timestamps
-- ============================================
CREATE TRIGGER update_kela_reimbursements_updated_at BEFORE UPDATE ON kela_reimbursements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_language_preferences_updated_at BEFORE UPDATE ON user_language_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Migration Complete
-- ============================================
-- This migration adds Finnish healthcare-specific fields
-- Run in Supabase SQL Editor

