-- Create tables for the Learning Adaptation Engine
-- Run this in Supabase SQL Editor

-- Learning events table - stores each learning signal
CREATE TABLE IF NOT EXISTS learning_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    suggestion_type VARCHAR(100),
    source VARCHAR(50),
    learning_signal FLOAT NOT NULL,
    user_role VARCHAR(50),
    user_specialty VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_learning_events_created_at ON learning_events(created_at);
CREATE INDEX IF NOT EXISTS idx_learning_events_source ON learning_events(source);
CREATE INDEX IF NOT EXISTS idx_learning_events_role ON learning_events(user_role);

-- Adaptation history table - tracks all UI adaptations
CREATE TABLE IF NOT EXISTS adaptations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    adaptation_type VARCHAR(100) NOT NULL,
    old_state JSONB,
    new_state JSONB,
    effectiveness_score FLOAT,
    user_reverted BOOLEAN DEFAULT FALSE,
    time_saved_seconds INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_at TIMESTAMP WITH TIME ZONE,
    reverted_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_adaptations_user_id ON adaptations(user_id);
CREATE INDEX IF NOT EXISTS idx_adaptations_type ON adaptations(adaptation_type);
CREATE INDEX IF NOT EXISTS idx_adaptations_created_at ON adaptations(created_at);

-- User preferences learned from behavior
CREATE TABLE IF NOT EXISTS user_learned_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) UNIQUE,
    preferred_section_order JSONB,
    suggestion_density_preference VARCHAR(20) DEFAULT 'medium',
    preferred_sources JSONB,
    theme_preference VARCHAR(20),
    shortcuts JSONB,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model performance tracking for research
CREATE TABLE IF NOT EXISTS model_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    sample_size INTEGER,
    confidence_interval_lower FLOAT,
    confidence_interval_upper FLOAT,
    measured_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_model_performance_model ON model_performance(model_name);
CREATE INDEX IF NOT EXISTS idx_model_performance_metric ON model_performance(metric_name);

-- Session analytics for behavior tracking
CREATE TABLE IF NOT EXISTS session_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_id VARCHAR(100) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    total_pages_viewed INTEGER DEFAULT 0,
    suggestions_viewed INTEGER DEFAULT 0,
    suggestions_accepted INTEGER DEFAULT 0,
    suggestions_rejected INTEGER DEFAULT 0,
    adaptations_applied INTEGER DEFAULT 0,
    adaptations_reverted INTEGER DEFAULT 0,
    feature_usage JSONB
);

CREATE INDEX IF NOT EXISTS idx_session_analytics_user ON session_analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_session_analytics_started ON session_analytics(started_at);

-- Grant permissions
ALTER TABLE learning_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE adaptations ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_learned_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_performance ENABLE ROW LEVEL SECURITY;
ALTER TABLE session_analytics ENABLE ROW LEVEL SECURITY;

-- Create policies for authenticated access
CREATE POLICY "Allow authenticated read learning_events" ON learning_events
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated insert learning_events" ON learning_events
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Allow authenticated read adaptations" ON adaptations
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated insert adaptations" ON adaptations
    FOR INSERT TO authenticated WITH CHECK (true);

CREATE POLICY "Allow authenticated manage preferences" ON user_learned_preferences
    FOR ALL TO authenticated USING (true);

CREATE POLICY "Allow authenticated read model_performance" ON model_performance
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Allow authenticated manage session_analytics" ON session_analytics
    FOR ALL TO authenticated USING (true);

-- Add helpful comments
COMMENT ON TABLE learning_events IS 'Stores learning signals from user feedback for the adaptive AI system';
COMMENT ON TABLE adaptations IS 'Tracks all UI adaptations made by the MAPE-K system';
COMMENT ON TABLE user_learned_preferences IS 'Learned user preferences derived from behavior patterns';
COMMENT ON TABLE model_performance IS 'Historical model performance metrics for research analysis';
COMMENT ON TABLE session_analytics IS 'Per-session analytics for user behavior research';

