# Quick Fix: AI Model Not Showing

## Problem
- Only seeing "RULES" suggestions
- No "AI_MODEL" or "HYBRID" badges
- 503 error when generating suggestions

## Root Cause
1. ✅ **protobuf installed** - Fixed
2. ⚠️ **Model loading failing** - BioGPT/DialoGPT might not be available
3. ⚠️ **Service might be hanging** during model load

## Quick Fix: Use GPT2 (Always Works)

The code now tries 3 models in order:
1. `microsoft/biogpt` (might not exist)
2. `microsoft/DialoGPT-medium` (might be too large)
3. `gpt2` (small, always available)

**GPT2 will work** - it's a small model that's always available on HuggingFace.

## Test It Now

1. **Generate suggestions** in the UI
2. **Wait 30-60 seconds** (first time downloads GPT2 model ~500MB)
3. **Check logs:**
   ```bash
   docker logs ehr-diagnosis-helper-service --tail 20 | grep -i "model\|ai"
   ```

## Expected Behavior

**First request (model download):**
- Takes 30-60 seconds
- Downloads GPT2 model
- Logs: "Attempting to load AI model: gpt2"
- Logs: "✅ AI model loaded successfully: gpt2"

**Subsequent requests:**
- Fast (~1-2 seconds)
- Shows "AI_MODEL" badges
- More suggestions (rules + AI)

## If Still Not Working

**Option 1: Disable AI (Use Rules Only)**
```bash
# Add to .env
USE_AI_MODEL=false
```

**Option 2: Check Logs**
```bash
docker logs ehr-diagnosis-helper-service --tail 50
```

Look for:
- "Failed to load" messages
- "AI model loaded successfully" ✅
- "Generated X AI suggestions" ✅

## Current Status

✅ Service is running  
✅ protobuf installed  
✅ Code fixed (tries 3 models)  
⚠️ Waiting for first model load (downloads on first use)  

**Try generating suggestions again - it should work now!**

