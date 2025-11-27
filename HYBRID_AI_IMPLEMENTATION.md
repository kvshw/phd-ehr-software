# Hybrid AI Implementation Guide

## Overview

The system now supports **hybrid AI models** that combine:
- ✅ **Rule-based logic** (explainable, fast, reliable)
- ✅ **Local AI models** (learned patterns, enhanced accuracy)

---

## Architecture

### **Diagnosis Helper: Rules + BioGPT**
- **Rules:** Fast, explainable suggestions
- **AI Model:** BioGPT-Base (medical LLM) for enhanced suggestions
- **Combination:** Merges both, removes duplicates, sorts by confidence

### **Vital Risk: Rules + LightGBM**
- **Rules:** Threshold-based risk scoring
- **ML Model:** LightGBM (gradient boosting) for pattern recognition
- **Combination:** Weighted ensemble (50% rules, 50% ML)

### **Image Analysis: Rules + CheXNet**
- **Rules:** Metadata and quality checks
- **CNN Model:** CheXNet (DenseNet-121) for chest X-ray analysis
- **Combination:** Uses CNN if high confidence, otherwise combines

---

## Installation

### **Option 1: Full AI Models (Recommended for Research)**

```bash
cd app/model-services

# Install AI model dependencies
pip install transformers torch torchvision

# Install ML model dependencies
pip install lightgbm scikit-learn numpy

# Install image processing
pip install Pillow
```

### **Option 2: Minimal (Rules Only)**

If you don't want AI models, the system will automatically fall back to rules-only mode.

---

## Configuration

### **Environment Variables**

Add to `.env` or set in Docker:

```bash
# Enable/disable AI models
USE_AI_MODEL=true          # Enable AI for diagnosis helper
USE_ML_MODEL=true          # Enable ML for vital risk
USE_CNN_MODEL=true         # Enable CNN for image analysis

# Weights for hybrid combination
RULE_WEIGHT=0.6            # 60% weight for rules
AI_WEIGHT=0.4              # 40% weight for AI

VITAL_RULE_WEIGHT=0.5      # 50% for vital risk rules
VITAL_ML_WEIGHT=0.5        # 50% for vital risk ML
```

### **Model Files**

Models are loaded lazily (on first use). Place model files in:

```
app/model-services/
├── diagnosis-helper/
│   └── models/          # BioGPT will auto-download on first use
├── vital-risk/
│   └── models/
│       └── vital_risk_model.pkl  # Trained LightGBM model (optional)
└── image-analysis/
    └── models/
        └── chexnet.pth  # CheXNet weights (optional)
```

---

## How It Works

### **1. Diagnosis Helper (Hybrid)**

```python
# Step 1: Generate rule-based suggestions
rule_suggestions = generate_rule_suggestions(patient_data)
# Example: "Low B12 may contribute to cognitive decline"

# Step 2: Generate AI suggestions (if enabled)
ai_suggestions = generate_ai_suggestions(patient_data)
# Example: "Patient shows signs of reversible cognitive impairment..."

# Step 3: Merge and deduplicate
combined = merge_suggestions(rule_suggestions, ai_suggestions)

# Step 4: Tag source
for suggestion in combined:
    suggestion.source = "rules" | "ai_model" | "hybrid"
```

### **2. Vital Risk (Hybrid)**

```python
# Step 1: Rule-based risk
rule_risk = assess_rule_risk(vitals)
# Score: 0.65, Level: "medium"

# Step 2: ML model risk
ml_risk = predict_ml_risk(vitals)
# Score: 0.72, Level: "high"

# Step 3: Weighted combination
combined_score = (0.65 * 0.5) + (0.72 * 0.5) = 0.685
# Final: "high" risk
```

### **3. Image Analysis (Hybrid)**

```python
# Step 1: Rule-based analysis
rule_result = analyze_rule_image(image)

# Step 2: CNN analysis (if chest X-ray)
cnn_result = analyze_image_cnn(image_data)

# Step 3: Combine
if cnn_confidence > 0.7:
    use_cnn_result
else:
    combine_both
```

---

## Model Details

