# User Story: Brain Health Patient Management Testing Protocol

## Research Question
**How can self-adaptive EHR interfaces, using the MAPE-K (Monitor, Analyze, Plan, Execute, Knowledge) architecture, reduce clinician cognitive load while maintaining clinical decision-making quality?**

---

## Overview

This user story provides a realistic clinical scenario for testing the self-adaptive EHR system in a brain health context. Clinicians will manage a complex patient case while the system adapts to their workflow patterns, reducing cognitive load through intelligent interface adjustments.

---

## Clinical Scenario: Complex Brain Health Case

### Patient Profile: "Sarah Chen"

**Background:**
- **Age:** 68 years old
- **Sex:** Female
- **Primary Diagnosis:** Mild Cognitive Impairment (MCI) with suspected progression to early-stage Alzheimer's Disease
- **Presenting Concerns:**
  - Progressive memory loss over 18 months
  - Difficulty with daily tasks (cooking, managing medications)
  - Family reports personality changes
  - Recent fall (no injury, but concerning)
  - Sleep disturbances

**Clinical Complexity:**
- Multiple comorbidities (hypertension, type 2 diabetes)
- Polypharmacy (5 medications)
- Family history of dementia
- Recent cognitive assessment (MoCA score: 22/30, down from 26/30 six months ago)
- MRI shows mild hippocampal atrophy
- Multiple lab abnormalities requiring review

---

## User Story: Complete Patient Assessment

### **As a clinician**, 
I need to **comprehensively assess and manage a complex brain health patient** so that I can:
- Make an accurate diagnosis
- Develop an appropriate treatment plan
- Monitor disease progression
- Coordinate care with specialists
- Document findings efficiently

### **The system should help me by:**
- Adapting the interface to prioritize information I need most
- Reducing the number of clicks to find critical data
- Highlighting abnormal values and concerning trends
- Providing AI-assisted insights (with explanations)
- Learning from my navigation patterns to improve efficiency

---

## Testing Tasks (Standardized Clinical Workflow)

### **Task 1: Initial Patient Review** (5 minutes)
**Objective:** Assess overall patient status and identify priority concerns

**Actions:**
1. Navigate to patient dashboard
2. Identify patient "Sarah Chen" from the list
3. Review patient summary and demographics
4. Check primary diagnosis and risk level
5. Identify any urgent flags or alerts

**Expected System Adaptation:**
- System learns you start with summary/demographics
- May prioritize these sections in future visits
- Highlights abnormal vitals or risk indicators

**Metrics to Collect:**
- Time to find patient
- Number of clicks to access key information
- Sections visited and order
- Time spent in each section

---

### **Task 2: Review Cognitive Assessment Results** (8 minutes)
**Objective:** Evaluate cognitive function and identify decline patterns

**Actions:**
1. Navigate to "Clinical Notes" section
2. Review most recent cognitive assessment (MoCA: 22/30)
3. Compare with previous assessment (6 months ago: 26/30)
4. Review conversation transcript from last visit
5. Check conversation summary and key points
6. Identify concerning patterns or changes

**Expected System Adaptation:**
- If you frequently check conversation summaries, system may prioritize this section
- System learns you compare current vs. previous assessments
- May suggest related sections (e.g., medications that might affect cognition)

**Metrics to Collect:**
- Time to locate cognitive assessment
- Number of back-and-forth navigations
- Whether AI suggestions were viewed/used
- Cognitive load indicators (mouse movements, dwell time)

---

### **Task 3: Review Imaging and Lab Results** (10 minutes)
**Objective:** Assess structural brain changes and rule out reversible causes

**Actions:**
1. Navigate to "Imaging" section
2. Review MRI brain scan
3. Use zoom/pan to examine hippocampal region
4. Review AI image analysis suggestions (if available)
5. Navigate to "Labs" section
6. Review recent lab results:
   - B12, Folate (rule out deficiency)
   - TSH (rule out hypothyroidism)
   - Glucose, HbA1c (diabetes control)
   - Creatinine (kidney function)
7. Identify any abnormal values requiring attention
8. Check lab trends over time

**Expected System Adaptation:**
- System learns you review imaging before labs
- May prioritize imaging section if abnormalities detected
- Suggests relevant labs based on imaging findings
- Highlights abnormal values automatically

**Metrics to Collect:**
- Time to review imaging
- Number of interactions with image viewer
- Time to identify abnormal labs
- Whether AI suggestions were helpful
- Navigation efficiency (optimal vs. actual path)

