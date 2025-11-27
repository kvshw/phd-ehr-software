# Brain Health EHR Conversion & Voice-to-Text Plan

## Overview

This plan outlines the conversion of the EHR platform from general medical to **brain health focused**, along with the addition of **voice-to-text transcription** and **conversation analysis** features for doctor-patient interactions.

## Part 1: Brain Health Conversion

### 1.1 Terminology & Domain Changes

#### Current → Brain Health Mapping
- **Patients** → **Patients** (same, but brain health context)
- **Vitals** → **Neurological Assessments** (add brain-specific metrics)
- **Labs** → **Neuroimaging & Biomarkers** (MRI, CT, EEG, biomarkers)
- **Imaging** → **Brain Imaging** (MRI, CT scans, PET scans)
- **Diagnoses** → **Neurological Diagnoses** (Alzheimer's, Parkinson's, Depression, etc.)
- **AI Suggestions** → **Brain Health AI Insights**

#### New Brain Health Specific Fields
- **Cognitive Assessments:**
  - MMSE (Mini-Mental State Examination)
  - MoCA (Montreal Cognitive Assessment)
  - PHQ-9 (Depression screening)
  - GAD-7 (Anxiety screening)
  - Clock Drawing Test
  - Trail Making Test

- **Neurological Vitals:**
  - Headache frequency/severity
  - Sleep quality
  - Mood scores
  - Cognitive function scores
  - Medication adherence

- **Brain Health Metrics:**
  - Brain volume (from MRI)
  - White matter integrity
  - Functional connectivity
  - Biomarker levels (Aβ, tau, etc.)

### 1.2 Database Schema Updates

#### New Tables Needed
```sql
-- Cognitive Assessments
CREATE TABLE cognitive_assessments (
  id UUID PRIMARY KEY,
  patient_id UUID REFERENCES patients(id),
  assessment_type VARCHAR(50), -- MMSE, MoCA, PHQ-9, etc.
  score INTEGER,
  max_score INTEGER,
  interpretation TEXT,
  timestamp TIMESTAMP,
  created_at TIMESTAMP
);

-- Neurological Vitals
CREATE TABLE neurological_vitals (
  id UUID PRIMARY KEY,
  patient_id UUID REFERENCES patients(id),
  headache_frequency INTEGER, -- per week
  headache_severity INTEGER, -- 1-10
  sleep_quality INTEGER, -- 1-10
  mood_score INTEGER, -- 1-10
  cognitive_score INTEGER, -- 1-100
  medication_adherence BOOLEAN,
  timestamp TIMESTAMP,
  created_at TIMESTAMP
);

-- Brain Imaging Metadata
ALTER TABLE imaging ADD COLUMN scan_type VARCHAR(50); -- MRI, CT, PET, EEG
ALTER TABLE imaging ADD COLUMN brain_region VARCHAR(100);
ALTER TABLE imaging ADD COLUMN findings TEXT;
```

### 1.3 AI Model Services for Brain Health

#### New Model Services

1. **Cognitive Assessment Analyzer**
   - **Purpose:** Analyze cognitive test results
   - **Input:** MMSE, MoCA scores, patient history
   - **Output:** Risk assessment, progression prediction, recommendations
   - **File:** `app/model-services/cognitive-analyzer/`

2. **Neuroimaging Analyzer** (Enhanced Image Analysis)
   - **Purpose:** Analyze brain scans (MRI, CT, PET)
   - **Input:** Brain imaging files
   - **Output:** Findings, abnormalities, risk scores
   - **File:** `app/model-services/neuroimaging-analyzer/`

3. **Brain Health Risk Predictor**
   - **Purpose:** Predict risk of cognitive decline, dementia, etc.
   - **Input:** Cognitive scores, vitals, history, biomarkers
   - **Output:** Risk scores, progression timeline, recommendations
   - **File:** `app/model-services/brain-health-risk/`

4. **Treatment Response Predictor**
   - **Purpose:** Predict response to treatments/therapies
   - **Input:** Patient data, treatment history
   - **Output:** Expected outcomes, alternative suggestions
   - **File:** `app/model-services/treatment-predictor/`

## Part 2: Voice-to-Text & Conversation Analysis

### 2.1 Architecture Overview

```
Doctor-Patient Conversation
    ↓
[Browser Microphone] → [Web Speech API / WebRTC]
    ↓
[Real-time Transcription] → [Backend API]
    ↓
[Storage] → [Analysis Pipeline]
    ↓
[Key Points Extraction] → [Summary Generation]
    ↓
[Display to Doctor]
```

