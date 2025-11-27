# Quick Learning Prompts for Specific Topics

Use these shorter prompts for focused learning on specific aspects of your project:

---

## 1. MAPE-K Architecture Deep Dive

```
I'm implementing MAPE-K (Monitor-Analyze-Plan-Execute-Knowledge) for a self-adaptive EHR system. 
Can you explain:

1. How the MAPE-K feedback loop works in practice with concrete examples?
2. What are the key design decisions when implementing each component (Monitor, Analyze, Plan, Execute, Knowledge)?
3. How does the Knowledge base improve over time and what should be stored there?
4. What are common pitfalls in MAPE-K implementation and how to avoid them?
5. How do you handle conflicting signals (e.g., user clicks feature A but ignores suggestions about A)?

Context: My system tracks dashboard interactions, analyzes usage patterns, generates JSON layout plans, and applies them to the frontend. I'm using FastAPI backend and Next.js frontend.
```

---

## 2. Dashboard Personalization & Learning

```
I'm building a dashboard that adapts based on doctor specialty and individual usage patterns. 
Help me understand:

1. How do you effectively learn user preferences from interaction data?
2. What's the optimal balance between specialty defaults and individual learning?
3. How do you handle the cold start problem (new users with no usage data)?
4. What thresholds should I use for promoting/hiding features (e.g., 10 uses/day = promote)?
5. How do you prevent over-adaptation (too personalized, loses general usability)?

Context: Doctors select specialty (cardiology, neurology, etc.), and dashboard learns from clicks. 
Features used frequently (e.g., ECG Review 17x/day) are promoted to top, rarely-used features are hidden.
```

---

## 3. Self-Adaptive Systems in Healthcare

```
I'm researching self-adaptive EHR systems for my PhD. Can you explain:

1. What are the unique challenges of self-adaptation in healthcare vs. other domains?
2. How do you ensure safety when the UI changes dynamically?
3. What are the ethical considerations of adaptive healthcare interfaces?
4. How do you measure adaptation effectiveness in healthcare contexts?
5. What are best practices for reducing cognitive load through adaptation?

Context: This is a research platform (not production), uses synthetic data, focuses on reducing 
clinician cognitive load through MAPE-K-based UI adaptation.
```

---

## 4. Usage Pattern Analysis & Algorithms

```
I need to analyze user behavior patterns for dashboard adaptation. Help me with:

1. What are efficient algorithms for identifying frequently-used features?
2. How do you detect workflow sequences (e.g., user always does A then B)?
3. What data structures are best for tracking usage patterns over time?
4. How do you handle time-of-day patterns (morning vs. afternoon workflows)?
5. What's the optimal time window for analysis (7 days, 30 days, 90 days)?

Context: I'm tracking dashboard clicks, analyzing feature frequencies, and identifying 
workflow patterns. Using Python/FastAPI backend, PostgreSQL database.
```

---

## 5. Research Methodology & Evaluation

```
I'm designing experiments to evaluate my self-adaptive EHR system. Help me with:

1. What are effective ways to measure adaptation effectiveness?
2. How do you design experiments to test self-adaptive systems?
3. What statistical methods are appropriate for analyzing adaptation impact?
4. How do you handle confounding variables in adaptation research?
5. What metrics indicate successful adaptation (time saved, clicks reduced, satisfaction)?

Context: Research questions focus on whether adaptive UI reduces task time, improves 
satisfaction, and learns effective adaptations. Expected impact: 75% reduction in clicks, 
40-60 minutes saved per day.
```

---

## 6. Technical Implementation Best Practices

```
I'm implementing a self-adaptive dashboard system. Help me with:

1. Best practices for implementing usage tracking (privacy, performance, scalability)?
2. How do you design efficient analysis algorithms for large usage datasets?
3. What are effective ways to store and query adaptation knowledge?
4. How do you test self-adaptive systems (unit tests, integration tests)?
5. How do you ensure analysis doesn't slow down the system?

Context: FastAPI backend, Next.js frontend, PostgreSQL database. Tracking dashboard 
interactions, analyzing patterns, generating JSON plans, applying to UI.
```

---

## 7. Comparison with Related Work

```
I'm researching self-adaptive EHR systems. Can you help me understand:

1. How does MAPE-K-based adaptation compare to other adaptive EHR systems?
2. What are the unique contributions of MAPE-K for UI adaptation?
3. How does this relate to recommender systems and personalization research?
4. What are the limitations compared to other adaptation approaches (rule-based, ML-based)?
5. What are promising extensions or future research directions?

Context: PhD research on self-adaptive AI-assisted EHR using MAPE-K architecture, 
focusing on specialty-based and usage-pattern-based dashboard adaptation.
```

---

## 8. Healthcare UI Design & Cognitive Load

```
I'm designing an adaptive EHR interface to reduce cognitive load. Help me understand:

1. What are best practices for reducing cognitive load in EHR systems?
2. How do you design interfaces that adapt without confusing users?
3. What are effective strategies for prioritizing information in healthcare contexts?
4. How do you balance information density with usability?
5. What are the design principles for adaptive healthcare interfaces?

Context: Dashboard adapts based on specialty and usage. Features are promoted/hidden, 
layouts change dynamically. Goal is to reduce clicks and time to find features.
```

---

## 9. Privacy, Ethics & Research Compliance

```
I'm building a research EHR platform with usage tracking. Help me with:

1. How do you ensure usage tracking doesn't violate privacy?
2. What data should be stored vs. aggregated for research?
3. How do you handle consent for adaptation research?
4. What are the ethical considerations of adaptive healthcare interfaces?
5. How do you ensure research compliance (GDPR, research ethics)?

Context: Research platform using synthetic data, tracking user interactions for 
adaptation research, storing patterns in knowledge base.
```

---

## 10. Performance & Scalability

```
I'm implementing a self-adaptive system that needs to scale. Help me with:

1. How do you ensure analysis doesn't slow down the system?
2. What are efficient data structures for tracking usage patterns?
3. How do you handle large numbers of users and features?
4. Should analysis run continuously or on-demand?
5. How do you optimize database queries for usage pattern analysis?

Context: FastAPI backend, PostgreSQL database, tracking dashboard interactions for 
potentially hundreds of users, analyzing patterns every time dashboard loads.
```

---

## How to Use These Prompts

1. **Copy the prompt** for the topic you want to learn about
2. **Paste into ChatGPT** (or your preferred AI assistant)
3. **Add your specific context** if needed (e.g., "I'm using PostgreSQL with 10,000+ actions per day")
4. **Follow up** with more specific questions based on the response

## Tips

- **Be specific**: Add details about your implementation if relevant
- **Ask for examples**: Request code examples, diagrams, or case studies
- **Challenge assumptions**: Ask about limitations and potential problems
- **Request comparisons**: Ask how your approach compares to alternatives
- **Get research insights**: Ask about implications for your PhD research

---

*Use these prompts to learn deeply about specific aspects of your research project.*

