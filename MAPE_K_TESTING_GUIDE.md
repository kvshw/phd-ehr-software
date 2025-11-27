# MAPE-K UI Adaptation Testing Guide

## Overview

This guide explains how to test and verify that the MAPE-K (Monitor, Analyze, Plan, Execute, Knowledge) adaptation system is working and applying UI changes based on user behavior.

## Quick Start: How to See Adaptations

### Step 1: Generate User Activity (Monitor Phase)

The system needs data to analyze. To trigger adaptations, you need to:

1. **Navigate between sections** on a patient detail page
   - Go to `/patients/[patient-id]`
   - Click through different sections: Summary, Vitals, Labs, Imaging, etc.
   - Each navigation is automatically logged

2. **Interact with AI suggestions** (if available)
   - Click "Generate Suggestions" in the Suggestions panel
   - Accept, ignore, or mark suggestions as "not relevant"
   - These interactions are logged

3. **Wait for risk changes** (if applicable)
   - Risk level changes are automatically logged when vitals are updated

### Step 2: Trigger Plan Generation (Analyze & Plan Phase)

After generating some activity, manually trigger a plan:

**Option A: Using Browser Console**
```javascript
// Open browser console (F12) on any patient page
// Replace PATIENT_ID with actual patient ID
fetch('http://localhost:8000/api/v1/mape-k/plan?patient_id=PATIENT_ID', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_TOKEN' // Get from browser cookies/localStorage
  }
})
.then(r => r.json())
.then(data => {
  console.log('Adaptation Plan:', data);
  // Reload page to see changes
  window.location.reload();
});
```

**Option B: Using API Client (Postman/curl)**
```bash
curl -X POST "http://localhost:8000/api/v1/mape-k/plan?patient_id=PATIENT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

**Option C: Add a Button (Recommended for Testing)**

We can add a "Generate Adaptation" button to the patient detail page for easier testing.

### Step 3: Verify UI Changes (Execute Phase)

After generating a plan, refresh the patient detail page. Look for:

1. **Adaptation Indicator Banner**
   - Blue banner at the top of patient detail page
   - Shows "UI Adapted for You" with explanation
   - Click "Show adaptation details" to see what changed

2. **Section Order Changes**
   - Sections in the navigation bar may be reordered
   - Most frequently visited sections move to the top
   - Check the section navigation tabs

3. **Suggestion Density Changes**
   - If you frequently ignore suggestions, density may decrease
   - If you frequently accept suggestions, density may increase
   - This affects how many suggestions are shown at once

## Detailed Testing Steps

### Test 1: Navigation-Based Adaptation

**Goal:** Verify that section order changes based on navigation patterns.

**Steps:**
1. Navigate to a patient detail page: `/patients/[patient-id]`
2. Navigate to these sections in this order (repeat 5-10 times):
   - Vitals
   - Labs
   - Imaging
   - Vitals (again)
   - Labs (again)
3. Open browser console and check logged navigations:
   ```javascript
   // Check network tab for POST requests to /monitor/log-navigation
   ```
4. Trigger plan generation (see Step 2 above)
5. Refresh the page
6. **Expected Result:** Vitals and Labs sections should appear earlier in the navigation order

### Test 2: Suggestion Interaction Adaptation

**Goal:** Verify that suggestion density adapts based on interaction patterns.

**Steps:**
1. Navigate to a patient detail page
2. Go to "AI Suggestions" section
3. Click "Generate Suggestions" multiple times
4. For each suggestion:
   - Accept some (click accept/checkmark)
   - Ignore others (click ignore/X)
   - Mark some as "not relevant"
5. Repeat steps 3-4 several times
6. Trigger plan generation
7. Refresh the page
8. **Expected Result:** 
   - If you accepted many: Suggestion density may increase
   - If you ignored many: Suggestion density may decrease
   - Check the adaptation explanation banner

### Test 3: Risk-Based Adaptation

**Goal:** Verify that UI adapts when patient risk level changes.

**Steps:**
1. Navigate to a patient detail page
2. Note the current risk level (shown in patient header)
3. If risk is "routine", add vitals that would increase risk:
   - High heart rate (>100)
   - Low SpO2 (<95)
   - High temperature (>38°C)
4. Risk level should automatically update
5. Trigger plan generation
6. Refresh the page
7. **Expected Result:** 
   - Risk-related sections (Vitals, Labs) may be prioritized
   - Adaptation explanation mentions risk escalation

### Test 4: Check Adaptation Indicator

**Goal:** Verify the adaptation indicator shows correctly.

**Steps:**
1. After generating a plan and refreshing, look for the blue banner
2. The banner should show:
   - "UI Adapted for You" title
   - "Experimental" badge
   - Explanation text (e.g., "Layout adapted based on your usage patterns")
   - "Show adaptation details" link
   - "Reset Layout" button
3. Click "Show adaptation details"
4. **Expected Result:** 
   - Details panel expands showing:
     - How adaptations work
     - What changed (section order, suggestion density)
     - Transparency information

### Test 5: Reset Adaptation

**Goal:** Verify that resetting returns to default layout.

**Steps:**
1. With an active adaptation, click "Reset Layout" button
2. Page should refresh
3. **Expected Result:**
   - Adaptation banner disappears
   - Sections return to default order
   - Suggestion density returns to default

## Checking Adaptation Status

### Method 1: Browser Console

```javascript
// Check if adaptation is active
// Open console on patient detail page
const store = window.__NEXT_DATA__; // Next.js internal
// Or check localStorage/sessionStorage for adaptation state