### 2.2 Technology Stack

#### Frontend (Voice Capture)
- **Web Speech API** (SpeechRecognition) - Browser-based
- **Alternative:** WebRTC + MediaRecorder for better quality
- **Library:** `react-speech-recognition` or native Web Speech API

#### Backend (Processing)
- **Speech-to-Text:** 
  - Option 1: OpenAI Whisper API (high accuracy)
  - Option 2: Google Cloud Speech-to-Text
  - Option 3: Azure Speech Services
  - Option 4: AssemblyAI (medical domain optimized)

- **Text Analysis:**
  - OpenAI GPT-4 for key points extraction
  - Custom NLP for medical terminology
  - Rule-based + AI for summary generation

#### Storage
- **Conversations Table:**
  - Store full transcriptions
  - Timestamps, speaker identification
  - Audio file references (optional)

### 2.3 Database Schema

```sql
-- Conversation Sessions
CREATE TABLE conversation_sessions (
  id UUID PRIMARY KEY,
  patient_id UUID REFERENCES patients(id),
  clinician_id UUID REFERENCES users(id),
  session_date TIMESTAMP,
  duration_seconds INTEGER,
  audio_file_url TEXT, -- Optional: store audio
  status VARCHAR(20), -- 'recording', 'processing', 'completed'
  created_at TIMESTAMP
);

-- Conversation Transcripts
CREATE TABLE conversation_transcripts (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES conversation_sessions(id),
  speaker VARCHAR(20), -- 'doctor', 'patient'
  text TEXT,
  timestamp_seconds INTEGER, -- Time in conversation
  confidence FLOAT, -- Speech recognition confidence
  created_at TIMESTAMP
);

-- Conversation Analysis
CREATE TABLE conversation_analysis (
  id UUID PRIMARY KEY,
  session_id UUID REFERENCES conversation_sessions(id),
  full_transcript TEXT,
  key_points JSONB, -- Array of key points
  summary TEXT,
  medical_terms JSONB, -- Extracted medical terms
  concerns_identified JSONB, -- Patient concerns
  recommendations TEXT,
  created_at TIMESTAMP
);
```

### 2.4 Implementation Components

#### Frontend Components

1. **VoiceRecorder Component**
   - Start/stop recording button
   - Real-time transcription display
   - Speaker identification (doctor/patient toggle)
   - Audio waveform visualization
   - File: `app/frontend/components/conversation/VoiceRecorder.tsx`

2. **ConversationTranscript Component**
   - Display full conversation
   - Highlight key points
   - Search functionality
   - Export options
   - File: `app/frontend/components/conversation/ConversationTranscript.tsx`

3. **ConversationSummary Component**
   - Display AI-generated summary
   - Key points list
   - Medical terms highlighted
   - Concerns and recommendations
   - File: `app/frontend/components/conversation/ConversationSummary.tsx`

#### Backend Services

1. **Conversation Service**
   - Create session
   - Store transcripts
   - Process audio files
   - File: `app/backend/services/conversation_service.py`

2. **Speech-to-Text Service**
   - Integrate with speech API
   - Handle real-time streaming
   - Process audio files
   - File: `app/backend/services/speech_to_text_service.py`

3. **Conversation Analysis Service**
   - Extract key points
   - Generate summaries
   - Identify medical terms
   - Extract concerns
   - File: `app/backend/services/conversation_analysis_service.py`

#### Model Service

1. **Conversation Analyzer Service**
   - AI-powered analysis
   - Key points extraction
   - Summary generation
   - Medical terminology extraction
   - File: `app/model-services/conversation-analyzer/`

## Part 3: Implementation Plan

### Phase 1: Brain Health Conversion (Week 1-2)

#### Step 1.1: Update Terminology
- [ ] Update all UI text to brain health context
- [ ] Change "Vitals" to "Neurological Assessments"
- [ ] Update patient forms with brain health fields
- [ ] Update dashboard labels and descriptions

#### Step 1.2: Database Schema
- [ ] Create cognitive_assessments table
- [ ] Create neurological_vitals table
- [ ] Update imaging table with brain-specific fields
- [ ] Create migration scripts

#### Step 1.3: Backend Models & APIs
- [ ] Create CognitiveAssessment model
- [ ] Create NeurologicalVital model
- [ ] Update Patient model with brain health fields
- [ ] Create API endpoints for new data types

