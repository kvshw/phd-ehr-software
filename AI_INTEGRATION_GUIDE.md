# AI Model Integration Guide

## Overview

The EHR platform has **3 AI model services** that provide suggestions with full explainability:

1. **Vital Risk Model** - Analyzes vital signs trends to predict patient risk
2. **Image Analysis Model** - Analyzes medical images for abnormalities
3. **Diagnosis Helper** - Generates rule-based diagnosis suggestions

## Current Status

### ✅ What's Implemented

1. **Backend AI Routing** (`app/backend/api/routes/ai.py`)
   - `/api/v1/ai/vitals-risk` - Routes to vital risk service
   - `/api/v1/ai/image-analysis` - Routes to image analysis service
   - `/api/v1/ai/diagnosis-helper` - Routes to diagnosis helper service
   - `/api/v1/ai/suggestions/{patient_id}` - Gets stored suggestions

2. **Model Services** (Rule-based implementations)
   - `app/model-services/vital-risk/` - Risk assessment service
   - `app/model-services/image-analysis/` - Image analysis service
   - `app/model-services/diagnosis-helper/` - Diagnosis suggestion service

3. **Frontend Components**
   - `SuggestionsPanel` - Displays AI suggestions with explanations
   - `AIStatusPanel` - Shows active AI models and versions
   - `SuggestionAuditTrail` - Shows suggestion history
   - `TransparencyInfo` - Explains AI behavior and data usage

4. **Explainability Features**
   - Every suggestion includes an `explanation` field
   - Confidence scores displayed
   - Source information (which model generated it)
   - Model version tracking
   - Safety guardrails (no prescriptive language)

### ❌ What's Missing

1. **Model Services Not Running** - The microservices need to be started
2. **No Automatic Suggestion Generation** - Suggestions must be triggered manually
3. **No UI Button to Generate Suggestions** - Users can't easily trigger AI analysis

## How It Works

### Architecture Flow

```
Frontend (SuggestionsPanel)
    ↓
Backend API (/api/v1/ai/diagnosis-helper)
    ↓
AI Service Client (routes to microservice)
    ↓
Model Service (vital-risk/image-analysis/diagnosis-helper)
    ↓
Returns: { suggestions, explanations, confidence, version }
    ↓
Backend stores in database (suggestions table)
    ↓
Frontend displays with explainability
```

### 1. Vital Risk Model

**Service:** `app/model-services/vital-risk/`
**Port:** 8001
**Endpoint:** `POST /predict`

**Input:**
```json
{
  "patient_id": "uuid",
  "vitals": [
    {
      "timestamp": "2024-01-01T10:00:00Z",
      "hr": 95,
      "bp_sys": 140,
      "bp_dia": 90,
      "spo2": 98,
      "rr": 18,
      "temp": 37.0,
      "pain": 2
    }
  ]
}
```

**Output:**
```json
{
  "version": "1.0.0",
  "risk_level": "needs_attention",
  "score": 0.65,
  "top_features": ["heart_rate_elevated", "bp_high"],
  "explanation": "Heart rate is elevated (95 bpm) and systolic BP is high (140 mmHg). Consider monitoring closely."
}
```

**Explainability:**
- Risk level (routine/needs_attention/high_concern)
- Risk score (0.0-1.0)
- Top contributing features
- Human-readable explanation

### 2. Image Analysis Model

**Service:** `app/model-services/image-analysis/`
**Port:** 8002
**Endpoint:** `POST /analyze`

**Input:**
```json
{
  "image_id": "uuid",
  "image_type": "X-ray"
}
```

**Output:**
```json
{
  "version": "1.0.0",
  "abnormality_score": 0.78,
  "classification": "suspicious",
  "heatmap_url": "/static/heatmaps/123.png",
  "explanation": "Opacity area detected in upper quadrant. May indicate consolidation or mass."
}
```

**Explainability:**
- Abnormality score (0.0-1.0)
- Classification (normal/suspicious/abnormal)
- Visual heatmap (if available)
- Explanation of findings

### 3. Diagnosis Helper

**Service:** `app/model-services/diagnosis-helper/`
**Port:** 8003
**Endpoint:** `POST /suggest`

**Input:**
```json
{
  "patient_id": "uuid",
  "age": 65,
  "sex": "M",
  "vitals": [...],
  "labs": [...],
  "diagnoses": ["Type 2 Diabetes"]
}
```

**Output:**
```json
{
  "version": "1.0.0",
  "suggestions": [
    {
      "id": "dx-postop-infection",
      "text": "Post-operative fever + redness may indicate infection.",
      "confidence": 0.7,
      "source": "rules",
      "explanation": "Triggered due to fever>38°C and wound redness observed."
    }
  ]
}
```

