-- Performance optimization: Add missing indexes for frequently queried columns

-- Vitals table indexes (heavily queried by patient_id and timestamp)
CREATE INDEX IF NOT EXISTS idx_vitals_patient_id ON vitals(patient_id);
CREATE INDEX IF NOT EXISTS idx_vitals_timestamp ON vitals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_vitals_patient_timestamp ON vitals(patient_id, timestamp DESC);

-- Labs table indexes (heavily queried by patient_id and timestamp)
CREATE INDEX IF NOT EXISTS idx_labs_patient_id ON labs(patient_id);
CREATE INDEX IF NOT EXISTS idx_labs_timestamp ON labs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_labs_patient_timestamp ON labs(patient_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_labs_lab_type ON labs(lab_type);

-- Imaging table indexes
CREATE INDEX IF NOT EXISTS idx_imaging_patient_id ON imaging(patient_id);
CREATE INDEX IF NOT EXISTS idx_imaging_created_at ON imaging(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_imaging_patient_created ON imaging(patient_id, created_at DESC);

-- Patients table indexes (for search queries)
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name);
CREATE INDEX IF NOT EXISTS idx_patients_age ON patients(age);
CREATE INDEX IF NOT EXISTS idx_patients_sex ON patients(sex);
CREATE INDEX IF NOT EXISTS idx_patients_diagnosis ON patients(primary_diagnosis);

-- User actions table indexes (for MAPE-K monitoring)
CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_actions_patient_id ON user_actions(patient_id);
CREATE INDEX IF NOT EXISTS idx_user_actions_timestamp ON user_actions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_actions_user_timestamp ON user_actions(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_actions_action_type ON user_actions(action_type);

-- Adaptations table indexes
CREATE INDEX IF NOT EXISTS idx_adaptations_user_id ON adaptations(user_id);
CREATE INDEX IF NOT EXISTS idx_adaptations_patient_id ON adaptations(patient_id);
CREATE INDEX IF NOT EXISTS idx_adaptations_timestamp ON adaptations(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_adaptations_user_patient_timestamp ON adaptations(user_id, patient_id, timestamp DESC);

-- Note: Diagnoses are stored in patients.primary_diagnosis field, not a separate table
-- Index already created above: idx_patients_diagnosis

