# MAPE-K Dashboard Adaptation Strategy
## Learning from Doctor Behavior to Optimize Workflow

---

## 🎯 Goal

Transform the dashboard from a **static layout** to a **self-adaptive interface** that:
- **Learns** which features each doctor uses most frequently
- **Prioritizes** those features on the dashboard
- **Hides** or **de-emphasizes** rarely-used features
- **Adapts** based on specialty AND individual usage patterns

---

## 📊 Current State vs. Adaptive State

### Current Dashboard (Static)
```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard (Same for Everyone)                                 │
│                                                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Total       │ │ Today's     │ │ Active      │          │
│  │ Patients    │ │ Appointments│ │ Sessions    │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                             │
│  [Quick Actions - Generic]                                 │
│  [Patient List - All Patients]                             │
│                                                             │
│  ❌ Same layout for cardiologist and neurologist           │
│  ❌ No learning from usage                                  │
│  ❌ Features buried in menus                                │
└─────────────────────────────────────────────────────────────┘
```

### Adaptive Dashboard (MAPE-K)
```
┌─────────────────────────────────────────────────────────────┐
│  Dashboard (Personalized for Dr. Smith - Cardiology)        │
│                                                             │
│  🔄 "Adapted based on your workflow patterns"               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ⚡ MOST USED FEATURES (Promoted)                     │   │
│  │ ┌──────────┐ ┌──────────┐ ┌──────────┐             │   │
│  │ │ECG Review│ │BP Trends │ │CV Risk   │             │   │
│  │ │(15x/day) │ │(12x/day) │ │Calc      │             │   │
│  │ └──────────┘ └──────────┘ └──────────┘             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📊 QUICK STATS (Relevant to Specialty)              │   │
│  │ • Cardiac Patients: 23                              │   │
│  │ • Pending ECGs: 5                                  │   │
│  │ • High BP Alerts: 3                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 👥 PATIENTS (Prioritized by Relevance)               │   │
│  │ 1. Sarah Johnson - Cardiac follow-up (Today)        │   │
│  │ 2. Mike Chen - BP check needed                      │   │
│  │ 3. ...                                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ✅ Features you use daily are at the top                   │
│  ✅ Rarely-used features moved to "More" menu              │
│  ✅ Layout optimized for YOUR workflow                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 MAPE-K Dashboard Adaptation Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    DASHBOARD ADAPTATION CYCLE                            │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  MONITOR: Track Dashboard Interactions                           │   │
│  │  ──────────────────────────────────────────────────────────────  │   │
│  │                                                                 │   │
│  │  • Which quick action buttons are clicked?                     │   │
│  │  • Which navigation items are used?                            │   │
│  │  • Which patient cards are opened?                              │   │
│  │  • Time spent on each dashboard section                         │   │
│  │  • Search queries and filters used                              │   │
│  │  • Feature access frequency (ECG, Labs, Imaging, etc.)          │   │
│  │                                                                 │   │
│  │  Example Data Collected:                                        │   │
│  │  {                                                              │   │
│  │    "user_id": "uuid",                                           │   │
│  │    "action_type": "dashboard_click",                            │   │
│  │    "feature": "ecg_review",                                      │   │
│  │    "timestamp": "2024-01-15T10:30:00Z",                         │   │
│  │    "context": { "specialty": "cardiology", "time_of_day": "morning" }│   │
│  │  }                                                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  ANALYZE: Identify Usage Patterns                                │   │
│  │  ──────────────────────────────────────────────────────────────  │   │
│  │                                                                 │   │
│  │  Analysis Results:                                              │   │
│  │  ┌──────────────────────────────────────────────────────────┐  │   │
│  │  │ Feature Usage Frequency (Last 30 days):                   │  │   │
│  │  │                                                           │  │   │
│  │  │ ECG Review:        ████████████████  85% (17/day)        │  │   │
│  │  │ BP Trends:         ██████████████    72% (14/day)        │  │   │
│  │  │ Patient Search:    ████████          45% (9/day)         │  │   │
│  │  │ Lab Results:       ██████            35% (7/day)         │  │   │
│  │  │ Imaging:           ██                12% (2/day)         │  │   │
│  │  │ Medications:      █                 5%  (1/day)          │  │   │
│  │  └──────────────────────────────────────────────────────────┘  │   │
│  │                                                                 │   │
│  │  Insights Generated:                                           │   │
│  │  • "ECG Review used 17x/day - promote to top"                 │   │
│  │  • "Imaging rarely used - move to secondary menu"              │   │
│  │  • "Morning workflow: ECG → BP → Patient Review"               │   │
│  │  • "Cardiology specialty confirmed by usage patterns"          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  PLAN: Generate Dashboard Layout                                │   │
│  │  ──────────────────────────────────────────────────────────────  │   │
│  │                                                                 │   │
│  │  JSON Dashboard Plan:                                           │   │
│  │  {                                                              │   │
│  │    "feature_priority": [                                       │   │
│  │      { "id": "ecg_review", "position": 1, "size": "large" },   │   │
│  │      { "id": "bp_trends", "position": 2, "size": "large" },    │   │
│  │      { "id": "cv_risk", "position": 3, "size": "medium" },    │   │
│  │      { "id": "patient_search", "position": 4, "size": "small" }│   │
│  │    ],                                                           │   │
│  │    "hidden_features": ["imaging", "medications"],              │   │
│  │    "quick_stats": [                                            │   │
│  │      "cardiac_patients_count",                                 │   │
│  │      "pending_ecgs",                                           │   │
│  │      "high_bp_alerts"                                          │   │
│  │    ],                                                           │   │
│  │    "patient_list_sort": "relevance",                           │   │
│  │    "patient_list_filters": ["cardiac_conditions"]              │   │
│  │  }                                                              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  EXECUTE: Apply Dashboard Adaptations                            │   │
│  │  ──────────────────────────────────────────────────────────────  │   │
│  │                                                                 │   │
│  │  Frontend React Component:                                      │   │
│  │  • Reorder quick action buttons                                 │   │
│  │  • Resize feature cards based on usage                          │   │
│  │  • Show/hide features dynamically                               │   │
│  │  • Update patient list sorting                                  │   │
│  │  • Apply specialty-specific filters                             │   │
│  │                                                                 │   │
│  │  Result: Dashboard matches doctor's actual workflow             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │  KNOWLEDGE: Store Learned Patterns                               │   │
│  │  ──────────────────────────────────────────────────────────────  │   │
│  │                                                                 │   │
│  │  Knowledge Base Updated:                                         │   │
│  │  • User preferences: { "ecg_review": "high_priority" }          │   │
│  │  • Workflow patterns: "morning_ecg_first"                       │   │
│  │  • Specialty confirmation: "cardiology" (from behavior)          │   │
│  │  • Feature relevance scores updated                              │   │
│  │                                                                 │   │
│  │  Next adaptation cycle uses this knowledge                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Plan

### Phase 1: Enhanced Monitor (Dashboard-Specific Tracking)

**File:** `app/backend/services/user_action_service.py`

```python
def log_dashboard_action(
    db: Session,
    user_id: UUID,
    action_type: str,  # 'quick_action_click', 'feature_access', 'navigation'
    feature_id: str,   # 'ecg_review', 'bp_trends', 'patient_search'
    metadata: dict = None
):
    """
    Log dashboard-specific user actions for MAPE-K adaptation
    
    Action Types:
    - quick_action_click: User clicked a quick action button
    - feature_access: User accessed a feature (via menu, search, etc.)
    - navigation: User navigated between dashboard sections
    - patient_card_click: User opened a patient from dashboard
    - search_query: User performed a search
    - filter_applied: User applied a filter
    """
    action = UserAction(
        user_id=user_id,
        action_type=f"dashboard_{action_type}",
        action_data={
            "feature_id": feature_id,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat(),
        },
        timestamp=datetime.utcnow()
    )
    db.add(action)
    db.commit()
