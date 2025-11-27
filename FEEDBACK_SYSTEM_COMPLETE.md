# Self-Adaptive AI Feedback System

## Overview

When clinicians interact with AI suggestions (Accept, Ignore, Not Relevant), the system:
1. **Records** the feedback in the database
2. **Analyzes** patterns over time
3. **Learns** by adjusting confidence scores
4. **Adapts** future suggestions based on what worked

---

## What Happens When a Clinician Acts on a Suggestion

### 1. Accept
- **Recorded as:** `action: "accept"`, `was_helpful: true`
- **Effect:** Increases acceptance rate for that suggestion type
- **Learning:** If acceptance rate > 70%, confidence is increased by 5%

### 2. Ignore
- **Recorded as:** `action: "ignore"`, `was_helpful: null`
- **Effect:** Neutral impact
- **Learning:** May indicate suggestion timing or presentation issues

### 3. Not Relevant
- **Recorded as:** `action: "not_relevant"`, `was_helpful: false`
- **Effect:** Decreases relevance score
- **Learning:** If acceptance rate < 30%, confidence is decreased by 5%

---

## Database Tables Created

### `suggestion_feedback`
Stores every clinician interaction with suggestions:
```sql
- suggestion_id: Which suggestion
- clinician_id: Who provided feedback
- action: accept/ignore/not_relevant
- clinical_relevance: 1-5 Likert rating (optional)
- agreement_rating: 1-5 (optional)
- clinician_comment: Free text (optional)
- patient_context: Age, sex, diagnosis for pattern learning
- feedback_used_for_training: Has AI learned from this?
```

### `learning_events`
Tracks when AI adapts:
```sql
- event_type: "confidence_adjustment", "rule_disabled", etc.
- affected_source: rules, ai_model, hybrid
- previous_value: Before learning
- new_value: After learning
- trigger_reason: Why this happened
- feedback_count_used: How much data triggered this
```

### `feedback_aggregation`
Periodic statistics:
```sql
- suggestion_source: rules, ai_model, hybrid
- total_shown, total_accepted, total_ignored
- acceptance_rate
- confidence_adjustment: How much to adjust
```

---

## Self-Adaptive Learning Algorithm

```python
# Thresholds
MIN_FEEDBACK = 10  # Need at least 10 feedback items
LOW_ACCEPTANCE = 0.3  # Below 30% = reduce confidence
HIGH_ACCEPTANCE = 0.7  # Above 70% = increase confidence
ADJUSTMENT_STEP = 0.05  # 5% adjustment per learning event

# Check if learning should occur
if feedback_count >= MIN_FEEDBACK:
    if acceptance_rate < LOW_ACCEPTANCE:
        # AI suggestions not being accepted
        # DECREASE confidence by 5%
        create_learning_event("confidence_adjustment", -0.05)
    
    elif acceptance_rate > HIGH_ACCEPTANCE:
        # AI suggestions being accepted
        # INCREASE confidence by 5%
        create_learning_event("confidence_adjustment", +0.05)
```

---

## How to Use

### 1. Run Database Migration
```bash
# In Supabase SQL Editor, run:
scripts/create_feedback_tables.sql
```

### 2. Restart Backend
```bash
docker compose -f devops/docker-compose.yml restart backend
```

### 3. View Analytics
- Navigate to: `/feedback/analytics`
- (Researcher/Admin only)

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/feedback` | POST | Submit feedback |
| `/api/v1/feedback/stats` | GET | Get aggregated stats |
| `/api/v1/feedback/timeline` | GET | Get time-series data |
| `/api/v1/feedback/learning-events` | GET | Get learning history |
| `/api/v1/feedback/confidence-adjustments` | GET | Get current adjustments |
| `/api/v1/feedback/my-feedback` | GET | Get clinician's own feedback |

---

## Analytics Dashboard Features

### 📊 Overview Stats
- Total feedback count
- Acceptance rate (with color coding)
- Learning readiness status
- Average ratings

### 📈 Timeline Chart
- Feedback trends over time
- Visual comparison of accepted vs rejected
- Configurable time periods (7, 14, 30, 90 days)

### 🧠 Self-Adaptive AI Status
- Current confidence adjustments per source
- Shows if rules/ai_model/hybrid have been adjusted
- Percentage change from baseline

### 📚 Learning Events History
- When AI learned
- What triggered the learning
- What changed
- Whether it's still active

### 📥 Export Data
- Export all analytics as JSON
- For academic analysis
- Includes all raw data

---

## Research Value

### Metrics Collected
1. **Acceptance Rate** - Do clinicians trust AI?
2. **Time to Decision** - Does AI speed up workflow?
3. **Rating Distributions** - Quality perception
4. **Learning Frequency** - How often AI adapts
5. **Confidence Drift** - How AI confidence changes

### Research Questions Enabled
- RQ1: Do evidence-based explanations increase acceptance?
- RQ2: Does self-adaptive AI improve over time?
- RQ3: What factors predict suggestion acceptance?
- RQ4: How does feedback type vary by clinician?

---

## Example Workflow

1. **Clinician views suggestion** → Logged by MAPE-K Monitor
2. **Clinician clicks "Accept"** → Feedback stored
3. **System checks if enough feedback** → 10+ items needed
4. **If acceptance rate > 70%** → Create learning event
5. **Adjust confidence by +5%** → Future suggestions boosted
6. **Researcher views analytics** → See the adaptation
7. **Export for paper** → Include in publication

---

## Files Created

| File | Purpose |
|------|---------|
| `models/suggestion_feedback.py` | Database models |
| `schemas/feedback.py` | API schemas |
| `services/feedback_service.py` | Business logic |
| `api/routes/feedback.py` | API endpoints |
| `frontend/app/feedback/analytics/page.tsx` | Analytics UI |
| `scripts/create_feedback_tables.sql` | Database migration |

---

## Summary

✅ **Feedback Storage** - Every interaction recorded  
✅ **Self-Adaptive Learning** - AI adjusts confidence  
✅ **Analytics Dashboard** - Visual insights  
✅ **Research Export** - Academic-ready data  
✅ **Audit Trail** - Learning history tracked  

The AI is now truly self-adaptive, learning from clinician feedback to improve over time! 🧠