#### Step 1.4: Frontend Components
- [ ] Create CognitiveAssessmentSection component
- [ ] Create NeurologicalVitalsSection component
- [ ] Update patient detail page with new sections
- [ ] Add brain health specific visualizations

### Phase 2: Brain Health AI Models (Week 2-3)

#### Step 2.1: Cognitive Analyzer Service
- [ ] Create service structure
- [ ] Implement rule-based analysis
- [ ] Add ML model integration (future)
- [ ] Create API endpoints

#### Step 2.2: Neuroimaging Analyzer
- [ ] Enhance existing image analysis
- [ ] Add brain-specific analysis
- [ ] Integrate with brain health risk
- [ ] Update frontend to show brain findings

#### Step 2.3: Brain Health Risk Predictor
- [ ] Create service structure
- [ ] Implement risk calculation
- [ ] Add progression prediction
- [ ] Create visualization components

### Phase 3: Voice-to-Text Infrastructure (Week 3-4)

#### Step 3.1: Frontend Voice Capture
- [ ] Create VoiceRecorder component
- [ ] Integrate Web Speech API
- [ ] Add real-time transcription display
- [ ] Implement speaker identification

#### Step 3.2: Backend API
- [ ] Create conversation_sessions table
- [ ] Create conversation_transcripts table
- [ ] Create API endpoints for sessions
- [ ] Implement audio file handling

#### Step 3.3: Speech-to-Text Integration
- [ ] Choose speech-to-text provider
- [ ] Create speech_to_text_service.py
- [ ] Implement real-time streaming
- [ ] Handle audio file processing

### Phase 4: Conversation Analysis (Week 4-5)

#### Step 4.1: Analysis Service
- [ ] Create conversation_analysis table
- [ ] Create conversation_analysis_service.py
- [ ] Implement key points extraction
- [ ] Implement summary generation

#### Step 4.2: AI Model Service
- [ ] Create conversation-analyzer service
- [ ] Integrate with OpenAI/GPT for analysis
- [ ] Implement medical term extraction
- [ ] Add concerns identification

#### Step 4.3: Frontend Display
- [ ] Create ConversationTranscript component
- [ ] Create ConversationSummary component
- [ ] Add to patient detail page
- [ ] Implement search and export

## Part 4: Technical Specifications

### 4.1 Voice-to-Text Options Comparison

| Option | Pros | Cons | Cost |
|--------|------|------|------|
| **Web Speech API** | Free, no backend needed, real-time | Lower accuracy, browser-dependent | Free |
| **OpenAI Whisper** | High accuracy, medical domain support | Requires API key, cost per minute | ~$0.006/min |
| **Google Cloud STT** | High accuracy, real-time streaming | Requires setup, cost | ~$0.006/min |
| **AssemblyAI** | Medical optimized, good accuracy | Cost, API dependency | ~$0.00025/sec |

**Recommendation:** Start with Web Speech API for MVP, upgrade to OpenAI Whisper for production.

### 4.2 Conversation Analysis Pipeline

```
1. Audio Input
   ↓
2. Speech-to-Text (Real-time or Post-processing)
   ↓
3. Transcript Storage
   ↓
4. AI Analysis:
   - Key Points Extraction (GPT-4)
   - Summary Generation (GPT-4)
   - Medical Term Extraction (NLP)
   - Concerns Identification (Rule-based + AI)
   ↓
5. Store Analysis Results
   ↓
6. Display to Doctor
```

### 4.3 Key Points Extraction Strategy

**Using GPT-4:**
```python
prompt = f"""
Analyze this doctor-patient conversation and extract:
1. Key medical points discussed
2. Patient concerns and symptoms
3. Doctor's observations
4. Treatment plans mentioned
5. Follow-up actions needed

Conversation:
{transcript}

Return as JSON:
{{
  "key_points": [...],
  "patient_concerns": [...],
  "doctor_observations": [...],
  "treatment_plans": [...],
  "follow_ups": [...]
}}
"""
```

### 4.4 Summary Generation Strategy

**Using GPT-4:**
```python
prompt = f"""
Create a concise clinical summary of this doctor-patient conversation.
Include:
- Chief complaint
- History of present illness
- Assessment
- Plan

Conversation:
{transcript}

Format as a clinical note (SOAP format).
"""
```

## Part 5: UI/UX Changes

