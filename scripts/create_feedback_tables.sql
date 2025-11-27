-- Create Suggestion Feedback and Learning Tables
-- Run this in Supabase SQL Editor

-- Table: suggestion_feedback
-- Stores individual feedback events from clinicians
CREATE TABLE IF NOT EXISTS suggestion_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    suggestion_id UUID NOT NULL REFERENCES suggestions(id),
    patient_id UUID NOT NULL REFERENCES patients(id),
    clinician_id UUID NOT NULL REFERENCES users(id),
    
    -- Action taken
    action VARCHAR(50) NOT NULL,
    
    -- Snapshot of suggestion at time of feedback
    suggestion_text TEXT NOT NULL,
    suggestion_source VARCHAR(100) NOT NULL,
    suggestion_confidence FLOAT,
    suggestion_type VARCHAR(100),
    
    -- Ratings (1-5 Likert scale)
    clinical_relevance INTEGER CHECK (clinical_relevance BETWEEN 1 AND 5),
    agreement_rating INTEGER CHECK (agreement_rating BETWEEN 1 AND 5),
    explanation_quality INTEGER CHECK (explanation_quality BETWEEN 1 AND 5),
    would_act_on INTEGER CHECK (would_act_on BETWEEN 1 AND 5),
    
    -- Free text
    clinician_comment TEXT,
    improvement_suggestion TEXT,
    
    -- Derived
    was_helpful BOOLEAN,
    
    -- Patient context at time of feedback
    patient_age INTEGER,
    patient_sex VARCHAR(10),
    patient_diagnosis VARCHAR(500),
    
    -- Learning metadata
    feedback_used_for_training BOOLEAN DEFAULT FALSE,
    training_batch_id VARCHAR(100),
    
    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for suggestion_feedback
CREATE INDEX IF NOT EXISTS idx_suggestion_feedback_suggestion ON suggestion_feedback(suggestion_id);
CREATE INDEX IF NOT EXISTS idx_suggestion_feedback_patient ON suggestion_feedback(patient_id);
CREATE INDEX IF NOT EXISTS idx_suggestion_feedback_clinician ON suggestion_feedback(clinician_id);
CREATE INDEX IF NOT EXISTS idx_suggestion_feedback_action ON suggestion_feedback(action);
CREATE INDEX IF NOT EXISTS idx_suggestion_feedback_source ON suggestion_feedback(suggestion_source);
CREATE INDEX IF NOT EXISTS idx_suggestion_feedback_created ON suggestion_feedback(created_at);


-- Table: feedback_aggregation
-- Aggregated feedback statistics for self-adaptive learning
CREATE TABLE IF NOT EXISTS feedback_aggregation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- What this aggregation is for
    suggestion_source VARCHAR(100) NOT NULL,
    suggestion_type VARCHAR(100),
    rule_id VARCHAR(100),
    
    -- Aggregated counts
    total_shown INTEGER DEFAULT 0,
    total_accepted INTEGER DEFAULT 0,
    total_ignored INTEGER DEFAULT 0,
    total_not_relevant INTEGER DEFAULT 0,
    total_incorrect INTEGER DEFAULT 0,
    
    -- Calculated metrics
    acceptance_rate FLOAT DEFAULT 0.0,
    relevance_score FLOAT DEFAULT 0.0,
    
    -- Average ratings
    avg_clinical_relevance FLOAT,
    avg_agreement FLOAT,
    avg_explanation_quality FLOAT,
    
    -- Confidence adjustment for self-adaptive AI
    confidence_adjustment FLOAT DEFAULT 0.0,
    
    -- Time period
    period_start TIMESTAMPTZ NOT NULL,
    period_end TIMESTAMPTZ NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Indexes for feedback_aggregation
CREATE INDEX IF NOT EXISTS idx_feedback_agg_source ON feedback_aggregation(suggestion_source);
CREATE INDEX IF NOT EXISTS idx_feedback_agg_rule ON feedback_aggregation(rule_id);
CREATE INDEX IF NOT EXISTS idx_feedback_agg_period ON feedback_aggregation(period_start, period_end);


-- Table: learning_events
-- Tracks when and how the AI system learned from feedback
CREATE TABLE IF NOT EXISTS learning_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- What triggered learning
    event_type VARCHAR(100) NOT NULL,
    
    -- What was affected
    affected_source VARCHAR(100) NOT NULL,
    affected_rule_id VARCHAR(100),
    
    -- What changed
    previous_value JSONB,
    new_value JSONB,
    
    -- Reasoning
    trigger_reason TEXT NOT NULL,
    feedback_count_used INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT 'system',
    
    -- Audit/rollback
    is_active BOOLEAN DEFAULT TRUE,
    rollback_event_id UUID REFERENCES learning_events(id)
);

-- Indexes for learning_events
CREATE INDEX IF NOT EXISTS idx_learning_events_type ON learning_events(event_type);
CREATE INDEX IF NOT EXISTS idx_learning_events_source ON learning_events(affected_source);
CREATE INDEX IF NOT EXISTS idx_learning_events_active ON learning_events(is_active);
CREATE INDEX IF NOT EXISTS idx_learning_events_created ON learning_events(created_at);


-- Success message
SELECT 'Feedback and Learning tables created successfully!' as status;

