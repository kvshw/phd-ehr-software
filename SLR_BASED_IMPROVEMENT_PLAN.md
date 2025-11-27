# SLR-Based Improvement Plan
## Advanced Techniques for Self-Adaptive EHR Platform

Based on Systematic Literature Review (SLR) recommendations for self-adaptive healthcare systems, this plan integrates federated learning, transfer learning, reinforcement learning (bandits), and ethics assurance into the existing MAPE-K architecture.

---

## 📋 Executive Summary

This plan enhances the existing MAPE-K dashboard adaptation system with:
- **Federated Learning (FL)** for privacy-preserving model updates
- **Transfer Learning** for specialty-aware models and cold-start handling
- **Contextual Bandits** for intelligent layout adaptation
- **Self-Learning Ensembles** for robust predictions
- **Runtime Assurance Layer** for ethics and safety

**Expected Impact:**
- Better cold-start performance (transfer learning)
- More stable adaptations (bandits with constraints)
- Privacy-preserving multi-site capability (federated learning)
- Enhanced safety and transparency (assurance layer)

---

## 🎯 Phase 1: Enhanced MAPE-K with Bandit-Based Planning

### 1.1 Backend: Bandit-Driven Plan Service

**File:** `app/backend/services/mape_k_plan_bandit.py` (NEW)

**Purpose:** Replace rule-based planning with Thompson Sampling contextual bandits for more intelligent feature promotion/demotion.

**Key Features:**
- Constrained Thompson Sampling (never hide critical features)
- Hysteresis and cooldowns (prevent layout thrashing)
- Bayesian credible intervals (change only when confident)
- Context-aware (specialty + time-of-day + workflow state)

**Implementation Steps:**

1. **Create Bandit Service**
   ```python
   # app/backend/services/mape_k_plan_bandit.py
   from typing import List, Dict, Optional
   from dataclasses import dataclass
   import random
   from datetime import datetime, timedelta
   
   @dataclass
   class FeatureStat:
       feature_key: str
       alpha: float  # successes (quick access, acceptance)
       beta: float   # failures (slow access, ignore)
       critical: bool = False
       last_promoted: Optional[datetime] = None
       last_demoted: Optional[datetime] = None
   
   class BanditPlanService:
       def generate_plan(
           self,
           user_id: UUID,
           specialty: str,
           context: Dict[str, Any],
           stats: List[FeatureStat]
       ) -> Dict[str, Any]:
           # Thompson Sampling with constraints
           # ...
   ```

2. **Integrate with Existing Plan Service**
   - Update `app/backend/services/mape_k_plan.py` to use bandit service
   - Keep rule-based as fallback
   - Add A/B testing flag to compare approaches

3. **Add Constraints**
   - Never hide critical features (safety, allergies, etc.)
   - Promotion cooldown: 24 hours
   - Demotion cooldown: 7 days
   - Max 3 promotions per adaptation cycle

**Files to Create/Modify:**
- `app/backend/services/mape_k_plan_bandit.py` (NEW)
- `app/backend/services/mape_k_plan.py` (MODIFY - integrate bandits)
- `app/backend/models/bandit_state.py` (NEW - store bandit parameters)

**Database Schema:**
```sql
CREATE TABLE bandit_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    feature_key VARCHAR(100),
    context_hash VARCHAR(64),  -- specialty + time_of_day
    alpha FLOAT DEFAULT 1.0,
    beta FLOAT DEFAULT 1.0,
    last_updated TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, feature_key, context_hash)
);
```

---

### 1.2 Frontend: Enhanced Tracking with Exposure Metrics

**File:** `app/frontend/hooks/useDashboardTracker.ts` (NEW)

**Purpose:** Track not just clicks, but also exposure time, context, and user behavior patterns.

**Key Features:**
- Exposure tracking (time spent viewing dashboard)
- Non-blocking tracking (navigator.sendBeacon)
- Context capture (time-of-day, specialty, workflow state)
- Privacy-preserving (hashed user IDs, bucketed timestamps)

**Implementation Steps:**

