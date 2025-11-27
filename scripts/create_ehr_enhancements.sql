-- Comprehensive EHR Enhancements Database Migration
-- Adds support for: visits, tasks, alerts, user preferences, enhanced roles

-- ============================================
-- 1. Enhance Users Table
-- ============================================
-- Add specialty and extended role support
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS specialty VARCHAR(100),
ADD COLUMN IF NOT EXISTS first_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS title VARCHAR(50), -- Dr., RN, NP, PA, etc.
ADD COLUMN IF NOT EXISTS department VARCHAR(100),
ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}'::jsonb;

-- Create index on specialty for faster queries
CREATE INDEX IF NOT EXISTS idx_users_specialty ON users(specialty);

-- ============================================
-- 2. Enhance Patients Table
-- ============================================
-- Add registration and contact information
ALTER TABLE patients
ADD COLUMN IF NOT EXISTS registration_status VARCHAR(50) DEFAULT 'complete', -- complete, pending, incomplete
ADD COLUMN IF NOT EXISTS phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20),
ADD COLUMN IF NOT EXISTS emergency_contact_relation VARCHAR(100),
ADD COLUMN IF NOT EXISTS insurance_provider VARCHAR(255),
ADD COLUMN IF NOT EXISTS insurance_id VARCHAR(100),
ADD COLUMN IF NOT EXISTS registration_completed_at TIMESTAMP WITH TIME ZONE;

-- Create index on registration status
CREATE INDEX IF NOT EXISTS idx_patients_registration_status ON patients(registration_status);

-- ============================================
-- 3. Visits/Encounters Table
-- ============================================
CREATE TABLE IF NOT EXISTS visits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id), -- Primary provider
    visit_type VARCHAR(50) NOT NULL, -- outpatient, inpatient, emergency, follow_up, consult
    visit_status VARCHAR(50) NOT NULL DEFAULT 'scheduled', -- scheduled, in_progress, completed, cancelled
    chief_complaint TEXT,
    visit_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    discharge_date TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255), -- Room, department, etc.
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_visit_type CHECK (visit_type IN ('outpatient', 'inpatient', 'emergency', 'follow_up', 'consult', 'procedure')),
    CONSTRAINT valid_visit_status CHECK (visit_status IN ('scheduled', 'in_progress', 'completed', 'cancelled', 'no_show'))
);

CREATE INDEX idx_visits_patient_id ON visits(patient_id);
CREATE INDEX idx_visits_user_id ON visits(user_id);
CREATE INDEX idx_visits_visit_date ON visits(visit_date);
CREATE INDEX idx_visits_status ON visits(visit_status);

-- ============================================
-- 4. Tasks Table
-- ============================================
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    assigned_to UUID NOT NULL REFERENCES users(id),
    assigned_by UUID REFERENCES users(id),
    task_type VARCHAR(100) NOT NULL, -- medication_administration, vital_check, documentation, follow_up, etc.
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, completed, cancelled, overdue
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    completion_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_task_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    CONSTRAINT valid_task_status CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled', 'overdue'))
);

CREATE INDEX idx_tasks_patient_id ON tasks(patient_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- ============================================
-- 5. Alerts Table
-- ============================================
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id), -- Alert for specific user, NULL = all users
    alert_type VARCHAR(100) NOT NULL, -- critical_vital, new_result, medication_due, task_overdue, etc.
    priority VARCHAR(20) NOT NULL DEFAULT 'medium', -- low, medium, high, critical
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'active', -- active, acknowledged, resolved, dismissed
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB, -- Additional context data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_alert_priority CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    CONSTRAINT valid_alert_status CHECK (status IN ('active', 'acknowledged', 'resolved', 'dismissed'))
);

CREATE INDEX idx_alerts_patient_id ON alerts(patient_id);
CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_status ON alerts(status);
CREATE INDEX idx_alerts_priority ON alerts(priority);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);

-- ============================================
-- 6. Clinical Decisions Table
-- ============================================
CREATE TABLE IF NOT EXISTS clinical_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    decision_maker_id UUID NOT NULL REFERENCES users(id), -- Primary decision maker
    decision_type VARCHAR(100) NOT NULL, -- diagnosis, treatment, medication, procedure, discharge, etc.
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'proposed', -- proposed, under_review, accepted, rejected, modified
    rationale TEXT,
    alternatives_considered TEXT,
    outcome TEXT, -- Track decision outcomes
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    decision_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_decision_status CHECK (status IN ('proposed', 'under_review', 'accepted', 'rejected', 'modified'))
);

CREATE INDEX idx_clinical_decisions_patient_id ON clinical_decisions(patient_id);
CREATE INDEX idx_clinical_decisions_decision_maker_id ON clinical_decisions(decision_maker_id);
CREATE INDEX idx_clinical_decisions_status ON clinical_decisions(status);
CREATE INDEX idx_clinical_decisions_decision_date ON clinical_decisions(decision_date);

-- ============================================
-- 7. Enhance Adaptations Table
-- ============================================
-- Add support for page-level and role-based adaptations
ALTER TABLE adaptations
ADD COLUMN IF NOT EXISTS page_type VARCHAR(50), -- dashboard, patient_detail, etc.
ADD COLUMN IF NOT EXISTS scope VARCHAR(50) DEFAULT 'patient', -- user, role, specialty, patient, global
ADD COLUMN IF NOT EXISTS adaptation_type VARCHAR(50) DEFAULT 'layout'; -- layout, visibility, ordering, etc.

CREATE INDEX IF NOT EXISTS idx_adaptations_page_type ON adaptations(page_type);
CREATE INDEX IF NOT EXISTS idx_adaptations_scope ON adaptations(scope);

-- ============================================
-- 8. Care Plans Table
-- ============================================
CREATE TABLE IF NOT EXISTS care_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id),
    plan_type VARCHAR(100) NOT NULL, -- treatment, discharge, preventive, chronic_management
    title VARCHAR(255) NOT NULL,
    description TEXT,
    goals JSONB, -- Array of care plan goals
    interventions JSONB, -- Array of interventions
    status VARCHAR(50) DEFAULT 'active', -- active, completed, cancelled, on_hold
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT valid_care_plan_status CHECK (status IN ('active', 'completed', 'cancelled', 'on_hold'))
);

CREATE INDEX idx_care_plans_patient_id ON care_plans(patient_id);
CREATE INDEX idx_care_plans_status ON care_plans(status);

-- ============================================
-- 9. Reports Table
-- ============================================
CREATE TABLE IF NOT EXISTS reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    visit_id UUID REFERENCES visits(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id),
    report_type VARCHAR(100) NOT NULL, -- discharge_summary, progress_report, consultation, etc.
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    template_used VARCHAR(255),
    version INTEGER DEFAULT 1,
    is_final BOOLEAN DEFAULT FALSE,
    shared_with JSONB, -- Array of user IDs who can view this report
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reports_patient_id ON reports(patient_id);
CREATE INDEX idx_reports_created_by ON reports(created_by);
CREATE INDEX idx_reports_report_type ON reports(report_type);

-- ============================================
-- 10. Update Timestamps Trigger
-- ============================================
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to new tables
CREATE TRIGGER update_visits_updated_at BEFORE UPDATE ON visits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clinical_decisions_updated_at BEFORE UPDATE ON clinical_decisions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_care_plans_updated_at BEFORE UPDATE ON care_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Migration Complete
-- ============================================
-- Run this script in Supabase SQL Editor
-- All tables are created with proper indexes and constraints

