# Testing Protocol Summary

## Quick Reference for Clinician Testing

### Research Question
**How can self-adaptive EHR interfaces reduce clinician cognitive load while maintaining clinical decision-making quality?**

---

## Test Patient: Sarah Chen

**Patient ID:** (Run `python3 scripts/create_test_patient_sarah.py` to create)

**Profile:**
- 68-year-old female
- Mild Cognitive Impairment (MCI) with suspected Alzheimer's progression
- Complex case with multiple comorbidities and abnormal labs

---

## Testing Tasks (50 minutes total)

1. **Initial Patient Review** (5 min)
   - Find patient, review summary, check risk level

2. **Review Cognitive Assessment** (8 min)
   - Check MoCA scores, conversation transcripts, summaries

3. **Review Imaging & Labs** (10 min)
   - MRI brain scan, lab results (B12, Folate, TSH abnormalities)

4. **Medication Review** (7 min)
   - 5 medications, check for cognitive side effects

5. **Review Patient History** (5 min)
   - PMH, PSH, Family History, Social History

6. **Generate Clinical Decision** (10 min)
   - Review AI suggestions, create SOAP note, document findings

7. **Follow-up Planning** (5 min)
   - Update problems, plan referrals, schedule follow-up

---

## What to Measure

### Automated (System Collects):
- Navigation patterns
- Time spent in sections
- Clicks to complete tasks
- AI suggestion interactions
- Adaptation events

### Surveys (You Complete):
- NASA-TLX (after Tasks 2, 4, 6)
- System Usability Scale (end of session)
- Trust in Automation Scale
- Adaptation perception questions

### Expert Review:
- Clinical decision quality
- Documentation completeness
- Treatment appropriateness

---

## Study Design

**Session 1:** Static Interface (Baseline)
- Complete all 7 tasks
- No adaptations active
- Collect baseline metrics

**Session 2:** Adaptive Interface (1 week later)
- Same patient, same tasks
- MAPE-K adaptations active
- System learns from your behavior

**Comparison:** Adaptive vs. Static performance

---

## Expected Benefits

- **20-30% reduction in cognitive load**
- **15-25% faster task completion**
- **No reduction in decision quality**
- **Better user experience**

---

## Key Features to Test

1. **Adaptive Section Ordering**
   - System reorders sections based on your usage
   - Look for adaptation indicator

2. **AI Suggestions**
   - Review diagnostic suggestions
   - Check explanations
   - Accept/ignore as appropriate

3. **Contextual Prioritization**
   - Abnormal values highlighted
   - Relevant sections suggested
   - Critical information surfaced

4. **Conversation Analysis**
   - Voice-to-text transcripts
   - Key points extraction
   - Summary generation

---

## Success Criteria

✅ Cognitive load reduced by 20-30%  
✅ Task completion 15-25% faster  
✅ Decision quality maintained (≥85% accuracy)  
✅ Positive user satisfaction (SUS > 70)  
✅ Adaptations feel helpful, not intrusive  

---

## For More Details

See `USER_STORY_BRAIN_HEALTH_TESTING.md` for complete protocol.

