# Fix: 503 Service Unavailable - Timeout Issue

## Problem

Getting `503 Service Unavailable` when generating AI suggestions.

**Root Cause:**
- Backend timeout: 30 seconds
- AI model loading: 30-60 seconds (first request)
- Backend times out before model service responds

## Fix Applied

✅ **Increased timeout from 30s to 120s** in `app/backend/services/ai_service.py`

```python
AI_SERVICE_TIMEOUT = 120.0  # 120 seconds (was 30.0)
```

## Test It Now

1. **Go to patient page**
2. **Click "AI Suggestions" tab**
3. **Click "Generate Suggestions"**
4. **Wait 30-60 seconds** (first time loads model)
5. **You should see:**
   - ✅ Suggestions appear
   - ✅ "RULES" badges (gray)
   - ✅ "AI_MODEL" badges (green)
   - ✅ No 503 error

## Expected Behavior

**First Request (Model Loading):**
- Takes 30-60 seconds
- Downloads/loads DialoGPT-medium model
- Returns suggestions with both "rules" and "ai_model" sources

**Subsequent Requests:**
- Fast (~2-5 seconds)
- Model already loaded
- Returns suggestions immediately

## If Still Getting 503

1. **Check backend logs:**
   ```bash
   docker logs ehr-backend --tail 20 | grep -i "timeout\|error"
   ```

2. **Check diagnosis-helper logs:**
   ```bash
   docker logs ehr-diagnosis-helper-service --tail 20 | grep -i "error\|model"
   ```

3. **Verify service is running:**
   ```bash
   docker ps | grep diagnosis-helper
   curl http://localhost:8003/health
   ```

## Status

✅ **Timeout increased to 120 seconds**  
✅ **Backend restarted**  
✅ **Ready to test**  

**Try generating suggestions again - it should work now!**

