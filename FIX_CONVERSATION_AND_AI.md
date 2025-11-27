# Fix Conversation and AI Suggestions Issues

## Problem 1: Conversation Tables Don't Exist

**Error:** `relation "conversation_sessions" does not exist`

### Solution: Create Conversation Tables in Supabase

1. **Go to Supabase Dashboard:**
   - Open your Supabase project
   - Navigate to **SQL Editor**

2. **Run the Migration Script:**
   - Copy the contents of `scripts/create_conversation_tables.sql`
   - Paste into SQL Editor
   - Click **Run**

   Or run this SQL directly:

```sql
-- Create conversation tables
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

CREATE TABLE IF NOT EXISTS conversation_transcripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    speaker VARCHAR(20) NOT NULL CHECK (speaker IN ('doctor', 'patient')),
    text TEXT NOT NULL,
    timestamp_seconds INTEGER,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

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

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_patient_id ON conversation_sessions(patient_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_clinician_id ON conversation_sessions(clinician_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_status ON conversation_sessions(status);
CREATE INDEX IF NOT EXISTS idx_conversation_transcripts_session_id ON conversation_transcripts(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_analysis_session_id ON conversation_analysis(session_id);
```

3. **Restart Backend:**
   ```bash
   docker compose -f devops/docker-compose.yml restart backend
   ```

---

## Problem 2: CORS Errors

**Error:** `Access to XMLHttpRequest ... has been blocked by CORS policy`

### Solution: Verify CORS Configuration

1. **Check Backend is Running:**
   ```bash
   docker compose -f devops/docker-compose.yml ps backend
   ```

2. **Check CORS Settings in `.env`:**
   - Ensure `CORS_ORIGINS` includes `http://localhost:3000`
   - This should already be set in `app/backend/core/config.py`

3. **Restart Backend:**
   ```bash
   docker compose -f devops/docker-compose.yml restart backend
   ```

4. **Check Backend Logs:**
   ```bash
   docker compose -f devops/docker-compose.yml logs backend --tail=20
   ```

---

## Problem 3: AI Suggestions Not Working

### Check AI Model Services

1. **Verify Services are Running:**
   ```bash
   docker compose -f devops/docker-compose.yml ps
   ```

   You should see:
   - `vital-risk-service`
   - `image-analysis-service`
   - `diagnosis-helper-service`

2. **Check Service Logs:**
   ```bash
   # Check diagnosis helper (most commonly used)
   docker compose -f devops/docker-compose.yml logs diagnosis-helper-service --tail=30
   ```

3. **Test AI Endpoint Directly:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ai/diagnosis-helper?patient_id=6c0f319d-e260-4063-93c0-401f65b0e0b5 \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json"
   ```

4. **Common Issues:**
   - **Service not running:** Start with `docker compose -f devops/docker-compose.yml up -d diagnosis-helper-service`
   - **503 Service Unavailable:** Check service logs for errors
   - **Missing Optional import:** Check `app/model-services/diagnosis-helper/suggestion_model.py` has `from typing import Optional`

---

## Quick Fix Checklist

- [ ] Run `scripts/create_conversation_tables.sql` in Supabase SQL Editor
- [ ] Restart backend: `docker compose -f devops/docker-compose.yml restart backend`
- [ ] Verify all AI services are running: `docker compose -f devops/docker-compose.yml ps`
- [ ] Check backend logs for errors: `docker compose -f devops/docker-compose.yml logs backend --tail=50`
- [ ] Test conversation endpoint: Try creating a session again
- [ ] Test AI suggestions: Click "Generate Suggestions" button

---

## After Fixing

1. **Test Conversation:**
   - Go to patient detail page
   - Navigate to "Conversation" section
   - Click "Start Recording"
   - Should create session successfully

2. **Test AI Suggestions:**
   - Go to "AI Suggestions" section
   - Click "Generate Suggestions"
   - Should see diagnostic suggestions appear

3. **Verify No Errors:**
   - Check browser console (F12)
   - Should see no CORS or 500 errors
   - Check Network tab for successful API calls

---

## Still Having Issues?

1. **Check Backend Logs:**
   ```bash
   docker compose -f devops/docker-compose.yml logs backend --tail=100 | grep -i error
   ```

2. **Check Frontend Console:**
   - Open browser DevTools (F12)
   - Check Console and Network tabs
   - Look for specific error messages

3. **Verify Database Connection:**
   - Check `.env` file has correct `DATABASE_URL`
   - Test connection in Supabase dashboard

4. **Verify Authentication:**
   - Make sure you're logged in
   - Check token is being sent in requests
   - Verify user role is `clinician` or `admin`