1. **Create Tracking Hook**
   ```typescript
   // app/frontend/hooks/useDashboardTracker.ts
   export function useDashboardTracker(userId: string) {
     const visibleAt = useRef<number>(Date.now());
     
     const trackExposure = () => {
       const payload = {
         userId: hashUserId(userId), // Privacy-preserving
         event: "dashboard_exposure",
         visibleMs: Date.now() - visibleAt.current,
         context: {
           timeOfDay: getTimeOfDay(),
           specialty: user?.specialty,
         },
         ts: bucketTimestamp(new Date()), // 15-min buckets
       };
       navigator.sendBeacon("/api/monitor/dashboard-action", JSON.stringify(payload));
     };
     
     const trackClick = (featureKey: string, metadata?: Record<string, any>) => {
       // Similar implementation
     };
     
     return { trackExposure, trackClick };
   }
   ```

2. **Update Dashboard Page**
   - Integrate tracking hook
   - Track exposure on mount/unmount
   - Track all feature clicks

**Files to Create/Modify:**
- `app/frontend/hooks/useDashboardTracker.ts` (NEW)
- `app/frontend/app/dashboard/page.tsx` (MODIFY - add tracking)
- `app/frontend/lib/privacy.ts` (NEW - hashing utilities)

---

### 1.3 Frontend: Adaptive Feature Grid with Bandit Sizes

**File:** `app/frontend/components/dashboard/AdaptiveFeatureGrid.tsx` (NEW)

**Purpose:** Render features based on bandit-generated plan with dynamic sizing and explanations.

**Key Features:**
- Dynamic grid layout (large/medium/small based on bandit scores)
- Visual indicators for promoted features
- "Why this moved" tooltips
- Smooth animations for layout changes

**Implementation Steps:**

1. **Create Adaptive Grid Component**
   ```typescript
   // app/frontend/components/dashboard/AdaptiveFeatureGrid.tsx
   interface FeatureItem {
     feature_key: string;
     size: 'lg' | 'md' | 'sm';
     priority: number;
     explanation?: string;
     critical?: boolean;
   }
   
   export function AdaptiveFeatureGrid({ items, onActivate }: Props) {
     return (
       <div className="grid grid-cols-12 gap-3">
         {items.map((item) => (
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

2. **Add Explanation Tooltips**
   - Show why feature was promoted
   - Display usage statistics
   - Link to change log

**Files to Create/Modify:**
- `app/frontend/components/dashboard/AdaptiveFeatureGrid.tsx` (NEW)
- `app/frontend/components/dashboard/FeatureCard.tsx` (NEW)
- `app/frontend/app/dashboard/page.tsx` (MODIFY - use adaptive grid)

---

## 🎯 Phase 2: Transfer Learning for Cold-Start & Specialty Adaptation

### 2.1 Specialty-Aware Model Fine-Tuning

**File:** `app/backend/services/transfer_learning_service.py` (NEW)

**Purpose:** Use transfer learning to fine-tune diagnosis models per specialty, reducing data needs and improving accuracy.

**Key Features:**
- Pre-trained base model (general medical knowledge)
- Specialty-specific heads (cardiology, neurology, etc.)
- Fine-tuning on synthetic specialty corpora
- Model versioning and rollback

**Implementation Steps:**

1. **Create Transfer Learning Service**
   ```python
   # app/backend/services/transfer_learning_service.py
   class TransferLearningService:
       def fine_tune_for_specialty(
           self,
           base_model_path: str,
           specialty: str,
           training_data: List[Dict],
           epochs: int = 5
       ) -> str:
           # Load base model
           # Freeze base layers
           # Fine-tune specialty head
           # Save and version model
           # ...
   ```

2. **Update Diagnosis Helper**
   - Load specialty-specific model
   - Fall back to base model if specialty model unavailable
   - Log model version for audit

**Files to Create/Modify:**
- `app/backend/services/transfer_learning_service.py` (NEW)
- `app/backend/services/diagnosis_helper_service.py` (MODIFY - use transfer learning)
- `app/model-services/diagnosis-helper/` (MODIFY - add transfer learning support)

**Database Schema:**
```sql
CREATE TABLE model_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_type VARCHAR(50),  -- 'diagnosis', 'vital_risk', etc.
    specialty VARCHAR(50),
    version VARCHAR(20),
    model_path TEXT,
    base_model_version VARCHAR(20),
    training_data_hash VARCHAR(64),
    accuracy_metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 2.2 Transfer Learning for UI Adaptation