```

**Frontend Integration:**
```typescript
// Track quick action clicks
const handleQuickActionClick = async (featureId: string) => {
  // Log to backend
  await apiClient.post('/user-actions', {
    action_type: 'dashboard_quick_action_click',
    feature_id: featureId,
    metadata: {
      specialty: user.specialty,
      time_of_day: new Date().getHours(),
    }
  });
  
  // Navigate to feature
  router.push(`/features/${featureId}`);
};
```

---

### Phase 2: Dashboard-Specific Analysis

**File:** `app/backend/services/mape_k_analyze.py` (extend existing)

```python
def analyze_dashboard_usage(
    db: Session,
    user_id: UUID,
    days: int = 30
) -> Dict[str, Any]:
    """
    Analyze dashboard usage patterns to identify:
    - Most frequently used features
    - Feature access patterns (time of day, day of week)
    - Workflow sequences (which features used together)
    - Rarely used features
    """
    # Get dashboard actions
    dashboard_actions = db.query(UserAction).filter(
        UserAction.user_id == user_id,
        UserAction.action_type.like('dashboard_%'),
        UserAction.timestamp >= datetime.utcnow() - timedelta(days=days)
    ).all()
    
    # Calculate feature frequencies
    feature_counts = {}
    feature_sequences = []
    
    for action in dashboard_actions:
        feature_id = action.action_data.get('feature_id')
        if feature_id:
            feature_counts[feature_id] = feature_counts.get(feature_id, 0) + 1
            
            # Track sequences (which features used together)
            feature_sequences.append({
                'feature': feature_id,
                'timestamp': action.timestamp,
                'context': action.action_data.get('metadata', {})
            })
    
    # Identify most/least used
    sorted_features = sorted(
        feature_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    most_used = [f[0] for f in sorted_features[:5]]  # Top 5
    least_used = [f[0] for f in sorted_features[-3:]]  # Bottom 3
    
    # Analyze workflow patterns
    workflow_patterns = analyze_feature_sequences(feature_sequences)
    
    return {
        "feature_frequencies": feature_counts,
        "most_used_features": most_used,
        "least_used_features": least_used,
        "workflow_patterns": workflow_patterns,
        "total_actions": len(dashboard_actions),
        "analysis_period_days": days
    }
```

---

### Phase 3: Dashboard Layout Plan Generation

**File:** `app/backend/services/mape_k_plan.py` (extend existing)

```python
def generate_dashboard_plan(
    db: Session,
    user_id: UUID,
    dashboard_analysis: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate dashboard layout plan based on usage analysis
    
    Returns JSON plan for dashboard adaptation
    """
    if not dashboard_analysis:
        dashboard_analysis = MAPEKAnalyzeService.analyze_dashboard_usage(db, user_id)
    
    feature_freqs = dashboard_analysis.get("feature_frequencies", {})
    most_used = dashboard_analysis.get("most_used_features", [])
    least_used = dashboard_analysis.get("least_used_features", [])
    
    # Get user specialty for defaults
    user = db.query(User).filter(User.id == user_id).first()
    specialty = user.specialty if user else None
    
    # Build feature priority list
    feature_priority = []
    position = 1
    
    # Add most used features first
    for feature_id in most_used:
        frequency = feature_freqs.get(feature_id, 0)
        # Determine size based on frequency
        if frequency > 15:  # Used >15 times in period
            size = "large"
        elif frequency > 8:
            size = "medium"
        else:
            size = "small"
        
        feature_priority.append({
            "id": feature_id,
            "position": position,
            "size": size,
            "usage_count": frequency
        })
        position += 1
    
    # Add specialty defaults for features not yet used
    specialty_defaults = get_specialty_default_features(specialty)
    for feature_id in specialty_defaults:
        if feature_id not in [f["id"] for f in feature_priority]:
            feature_priority.append({
                "id": feature_id,
                "position": position,
                "size": "medium",
                "usage_count": 0,
                "source": "specialty_default"
            })
            position += 1
    
    # Build quick stats based on specialty and usage
    quick_stats = determine_relevant_stats(specialty, feature_freqs)
    
    # Patient list adaptations
    patient_list_config = {
        "sort_by": "relevance",  # relevance, recent, name
        "default_filters": get_specialty_filters(specialty),
        "items_per_page": 10
    }
    
    return {
        "plan_type": "dashboard",
        "version": "1.0",
        "feature_priority": feature_priority,
        "hidden_features": least_used[:3],  # Hide bottom 3
        "quick_stats": quick_stats,
        "patient_list": patient_list_config,
        "explanation": generate_dashboard_explanation(feature_freqs, specialty)
    }
```

---

### Phase 4: Adaptive Dashboard Component

**File:** `app/frontend/components/dashboard/AdaptiveDashboard.tsx` (NEW)

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { adaptationService } from '@/lib/adaptationService';

interface DashboardPlan {
  feature_priority: Array<{
    id: string;
    position: number;
    size: 'large' | 'medium' | 'small';
    usage_count: number;
  }>;
  hidden_features: string[];
  quick_stats: string[];
  patient_list: {
    sort_by: string;
    default_filters: string[];
  };
  explanation: string;
}

export function AdaptiveDashboard() {
  const { user } = useAuthStore();
  const [dashboardPlan, setDashboardPlan] = useState<DashboardPlan | null>(null);
  const [isAdapted, setIsAdapted] = useState(false);

  useEffect(() => {
    if (user) {
      fetchDashboardAdaptation();
    }
  }, [user]);

  const fetchDashboardAdaptation = async () => {
    try {
      // Get dashboard-specific adaptation plan
      const response = await apiClient.get('/mape-k/dashboard/plan');
      if (response.data) {
        setDashboardPlan(response.data);
        setIsAdapted(true);
      }
    } catch (error) {
      console.error('Failed to fetch dashboard adaptation:', error);
      // Fall back to default layout
      setIsAdapted(false);
    }
  };

  // Render features in priority order
  const renderAdaptiveFeatures = () => {
    if (!dashboardPlan) return null;

    return dashboardPlan.feature_priority.map((feature) => {
      const FeatureComponent = getFeatureComponent(feature.id);
      const sizeClass = {
        large: 'col-span-2 row-span-2',
        medium: 'col-span-1 row-span-1',
        small: 'col-span-1 row-span-1 text-sm'
      }[feature.size];

      return (
        <div key={feature.id} className={sizeClass}>
          <FeatureComponent 
            highlighted={feature.usage_count > 10}
            usageCount={feature.usage_count}
          />
        </div>
      );
    });
  };

  return (
    <div>
      {isAdapted && dashboardPlan && (
        <div className="mb-4 p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
          <p className="text-sm text-indigo-800">
            🔄 <strong>Dashboard Adapted:</strong> {dashboardPlan.explanation}
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-4 gap-4">
        {renderAdaptiveFeatures()}
      </div>
    </div>
  );
}
```

---

## 🎯 Concrete Examples by Specialty

### Example 1: Cardiologist Dashboard Adaptation

**After 2 weeks of usage, MAPE-K learns:**

```
MONITOR Data:
- ECG Review clicked: 238 times (17/day)
- BP Trends accessed: 196 times (14/day)
- CV Risk Calculator: 98 times (7/day)
- Patient Search: 63 times (4.5/day)
- Imaging: 14 times (1/day) ← Rarely used
- Medications: 7 times (0.5/day) ← Very rarely used

ANALYZE Results:
- Most used: ECG Review (85% of actions)
- Workflow pattern: Morning → ECG Review → BP Check → Patient Review
- Specialty confirmed: Cardiology (matches user profile)

PLAN Generated:
{
  "feature_priority": [
    { "id": "ecg_review", "position": 1, "size": "large", "usage_count": 238 },
    { "id": "bp_trends", "position": 2, "size": "large", "usage_count": 196 },
    { "id": "cv_risk", "position": 3, "size": "medium", "usage_count": 98 },
    { "id": "patient_search", "position": 4, "size": "small", "usage_count": 63 }
  ],
  "hidden_features": ["imaging", "medications"],
  "quick_stats": ["cardiac_patients", "pending_ecgs", "high_bp_alerts"],
  "explanation": "Dashboard optimized for your cardiology workflow. ECG Review and BP Trends promoted based on 17 and 14 daily uses respectively."
}

EXECUTE Result:
┌─────────────────────────────────────────────────────────────┐
│  Dashboard - Dr. Smith (Cardiology)                        │
│  🔄 "Adapted based on your workflow"                       │
│                                                             │
│  ┌──────────────────────┐ ┌──────────────────────┐        │
│  │   ECG REVIEW         │ │   BP TRENDS          │        │
│  │   (Large Card)       │ │   (Large Card)       │        │
│  │   Used 17x/day       │ │   Used 14x/day       │        │
│  │   [Quick Access]     │ │   [Quick Access]     │        │
│  └──────────────────────┘ └──────────────────────┘        │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐                        │
│  │ CV Risk Calc │ │ Patient      │                        │
│  │ (Medium)     │ │ Search       │                        │
│  └──────────────┘ └──────────────┘                        │
│                                                             │
│  [More Features ▼] ← Imaging, Medications hidden here     │
└─────────────────────────────────────────────────────────────┘
```

### Example 2: Neurologist Dashboard Adaptation

**After 2 weeks of usage:**

```
MONITOR Data:
- MRI Review: 189 times (13.5/day)
- Neuro Exam Tools: 154 times (11/day)
- Cognitive Tests: 112 times (8/day)
- Patient History: 84 times (6/day)
- ECG Review: 7 times (0.5/day) ← Rarely used

PLAN Generated:
{
  "feature_priority": [
    { "id": "mri_review", "position": 1, "size": "large" },
    { "id": "neuro_exam", "position": 2, "size": "large" },
    { "id": "cognitive_tests", "position": 3, "size": "medium" },
    { "id": "patient_history", "position": 4, "size": "small" }
  ],
  "hidden_features": ["ecg_review", "bp_trends"],
  "quick_stats": ["neurological_patients", "pending_mris", "cognitive_assessments"],
  "explanation": "Dashboard optimized for neurology workflow. MRI Review and Neuro Exam promoted based on frequent use."
}

EXECUTE Result:
┌─────────────────────────────────────────────────────────────┐
│  Dashboard - Dr. Johnson (Neurology)                       │
│  🔄 "Adapted for your neurology workflow"                   │
│                                                             │
│  ┌──────────────────────┐ ┌──────────────────────┐        │
│  │   MRI REVIEW         │ │   NEURO EXAM         │        │
│  │   (Large Card)       │ │   (Large Card)       │        │
│  │   Used 13.5x/day     │ │   Used 11x/day       │        │
│  └──────────────────────┘ └──────────────────────┘        │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐                        │
│  │ Cognitive    │ │ Patient      │                        │
│  │ Tests        │ │ History      │                        │
│  └──────────────┘ └──────────────┘                        │
│                                                             │
│  [More Features ▼] ← ECG, BP hidden here                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation Steps

### Step 1: Backend - Dashboard Action Logging

**Create:** `app/backend/api/routes/dashboard.py`

```python
@router.post("/actions")
async def log_dashboard_action(
    action_data: dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log dashboard action for MAPE-K monitoring"""
    from services.user_action_service import UserActionService
    
    UserActionService.log_action(
        db,
        user_id=current_user.user_id,
        action_type=f"dashboard_{action_data.get('type')}",
        feature_id=action_data.get('feature_id'),
        metadata=action_data.get('metadata', {})
    )
    
    return {"success": True}
```

### Step 2: Backend - Dashboard Analysis Endpoint

**Add to:** `app/backend/api/routes/mape_k.py`

```python
@router.get("/dashboard/analyze", response_model=AnalyzeResponse)
async def analyze_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Analyze dashboard usage patterns"""
    analysis = MAPEKAnalyzeService.analyze_dashboard_usage(
        db, current_user.user_id, days=30
    )
    return AnalyzeResponse(**analysis)
```

### Step 3: Backend - Dashboard Plan Endpoint

**Add to:** `app/backend/api/routes/mape_k.py`

```python
@router.get("/dashboard/plan")
async def get_dashboard_plan(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Get dashboard adaptation plan"""
    analysis = MAPEKAnalyzeService.analyze_dashboard_usage(
        db, current_user.user_id
    )
    plan = MAPEKPlanService.generate_dashboard_plan(
        db, current_user.user_id, analysis
    )
    return plan
```

### Step 4: Frontend - Track Dashboard Interactions

**Update:** `app/frontend/app/dashboard/page.tsx`

```typescript
// Add tracking to all interactive elements
const trackDashboardAction = async (actionType: string, featureId: string) => {
  try {
    await apiClient.post('/dashboard/actions', {
      type: actionType,
      feature_id: featureId,
      metadata: {
        specialty: user?.specialty,
        time_of_day: new Date().getHours(),
      }
    });
  } catch (error) {
    // Fail silently - tracking shouldn't break UX
    console.error('Failed to track action:', error);
  }
};

// Use in components:
<button onClick={() => {
  trackDashboardAction('quick_action_click', 'ecg_review');
  router.push('/ecg');
}}>
  ECG Review
</button>
```

### Step 5: Frontend - Apply Dashboard Adaptations

**Create:** `app/frontend/components/dashboard/AdaptiveFeatureGrid.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/store/authStore';
import { apiClient } from '@/lib/apiClient';

interface FeatureConfig {
  id: string;
  position: number;
  size: 'large' | 'medium' | 'small';
  usage_count: number;
  source?: string;
}

export function AdaptiveFeatureGrid() {
  const { user } = useAuthStore();
  const [features, setFeatures] = useState<FeatureConfig[]>([]);
  const [hiddenFeatures, setHiddenFeatures] = useState<string[]>([]);
  const [explanation, setExplanation] = useState<string>('');

  useEffect(() => {
    if (user) {
      fetchDashboardPlan();
    }
  }, [user]);

  const fetchDashboardPlan = async () => {
    try {
      const response = await apiClient.get('/mape-k/dashboard/plan');
      if (response.data) {
        setFeatures(response.data.feature_priority || []);
        setHiddenFeatures(response.data.hidden_features || []);
        setExplanation(response.data.explanation || '');
      }
    } catch (error) {
      // Fall back to default features
      setFeatures(getDefaultFeatures(user?.specialty));
    }
  };

  return (
    <div>
      {explanation && (
        <div className="mb-4 p-3 bg-indigo-50 border border-indigo-200 rounded-lg">
          <p className="text-sm text-indigo-800">
            🔄 <strong>Adapted:</strong> {explanation}
          </p>
        </div>
      )}
      
      <div className="grid grid-cols-4 gap-4">
        {features.map((feature) => (
          <FeatureCard
            key={feature.id}
            feature={feature}
            size={feature.size}
            highlighted={feature.usage_count > 10}
          />
        ))}
      </div>
      
      {hiddenFeatures.length > 0 && (
        <details className="mt-4">
          <summary className="cursor-pointer text-gray-600">
            More Features ({hiddenFeatures.length} hidden)
          </summary>
          <div className="mt-2">
            {hiddenFeatures.map(featureId => (
              <FeatureCard key={featureId} feature={{ id: featureId, ... }} size="small" />
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
```

---

## 📊 Knowledge Base Rules for Dashboard

```python
DASHBOARD_KNOWLEDGE_BASE = {
    # Promotion thresholds
    "high_usage_threshold": 10,  # Uses per day to promote
    "medium_usage_threshold": 5,
    "low_usage_threshold": 2,
    
    # Hiding thresholds
    "hide_threshold": 1,  # Uses per day to hide
    
    # Size mapping
    "size_mapping": {
        "large": lambda count: count > 15,
        "medium": lambda count: 5 < count <= 15,
        "small": lambda count: count <= 5
    },
    
    # Specialty defaults (used when no usage data)
    "specialty_defaults": {
        "cardiology": ["ecg_review", "bp_trends", "cv_risk", "patient_search"],
        "neurology": ["mri_review", "neuro_exam", "cognitive_tests", "patient_history"],
        "emergency": ["triage", "vitals", "safety_alerts", "patient_search"],
        # ... etc
    },
    
    # Quick stats by specialty
    "specialty_stats": {
        "cardiology": ["cardiac_patients", "pending_ecgs", "high_bp_alerts"],
        "neurology": ["neurological_patients", "pending_mris", "cognitive_assessments"],
        # ... etc
    }
}
```

---

## 🎯 Benefits for Doctors

| Benefit | Description |
|---------|-------------|
| **Time Savings** | Frequently used features at top = fewer clicks |
| **Reduced Cognitive Load** | Less searching, more doing |
| **Personalized** | Dashboard matches YOUR workflow, not generic |
| **Learning System** | Gets better the more you use it |
| **Specialty-Aware** | Starts with sensible defaults for your specialty |

---

## 📈 Expected Impact

**Before MAPE-K Adaptation:**
- Average clicks to access ECG Review: **3-4 clicks** (menu → features → cardiology → ECG)
- Time to find feature: **15-20 seconds**
- Features buried in menus

**After MAPE-K Adaptation:**
- Average clicks to access ECG Review: **1 click** (on dashboard)
- Time to find feature: **<2 seconds**
- Most-used features visible immediately

**Estimated Time Savings:** 2-3 minutes per patient × 20 patients/day = **40-60 minutes saved per day**

---

*This document outlines the complete MAPE-K dashboard adaptation strategy for your PhD research platform.*