---

### **Task 4: Medication Review and Drug Interactions** (7 minutes)
**Objective:** Assess medication appropriateness and potential cognitive side effects

**Actions:**
1. Navigate to "Medications" section
2. Review current medications (5 total)
3. Check for medications that might affect cognition:
   - Anticholinergics
   - Benzodiazepines
   - Antihistamines
4. Review medication interactions
5. Check adherence patterns
6. Navigate to "Allergies" section
7. Verify no new allergies or reactions

**Expected System Adaptation:**
- System learns you check medications after reviewing cognitive status
- May highlight medications with cognitive side effects
- Suggests reviewing allergies when checking medications
- Prioritizes medication section if interactions detected

**Metrics to Collect:**
- Time to review all medications
- Whether drug interaction warnings were noticed
- Number of sections visited
- Cognitive load (measured via eye tracking or self-report)

---

### **Task 5: Review Patient History and Social Context** (5 minutes)
**Objective:** Understand patient's background and social support

**Actions:**
1. Navigate to "History" section
2. Review:
   - Past Medical History (PMH)
   - Past Surgical History (PSH)
   - Family History (especially dementia)
   - Social History (living situation, support systems)
3. Check if family history explains current presentation
4. Assess social support availability

**Expected System Adaptation:**
- System learns you review history after clinical data
- May suggest relevant history sections based on current findings
- Highlights family history if relevant to diagnosis

**Metrics to Collect:**
- Time to review history
- Information found vs. information needed
- Navigation patterns

---

### **Task 6: Generate Clinical Decision** (10 minutes)
**Objective:** Synthesize information and make diagnostic/treatment decisions

**Actions:**
1. Navigate to "AI Suggestions" section
2. Review AI-generated diagnostic suggestions
3. Read explanations for each suggestion
4. Accept, ignore, or mark suggestions as "not relevant"
5. Navigate to "Clinical Notes" section
6. Create a new SOAP note documenting:
   - **Subjective:** Patient and family concerns
   - **Objective:** Findings from assessment, labs, imaging
   - **Assessment:** Diagnosis and clinical reasoning
   - **Plan:** Treatment recommendations, follow-up, referrals
7. Add new problems to problem list if needed
8. Document medication changes if any

**Expected System Adaptation:**
- System learns which AI suggestions you find useful
- Adapts suggestion density based on your acceptance rate
- Prioritizes sections you use for documentation
- May reorder sections to match your workflow

**Metrics to Collect:**
- Time to make decision
- Number of AI suggestions reviewed
- Acceptance rate of suggestions
- Quality of clinical decision (expert review)
- Documentation completeness
- Cognitive load (NASA-TLX survey)

---

### **Task 7: Follow-up Planning** (5 minutes)
**Objective:** Plan next steps and coordinate care

**Actions:**
1. Review "Problems" section
2. Update problem statuses (e.g., mark "MCI" as active, progressing)
3. Add new problems if identified
4. Check "Safety & Transparency" section
5. Review adaptation explanations (if any occurred)
6. Plan follow-up appointment
7. Consider referrals (neurology, neuropsychology)

**Expected System Adaptation:**
- System learns your follow-up workflow
- May suggest relevant specialists based on findings
- Adapts problem list prioritization

**Metrics to Collect:**
- Time to complete follow-up planning
- Whether adaptation explanations were understood
- User satisfaction with adaptations

---

## Total Session Time: ~50 minutes

---

## Data Collection Points

### **Quantitative Metrics (Automated)**

1. **Navigation Patterns:**
   - Sections visited and order
   - Time spent in each section
   - Number of clicks to complete tasks
   - Backtracking frequency
   - Optimal vs. actual navigation path

2. **AI Interaction:**
   - Suggestions viewed
   - Acceptance/ignore/not relevant rates
   - Time to review suggestions
   - Explanation views

3. **System Adaptations:**
   - Adaptation events triggered
   - Section reordering occurrences
   - Suggestion density changes
   - User acceptance of adaptations

4. **Efficiency Metrics:**
   - Task completion time
   - Information access speed
   - Documentation time
   - Overall session duration

5. **Objective Cognitive Load Indicators:**
   - Mouse movement entropy
   - Dwell time on sections
   - Search time
   - Backtracking frequency

### **Qualitative Metrics (Surveys & Interviews)**

1. **Cognitive Load Assessment:**
   - NASA-TLX (6 dimensions) - after each major task
   - Workload Profile (8 dimensions) - end of session
   - Subjective mental effort rating (1-10)

