# Voice-to-Text & Conversation Analysis Implementation

## Overview

This document describes the voice-to-text conversation feature that allows doctors to record and transcribe conversations with patients, with AI-powered analysis for key points, summaries, and medical term extraction.

## Features Implemented

### 1. Voice Recording Component
- **Location**: `app/frontend/components/conversation/VoiceRecorder.tsx`
- **Features**:
  - Real-time speech-to-text using Web Speech API
  - Speaker identification (Doctor/Patient toggle)
  - Session management
  - Live transcript display
  - Browser-based (Chrome, Edge, Safari supported)

### 2. Conversation Storage
- **Database Tables**:
  - `conversation_sessions` - Stores conversation sessions
  - `conversation_transcripts` - Stores individual transcript entries
  - `conversation_analysis` - Stores AI-generated analysis
- **Migration Script**: `scripts/create_conversation_tables.sql`

### 3. Backend API
- **Routes**: `app/backend/api/routes/conversations.py`
- **Endpoints**:
  - `POST /api/v1/conversations/sessions` - Create new session
  - `GET /api/v1/conversations/sessions/{session_id}` - Get session with transcripts
  - `GET /api/v1/conversations/patients/{patient_id}/sessions` - Get patient's sessions
  - `POST /api/v1/conversations/transcripts` - Add transcript entry
  - `POST /api/v1/conversations/sessions/{session_id}/complete` - Complete session
  - `POST /api/v1/conversations/sessions/{session_id}/analyze` - Analyze conversation

### 4. Conversation Analysis Service
- **Location**: `app/backend/services/conversation_analysis_service.py`
- **Features**:
  - Key points extraction
  - Summary generation (SOAP format)
  - Medical term identification
  - Patient concerns extraction
  - Recommendations generation
- **AI Integration**: Uses OpenAI GPT-4 when available, falls back to rule-based analysis

### 5. Frontend Components
- **ConversationSection**: Main component integrating all features
- **ConversationTranscript**: Displays full conversation transcript
- **ConversationSummary**: Displays AI-generated analysis

## Setup Instructions

### 1. Database Migration

Run the SQL migration script in Supabase:

```bash
# In Supabase SQL Editor, run:
scripts/create_conversation_tables.sql
```

Or via psql:
```bash
psql $DATABASE_URL -f scripts/create_conversation_tables.sql
```

### 2. Backend Dependencies

Add OpenAI support (optional, for AI analysis):

```bash
cd app/backend
pip install openai>=1.0.0
```

Add to `requirements.txt`:
```
openai>=1.0.0
```

Set environment variable:
```bash
OPENAI_API_KEY=your_api_key_here
```

### 3. Frontend Integration

The conversation section is already integrated into the patient detail page. Navigate to any patient and click the "Conversation" tab.

## Usage

### Recording a Conversation

1. Navigate to a patient's detail page
2. Click the "Conversation" tab
3. Click "Start Recording"
4. Toggle between "Doctor" and "Patient" when different speakers are talking
5. Click "Stop Recording" when done
6. The system will automatically:
   - Save all transcripts
   - Complete the session
   - Generate analysis (key points, summary, etc.)

### Viewing Previous Conversations

- All previous conversations are listed in the "Previous Conversations" section
- Click on any session to view its transcript and analysis
- Use "Regenerate" to re-analyze with updated AI models

### Analysis Features

The AI analysis provides:
- **Key Points**: Main medical points discussed
- **Summary**: Clinical summary in SOAP format
- **Medical Terms**: Extracted medical terminology
- **Patient Concerns**: Identified patient concerns and symptoms
- **Recommendations**: Suggested follow-up actions

## Technical Details

### Web Speech API

The frontend uses the browser's native Web Speech API:
- **Browser Support**: Chrome, Edge, Safari (latest versions)
- **Limitations**: 
  - Requires internet connection
  - Accuracy depends on microphone quality
  - May not work in all browsers

### AI Analysis

When `OPENAI_API_KEY` is set:
- Uses GPT-4 for analysis
- Higher quality summaries and key points
- Better medical term extraction

When not available:
- Falls back to rule-based analysis
- Still provides basic summaries and key points
- Medical term extraction via keyword matching

### Database Schema

```sql
-- Sessions
conversation_sessions (
  id, patient_id, clinician_id, session_date,
  duration_seconds, status, created_at, updated_at
)

-- Transcripts
conversation_transcripts (
  id, session_id, speaker, text,
  timestamp_seconds, confidence, created_at
)

-- Analysis
conversation_analysis (
  id, session_id, full_transcript,
  key_points (JSONB), summary, medical_terms (JSONB),
  concerns_identified (JSONB), recommendations, created_at
)
```

## Future Enhancements

1. **Audio File Storage**: Store actual audio files in MinIO/S3
2. **Advanced Speech Recognition**: Integrate with cloud services (Google Cloud STT, AssemblyAI)
3. **Real-time Analysis**: Analyze during recording, not just after
4. **Multi-language Support**: Support for multiple languages
5. **Speaker Diarization**: Automatic speaker identification
6. **Integration with Clinical Notes**: Auto-populate clinical notes from summaries

## Troubleshooting

### Speech Recognition Not Working

- **Check Browser**: Use Chrome or Edge for best support
- **Check Microphone**: Ensure microphone permissions are granted
- **Check HTTPS**: Web Speech API requires secure context (HTTPS or localhost)

### Analysis Not Generating

- **Check OpenAI Key**: If using AI analysis, ensure `OPENAI_API_KEY` is set
- **Check Transcripts**: Ensure transcripts were saved before analysis
- **Check Backend Logs**: Look for errors in conversation analysis service

### Transcripts Not Saving

- **Check Network**: Ensure frontend can reach backend
- **Check Backend**: Verify conversation API endpoints are working
- **Check Database**: Ensure conversation tables exist

## Security & Privacy

- ✅ All conversations are stored securely in the database
- ✅ Only the treating clinician can access their sessions
- ✅ Admins can access all sessions (for research)
- ✅ Transcripts are encrypted at rest (via database encryption)
- ✅ No PHI should be included (synthetic data only)

## Research Value

This feature enables:
- **Conversation Analysis**: Study doctor-patient communication patterns
- **AI Performance**: Evaluate AI analysis quality
- **Workflow Efficiency**: Measure time saved with automated summaries
- **Clinical Documentation**: Study how summaries affect documentation quality

