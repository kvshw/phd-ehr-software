# Paper 1: Improved Methodology

## Current vs. Improved Approach

### ❌ Current Approach (Good but Limited)
- Simple A/B comparison: Adaptive vs. Static
- Single session study
- Subjective cognitive load only (NASA-TLX)
- Within-subjects design only

### ✅ Improved Approach (Publication-Ready)

---

## Enhanced Research Design

### Multi-Arm Study (4 Conditions)

Instead of just 2 conditions, use **4 conditions** to provide richer insights:

1. **Baseline (Static Interface)**
   - No adaptation
   - Standard EHR layout
   - Control condition

2. **Rule-Based Adaptation**
   - Simple if-then rules (e.g., "if vitals abnormal, show vitals first")
   - No learning or personalization
   - Deterministic adaptation

3. **MAPE-K with Explanations** (Your Main Contribution)
   - Full MAPE-K adaptation engine
   - Personalized learning from user behavior
   - Adaptation explanations shown to users

4. **MAPE-K without Explanations**
   - Same adaptation engine
   - No explanations shown
   - Tests importance of transparency

**Why this is better:**
- Shows your MAPE-K contribution vs. simpler approaches
- Isolates the effect of explanations
- Provides more nuanced understanding
- Stronger comparison than just "adaptive vs. static"

---

## Mixed-Methods Design

### Phase 1: Quantitative Study (8 weeks)

**Participants:** 40-50 clinicians
- 20 residents (early-career)
- 20 attending physicians (experienced)
- 10 specialists (neurology/cardiology)

**Design:** Between-subjects + within-subjects hybrid
- Each participant assigned to ONE adaptation condition (between-subjects)
- But completes MULTIPLE tasks within their condition (within-subjects)
- Reduces learning effects from switching conditions

**Tasks:** Standardized clinical scenarios (6 per participant)
1. **Routine Review**: "Review patient with stable vitals"
2. **Urgent Assessment**: "Identify patient with deteriorating condition"
3. **Diagnostic Workup**: "Review labs and imaging for diagnosis"
4. **Complex Case**: "Patient with multiple abnormalities"
5. **Follow-up**: "Check response to treatment"
6. **Documentation**: "Complete clinical note"

**Why standardized tasks?**
- Consistent difficulty across conditions
- Allows fair comparison
- Realistic clinical workflows

---

### Phase 2: Longitudinal Study (4 weeks)

**Purpose:** Measure adaptation effectiveness over time

**Participants:** 20 clinicians (subset from Phase 1)
- 10 in MAPE-K condition
- 10 in baseline condition

**Protocol:**
- Use system daily for 4 weeks
- System learns from their behavior
- Weekly surveys + final interview

**Metrics:**
- Week 1: Initial performance (learning curve)
- Week 2-3: Adaptation refinement
- Week 4: Plateau performance
- Track: Adaptation acceptance, satisfaction, efficiency gains

**Why longitudinal?**
- Shows adaptation improves over time (personalization works)
- Demonstrates long-term usability
- Captures initial resistance → acceptance trajectory

---

## Enhanced Metrics (Multi-Dimensional)

### 1. Cognitive Load (Subjective + Objective)

#### Subjective Measures
- **NASA-TLX** (standard, 6 dimensions)
- **Workload Profile** (8 dimensions, more sensitive)
- **Post-task satisfaction** (5-point Likert)

#### Objective Measures (NEW - More Rigorous)
- **Mouse movement entropy** (higher = more cognitive load)
- **Dwell time on sections** (longer = harder to process)
- **Backtracking frequency** (more = poor information architecture)
- **Search time** (time to find critical information)
- **Pupillometry** (optional, if you have eye-tracking hardware)

**Why objective measures?**
- Less biased than self-report
- Continuous monitoring (not just post-task)
- Publishable in top-tier venues (CHI loves objective measures)

---

### 2. Decision Quality (Clinical Accuracy)

#### Primary Outcomes
- **Diagnostic accuracy** (correct diagnosis rate)
- **Treatment appropriateness** (expert review)
- **Critical information missed** (safety metric)
- **Time to critical decision** (efficiency)

#### How to Measure
- Have 2-3 expert clinicians (gold standard) review each case
- Score participant decisions against gold standard
- Use Cohen's kappa for inter-rater reliability

**Why decision quality?**
- Shows adaptation doesn't compromise clinical care
- Addresses potential concern: "Does adaptation distract?"
- Critical for medical informatics journals

---

### 3. Efficiency Metrics

- **Task completion time**
- **Clicks to complete task**
- **Navigation path efficiency** (optimal vs. actual path)
- **Information access speed** (time to reach critical data)

---

### 4. User Experience

- **System Usability Scale (SUS)** (industry standard)
- **User Engagement Scale (UES)** (for adaptive systems)
- **Trust in Automation Scale** (for AI/adaptation)
- **Perceived Usefulness** (TAM model)

---