2. **User Experience:**
   - System Usability Scale (SUS) - end of session
   - Trust in Automation Scale - after AI suggestions
   - Perceived Usefulness (TAM model)

3. **Adaptation Perception:**
   - Did you notice adaptations? (Yes/No)
   - Were adaptations helpful? (1-5 scale)
   - Did adaptations feel intrusive? (1-5 scale)
   - Understanding of adaptation explanations (1-5 scale)

4. **Clinical Decision Quality:**
   - Confidence in diagnosis (1-10)
   - Completeness of assessment (expert review)
   - Appropriateness of treatment plan (expert review)

5. **Post-Session Interview:**
   - What worked well?
   - What was frustrating?
   - When did adaptations help/hinder?
   - Would you use this system in practice?

---

## Research Protocol

### **Study Design: Within-Subjects Crossover**

**Phase 1: Baseline (Static Interface)**
- Clinician completes all 7 tasks using **non-adaptive** interface
- System collects baseline metrics
- No MAPE-K adaptations active

**Phase 2: Adaptive Interface (MAPE-K Enabled)**
- Same clinician completes same tasks using **adaptive** interface
- System learns from behavior and adapts
- MAPE-K adaptations active with explanations

**Comparison:**
- Cognitive load: Adaptive vs. Static
- Task completion time: Adaptive vs. Static
- Decision quality: Adaptive vs. Static
- User satisfaction: Adaptive vs. Static

---

## Success Criteria

### **Primary Outcome:**
- **20-30% reduction in cognitive load** (NASA-TLX score) with adaptive interface
- **No reduction in decision quality** (non-inferiority test)

### **Secondary Outcomes:**
- **15-25% reduction in task completion time**
- **30-40% increase in AI suggestion acceptance rate**
- **Positive user satisfaction** (SUS score > 70)

### **Qualitative Insights:**
- Clinicians understand and trust adaptations
- Adaptations feel helpful, not intrusive
- System learns effectively from user behavior

---

## Pre-Testing Setup

### **1. System Preparation:**
- Load patient "Sarah Chen" with complete data:
  - Demographics
  - Cognitive assessments (current + historical)
  - Conversation transcripts and summaries
  - MRI brain imaging
  - Lab results (normal + abnormal)
  - Medications (5 medications, some with cognitive side effects)
  - Allergies
  - Medical/surgical/family/social history
  - Clinical notes (SOAP format)
  - Problem list

### **2. AI Model Preparation:**
- Vital Risk Model: Configured for brain health metrics
- Image Analysis Model: Trained on brain MRI patterns
- Diagnosis Helper: Configured with brain health rules
- Conversation Analysis: Ready to analyze doctor-patient conversations

### **3. MAPE-K Configuration:**
- Monitor: Active, collecting all user actions
- Analyze: Rules configured for brain health workflow
- Plan: Adaptation strategies enabled
- Execute: Frontend adaptation engine active
- Knowledge: Brain health-specific adaptation rules loaded

### **4. Clinician Briefing:**
- Explain the research purpose
- Demonstrate system features (one-time)
- Explain MAPE-K adaptations (with examples)
- Emphasize: "Use the system naturally, as you would in practice"
- No training on optimal workflow (we want natural behavior)

---

## Testing Session Flow

### **Session 1: Static Interface (Baseline)**
1. **Pre-Session:**
   - Informed consent
   - Demographics questionnaire
   - Brief system overview (no adaptation training)

2. **Task Execution:**
   - Complete all 7 tasks
   - NASA-TLX after Tasks 2, 4, 6
   - Think-aloud protocol (optional, subset of participants)

3. **Post-Session:**
   - SUS questionnaire
   - Workload Profile
   - Brief interview

### **Session 2: Adaptive Interface (1 week later)**
1. **Pre-Session:**
   - Reminder of system features
   - Explain adaptations will occur (with examples)
   - Same patient, same tasks

2. **Task Execution:**
   - Complete all 7 tasks
   - System adapts in real-time
   - NASA-TLX after Tasks 2, 4, 6
   - Think-aloud protocol

3. **Post-Session:**
   - SUS questionnaire
   - Workload Profile
   - Trust in Automation Scale
   - Adaptation perception survey
   - Detailed interview

---

## Expected Adaptations (Examples)

### **Example 1: Section Reordering**
**Scenario:** Clinician frequently visits "Conversation" section after "Clinical Notes"