**File:** `app/backend/services/adaptation_transfer_service.py` (NEW)

**Purpose:** Transfer learned usage patterns from similar doctors/specialties to new users (cold-start solution).

**Key Features:**
- Global usage priors (learned from all users)
- Specialty-specific priors (learned from specialty users)
- Transfer to new user with small exploration (ε-greedy)
- Gradual transition from priors to personal data

**Implementation Steps:**

1. **Create Adaptation Transfer Service**
   ```python
   # app/backend/services/adaptation_transfer_service.py
   class AdaptationTransferService:
       def get_transferred_priors(
           self,
           specialty: str,
           user_experience_days: int
       ) -> Dict[str, FeatureStat]:
           if user_experience_days < 7:
               # Use specialty priors
               return self._get_specialty_priors(specialty)
           elif user_experience_days < 30:
               # Blend priors with personal data
               return self._blend_priors_and_personal(specialty, user_id)
           else:
               # Use personal data only
               return self._get_personal_stats(user_id)
   ```

2. **Integrate with Bandit Service**
   - Use transferred priors as initial alpha/beta
   - Gradually update with personal data
   - Maintain exploration (ε-greedy) for new features

**Files to Create/Modify:**
- `app/backend/services/adaptation_transfer_service.py` (NEW)
- `app/backend/services/mape_k_plan_bandit.py` (MODIFY - use transfer priors)

---

## 🎯 Phase 3: Federated Learning for Privacy-Preserving Updates

### 3.1 FL Infrastructure for Vital Risk Model

**File:** `app/backend/services/federated_learning_service.py` (NEW)

**Purpose:** Enable federated learning for vital risk prediction across synthetic "sites" (departments/hospitals).

**Key Features:**
- Federated aggregation (FedAvg)
- Personalization heads per site
- Secure communication (signed messages)
- Non-IID handling (dual-aggregated FL variant)

**Implementation Steps:**

1. **Create FL Coordinator Service**
   ```python
   # app/backend/services/federated_learning_service.py
   class FederatedLearningService:
       def aggregate_updates(
           self,
           client_updates: List[Dict],
           weights: List[float]
       ) -> Dict:
           # Weighted average aggregation
           # Handle non-IID with personalization heads
           # ...
       
       def distribute_global_model(
           self,
           model_weights: Dict,
           clients: List[str]
       ):
           # Send global weights to clients
           # ...
   ```

2. **Create FL Client Service**
   ```python
   # app/model-services/vital-risk/fl_client.py
   class FLClient:
       def train_local(
           self,
           global_weights: Dict,
           local_data: List[Dict],
           epochs: int = 1
       ) -> Dict:
           # Load global weights
           # Train on local data
           # Return weight updates
           # ...
   ```

3. **Simulate Multi-Site Setup**
   - Create 3 synthetic "sites" (departments)
   - Each site has local vital risk model
   - Coordinate federated rounds
   - Log policy versions for audit

**Files to Create/Modify:**
- `app/backend/services/federated_learning_service.py` (NEW)
- `app/model-services/vital-risk/fl_client.py` (NEW)
- `app/model-services/vital-risk/fl_coordinator.py` (NEW)
- `scripts/simulate_fl_rounds.py` (NEW - for testing)

**Database Schema:**
```sql
CREATE TABLE fl_rounds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_number INT,
    global_model_version VARCHAR(20),
    aggregation_method VARCHAR(50),  -- 'fedavg', 'dual_aggregated', etc.
    participant_count INT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE fl_client_updates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    round_id UUID REFERENCES fl_rounds(id),
    client_id VARCHAR(100),  -- site/department identifier
    model_weights_hash VARCHAR(64),
    sample_count INT,
    sent_at TIMESTAMP DEFAULT NOW()
);
```

---

### 3.2 FL for Adaptation Policy Learning

**File:** `app/backend/services/policy_federated_learning.py` (NEW)

**Purpose:** Federate UI adaptation policies (not just clinical models) so layout policies learn across doctors/sites.