## Advanced Statistical Analysis

### Instead of Simple t-tests...

#### 1. Mixed-Effects Models
```r
# Example model
lmer(cognitive_load ~ condition * experience_level + (1|participant) + (1|task))
```
- Accounts for individual differences
- Handles repeated measures
- Controls for task difficulty

#### 2. Learning Curves Analysis
- Model performance improvement over time
- Compare learning rates across conditions
- Show MAPE-K accelerates learning

#### 3. Path Analysis / SEM
- Model relationships: Adaptation → Cognitive Load → Decision Quality
- Test mediation effects
- Show causal pathways

#### 4. Interaction Effects
- Condition × Experience level
- Condition × Task complexity
- Shows adaptation benefits vary by user/task

**Why advanced stats?**
- Required for top-tier venues
- Handles complexity of your design
- Provides richer insights

---

## Qualitative Component (Critical for CHI)

### Semi-Structured Interviews (After Phase 1)

**Questions:**
1. "How did the interface adaptation affect your workflow?"
2. "When did you notice adaptations? How did they feel?"
3. "Did adaptations help or hinder your decision-making?"
4. "How much control do you want over adaptations?"
5. "What would improve the adaptation system?"

**Analysis:**
- Thematic coding (2 independent coders)
- Use NVivo or Atlas.ti
- Identify themes: Trust, Control, Transparency, Efficiency

### Think-Aloud Protocol (Subset of Participants)

**During tasks:**
- Participants verbalize their thoughts
- Recorded and transcribed
- Reveals cognitive processes

**Insights:**
- Where users get confused
- When adaptations help/hinder
- Unexpected usage patterns

**Why qualitative?**
- CHI requires mixed-methods
- Provides rich context for quantitative findings
- Reveals design improvements

---

## Comparison Baselines (Stronger Validation)

### Don't just compare to static interface...

#### 1. Commercial EHR (Epic/Cerner)
- Show screenshots/videos of typical workflow
- Highlight lack of adaptation
- Position your work as innovation

#### 2. Other Adaptive Systems
- Literature review: Adaptive UI systems in other domains
- Compare MAPE-K to simpler adaptation strategies
- Show your approach is better

#### 3. User-Customizable Interface
- Let users manually reorder sections
- Compare to automatic MAPE-K adaptation
- Show automation is better than manual customization

---

## Adaptation Transparency Study (Within Paper 1)

### Sub-Study: Explanation Impact

**Question:** Do adaptation explanations increase trust and acceptance?

**Design:** 2×2 factorial within MAPE-K condition
- Adaptation: Yes/No
- Explanation: Yes/No

**Metrics:**
- Trust in system
- Acceptance of adaptations
- Understanding of adaptations

**Findings:**
- Hypothesis: Explanations increase trust by 30-40%
- Shows transparency matters

---

## Enhanced MAPE-K Knowledge Base (Make it Smarter)

### Instead of simple rules, use:

#### 1. Contextual Adaptation Rules
```python
# Current: Simple frequency-based
if vitals_visits > 10:
    prioritize('vitals')

# Better: Context-aware
if (vitals_visits > 10 AND patient_risk == 'high'):
    prioritize('vitals')
elif (vitals_abnormal AND not_yet_viewed):
    prioritize('vitals')
    show_alert('Critical vitals pending review')
```

#### 2. User Modeling
- Track expertise level (resident vs. attending)
- Adapt differently for different users
- Personalized adaptation

#### 3. Task Modeling
- Detect current task (routine review vs. urgent)
- Adapt based on task type
- Show adaptation is context-aware

---

## Safety & Validity Checks

### 1. Adaptation Validity
- Expert review of adaptation decisions
- Are adaptations clinically appropriate?
- No maladaptation examples

### 2. Non-Inferiority Analysis
- Show MAPE-K doesn't reduce decision quality
- Statistical non-inferiority test
- Critical for medical applications

### 3. Cognitive Load Threshold
- Ensure no condition exceeds acceptable workload
- NASA-TLX score < 70 (threshold)
- Safety first

---

## Publication Strategy

### Target Venue: CHI (Top-Tier HCI)

**Why CHI?**
- Highest impact HCI venue
- Values novel systems + rigorous evaluation
- Mixed-methods appreciated
- Adaptive UIs are hot topic

**Submission Requirements:**
- ✅ Novel contribution (MAPE-K in EHR)
- ✅ Rigorous evaluation (multi-phase, mixed-methods)
- ✅ Objective + subjective measures
- ✅ Qualitative insights
- ✅ Statistical rigor
- ✅ Generalizable findings

### Alternative Venues (If CHI Rejects)

1. **AMIA Annual Symposium** (medical informatics)
2. **UIST** (User Interface Software and Technology)
3. **Journal of Medical Internet Research (JMIR)** (journal, slower)

---

## Sample Size & Power Analysis

### Quantitative Study (Phase 1)

