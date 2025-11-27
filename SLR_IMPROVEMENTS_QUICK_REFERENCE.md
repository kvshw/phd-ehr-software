# SLR-Based Improvements - Quick Reference

## 🎯 Overview

This document provides a quick reference for implementing SLR-based improvements to the self-adaptive EHR platform.

---

## 📊 Implementation Phases at a Glance

| Phase | Focus | Duration | Key Deliverable |
|-------|-------|----------|-----------------|
| **Phase 1** | Bandit-Based Planning | 2 weeks | Intelligent feature promotion/demotion |
| **Phase 2** | Transfer Learning | 2 weeks | Cold-start handling, specialty models |
| **Phase 3** | Federated Learning | 3 weeks | Privacy-preserving multi-site updates |
| **Phase 4** | Runtime Assurance | 2 weeks | Ethics, safety, transparency layer |
| **Phase 5** | Self-Learning Ensembles | 2 weeks | Robust predictions |
| **Phase 6** | Enhanced Monitor | 1 week | Multi-window analysis |
| **Phase 7** | Privacy & Security | 2 weeks | Privacy-by-design, threat detection |
| **Phase 8** | Research Infrastructure | 2 weeks | Metrics, A/B testing |

**Total: 16 weeks (4 months)**

---

## 🔑 Key Techniques from SLR

### 1. Federated Learning (FL)
**What:** Train models across distributed sites without sharing raw data  
**Where:** Vital risk prediction, diagnosis helper, adaptation policies  
**Why:** Privacy-preserving, prepares for multi-site studies  
**Files:** `federated_learning_service.py`, `fl_client.py`, `fl_coordinator.py`

### 2. Transfer Learning
**What:** Fine-tune pre-trained models for specific specialties  
**Where:** Diagnosis suggestions, UI adaptation (cold-start)  
**Why:** Faster convergence, better personalization  
**Files:** `transfer_learning_service.py`, `adaptation_transfer_service.py`

### 3. Contextual Bandits (Thompson Sampling)
**What:** Online learning for feature promotion/demotion  
**Where:** MAPE-K Plan component (dashboard layout)  
**Why:** Safer than full RL, built-in exploration control  
**Files:** `mape_k_plan_bandit.py`, `bandit_state.py`

### 4. Self-Learning Ensembles
**What:** Weighted ensemble of models, updated by clinician feedback  
**Where:** Vital risk prediction, diagnosis helper  
**Why:** Robust to dataset variations  
**Files:** `ensemble_service.py`

### 5. Runtime Assurance
**What:** Shadow testing, gradual rollouts, rollback on regression  
**Where:** All adaptations (dashboard, suggestions)  
**Why:** Ethics, safety, transparency  
**Files:** `assurance_service.py`, `change_log_service.py`

---

## 🗺️ Architecture Integration

```
┌─────────────────────────────────────────────────────────────┐
│                    EXISTING MAPE-K LOOP                     │
│                                                             │
│  MONITOR → ANALYZE → PLAN → EXECUTE → KNOWLEDGE            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│              SLR ENHANCEMENTS (NEW LAYERS)                  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  MONITOR (Enhanced)                                  │   │
│  │  • Multi-window analysis (7/30/90 days)             │   │
│  │  • Privacy-preserving (hashed IDs, bucketed times)  │   │
│  │  • Exposure tracking (time spent viewing)           │   │
│  └──────────────────────────────────────────────────────┘   │
│                    │                                         │
│                    ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ANALYZE (Enhanced)                                   │   │
│  │  • Transfer learning priors (cold-start)            │   │
│  │  • Federated policy aggregation                      │   │
│  │  • Drift detection                                   │   │
│  └──────────────────────────────────────────────────────┘   │
│                    │                                         │
│                    ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  PLAN (Bandit-Based)                                  │   │
│  │  • Thompson Sampling (constrained)                   │   │
│  │  • Hysteresis & cooldowns                            │   │
│  │  • Bayesian credible intervals                       │   │
│  │  • Context-aware (specialty + time + workflow)       │   │
│  └──────────────────────────────────────────────────────┘   │
│                    │                                         │
│                    ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  EXECUTE (Assured)                                    │   │
│  │  • Shadow testing first                              │   │
│  │  • Gradual rollout                                    │   │
│  │  • Rollback on regression                             │   │
│  │  • Explanations & change logs                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                    │                                         │
│                    ▼                                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  KNOWLEDGE (Enhanced)                                 │   │
│  │  • Bandit state (alpha/beta per feature)             │   │
│  │  • Federated policies                                 │   │
│  │  • Assurance cases                                    │   │
│  │  • Model versions (FL rounds)                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

### New Backend Services
```
app/backend/services/
├── mape_k_plan_bandit.py          # Bandit-based planning
├── transfer_learning_service.py   # Transfer learning
├── adaptation_transfer_service.py # Cold-start handling
├── federated_learning_service.py  # FL coordinator
├── policy_federated_learning.py   # Policy FL
├── assurance_service.py           # Runtime assurance
├── change_log_service.py          # Change logging
├── ensemble_service.py            # Self-learning ensembles
├── privacy_service.py             # Privacy-preserving
├── security_service.py            # Security & threats
├── governance_service.py          # Governance & assurance
├── metrics_service.py             # Research metrics
└── ab_testing_service.py          # A/B testing
```

### New Frontend Components
```
app/frontend/
├── hooks/
│   └── useDashboardTracker.ts     # Enhanced tracking
└── components/
    ├── dashboard/
    │   ├── AdaptiveFeatureGrid.tsx
    │   ├── AdaptationExplanation.tsx
    │   └── ChangeLogDrawer.tsx
    ├── admin/
    │   └── AssuranceDashboard.tsx
    └── research/
        └── MetricsDashboard.tsx