**Explainability:**
- Each suggestion has an explanation
- Confidence score
- Source (rules/vital_risk/lab_analysis)
- Non-prescriptive language (safety guardrails)

## How to Enable AI Suggestions

### Step 1: Start Model Services

The model services are **not currently in docker-compose.yml**. You need to start them manually:

```bash
# Terminal 1: Vital Risk Service
cd app/model-services/vital-risk
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 2: Image Analysis Service
cd app/model-services/image-analysis
python3 -m uvicorn main:app --host 0.0.0.0 --port 8002

# Terminal 3: Diagnosis Helper Service
cd app/model-services/diagnosis-helper
python3 -m uvicorn main:app --host 0.0.0.0 --port 8003
```

Or add them to `docker-compose.yml` (recommended).

### Step 2: Verify Services Are Running

```bash
# Check vital risk service
curl http://localhost:8001/health

# Check image analysis service
curl http://localhost:8002/health

# Check diagnosis helper service
curl http://localhost:8003/health
```

### Step 3: Generate Suggestions

Currently, suggestions must be **manually triggered** via API calls. There's no UI button yet.

**Option A: Use API directly**
```bash
# Generate diagnosis suggestions for a patient
curl -X POST http://localhost:8000/api/v1/ai/diagnosis-helper \
  -H "Content-Type: application/json" \
  -H "Cookie: access_token=YOUR_TOKEN" \
  -d '{"patient_id": "PATIENT_UUID"}'
```

**Option B: Add UI Button** (recommended - see below)

## Explainability Features

### 1. Suggestion Explanations

Every suggestion includes:
- **Explanation field** - Human-readable reasoning
- **Confidence score** - 0.0-1.0 (displayed as percentage)
- **Source** - Which model/service generated it
- **Model version** - For tracking and reproducibility

### 2. Visual Display

In `SuggestionsPanel.tsx`:
- Explanation box with icon
- Confidence badge (color-coded: green/yellow/red)
- Source badge (vital_risk/image_analysis/diagnosis_helper)
- "Experimental" badge on all suggestions
- Safety notice at bottom

### 3. Transparency Components

- **AIStatusPanel** - Shows active models and versions
- **SuggestionAuditTrail** - History of all suggestions
- **TransparencyInfo** - Explains AI behavior and data usage

### 4. Safety Guardrails

- **No prescriptive language** - Suggestions use "may indicate" not "you should"
- **All outputs labeled "Experimental"**
- **Full audit trail** - All suggestions logged
- **User feedback** - Accept/Ignore/Not Relevant buttons

## Adding UI Button to Generate Suggestions

To make suggestions visible, add a "Generate AI Suggestions" button to the SuggestionsPanel:

```typescript
// In SuggestionsPanel.tsx, add:

const generateSuggestions = async () => {
  setLoading(true);
  try {
    // Call diagnosis helper endpoint
    await apiClient.post(`/ai/diagnosis-helper`, {
      patient_id: patientId
    });
    
    // Refresh suggestions
    await fetchSuggestions();
  } catch (err) {
    console.error('Error generating suggestions:', err);
  } finally {
    setLoading(false);
  }
};

// Add button in UI:
<button onClick={generateSuggestions}>
  Generate AI Suggestions
</button>
```

## Current Limitations

1. **Model Services Not Running** - Need to be started manually
2. **No Auto-Generation** - Suggestions don't generate automatically
3. **No UI Trigger** - No button to generate suggestions
4. **Rule-Based Only** - Currently using rule-based models, not ML models

## Next Steps to Enable AI

1. **Add Model Services to Docker Compose** (recommended)
2. **Add "Generate Suggestions" button** to SuggestionsPanel
3. **Auto-generate on patient page load** (optional)
4. **Add loading states** for suggestion generation

## Testing AI Suggestions

Once services are running:

1. Open a patient detail page
2. Navigate to "AI Suggestions" section
3. Click "Generate AI Suggestions" (if button is added)
4. View suggestions with explanations
5. Test Accept/Ignore/Not Relevant actions
6. Check SuggestionAuditTrail for history

## Explainability Checklist

✅ Every suggestion has an explanation
✅ Confidence scores displayed
✅ Source information shown
✅ Model versions tracked
✅ Safety guardrails in place
✅ Non-prescriptive language enforced
✅ "Experimental" labels on all outputs
✅ Audit trail maintained
✅ User feedback collected

## Summary

The AI integration is **fully implemented** but **not enabled** because:
1. Model services need to be started
2. Suggestions need to be triggered (no auto-generation)
3. No UI button to generate suggestions

**To see AI suggestions:**
1. Start the 3 model services
2. Add a "Generate Suggestions" button (or use API directly)
3. Suggestions will appear with full explainability

The explainability features are **already in the UI** - they just need suggestions to display!