### **BioGPT-Base (Diagnosis Helper)**
- **Model:** `microsoft/BioGPT-Base`
- **Size:** ~350MB
- **RAM:** ~2GB
- **Inference:** 1-2 seconds (CPU), <500ms (GPU)
- **Auto-downloads:** Yes (on first use)
- **Fallback:** Rules-only if model unavailable

### **LightGBM (Vital Risk)**
- **Model:** Trained LightGBM classifier
- **Size:** ~10MB
- **RAM:** ~100MB
- **Inference:** <100ms
- **Training:** Requires training data (can use MIMIC-III)
- **Fallback:** Rules-only if model file missing

### **CheXNet (Image Analysis)**
- **Model:** DenseNet-121 (ChestX-ray14)
- **Size:** ~30MB
- **RAM:** ~500MB
- **Inference:** 500ms-1s (CPU), <200ms (GPU)
- **Supports:** Chest X-rays only
- **Fallback:** Rules-only for other image types

---

## Testing

### **Test Diagnosis Helper (Hybrid)**

1. **Enable AI:**
   ```bash
   export USE_AI_MODEL=true
   ```

2. **Restart service:**
   ```bash
   docker compose -f devops/docker-compose.yml restart diagnosis-helper-service
   ```

3. **Test in app:**
   - Go to patient "Sarah Chen"
   - Click "Generate Suggestions"
   - Should see suggestions from both rules and AI model

### **Test Vital Risk (Hybrid)**

1. **Enable ML:**
   ```bash
   export USE_ML_MODEL=true
   ```

2. **Restart service:**
   ```bash
   docker compose -f devops/docker-compose.yml restart vital-risk-service
   ```

3. **Test via API:**
   ```bash
   curl -X POST http://localhost:8001/predict \
     -H "Content-Type: application/json" \
     -d '{"patient_id":"test","vitals":[...]}'
   ```

### **Test Image Analysis (Hybrid)**

1. **Enable CNN:**
   ```bash
   export USE_CNN_MODEL=true
   ```

2. **Restart service:**
   ```bash
   docker compose -f devops/docker-compose.yml restart image-analysis-service
   ```

3. **Upload chest X-ray:**
   - Go to patient detail page
   - Upload a chest X-ray image
   - Should see CNN analysis results

---

## Research Benefits

### **Compare Approaches:**
1. **Rules Only:** Baseline, fully explainable
2. **AI Only:** Learned patterns, less explainable
3. **Hybrid:** Best of both worlds

### **Metrics to Track:**
- Suggestion acceptance rate (rules vs AI vs hybrid)
- Clinician preference (which source they trust more)
- Accuracy comparison
- Response time (rules vs AI)
- Explainability ratings

### **A/B Testing:**
- Randomly assign clinicians to rules-only vs hybrid
- Measure cognitive load (NASA-TLX)
- Measure decision quality
- Compare outcomes

---

## Performance Considerations

### **Memory Usage:**
- BioGPT: ~2GB RAM
- LightGBM: ~100MB RAM
- CheXNet: ~500MB RAM
- **Total:** ~2.6GB RAM for all models

### **Inference Speed:**
- Rules: <10ms
- BioGPT: 1-2s (CPU), <500ms (GPU)
- LightGBM: <100ms
- CheXNet: 500ms-1s (CPU), <200ms (GPU)

### **Optimization:**
- Lazy loading (models load on first use)
- Model caching (loaded once, reused)
- GPU acceleration (if available)
- Quantization (4-bit models for smaller size)

---

## Fallback Behavior

If AI models are unavailable or fail:
- ✅ System automatically falls back to rules-only
- ✅ No errors or crashes
- ✅ Logs warning messages
- ✅ Continues functioning normally

---

## Next Steps

1. **Install dependencies** (if you want AI models)
2. **Configure environment variables**
3. **Test hybrid mode** with Sarah Chen patient
4. **Compare results** (rules vs hybrid)
5. **Measure performance** impact
6. **Collect research data** on clinician preferences

---

## Status

✅ **Code implemented** - Hybrid models are ready  
⚠️ **Models not installed** - Need to install dependencies  
⚠️ **Models not trained** - LightGBM needs training data  

**Current behavior:** Falls back to rules-only (works as before)

**To enable AI:** Install dependencies and set environment variables.