**Adaptation:**
- System moves "Conversation" section higher in navigation
- Shows adaptation indicator: "Interface adapted based on your workflow"

**Expected Benefit:**
- Fewer clicks to access frequently used information
- Reduced cognitive load from searching

### **Example 2: Suggestion Density**
**Scenario:** Clinician accepts 80% of AI suggestions, finds them helpful

**Adaptation:**
- System increases suggestion density from "medium" to "high"
- Shows more AI insights proactively

**Expected Benefit:**
- More relevant information surfaced automatically
- Less need to manually search for insights

### **Example 3: Contextual Prioritization**
**Scenario:** Abnormal lab values detected (B12 low, TSH elevated)

**Adaptation:**
- System prioritizes "Labs" section
- Highlights abnormal values
- Suggests reviewing "Medications" (some meds affect B12/TSH)

**Expected Benefit:**
- Critical information surfaced immediately
- Reduced risk of missing important findings

---

## Data Analysis Plan

### **Quantitative Analysis:**
1. **Mixed-Effects Models:**
   - Cognitive load ~ Condition × Task + (1|Participant) + (1|Task)
   - Task time ~ Condition × Experience + (1|Participant)
   - Suggestion acceptance ~ Condition × Suggestion type

2. **Learning Curves:**
   - Performance improvement over session
   - Adaptation acceptance over time

3. **Path Analysis:**
   - Adaptation → Cognitive Load → Decision Quality
   - Test mediation effects

### **Qualitative Analysis:**
1. **Thematic Coding:**
   - Interview transcripts
   - Think-aloud protocols
   - Open-ended survey responses

2. **Key Themes:**
   - Trust in adaptations
   - Control vs. automation
   - Transparency and explanations
   - Clinical workflow integration

---

## Deliverables

### **For Research Paper:**
1. Quantitative results (cognitive load, efficiency, decision quality)
2. Qualitative insights (themes, user perceptions)
3. Adaptation effectiveness analysis
4. Design guidelines for adaptive EHRs

### **For System Improvement:**
1. User feedback on adaptations
2. Identified pain points
3. Suggested enhancements
4. Workflow optimization recommendations

---

## Ethical Considerations

1. **Informed Consent:**
   - Explain research purpose
   - Explain data collection
   - Explain adaptations
   - Right to withdraw

2. **Data Privacy:**
   - All data synthetic (no PHI)
   - User actions anonymized
   - No real patient information

3. **Safety:**
   - All AI suggestions labeled "Experimental"
   - No autonomous clinical actions
   - Clinician maintains full control

---

## Timeline

- **Preparation:** 1 week (patient data, system setup)
- **Pilot Testing:** 1 week (3-5 clinicians)
- **Data Collection:** 4-6 weeks (20-30 clinicians)
- **Analysis:** 2-3 weeks
- **Writing:** 2-3 weeks

**Total: 10-13 weeks**

---

## Success Metrics Summary

| Metric | Baseline (Static) | Target (Adaptive) | Measurement |
|--------|-------------------|-------------------|-------------|
| **Cognitive Load (NASA-TLX)** | 60-70 | 40-50 (30% reduction) | Subjective + Objective |
| **Task Completion Time** | 50 min | 40 min (20% reduction) | Automated |
| **Decision Quality** | 85% accuracy | ≥85% (non-inferior) | Expert review |
| **Suggestion Acceptance** | 60% | 80% (33% increase) | Automated |
| **User Satisfaction (SUS)** | 65 | 75+ | Survey |
| **Trust in Automation** | 3.5/5 | 4.0/5 | Survey |

---

## Next Steps

1. **Create Patient Data:**
   - Generate "Sarah Chen" with all required data
   - Ensure realistic complexity
   - Include both normal and abnormal findings

2. **Configure MAPE-K Rules:**
   - Brain health-specific adaptation rules
   - Context-aware prioritization
   - Suggestion density thresholds

3. **Prepare Testing Materials:**
   - Informed consent forms
   - Task instructions
   - Survey questionnaires
   - Interview guides

4. **Recruit Participants:**
   - 20-30 clinicians (neurologists, geriatricians, primary care)
   - Mix of experience levels
   - IRB approval

5. **Run Pilot Study:**
   - Test protocol with 3-5 clinicians
   - Refine tasks and materials
   - Adjust system based on feedback

---

**This user story provides a comprehensive, realistic testing scenario that directly addresses your research question while ensuring the system is evaluated in a meaningful clinical context.**