### 5.1 Brain Health Dashboard
- Replace general health metrics with:
  - Cognitive function trends
  - Neurological assessment scores
  - Brain imaging status
  - Treatment adherence

### 5.2 Patient Detail Page
- Add new sections:
  - Cognitive Assessments
  - Neurological Vitals
  - Brain Imaging (enhanced)
  - Conversation History
  - Brain Health AI Insights

### 5.3 Conversation Interface
- New page: `/patients/[id]/conversation`
- Features:
  - Voice recorder with start/stop
  - Real-time transcription
  - Speaker toggle (Doctor/Patient)
  - Live key points display
  - Summary panel
  - Export options

## Part 6: File Structure

### New Files to Create

```
app/
├── backend/
│   ├── models/
│   │   ├── cognitive_assessment.py (NEW)
│   │   ├── neurological_vital.py (NEW)
│   │   ├── conversation_session.py (NEW)
│   │   └── conversation_transcript.py (NEW)
│   ├── services/
│   │   ├── conversation_service.py (NEW)
│   │   ├── speech_to_text_service.py (NEW)
│   │   └── conversation_analysis_service.py (NEW)
│   └── api/routes/
│       ├── cognitive_assessments.py (NEW)
│       ├── neurological_vitals.py (NEW)
│       └── conversations.py (NEW)
├── model-services/
│   ├── cognitive-analyzer/ (NEW)
│   ├── neuroimaging-analyzer/ (NEW)
│   ├── brain-health-risk/ (NEW)
│   └── conversation-analyzer/ (NEW)
└── frontend/
    ├── components/
    │   ├── brain-health/
    │   │   ├── CognitiveAssessmentSection.tsx (NEW)
    │   │   └── NeurologicalVitalsSection.tsx (NEW)
    │   └── conversation/
    │       ├── VoiceRecorder.tsx (NEW)
    │       ├── ConversationTranscript.tsx (NEW)
    │       └── ConversationSummary.tsx (NEW)
    └── app/
        └── patients/
            └── [id]/
                └── conversation/
                    └── page.tsx (NEW)
```

## Part 7: Implementation Priority

### High Priority (MVP)
1. ✅ Basic brain health terminology updates
2. ✅ Cognitive assessments data model
3. ✅ Voice-to-text recording (Web Speech API)
4. ✅ Basic conversation storage
5. ✅ Simple summary generation

### Medium Priority
1. Neurological vitals tracking
2. Brain imaging enhancements
3. Key points extraction
4. Conversation analysis UI

### Low Priority (Future)
1. Advanced AI models (ML-based)
2. Audio file storage
3. Multi-language support
4. Advanced analytics

## Part 8: Dependencies

### New Python Packages
```txt
# For speech-to-text
openai>=1.0.0  # For Whisper API
# OR
google-cloud-speech>=2.0.0
# OR
assemblyai>=0.15.0

# For conversation analysis
openai>=1.0.0  # For GPT-4
spacy>=3.5.0  # For NLP
```

### New Frontend Packages
```json
{
  "react-speech-recognition": "^3.10.0",
  "wavesurfer.js": "^7.0.0" // For audio visualization
}
```

## Part 9: Testing Strategy

### Brain Health Features
- Test cognitive assessment entry
- Test neurological vitals tracking
- Test brain imaging upload
- Test AI model predictions

### Voice-to-Text Features
- Test microphone access
- Test real-time transcription
- Test speaker identification
- Test accuracy with medical terms

### Conversation Analysis
- Test key points extraction
- Test summary generation
- Test medical term identification
- Test concerns extraction

## Part 10: Security & Privacy

### Voice Data
- ✅ Encrypt audio files at rest
- ✅ Secure transmission (HTTPS)
- ✅ Automatic deletion after processing (optional)
- ✅ PHI detection and redaction
- ✅ Access control (only treating clinician)

### Conversation Data
- ✅ Store transcripts securely
- ✅ Redact PHI if needed
- ✅ Audit logging
- ✅ Patient consent tracking

## Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Choose speech-to-text provider** - Web Speech API vs. paid service
3. **Start Phase 1** - Brain health conversion
4. **Implement voice recording** - Frontend component
5. **Add conversation analysis** - Backend service

---

**Would you like me to start implementing? I recommend starting with:**
1. Brain health terminology updates
2. Voice recorder component (Web Speech API)
3. Basic conversation storage
4. Simple summary generation

This will give you a working MVP quickly, then we can enhance with advanced features.