// Check network requests
// Open Network tab, filter by "adaptation"
// Look for GET /api/v1/mape-k/adaptation/latest
```

### Method 2: API Endpoint

```bash
# Get latest adaptation for current user
curl -X GET "http://localhost:8000/api/v1/mape-k/adaptation/latest?patient_id=PATIENT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response includes:
# {
#   "id": "...",
#   "user_id": "...",
#   "patient_id": "...",
#   "plan_json": {
#     "order": ["vitals", "labs", "summary", ...],
#     "suggestion_density": "medium",
#     "explanation": "..."
#   },
#   "timestamp": "..."
# }
```

### Method 3: Researcher Dashboard

1. Log in as researcher or admin
2. Go to `/researcher/dashboard`
3. Check "Adaptation Metrics" section
4. View adaptation events and density distribution

## What UI Changes to Look For

### Section Order Changes

**Default Order:**
1. Summary
2. Demographics
3. Diagnoses
4. Clinical Notes
5. Problems
6. Medications
7. Allergies
8. History
9. Vitals
10. Labs
11. Imaging
12. AI Suggestions
13. Safety & Transparency

**After Adaptation:**
- Most visited sections move to the top
- Example: If you visit "Vitals" 15 times and "Labs" 8 times:
  - Vitals might move to position 1-2
  - Labs might move to position 3-4
  - Other sections shift down

### Suggestion Density Changes

**Default:** `medium`
- Shows moderate number of suggestions

**After Adaptation:**
- `low`: Fewer suggestions (if you ignore many)
- `high`: More suggestions (if you accept many)
- `medium`: Balanced (default or balanced interaction)

### Visual Indicators

1. **Adaptation Banner** (blue, top of patient detail page)
2. **Section Navigation** (reordered tabs)
3. **Suggestion Panel** (different number of suggestions shown)

## Troubleshooting

### No Adaptation Banner Appears

**Possible Causes:**
1. No plan has been generated yet
   - **Solution:** Trigger plan generation (see Step 2)
2. Not enough data collected
   - **Solution:** Generate more navigation/suggestion activity
3. Plan generation failed
   - **Solution:** Check backend logs for errors

### Sections Not Reordering

**Possible Causes:**
1. Plan doesn't include order changes
   - **Solution:** Generate more diverse navigation patterns
2. Frontend not applying plan
   - **Solution:** Check browser console for errors
   - Check that `fetchAndApplyAdaptation()` is called on page load

### Suggestion Density Not Changing

**Possible Causes:**
1. No suggestion interactions logged
   - **Solution:** Interact with suggestions more
2. Analysis doesn't detect pattern
   - **Solution:** Make interactions more consistent (e.g., always accept or always ignore)

## Advanced: Manual Testing with API

### 1. Check Monitoring Data

```bash
# View logged navigations (requires researcher/admin role)
curl -X GET "http://localhost:8000/api/v1/research/navigation-metrics?days=7" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Trigger Analysis

```bash
# Analyze user behavior
curl -X POST "http://localhost:8000/api/v1/mape-k/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "YOUR_USER_ID",
    "patient_id": "PATIENT_ID",
    "days": 30
  }'
```

### 3. Generate Plan

```bash
# Generate adaptation plan
curl -X POST "http://localhost:8000/api/v1/mape-k/plan?patient_id=PATIENT_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. View All Adaptations

```bash
# Get all adaptations for current user (researcher/admin only)
curl -X GET "http://localhost:8000/api/v1/mape-k/adaptations?limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Quick Test Script

Here's a quick way to test the full cycle:

1. **Open patient detail page** in browser
2. **Open browser console** (F12)
3. **Navigate sections** 10-15 times (click through tabs)
4. **Generate suggestions** and interact with them
5. **Run this in console:**
   ```javascript
   // Get patient ID from URL
   const patientId = window.location.pathname.split('/patients/')[1];
   
   // Trigger plan generation
   fetch(`http://localhost:8000/api/v1/mape-k/plan?patient_id=${patientId}`, {
     method: 'POST',
     credentials: 'include' // Include cookies for auth
   })
   .then(r => r.json())
   .then(data => {
     console.log('✅ Plan generated:', data);
     console.log('🔄 Reloading page to apply changes...');
     setTimeout(() => window.location.reload(), 1000);
   })
   .catch(err => console.error('❌ Error:', err));
   ```
6. **After reload, check for:**
   - Blue adaptation banner
   - Reordered sections
   - Adaptation explanation

## Expected Behavior Summary

| Action | Expected Result |
|--------|----------------|
| Navigate sections 10+ times | Sections reorder based on frequency |
| Accept many suggestions | Suggestion density increases |
| Ignore many suggestions | Suggestion density decreases |
| Risk level escalates | Risk-related sections prioritized |
| Generate plan | Plan created and stored |
| Refresh page | Adaptation applied automatically |
| Reset layout | Returns to default order |

## Next Steps

For easier testing, we can add:
1. A "Generate Adaptation" button on patient detail page
2. A "View Adaptation Details" modal
3. Real-time adaptation status indicator
4. Adaptation history viewer

Would you like me to add any of these features?