**Key Features:**
- Aggregate bandit parameters (alpha/beta) across users
- Specialty-specific policy aggregation
- Privacy-preserving (only aggregate parameters, not raw events)
- Versioned policy updates

**Implementation Steps:**

1. **Create Policy FL Service**
   ```python
   # app/backend/services/policy_federated_learning.py
   class PolicyFederatedLearning:
       def aggregate_bandit_policies(
           self,
           specialty: str,
           user_policies: List[Dict]
       ) -> Dict:
           # Aggregate alpha/beta per feature
           # Weight by user experience (more data = higher weight)
           # Return aggregated policy
           # ...
   ```

2. **Integrate with Bandit Service**
   - Use federated policies as priors
   - Update with local data
   - Maintain privacy (no raw event sharing)

**Files to Create/Modify:**
- `app/backend/services/policy_federated_learning.py` (NEW)
- `app/backend/services/mape_k_plan_bandit.py` (MODIFY - use federated policies)

---

## 🎯 Phase 4: Runtime Assurance Layer

### 4.1 Ethics & Safety Assurance

**File:** `app/backend/services/assurance_service.py` (NEW)

**Purpose:** Add runtime assurance layer to MAPE-K for ethics, safety, and transparency.

**Key Features:**
- Shadow testing (test new policies before applying)
- Gradual rollouts (A/B testing)
- Rollback on regression (automatic if metrics degrade)
- Clinician-visible change logs
- Bias/drift dashboards

**Implementation Steps:**

1. **Create Assurance Service**
   ```python
   # app/backend/services/assurance_service.py
   class AssuranceService:
       def shadow_test_policy(
           self,
           new_policy: Dict,
           current_policy: Dict,
           duration_days: int = 7
       ) -> Dict[str, Any]:
           # Run new policy in shadow mode
           # Compare metrics (time-to-target, clicks, satisfaction)
           # Return recommendation (approve/reject/modify)
           # ...
       
       def gradual_rollout(
           self,
           policy: Dict,
           rollout_percentage: float,
           success_threshold: float
       ):
           # Gradually increase rollout percentage
           # Monitor metrics
           # Pause/rollback if below threshold
           # ...
       
       def check_regression(
           self,
           baseline_metrics: Dict,
           current_metrics: Dict
       ) -> bool:
           # Check if current metrics regressed
           # Return True if regression detected
           # ...
   ```

2. **Create Change Log Service**
   ```python
   # app/backend/services/change_log_service.py
   class ChangeLogService:
       def log_adaptation(
           self,
           user_id: UUID,
           adaptation_type: str,
           old_state: Dict,
           new_state: Dict,
           explanation: str,
           metrics: Dict
       ):
           # Log adaptation with full provenance
           # Store who/what/why/when
           # ...
   ```

3. **Create Bias/Drift Dashboard**
   - Monitor adaptation effectiveness by specialty
   - Detect drift in usage patterns
   - Alert on bias (some groups benefit more than others)

**Files to Create/Modify:**
- `app/backend/services/assurance_service.py` (NEW)
- `app/backend/services/change_log_service.py` (NEW)
- `app/backend/api/routes/assurance.py` (NEW)
- `app/frontend/components/admin/AssuranceDashboard.tsx` (NEW)

**Database Schema:**
```sql
CREATE TABLE adaptation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    adaptation_type VARCHAR(50),  -- 'dashboard_layout', 'suggestion_density', etc.
    old_state JSONB,
    new_state JSONB,
    explanation TEXT,
    metrics_before JSONB,
    metrics_after JSONB,
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE shadow_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID,
    test_group_size INT,
    control_group_size INT,
    duration_days INT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    results JSONB,
    recommendation VARCHAR(20)  -- 'approve', 'reject', 'modify'
);
```

---

### 4.2 Explainability & Transparency

**File:** `app/frontend/components/dashboard/AdaptationExplanation.tsx` (NEW)

**Purpose:** Show users why adaptations were made, building trust and transparency.

**Key Features:**
- "Why this moved" tooltips on promoted features
- Change log drawer (visible history of adaptations)
- Usage statistics (show actual usage data)
- Explanation generation (natural language)

