# Fix: AI Model Not Loading - Only Rules Showing

## Problem

You're only seeing "RULES" suggestions, not "AI_MODEL" or "HYBRID" ones.

**Error in logs:**
```
Error loading AI model: microsoft/BioGPT-Base is not a local folder and is not a valid model identifier
```

## Root Causes

1. **Wrong model name:** `microsoft/BioGPT-Base` doesn't exist on HuggingFace
2. **Model might not be installed:** Transformers library might not be installed
3. **Model too large:** BioGPT might be too large for your system

## Solutions

### **Solution 1: Use Correct Model Name (Quick Fix)**

The model name has been updated to `microsoft/biogpt`. Restart the service:

```bash
docker compose -f devops/docker-compose.yml restart diagnosis-helper-service
```

### **Solution 2: Use Smaller Alternative Model**

If BioGPT still doesn't work, the code now falls back to `microsoft/DialoGPT-medium` (smaller, more available).

### **Solution 3: Disable AI Model (Use Rules Only)**

If you want to disable AI and use rules only:

```bash
# Add to .env file
USE_AI_MODEL=false
```

Then restart:
```bash
docker compose -f devops/docker-compose.yml restart diagnosis-helper-service
```

### **Solution 4: Install Dependencies**

If transformers isn't installed:

```bash
docker exec -it ehr-diagnosis-helper-service pip install transformers torch
```

---

## Verify It's Working

### **Check Logs:**

```bash
docker logs ehr-diagnosis-helper-service --tail 50 | grep -i "ai\|hybrid\|model"
```

**Look for:**
- ✅ "Loading AI model: microsoft/biogpt" (or fallback model)
- ✅ "AI model loaded successfully"
- ✅ "Generated X AI suggestions"
- ❌ "Error loading AI model" = still not working

### **Test in UI:**

1. Go to patient "Sarah Chen"
2. Click "AI Suggestions" tab
3. Click "Generate Suggestions"
4. Check suggestion badges:
   - Should see "RULES", "AI_MODEL", or "HYBRID" badges
   - If only "RULES" = AI model not working

### **Test via API:**

```bash
curl -X POST http://localhost:8003/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test",
    "age": 68,
    "sex": "F",
    "primary_diagnosis": "Mild Cognitive Impairment",
    "vitals": [{"timestamp": "2025-01-01T00:00:00Z", "hr": 95, "bp_sys": 158, "bp_dia": 98, "spo2": 96, "rr": 19, "temp": 36.8}],
    "labs": [{"timestamp": "2025-01-01T00:00:00Z", "lab_type": "B12", "value": 180, "normal_range": "200-900"}],
    "diagnoses": ["Mild Cognitive Impairment"]
  }' | python3 -m json.tool | grep -i "source"
```

**Check response for:**
- `"source": "rules"` = Rules only
- `"source": "ai_model"` = AI working!
- `"source": "hybrid"` = Combined

---

## Expected Behavior

### **With AI Model Working:**
- ✅ Suggestions show "RULES", "AI_MODEL", or "HYBRID" badges
- ✅ More suggestions (8-12 instead of 6)
- ✅ Some suggestions have `source: "ai_model"`
- ✅ Logs show "Generated X AI suggestions"

### **With AI Model Not Working (Current State):**
- ⚠️ All suggestions show "RULES" badge
- ⚠️ Only 6 suggestions (rules only)
- ⚠️ Logs show "Generated 0 AI suggestions"
- ⚠️ Error: "Error loading AI model"

---

## Quick Fix Commands

```bash
# 1. Restart service (after code fix)
docker compose -f devops/docker-compose.yml restart diagnosis-helper-service

# 2. Check if transformers is installed
docker exec -it ehr-diagnosis-helper-service python -c "import transformers; print('✅ Installed')"

# 3. If not installed, install it
docker exec -it ehr-diagnosis-helper-service pip install transformers torch

# 4. Check logs
docker logs ehr-diagnosis-helper-service --tail 30 | grep -i "ai\|error"

# 5. Test again in UI
# Go to patient → AI Suggestions → Generate Suggestions
```

---

## Alternative: Use Simpler Model

If BioGPT is too large or unavailable, you can use a smaller model by updating `ai_model.py`:

```python
# Change this line:
model_name = "microsoft/biogpt"

# To this (smaller, faster):
model_name = "gpt2"  # Very small, always available
# Or:
model_name = "microsoft/DialoGPT-small"  # Small medical-ish model
```

Then restart the service.

---

## Current Status

✅ **Code fixed:** Model name updated to `microsoft/biogpt`  
✅ **Fallback added:** Will try `microsoft/DialoGPT-medium` if BioGPT fails  
⚠️ **Need to restart:** Service needs restart to pick up changes  
⚠️ **Dependencies:** Make sure transformers is installed  

**Next step:** Restart the service and test again!

