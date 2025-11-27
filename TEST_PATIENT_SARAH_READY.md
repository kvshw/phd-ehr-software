# Test Patient "Sarah Chen" - Ready for Testing! ✅

## Patient Created Successfully

**Patient ID:** `6c0f319d-e260-4063-93c0-401f65b0e0b5`  
**Name:** Sarah Chen  
**Age:** 68  
**Diagnosis:** Mild Cognitive Impairment (MCI) with suspected progression to early-stage Alzheimer's Disease

---

## Patient Data Summary

✅ **7 Vital Records** - Trending upward (BP, HR increasing over 6 months)  
✅ **16 Lab Records** - Mix of normal and abnormal (B12, Folate, TSH abnormalities)  
✅ **3 Clinical Notes** - SOAP format with cognitive assessment details  
✅ **5 Problems** - MCI, Hypertension, Diabetes, B12 Deficiency, Hypothyroidism  
✅ **5 Medications** - Including Lorazepam (cognitive side effect)  
✅ **2 Allergies** - Penicillin, Sulfa drugs  
⚠️ **Conversations** - Tables not created yet (optional, see below)

---

## How to Test the Workflow

### 1. **Access the Patient**
- Log in as a clinician or admin
- Go to Dashboard
- Search for "Sarah Chen" or scroll through patient list
- Click on the patient to open detail page

### 2. **Follow the Testing Tasks** (from USER_STORY_BRAIN_HEALTH_TESTING.md)

#### **Task 1: Initial Patient Review** (5 min)
- Navigate to patient dashboard
- Find "Sarah Chen"
- Review summary and demographics
- Check primary diagnosis and risk level

#### **Task 2: Review Cognitive Assessment** (8 min)
- Go to "Clinical Notes" section
- Review most recent cognitive assessment notes
- Check conversation transcript (if tables created)
- Review conversation summary and key points

#### **Task 3: Review Imaging and Lab Results** (10 min)
- Go to "Imaging" section (if MRI uploaded)
- Go to "Labs" section
- Review recent lab results:
  - **B12: 180** (LOW - abnormal) ⚠️
  - **Folate: 2.8** (LOW - abnormal) ⚠️
  - **TSH: 4.8** (ELEVATED - abnormal) ⚠️
  - **Glucose: 118** (abnormal)
  - **HbA1c: 7.2%** (abnormal)
- Check lab trends over time

#### **Task 4: Medication Review** (7 min)
- Go to "Medications" section
- Review 5 medications
- **Note:** Lorazepam has cognitive side effects (check notes)
- Review medication interactions
- Check "Allergies" section

#### **Task 5: Review Patient History** (5 min)
- Go to "History" section
- Review:
  - Past Medical History (Hypertension, Diabetes, Osteoarthritis)
  - Past Surgical History (Cholecystectomy, Cataract surgery)
  - **Family History** (Mother: Alzheimer's Disease - important!)
  - Social History (Lives alone, widowed)

#### **Task 6: Generate Clinical Decision** (10 min)
- Go to "AI Suggestions" section
- Click "Generate Suggestions" button
- Review AI-generated diagnostic suggestions
- Read explanations
- Accept/ignore suggestions
- Go to "Clinical Notes" section
- Create a new SOAP note documenting findings
- Add/update problems if needed

#### **Task 7: Follow-up Planning** (5 min)
- Review "Problems" section
- Update problem statuses
- Check "Safety & Transparency" section
- Review adaptation explanations (if any occurred)
- Plan follow-up and referrals

---

## Key Findings to Look For

### **Abnormal Labs (Today's Values):**
- **B12: 180** (normal: 200-900) - **LOW** ⚠️
- **Folate: 2.8** (normal: >3.0) - **LOW** ⚠️
- **TSH: 4.8** (normal: 0.4-4.0) - **ELEVATED** ⚠️
- **Glucose: 118** (normal: 70-100) - **HIGH**
- **HbA1c: 7.2%** (normal: <5.7) - **HIGH**

### **Concerning Trends:**
- **Blood Pressure:** Trending upward (142/88 → 158/98)
- **Heart Rate:** Increasing (78 → 95 bpm)
- **B12:** Declining (350 → 280 → 180)

### **Clinical Concerns:**
- Progressive memory loss (MoCA: 26 → 22)
- Recent fall (safety concern)
- Lives alone (safety risk)
- Family history of Alzheimer's
- Medication with cognitive side effects (Lorazepam)

---

## Optional: Enable Conversation Features

To test voice-to-text and conversation analysis:

1. **Go to Supabase SQL Editor**
2. **Run the migration script:**
   ```sql
   -- Copy and paste contents of scripts/create_conversation_tables.sql
   ```
3. **Re-run the patient creation script** (it will add conversation data):
   ```bash
   python3 scripts/create_test_patient_sarah.py
   ```

Or manually create conversation data through the UI using the voice recorder.

---

## Testing MAPE-K Adaptations

As you use the system, watch for:

1. **Section Reordering:**
   - System learns which sections you visit most
   - May reorder navigation based on your workflow
   - Look for adaptation indicator

2. **Suggestion Density:**
   - If you accept many AI suggestions, density may increase
   - System learns your preferences

3. **Contextual Prioritization:**
   - Abnormal labs should be highlighted
   - Relevant sections may be suggested
   - Critical information surfaced automatically

---

## Expected AI Suggestions

When you click "Generate Suggestions" in the AI Suggestions panel, you should see:

1. **B12/Folate Deficiency** - Based on low lab values
2. **Hypothyroidism** - Based on elevated TSH
3. **Cognitive Side Effects** - Based on Lorazepam medication
4. **Safety Concerns** - Based on falls and living alone
5. **Family History Risk** - Based on mother's Alzheimer's

Each suggestion should include:
- Explanation (why it was triggered)
- Confidence score
- Source attribution
- "Experimental" label

---

## Data Collection

While testing, the system automatically collects:

- ✅ Navigation patterns (sections visited, order, time)
- ✅ AI suggestion interactions (accept/ignore/not relevant)
- ✅ Adaptation events
- ✅ User actions and timestamps

**View collected data:**
- Go to Researcher Dashboard (if logged in as researcher)
- Check metrics and logs
- Export data for analysis

---

## Next Steps

1. **Test the workflow** following the 7 tasks above
2. **Observe MAPE-K adaptations** as you use the system
3. **Complete NASA-TLX surveys** after Tasks 2, 4, 6 (if doing formal study)
4. **Document your experience** - what worked, what didn't
5. **Check adaptation explanations** - do they make sense?

---

## Patient is Ready! 🎯

The test patient "Sarah Chen" is fully loaded with realistic brain health data. You can now:

- Test all system features
- Evaluate MAPE-K adaptations
- Measure cognitive load
- Assess decision quality
- Collect research data

**Start testing by logging in and navigating to the patient!**