**Implementation Steps:**

1. **Create Explanation Component**
   ```typescript
   // app/frontend/components/dashboard/AdaptationExplanation.tsx
   export function AdaptationExplanation({ feature, adaptation }: Props) {
     return (
       <Tooltip>
         <TooltipContent>
           <h4>Why {feature} was promoted</h4>
           <p>{adaptation.explanation}</p>
           <Stats>
             <Stat label="Uses per day">{adaptation.daily_average}</Stat>
             <Stat label="Total uses">{adaptation.usage_count}</Stat>
             <Stat label="Promoted since">{adaptation.promoted_at}</Stat>
           </Stats>
         </TooltipContent>
       </Tooltip>
     );
   }
   ```

2. **Create Change Log Drawer**
   - Show history of adaptations
   - Filter by date, type, feature
   - Link to detailed metrics

**Files to Create/Modify:**
- `app/frontend/components/dashboard/AdaptationExplanation.tsx` (NEW)
- `app/frontend/components/dashboard/ChangeLogDrawer.tsx` (NEW)
- `app/frontend/app/dashboard/page.tsx` (MODIFY - add explanation components)

---

## 🎯 Phase 5: Self-Learning Ensembles

### 5.1 Ensemble for Vital Risk Prediction

**File:** `app/backend/services/ensemble_service.py` (NEW)

**Purpose:** Use weighted, self-learning ensembles for robust vital risk predictions.

**Key Features:**
- Ensemble of classical models + neural networks
- Online weight updates based on acceptance/override rates
- Clinician feedback as "teacher signal"
- Robust to dataset variations

**Implementation Steps:**

1. **Create Ensemble Service**
   ```python
   # app/backend/services/ensemble_service.py
   class EnsembleService:
       def __init__(self):
           self.models = [
               ClassicalRiskModel(),
               NeuralRiskModel(),
               RuleBasedModel()
           ]
           self.weights = [0.33, 0.33, 0.34]  # Initial equal weights
       
       def predict(self, vitals: Dict) -> Dict:
           predictions = [m.predict(vitals) for m in self.models]
           # Weighted average
           return self._weighted_average(predictions, self.weights)
       
       def update_weights(self, feedback: Dict):
           # Update weights based on acceptance/override rates
           # Increase weight of models with high acceptance
           # Decrease weight of models with high override
           # ...
   ```

2. **Integrate with Vital Risk Service**
   - Use ensemble instead of single model
   - Log which model contributed most
   - Update weights based on feedback

**Files to Create/Modify:**
- `app/backend/services/ensemble_service.py` (NEW)
- `app/backend/services/vital_risk_service.py` (MODIFY - use ensemble)
- `app/model-services/vital-risk/ensemble_models.py` (NEW)

---

## 🎯 Phase 6: Enhanced Monitor with Multi-Window Analysis

### 6.1 Multi-Window Statistics

**File:** `app/backend/services/mape_k_analyze.py` (MODIFY)

**Purpose:** Maintain statistics across multiple time windows (7/30/90 days) with exponential decay for recency vs. stability balance.

**Key Features:**
- Multi-window analysis (short-term, medium-term, long-term)
- Exponential decay (recent data weighted more)
- Non-stationarity handling (detect drift)
- Context-aware windows (different windows for different features)

**Implementation Steps:**

1. **Enhance Analyze Service**
   ```python
   # app/backend/services/mape_k_analyze.py (MODIFY)
   class MAPEKAnalyzeService:
       def analyze_with_windows(
           self,
           user_id: UUID,
           windows: List[int] = [7, 30, 90]
       ) -> Dict[str, Any]:
           results = {}
           for window in windows:
               window_data = self._get_window_data(user_id, window)
               results[f"{window}_day"] = self._analyze_window(window_data)
           
           # Combine with exponential decay
           combined = self._combine_with_decay(results)
           return combined
       
       def _combine_with_decay(self, window_results: Dict) -> Dict:
           # Weight recent windows more heavily
           # 7-day: weight 0.5, 30-day: weight 0.3, 90-day: weight 0.2
           # ...
   ```