```

### New Database Tables
```sql
-- Bandit state
bandit_state (user_id, feature_key, context_hash, alpha, beta)

-- Federated learning
fl_rounds (round_number, global_model_version, aggregation_method)
fl_client_updates (round_id, client_id, model_weights_hash)

-- Assurance
adaptation_logs (user_id, adaptation_type, old_state, new_state, explanation)
shadow_tests (policy_id, test_group_size, results, recommendation)
assurance_cases (adaptation_id, goal, evidence, risks, mitigations)

-- Model versions
model_versions (model_type, specialty, version, model_path, accuracy_metrics)
```

---

## 🚀 Quick Start: Sprint 1 (Bandit System)

### Step 1: Create Bandit Service
```python
# app/backend/services/mape_k_plan_bandit.py
from typing import List, Dict
import random

def thompson_sampling(stats: List[FeatureStat]) -> List[Tuple[str, float]]:
    """Constrained Thompson Sampling"""
    samples = []
    for stat in stats:
        if stat.critical:
            # Never hide critical features
            score = 1.0
        else:
            score = random.betavariate(stat.alpha, stat.beta)
        samples.append((stat.feature_key, score))
    return sorted(samples, key=lambda x: x[1], reverse=True)
```

### Step 2: Add Tracking Hook
```typescript
// app/frontend/hooks/useDashboardTracker.ts
export function useDashboardTracker(userId: string) {
  const trackClick = (featureKey: string) => {
    navigator.sendBeacon('/api/monitor/dashboard-action', JSON.stringify({
      userId: hashUserId(userId),
      event: 'feature_click',
      featureKey,
      ts: bucketTimestamp(new Date())
    }));
  };
  return { trackClick };
}
```

### Step 3: Create Adaptive Grid
```typescript
// app/frontend/components/dashboard/AdaptiveFeatureGrid.tsx
export function AdaptiveFeatureGrid({ items, onActivate }: Props) {
  return (
    <div className="grid grid-cols-12 gap-3">
      {items.map(item => (
        <FeatureCard
          key={item.feature_key}
          item={item}
          onClick={() => onActivate(item.feature_key)}
        />
      ))}
    </div>
  );
}
```

---

## 📊 Key Metrics to Track

### Adaptation Effectiveness
- **Time-to-target:** Dashboard open → feature activation (target: 50% reduction)
- **Click reduction:** % reduction in clicks (target: 75% reduction)
- **Adaptation accuracy:** Top-N promoted features actually used (target: 80%)

### System Health
- **Layout stability:** Max changes per day (target: ≤3)
- **Cold-start performance:** Days to reach 80% optimal (target: <7 days)
- **FL accuracy:** Model accuracy across sites (target: maintain baseline)

### Safety & Ethics
- **Critical features hidden:** Should be 0
- **Adaptations without explanations:** Should be 0
- **Rollback success rate:** Should be 100%

---

## 🔒 Privacy & Security Checklist

- ✅ Hash user IDs (salted)
- ✅ Bucket timestamps (15-minute bins)
- ✅ Aggregate and delete raw events after analysis
- ✅ Data retention policy (30 days max)
- ✅ Anomaly detection on FL updates
- ✅ Gradient clipping (prevent inversion)
- ✅ Secure communication (signed messages)

---

## 🎓 Research Integration

### Study Design
- **Type:** A/B/BA crossover within-subjects
- **Conditions:** Generic vs. Adaptive dashboard
- **Analysis:** Mixed-effects models
- **Stopping:** Sequential analysis (stop early if large benefit)

### Data Export
```python
# Export for analysis
df = ab_testing_service.export_for_analysis(study_id='dashboard_adaptation')
# Columns: outcome, condition, user_id, day, time_of_day, specialty, ...
```

### Metrics Dashboard
- Real-time visualization
- Compare adaptive vs. baseline
- Export to CSV/JSON for statistical analysis

---

## ⚠️ Common Pitfalls & Solutions

| Pitfall | Solution |
|---------|----------|
| **Layout thrashing** | Hysteresis & cooldowns (24h promote, 7d demote) |
| **Cold-start problem** | Transfer learning priors + ε-greedy exploration |
| **Over-personalization** | Cap deviation from specialty defaults |
| **Non-IID drift** | Multi-window analysis + drift detection |
| **Explainability gap** | Tooltips + change logs + usage stats |
| **Compute limits** | Bandits (lightweight) vs. full RL |
| **Privacy concerns** | Hash IDs, bucket times, aggregate-only |

---

## 📚 SLR Citations

When writing your dissertation, cite:

- **Federated Learning:** "FL repeatedly appears as the workhorse for training with distributed, non-IID clinical data" (Section 4.3, Table 5)
- **Transfer Learning:** "Transfer learning maintains accuracy when imaging conditions or domains vary" (Section 4.3, Table 5)
- **RL/Bandits:** "RL has been used to adapt model parameters while balancing accuracy and compute" (Section 4.3, Table 5)
- **Ethics/Assurance:** "Adoption hinges on transparency, clinician oversight, post-deployment monitoring" (Section 4.4, Table 7)

---

## 🎯 Next Steps

1. **Review the full plan:** `SLR_BASED_IMPROVEMENT_PLAN.md`
2. **Start with Sprint 1:** Bandit-based planning (2 weeks)
3. **Test incrementally:** Each phase builds on previous
4. **Document as you go:** Update docs with each implementation
5. **Collect metrics:** Start tracking from day 1

---

*Quick reference for SLR-based improvements. See full plan for detailed implementation.*

