# How to Use Hybrid AI Models

## Step 1: Enable AI Models

Add these environment variables to your `.env` file (in project root):

```bash
# Enable AI models
USE_AI_MODEL=true          # For diagnosis helper (BioGPT)
USE_ML_MODEL=true          # For vital risk (LightGBM)
USE_CNN_MODEL=true         # For image analysis (CheXNet)

# Optional: Adjust weights (default is 50/50)
RULE_WEIGHT=0.6            # 60% weight for rules
AI_WEIGHT=0.4              # 40% weight for AI
VITAL_RULE_WEIGHT=0.5      # 50% for vital risk rules
VITAL_ML_WEIGHT=0.5        # 50% for vital risk ML
```

**Or set them directly:**
```bash
export USE_AI_MODEL=true
export USE_ML_MODEL=true
export USE_CNN_MODEL=true
```

---

## Step 2: Restart Services

After setting environment variables, restart the model services:

```bash
cd /Users/kavee/Projects/PhD/Medical\ EHR\ Software

docker compose -f devops/docker-compose.yml restart \
  diagnosis-helper-service \
  vital-risk-service \
  image-analysis-service
```

---

## Step 3: Using Each Model

### **1. Diagnosis Helper (Rules + BioGPT)**

**Where to use:**
- Patient Detail Page → "AI Suggestions" section

**How to use:**
1. Navigate to a patient (e.g., Sarah Chen)
2. Click on "AI Suggestions" tab
3. Click "Generate Suggestions" button
4. You'll see suggestions from:
   - **Rules:** Fast, explainable suggestions (e.g., "Low B12 may contribute to cognitive decline")
   - **AI Model:** Contextual suggestions from BioGPT (e.g., "Patient shows signs of reversible cognitive impairment...")
   - **Hybrid:** Combined and deduplicated suggestions

**What you'll see:**
- Each suggestion has a `source` tag: "rules", "ai_model", or "hybrid"
- Confidence scores (0.0-1.0)
- Explanations for each suggestion

**Example:**
```
✅ Suggestion 1 (Rules)
   "Low B12 levels may contribute to cognitive decline..."
   Confidence: 0.7 | Source: rules

✅ Suggestion 2 (AI Model)
   "Patient's combination of elevated TSH and cognitive symptoms suggests..."
   Confidence: 0.65 | Source: ai_model

✅ Suggestion 3 (Hybrid)
   "Hypertension with cognitive decline may indicate vascular dementia risk..."
   Confidence: 0.75 | Source: hybrid
```

---

### **2. Vital Risk (Rules + LightGBM)**

**Where to use:**
- Patient Detail Page → "Vitals" section
- Dashboard → Patient cards (risk indicators)

**How to use:**
1. Navigate to a patient with vital signs data
2. View the "Vitals" section
3. Risk assessment is automatically calculated
4. You'll see:
   - **Rule-based risk:** Threshold-based assessment
   - **ML model risk:** Pattern-based prediction
   - **Hybrid risk:** Weighted combination

**What you'll see:**
- Risk level: "routine", "needs_attention", or "high_concern"
- Risk score: 0.0-1.0
- Explanation: "Hybrid assessment: Rule-based (medium, score: 0.65) + ML model (high, score: 0.72) = high risk (combined score: 0.685)"

**Note:** LightGBM model needs to be trained first. If model file is missing, it will use rules-only.

---

### **3. Image Analysis (Rules + CheXNet)**

**Where to use:**
- Patient Detail Page → "Imaging" section

**How to use:**
1. Navigate to a patient
2. Click on "Imaging" tab
3. Upload a chest X-ray image
4. The system will analyze using:
   - **Rules:** Metadata and quality checks
   - **CNN (CheXNet):** Deep learning analysis for abnormalities
   - **Hybrid:** Combined results

**What you'll see:**
- Abnormality score: 0.0-1.0
- Classification: e.g., "Pneumonia", "Atelectasis", "Normal"
- Explanation: "Hybrid analysis: CNN model detected Pneumonia (75% confidence). Rule-based: suspicious (60%)."

**Note:** CheXNet only works for chest X-rays. Other image types use rules-only.

---

## Step 4: Verify Models Are Working

### **Check Service Logs:**

```bash
# Diagnosis Helper logs
docker logs ehr-diagnosis-helper-service | grep -i "ai\|hybrid\|model"

# Vital Risk logs
docker logs ehr-vital-risk-service | grep -i "ml\|hybrid\|model"

# Image Analysis logs
docker logs ehr-image-analysis-service | grep -i "cnn\|hybrid\|model"
```

**Look for:**
- "Generating AI model suggestions..."
- "Hybrid model generated X suggestions"
- "ML model risk: high"
- "CNN detected: Pneumonia"