**Files to Modify:**
- `app/backend/services/mape_k_analyze.py` (MODIFY - add multi-window support)

---

## 🎯 Phase 7: Privacy, Security & Governance

### 7.1 Privacy-Preserving Tracking

**File:** `app/backend/services/privacy_service.py` (NEW)

**Purpose:** Implement privacy-by-design for usage tracking.

**Key Features:**
- Hashed user IDs (salted)
- Bucketed timestamps (15-minute bins)
- Aggregate-only storage (no raw events after analysis)
- Data retention policies

**Implementation Steps:**

1. **Create Privacy Service**
   ```python
   # app/backend/services/privacy_service.py
   class PrivacyService:
       def hash_user_id(self, user_id: UUID, salt: str) -> str:
           # Hash user ID with salt
           # ...
       
       def bucket_timestamp(self, timestamp: datetime) -> datetime:
           # Round to 15-minute buckets
           # ...
       
       def aggregate_and_delete_raw(self, events: List[Dict]) -> Dict:
           # Aggregate events
           # Delete raw events
           # Return aggregates only
           # ...
   ```

2. **Update Monitor Service**
   - Hash user IDs before storage
   - Bucket timestamps
   - Aggregate and delete raw events after analysis

**Files to Create/Modify:**
- `app/backend/services/privacy_service.py` (NEW)
- `app/backend/services/user_action_service.py` (MODIFY - use privacy service)
- `app/backend/api/routes/monitor.py` (MODIFY - apply privacy)

---

### 7.2 Security & Threat Detection

**File:** `app/backend/services/security_service.py` (NEW)

**Purpose:** Detect and mitigate security threats in FL and adaptation systems.

**Key Features:**
- Anomaly detection on client updates (FL poisoning)
- Gradient clipping (prevent model inversion)
- Continuous monitoring
- Alert system

**Implementation Steps:**

1. **Create Security Service**
   ```python
   # app/backend/services/security_service.py
   class SecurityService:
       def detect_poisoning(self, updates: List[Dict]) -> bool:
           # Detect anomalous updates
           # Check for gradient outliers
           # Return True if poisoning detected
           # ...
       
       def clip_gradients(self, gradients: Dict, max_norm: float):
           # Clip gradients to prevent inversion
           # ...
   ```

2. **Integrate with FL Service**
   - Check updates before aggregation
   - Reject suspicious updates
   - Alert administrators

**Files to Create/Modify:**
- `app/backend/services/security_service.py` (NEW)
- `app/backend/services/federated_learning_service.py` (MODIFY - add security checks)

---

### 7.3 Governance & Assurance Cases

**File:** `app/backend/services/governance_service.py` (NEW)

**Purpose:** Maintain assurance case artifacts per adaptation for ethics and compliance.

**Key Features:**
- Goal definition (what adaptation aims to achieve)
- Evidence collection (A/B metrics, user feedback)
- Risk assessment (potential harms)
- Mitigation strategies
- Approval workflow

**Implementation Steps:**

1. **Create Governance Service**
   ```python
   # app/backend/services/governance_service.py
   class GovernanceService:
       def create_assurance_case(
           self,
           adaptation: Dict,
           goal: str,
           evidence: Dict,
           risks: List[str],
           mitigations: List[str]
       ) -> Dict:
           # Create assurance case artifact
           # Store in database
           # Link to adaptation
           # ...
   ```

**Files to Create/Modify:**
- `app/backend/services/governance_service.py` (NEW)
- `app/backend/api/routes/admin.py` (MODIFY - add governance endpoints)

