# Testing Guide for Self-Adaptive EHR Platform

## Overview

This guide provides multiple strategies for testing the feedback and analytics system when you don't have real clinicians available.

---

## 🎯 Strategy 1: Automated Test Data Generation (Recommended)

### Quick Start

```bash
# Generate 50 feedback items over the last 30 days
python3 scripts/generate_test_feedback.py --count 50 --days 30

# Generate 100 feedback items over 90 days (more realistic)
python3 scripts/generate_test_feedback.py --count 100 --days 90

# Generate feedback for a specific clinician
python3 scripts/generate_test_feedback.py --count 50 --clinician-id <uuid>
```

### What It Creates

- **Realistic distribution:**
  - 55% Accept
  - 30% Ignore
  - 15% Not Relevant

- **Realistic ratings:**
  - 40% of feedback includes detailed Likert ratings
  - Ratings correlate with action (accept = higher ratings)

- **Realistic comments:**
  - 20% have clinician comments
  - 10% have improvement suggestions

- **Time distribution:**
  - Spreads feedback over the specified time period
  - Creates natural timeline patterns

### Expected Results

After running the script, you should see:
- ✅ Analytics dashboard populated with data
- ✅ Timeline chart showing feedback trends
- ✅ Acceptance rate around 55%
- ✅ Learning events (if >10 feedback items)

---

## 🎯 Strategy 2: Manual Testing Interface

### Create a Simple Test Page

You can create a test page at `/feedback/test` that allows you to:
1. Select a suggestion
2. Click "Accept", "Ignore", or "Not Relevant"
3. Optionally add ratings and comments
4. See immediate feedback in analytics

### Implementation

```typescript
// app/frontend/app/feedback/test/page.tsx
// Simple interface to manually create feedback
```

---

## 🎯 Strategy 3: Simulated User Study

### For PhD Demonstration

1. **Create Test Scenarios:**
   - Scenario A: High acceptance rate (70%+) → AI should increase confidence
   - Scenario B: Low acceptance rate (30%-) → AI should decrease confidence
   - Scenario C: Mixed feedback → AI should stabilize

2. **Generate Data for Each:**
   ```bash
   # High acceptance scenario
   python3 scripts/generate_test_feedback.py --count 30 --days 7
   # Then manually update some to "accept" in database
   
   # Low acceptance scenario
   python3 scripts/generate_test_feedback.py --count 30 --days 7
   # Then manually update some to "not_relevant"
   ```

3. **Demonstrate Learning:**
   - Show analytics before learning
   - Trigger learning (need 10+ feedback)
   - Show analytics after learning
   - Explain confidence adjustments

---

## 🎯 Strategy 4: Scripted Demo Flow

### For Professor/Clinician Presentation

Create a demo script that:
1. Generates initial feedback (low acceptance)
2. Shows analytics dashboard
3. Generates more feedback (high acceptance)
4. Shows learning event triggered
5. Shows confidence adjustment
6. Explains the self-adaptive behavior

### Demo Script

```bash
#!/bin/bash
# demo_feedback.sh

echo "Step 1: Generate initial feedback (low acceptance)"
python3 scripts/generate_test_feedback.py --count 15 --days 7

echo "Step 2: Check analytics - should show low acceptance"
echo "Visit: http://localhost:3000/feedback/analytics"

echo "Step 3: Generate more feedback (high acceptance)"
python3 scripts/generate_test_feedback.py --count 20 --days 7

echo "Step 4: Check learning events - should see confidence adjustment"
echo "Visit: http://localhost:3000/feedback/analytics"
```

---

## 🎯 Strategy 5: Database Direct Manipulation

### For Fine-Tuned Testing

You can directly insert feedback in Supabase:

```sql
-- Insert test feedback
INSERT INTO suggestion_feedback (
    suggestion_id,
    patient_id,
    clinician_id,
    action,
    suggestion_text,
    suggestion_source,
    suggestion_confidence,
    clinical_relevance,
    agreement_rating,
    created_at
) VALUES (
    '<suggestion-uuid>',
    '<patient-uuid>',
    '<clinician-uuid>',
    'accept',
    'Test suggestion text',
    'ai_model',
    0.75,
    5,
    5,
    NOW() - INTERVAL '5 days'
);
```