### **Test via API:**

**Test Diagnosis Helper:**
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
  }'
```

**Check response for:**
- Suggestions with `"source": "ai_model"` or `"source": "hybrid"`
- Multiple suggestions (rules + AI)

**Test Vital Risk:**
```bash
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "test",
    "vitals": [
      {"timestamp": "2025-01-01T00:00:00Z", "hr": 95, "bp_sys": 158, "bp_dia": 98, "spo2": 96, "rr": 19, "temp": 36.8}
    ]
  }'
```

**Check response for:**
- Explanation mentioning "Hybrid assessment" or "ML model"

---

## Step 5: Compare Rules vs Hybrid

### **In the UI:**

1. **Disable AI models** (set `USE_AI_MODEL=false` in `.env`)
2. Generate suggestions → See rules-only results
3. **Enable AI models** (set `USE_AI_MODEL=true`)
4. Generate suggestions → See hybrid results
5. Compare the difference!

### **What to Look For:**

**Rules-only:**
- Fewer suggestions (typically 3-7)
- Very specific, rule-based
- Fast response (<100ms)
- Fully explainable

**Hybrid (Rules + AI):**
- More suggestions (typically 5-12)
- More contextual and nuanced
- Slightly slower (1-2 seconds for AI)
- Combines explainability with learned patterns

---

## Troubleshooting

### **Models Not Working?**

1. **Check if dependencies are installed:**
   ```bash
   docker exec -it ehr-diagnosis-helper-service python -c "import transformers, torch; print('✅ Installed')"
   ```

2. **Check environment variables:**
   ```bash
   docker exec -it ehr-diagnosis-helper-service env | grep USE_AI
   ```

3. **Check service logs:**
   ```bash
   docker logs ehr-diagnosis-helper-service --tail 50
   ```

### **BioGPT Not Loading?**

- First load takes time (~30 seconds) to download model
- Check logs: `docker logs ehr-diagnosis-helper-service | grep -i "loading\|model"`
- Model auto-downloads on first use (~350MB)

### **LightGBM Not Working?**

- Model file needs to be trained first
- System falls back to rules-only if model missing
- This is expected - you can train a model later or use rules-only

### **CheXNet Not Working?**

- Only works for chest X-rays
- Other image types use rules-only (expected)
- Check logs for "CNN model only supports chest X-rays"

---

## Expected Behavior

### **With AI Models Enabled:**
- ✅ More suggestions (rules + AI combined)
- ✅ Suggestions tagged with source
- ✅ Slightly slower (1-2 seconds for AI inference)
- ✅ Better coverage of edge cases

### **With AI Models Disabled:**
- ✅ Rules-only (works as before)
- ✅ Fast response (<100ms)
- ✅ Fully explainable
- ✅ No errors or crashes

---

## Research Use Cases

### **Compare Approaches:**
1. **A/B Testing:** Randomly assign clinicians to rules-only vs hybrid
2. **Preference Study:** Ask clinicians which suggestions they prefer
3. **Accuracy Study:** Measure which approach catches more issues
4. **Cognitive Load:** Compare NASA-TLX scores for rules vs hybrid

### **Metrics to Track:**
- Suggestion acceptance rate (rules vs AI vs hybrid)
- Time to decision
- Clinician confidence scores
- False positive/negative rates

---

## Quick Start Checklist

- [ ] Dependencies installed (`transformers`, `torch`, `lightgbm`)
- [ ] Environment variables set (`USE_AI_MODEL=true`, etc.)
- [ ] Services restarted
- [ ] Tested with Sarah Chen patient
- [ ] Verified suggestions show "ai_model" or "hybrid" source
- [ ] Checked service logs for confirmation

---

## Example Workflow

1. **Login** as clinician
2. **Navigate** to patient "Sarah Chen"
3. **Click** "AI Suggestions" tab
4. **Click** "Generate Suggestions"
5. **See** suggestions from both rules and AI:
   ```
   ✅ Low B12 levels may contribute to cognitive decline... (Rules)
   ✅ Patient shows signs of reversible cognitive impairment... (AI Model)
   ✅ Hypertension with cognitive decline may indicate... (Hybrid)
   ```
6. **Review** each suggestion's source, confidence, and explanation
7. **Compare** with rules-only mode (disable AI, regenerate)

---

**That's it!** Your hybrid AI system is now active and ready to use! 🚀

For more details, see:
- `HYBRID_AI_IMPLEMENTATION.md` - Technical details
- `HYBRID_AI_SETUP_COMPLETE.md` - Setup summary
- `AI_MODELS_EXPLANATION.md` - What models are used