**Database Schema:**
```sql
CREATE TABLE assurance_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    adaptation_id UUID REFERENCES adaptations(id),
    goal TEXT,
    evidence JSONB,
    risks JSONB,
    mitigations JSONB,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 Phase 8: Research Design & Metrics

### 8.1 Enhanced Metrics Collection

**File:** `app/backend/services/metrics_service.py` (NEW)

**Purpose:** Collect comprehensive metrics for research evaluation.

**Key Metrics:**
- Time-to-target (dashboard open to feature activation)
- Click reduction (%)
- Suggestion acceptance/ignore rate
- Adaptation accuracy (top-N promoted features actually used)
- User satisfaction (surveys)

**Implementation Steps:**

1. **Create Metrics Service**
   ```python
   # app/backend/services/metrics_service.py
   class MetricsService:
       def measure_time_to_target(
           self,
           user_id: UUID,
           feature_key: str
       ) -> float:
           # Measure time from dashboard open to feature activation
           # ...
       
       def calculate_click_reduction(
           self,
           user_id: UUID,
           baseline_clicks: int,
           adaptive_clicks: int
       ) -> float:
           # Calculate percentage reduction
           # ...
       
       def measure_adaptation_accuracy(
           self,
           user_id: UUID,
           promoted_features: List[str],
           actually_used: List[str]
       ) -> float:
           # Calculate precision/recall
           # ...
   ```

2. **Create Research Dashboard**
   - Visualize metrics over time
   - Compare adaptive vs. baseline
   - Export data for analysis

**Files to Create/Modify:**
- `app/backend/services/metrics_service.py` (NEW)
- `app/frontend/components/research/MetricsDashboard.tsx` (NEW)
- `app/backend/api/routes/research.py` (MODIFY - add metrics endpoints)

---

### 8.2 A/B Testing Infrastructure

**File:** `app/backend/services/ab_testing_service.py` (NEW)

**Purpose:** Support A/B/BA crossover within-subjects study design.

**Key Features:**
- Random assignment to conditions
- Crossover support (switch conditions)
- Mixed-effects model data export
- Sequential analysis (stop early if large benefit)

**Implementation Steps:**

1. **Create A/B Testing Service**
   ```python
   # app/backend/services/ab_testing_service.py
   class ABTestingService:
       def assign_condition(
           self,
           user_id: UUID,
           study_id: str
       ) -> str:
           # Random assignment (A or B)
           # Track assignment
           # ...
       
       def crossover(
           self,
           user_id: UUID,
           study_id: str
       ):
           # Switch user to other condition
           # Track crossover time
           # ...
       
       def export_for_analysis(
           self,
           study_id: str
       ) -> pd.DataFrame:
           # Export data for mixed-effects models
           # Include: outcome, condition, user_id, day, covariates
           # ...
   ```

**Files to Create/Modify:**
- `app/backend/services/ab_testing_service.py` (NEW)
- `app/backend/api/routes/research.py` (MODIFY - add A/B testing endpoints)

---

## 📅 Implementation Timeline

### Sprint 1 (2 weeks): Core Bandit System
- ✅ Implement bandit-based planning service
- ✅ Add exposure + click tracking (frontend)
- ✅ Create adaptive feature grid
- ✅ Add explanations and change log
- ✅ Test with synthetic data

**Deliverables:**
- Bandit plan service working
- Frontend tracking integrated
- Adaptive grid rendering
- Basic explanations

---

### Sprint 2 (2 weeks): Transfer Learning & Cold-Start
- ✅ Implement transfer learning for diagnosis models
- ✅ Add adaptation transfer service (cold-start)
- ✅ Integrate with bandit service
- ✅ Test cold-start performance

**Deliverables:**
- Specialty-specific models fine-tuned
- Cold-start handling working
- Better initial adaptations

---

### Sprint 3 (3 weeks): Federated Learning
- ✅ Implement FL infrastructure
- ✅ Create FL coordinator and clients
- ✅ Simulate multi-site setup
- ✅ Add policy federated learning
- ✅ Test with synthetic sites

**Deliverables:**
- FL working for vital risk model
- Policy FL working
- Multi-site simulation

---

### Sprint 4 (2 weeks): Runtime Assurance
- ✅ Implement assurance service
- ✅ Add shadow testing
- ✅ Create gradual rollout system
- ✅ Build change log service
- ✅ Create bias/drift dashboard

**Deliverables:**
- Assurance layer working
- Shadow testing functional
- Change logs visible to clinicians

---

### Sprint 5 (2 weeks): Ensembles & Enhanced Analysis
- ✅ Implement ensemble service
- ✅ Add multi-window analysis
- ✅ Integrate with existing services
- ✅ Test robustness

**Deliverables:**
- Ensemble predictions working
- Multi-window analysis functional

---

### Sprint 6 (2 weeks): Privacy, Security, Governance
- ✅ Implement privacy service
- ✅ Add security checks
- ✅ Create governance service
- ✅ Build assurance cases

**Deliverables:**
- Privacy-preserving tracking
- Security monitoring
- Governance artifacts

---

### Sprint 7 (2 weeks): Research Infrastructure
- ✅ Implement metrics service
- ✅ Create A/B testing infrastructure
- ✅ Build research dashboard
- ✅ Export functionality

**Deliverables:**
- Comprehensive metrics collection
- A/B testing ready
- Research dashboard

---

### Sprint 8 (2 weeks): Integration & Testing
- ✅ Integrate all components
- ✅ End-to-end testing
- ✅ Performance optimization
- ✅ Documentation

**Deliverables:**
- Fully integrated system
- Tested and optimized
- Complete documentation

---

## 🎯 Success Criteria

### Technical Metrics
- ✅ Bandit system reduces layout thrashing (max 3 changes/day)
- ✅ Cold-start: <7 days to reach 80% of optimal performance
- ✅ FL: Model accuracy maintained across sites
- ✅ Assurance: 100% of adaptations have assurance cases
- ✅ Privacy: No raw events stored >30 days

### Research Metrics
- ✅ Time-to-target: 50%+ reduction
- ✅ Click reduction: 75%+ reduction
- ✅ Adaptation accuracy: 80%+ (top-3 promoted features actually used)
- ✅ User satisfaction: 4.0+ / 5.0

### Safety Metrics
- ✅ Zero critical features hidden
- ✅ Zero adaptations without explanations
- ✅ 100% rollback success rate on regression
- ✅ Zero security incidents

---

## 📚 References & Citations

### SLR Techniques Used
- **Federated Learning:** Section 4.3, Table 5 (FL for non-IID clinical data)
- **Transfer Learning:** Section 4.3, Table 5 (domain adaptation)
- **Reinforcement Learning/Bandits:** Section 4.3, Table 5 (RL-enhanced DCNN)
- **Self-Learning Ensembles:** Section 4.3 (weighted ensembles for EEG)
- **Ethics/Assurance:** Section 4.4, Table 7 (transparency, oversight, monitoring)

### Key Tables/Figures
- **Figure 1 (p.2):** Static vs. self-adaptive software (use to frame MAPE-K UI loop)
- **Table 5 (p.8):** Technique → application mapping
- **Table 7 (p.9):** Challenge list (non-IID, explainability, audit, compute)

---

## 🔧 Code Locations Summary

### Backend Services
- `app/backend/services/mape_k_plan_bandit.py` - Bandit-based planning
- `app/backend/services/transfer_learning_service.py` - Transfer learning
- `app/backend/services/federated_learning_service.py` - FL coordinator
- `app/backend/services/assurance_service.py` - Runtime assurance
- `app/backend/services/ensemble_service.py` - Self-learning ensembles
- `app/backend/services/privacy_service.py` - Privacy-preserving tracking
- `app/backend/services/security_service.py` - Security & threat detection
- `app/backend/services/governance_service.py` - Governance & assurance cases
- `app/backend/services/metrics_service.py` - Research metrics
- `app/backend/services/ab_testing_service.py` - A/B testing infrastructure

### Frontend Components
- `app/frontend/hooks/useDashboardTracker.ts` - Enhanced tracking
- `app/frontend/components/dashboard/AdaptiveFeatureGrid.tsx` - Adaptive grid
- `app/frontend/components/dashboard/AdaptationExplanation.tsx` - Explanations
- `app/frontend/components/dashboard/ChangeLogDrawer.tsx` - Change log
- `app/frontend/components/admin/AssuranceDashboard.tsx` - Assurance dashboard
- `app/frontend/components/research/MetricsDashboard.tsx` - Research metrics

### Database Migrations
- `scripts/create_bandit_tables.sql` - Bandit state storage
- `scripts/create_fl_tables.sql` - Federated learning tables
- `scripts/create_assurance_tables.sql` - Assurance & governance tables

---

*This plan integrates SLR recommendations into your existing MAPE-K architecture, providing a roadmap for advanced self-adaptive capabilities.*