**Effect size:** Medium (Cohen's d = 0.5)
- Expected 20% reduction in cognitive load
- Moderate effect based on literature

**Power:** 0.80 (standard)
**Alpha:** 0.05 (standard)

**Required N:** 
- 4 conditions × 10 participants = **40 participants minimum**
- Recommend: **50 participants** (account for dropouts)

### Longitudinal Study (Phase 2)

**Effect size:** Large (d = 0.8)
- Expected 30% improvement over 4 weeks
- Larger effect due to personalization

**Power:** 0.80
**Alpha:** 0.05

**Required N:**
- 2 conditions × 10 participants = **20 participants minimum**

---

## Timeline (Realistic)

### Phase 1: Preparation (2 months)
- IRB approval
- Participant recruitment
- Task development
- Pilot testing (5 participants)

### Phase 2: Data Collection (3 months)
- **Month 1:** Quantitative study (40-50 participants)
- **Month 2:** Longitudinal study setup (20 participants)
- **Month 3:** Longitudinal monitoring + interviews

### Phase 3: Analysis (2 months)
- Quantitative analysis (mixed-effects models)
- Qualitative coding (thematic analysis)
- Integration of findings

### Phase 4: Writing (2 months)
- Draft manuscript
- Internal review
- Revisions

### Phase 5: Submission & Revision (3 months)
- Submit to CHI
- Await reviews
- Revisions (if needed)

**Total Timeline: 12 months** (more realistic than 7-8 months)

---

## Expected Contributions (For Abstract)

### Primary Contributions

1. **Architectural Innovation**
   - First MAPE-K implementation in clinical EHR context
   - Demonstrates feasibility and effectiveness

2. **Empirical Evidence**
   - Rigorous multi-phase evaluation
   - Quantitative + qualitative findings
   - Longitudinal validation

3. **Design Guidelines**
   - When/how to adapt EHR interfaces
   - Importance of explanations
   - User control vs. automation balance

4. **Open-Source Platform**
   - Research community can replicate
   - Extension for other domains

### Secondary Contributions

5. **Methodological Framework**
   - How to evaluate adaptive medical systems
   - Safety considerations
   - Ethical guidelines

---

## Key Improvements Summary

| Aspect | Current Approach | Improved Approach |
|--------|-----------------|-------------------|
| **Design** | 2 conditions | 4 conditions (more nuanced) |
| **Duration** | Single session | Multi-phase (quantitative + longitudinal) |
| **Metrics** | Subjective only | Subjective + objective |
| **Analysis** | t-tests | Mixed-effects models, SEM |
| **Methods** | Quantitative only | Mixed-methods (qual + quant) |
| **Sample Size** | 30-50 | 50 (quantitative) + 20 (longitudinal) |
| **Validity** | Self-report | Decision quality + efficiency |
| **Insights** | Surface-level | Deep understanding via interviews |
| **Comparison** | Static only | Rule-based + explanation variants |
| **Timeline** | 7-8 months | 12 months (more realistic) |

---

## Why This Approach is Better

### 1. Stronger Evidence
- Multi-phase design provides convergent validity
- Objective measures reduce bias
- Longitudinal component shows sustained benefits

### 2. Richer Insights
- Qualitative data explains quantitative findings
- Understanding of when/why adaptation works
- Design implications for future systems

### 3. Higher Impact
- Top-tier venue (CHI) requirements met
- Novel + rigorous = high acceptance rate
- Citable methodology for others

### 4. Defensible in PhD
- Rigorous evaluation demonstrates research skills
- Multiple methods show breadth
- Strong contribution to field

### 5. Generalizable
- Findings apply beyond your specific system
- Design guidelines for adaptive EHRs
- Framework for future research

---

## Next Steps

### 1. Refine Research Questions
- Primary: Cognitive load reduction
- Secondary: Decision quality, efficiency, trust
- Exploratory: When does adaptation help most?

### 2. Develop Task Scenarios
- 6 standardized clinical tasks
- Validated by expert clinicians
- Consistent difficulty

### 3. IRB Protocol
- Informed consent
- Data privacy (synthetic data only)
- Participant safety

### 4. Pilot Study
- 5 participants
- Test tasks, measures, procedures
- Refine based on feedback

### 5. Full Study Launch
- Recruit participants
- Collect data systematically
- Monitor quality

---

## Bottom Line

**The improved approach is:**
- ✅ More rigorous (multi-phase, mixed-methods)
- ✅ More insightful (qualitative + quantitative)
- ✅ More publishable (meets CHI standards)
- ✅ More defensible (in PhD context)
- ✅ More generalizable (design guidelines)

**Trade-off:** Takes longer (12 months vs. 7-8 months), but **much stronger publication** and **higher impact**.

If you want to publish in **CHI** (top-tier), use this approach. If you want faster publication in a **medical informatics venue** (AMIA), the simpler approach might work.

**Recommendation:** Go with the improved approach. It's worth the extra time for a stronger PhD contribution.