---

## 📊 Testing Scenarios

### Scenario 1: Empty State
**Goal:** Test UI when no feedback exists
```bash
# Don't generate any feedback
# Visit analytics page
# Should show: 0 feedback, empty charts, helpful messages
```

### Scenario 2: Learning Trigger
**Goal:** Test self-adaptive learning
```bash
# Generate exactly 10 feedback items with 80% acceptance
python3 scripts/generate_test_feedback.py --count 10 --days 7
# Then manually update 8 to "accept" in database
# Should trigger learning event
```

### Scenario 3: Timeline Visualization
**Goal:** Test timeline chart
```bash
# Generate feedback spread over 30 days
python3 scripts/generate_test_feedback.py --count 50 --days 30
# Should show nice timeline with trends
```

### Scenario 4: Multiple Sources
**Goal:** Test feedback by source
```bash
# Generate feedback for different sources
# Should show breakdown: rules, ai_model, hybrid
```

---

## 🎓 For PhD Research

### What to Document

1. **Test Data Generation:**
   - How many feedback items generated
   - Time period covered
   - Distribution of actions

2. **Learning Events:**
   - When learning was triggered
   - What confidence adjustments occurred
   - How many feedback items triggered learning

3. **Analytics Screenshots:**
   - Before learning
   - After learning
   - Timeline charts
   - Learning events history

4. **Demonstration Script:**
   - Step-by-step walkthrough
   - Expected outcomes
   - How to interpret results

---

## 🚀 Quick Test Commands

```bash
# Minimal test (10 items, 7 days)
python3 scripts/generate_test_feedback.py --count 10 --days 7

# Realistic test (50 items, 30 days)
python3 scripts/generate_test_feedback.py --count 50 --days 30

# Large dataset (200 items, 90 days)
python3 scripts/generate_test_feedback.py --count 200 --days 90

# Test specific scenario
python3 scripts/generate_test_feedback.py --count 30 --days 14 --clinician-id <uuid>
```

---

## ✅ Verification Checklist

After generating test data, verify:

- [ ] Analytics page loads without errors
- [ ] Total feedback count is correct
- [ ] Acceptance rate is calculated correctly
- [ ] Timeline chart shows data points
- [ ] Learning events appear (if >10 feedback)
- [ ] Confidence adjustments are visible
- [ ] Export functionality works
- [ ] Different time periods (7/14/30/90 days) work

---

## 🎬 Demo Presentation Flow

1. **Introduction** (2 min)
   - Show empty analytics page
   - Explain what we're measuring

2. **Generate Test Data** (1 min)
   - Run script: `python3 scripts/generate_test_feedback.py --count 50`
   - Explain the realistic distribution

3. **Show Analytics** (3 min)
   - Overview stats
   - Timeline chart
   - Breakdown by source

4. **Demonstrate Learning** (3 min)
   - Show learning events
   - Explain confidence adjustments
   - Show how AI adapts

5. **Export for Research** (1 min)
   - Show export functionality
   - Explain how data can be analyzed

**Total: ~10 minutes**

---

## 📝 Notes for PhD Defense

- **Emphasize:** This is a research platform, not production
- **Explain:** Test data generation is a standard practice for system validation
- **Show:** The system works correctly with realistic data patterns
- **Demonstrate:** Self-adaptive learning actually occurs
- **Document:** All test data generation methods for reproducibility

---

## 🔧 Troubleshooting

### "No clinicians found"
```bash
# Create a clinician user first
python3 scripts/create_admin_user.py
# Or create via Supabase dashboard
```

### "No patients found"
```bash
# Generate test patients
python3 scripts/generate_patients.py --count 20
```

### "No suggestions found"
```bash
# The script will create sample suggestions automatically
# Or generate suggestions via the UI first
```

---

## 📚 Next Steps

1. Run the test data generation script
2. Verify analytics dashboard shows data
3. Test different scenarios
4. Document your testing approach
5. Prepare demo for professor/clinicians

**The system is ready for testing!** 🎉
