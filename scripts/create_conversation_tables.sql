-- Create conversation tables for voice-to-text functionality
-- Run this in Supabase SQL Editor or via migration

-- Conversation Sessions
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    clinician_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    duration_seconds INTEGER,
    audio_file_url TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'recording',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Conversation Transcripts
CREATE TABLE IF NOT EXISTS conversation_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    speaker VARCHAR(20) NOT NULL CHECK (speaker IN ('doctor', 'patient')),
    text TEXT NOT NULL,
    timestamp_seconds INTEGER,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Conversation Analysis
CREATE TABLE IF NOT EXISTS conversation_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL UNIQUE REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    full_transcript TEXT NOT NULL,
    key_points JSONB,
    summary TEXT,
    medical_terms JSONB,
    concerns_identified JSONB,
    recommendations TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_patient_id ON conversation_sessions(patient_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_clinician_id ON conversation_sessions(clinician_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_status ON conversation_sessions(status);
CREATE INDEX IF NOT EXISTS idx_conversation_transcripts_session_id ON conversation_transcripts(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_analysis_session_id ON conversation_analysis(session_id);

-- Add comments
COMMENT ON TABLE conversation_sessions IS 'Stores voice conversation sessions between doctors and patients';
COMMENT ON TABLE conversation_transcripts IS 'Stores individual transcript entries for conversations';
COMMENT ON TABLE conversation_analysis IS 'Stores AI-generated analysis of conversations (key points, summaries, etc.)';

