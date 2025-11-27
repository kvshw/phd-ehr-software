-- Add missing emergency contact columns to patients table
-- Run this in Supabase SQL Editor

ALTER TABLE patients
ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS emergency_contact_relation VARCHAR(100),
ADD COLUMN IF NOT EXISTS registration_status VARCHAR(50) DEFAULT 'complete',
ADD COLUMN IF NOT EXISTS registration_completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS insurance_provider VARCHAR(255),
ADD COLUMN IF NOT EXISTS insurance_id VARCHAR(100);

