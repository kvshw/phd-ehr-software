# Role-Based Login Implementation Plan

## Current State Analysis

### ✅ What's Already Implemented
1. **Backend RBAC:**
   - Three roles: `clinician`, `researcher`, `admin`
   - Role validation in auth service
   - Role-based route protection via `require_role()` dependency
   - JWT tokens include role information

2. **Frontend Authentication:**
   - Login page with email/password
   - Role-based redirects after login (`getRedirectPath()`)
   - Auth store with user role state
   - Protected routes via middleware

3. **Current Redirects:**
   - `clinician` → `/dashboard` (patient list)
   - `researcher` → `/researcher/dashboard` (analytics)
   - `admin` → `/admin/controls` (system management)

### ❌ What's Missing
1. **Visual Role Selection** - No role indicator on login page
2. **Role-Specific Login UI** - Same form for all roles
3. **Role Preview** - Can't see what each role can access
4. **Quick Role Switcher** - For testing/demo purposes
5. **Role Badges** - Visual indicators of user role
6. **Role-Based Welcome Messages** - Personalized login experience

## Proposed Implementation

### Option 1: Enhanced Login with Role Selection (Recommended)
**Best for:** Production use, clear role distinction

**Features:**
- Role selection tabs/cards on login page
- Visual role indicators with icons
- Role-specific descriptions
- Pre-filled role hint (optional)
- Role-based welcome messages

**UI Design:**
```
┌─────────────────────────────────────┐
│  EHR Research Platform              │
│                                     │
│  ┌──────┐ ┌──────┐ ┌──────┐       │
│  │ 👨‍⚕️  │ │ 📊  │ │ ⚙️   │       │
│  │Clin. │ │Res.  │ │Admin │       │
│  └──────┘ └──────┘ └──────┘       │
│                                     │
│  Email: [________________]         │
│  Password: [____________]           │
│                                     │
│  [Sign In]                          │
└─────────────────────────────────────┘
```

### Option 2: Role-Aware Login with Auto-Detection
**Best for:** Seamless UX, single account multiple roles

**Features:**
- Auto-detect role from email/domain
- Show role badge after login
- Allow role switching (if user has multiple roles)
- Role-specific dashboard preview

### Option 3: Role Selection After Login
**Best for:** Users with multiple roles

**Features:**
- Login with email/password
- If user has access to multiple roles, show role selector
- Choose role → redirect to appropriate dashboard
- Remember role preference

## Recommended Implementation Plan

### Phase 1: Enhanced Login UI (Option 1 - Recommended)

#### 1.1 Update Login Page Component
**File:** `app/frontend/app/login/page.tsx`

**Changes:**
- Add role selection UI (tabs or cards)
- Add role icons and descriptions
- Visual feedback for selected role
- Role-specific welcome messages
- Optional: Remember role preference

**Role Cards:**
```typescript
const roles = [
  {
    id: 'clinician',
    label: 'Clinician',
    icon: '👨‍⚕️',
    description: 'Access patient records, vitals, and AI suggestions',
    color: 'blue',
    route: '/dashboard'
  },
  {
    id: 'researcher',
    label: 'Researcher',
    icon: '📊',
    description: 'View analytics, metrics, and research data',
    color: 'purple',
    route: '/researcher/dashboard'
  },
  {
    id: 'admin',
    label: 'Administrator',
    icon: '⚙️',
    description: 'System controls and user management',
    color: 'indigo',
    route: '/admin/controls'
  }
];
```

#### 1.2 Role Selection Component
**New File:** `app/frontend/components/auth/RoleSelector.tsx`

**Features:**
- Visual role cards with icons
- Hover effects and selection state
- Role descriptions
- Click to select role
- Optional: Role preview modal

#### 1.3 Update Auth Store
**File:** `app/frontend/store/authStore.ts`

**Changes:**
- Add `selectedRole` state (optional, for pre-selection)
- Update login to use selected role if provided
- Validate role matches user's actual role after login

#### 1.4 Role Badge Component
**New File:** `app/frontend/components/auth/RoleBadge.tsx`

**Features:**
- Display user role with icon
- Color-coded badges
- Used in TopHeader and user profile

### Phase 2: Backend Enhancements

#### 2.1 Role Validation on Login
**File:** `app/backend/api/routes/auth.py`

**Changes:**
- Optional: Accept `preferred_role` in login request
- Validate preferred role matches user's actual role
- Return role information in login response
- Add role metadata (permissions, dashboard route)

#### 2.2 Role Metadata Endpoint
**New Endpoint:** `GET /api/v1/auth/roles`

**Response:**
```json
{
  "roles": [
    {
      "id": "clinician",
      "label": "Clinician",
      "description": "Access patient records and AI suggestions",
      "permissions": ["view_patients", "create_patients", "view_suggestions"],
      "dashboard_route": "/dashboard"
    },
    ...
  ]
}
```

### Phase 3: UI Enhancements

#### 3.1 Role-Based Welcome Messages
**File:** `app/frontend/app/login/page.tsx`

**Features:**
- Dynamic welcome message based on selected role
- Role-specific instructions
- Preview of what they'll see after login

#### 3.2 TopHeader Role Badge
**File:** `app/frontend/components/layout/TopHeader.tsx`

**Changes:**
- Add role badge next to user profile
- Color-coded by role
- Click to see role details

#### 3.3 Role Switcher (Optional - for testing)
**New Component:** `app/frontend/components/auth/RoleSwitcher.tsx`

**Features:**
- Dropdown to switch roles (if user has multiple)
- Only visible in development/testing mode
- Quick role switching for demos

## Implementation Details

### Component Structure

```
app/frontend/
├── app/
│   └── login/
│       └── page.tsx (Enhanced with role selection)
├── components/
│   ├── auth/
│   │   ├── RoleSelector.tsx (New)
│   │   ├── RoleBadge.tsx (New)
│   │   └── RoleSwitcher.tsx (New - Optional)
│   └── layout/
│       └── TopHeader.tsx (Add role badge)
└── lib/
    └── auth.ts (Add role utilities)
```

### State Management

```typescript
// Auth Store Updates
interface AuthState {
  user: User | null;
  selectedRole: 'clinician' | 'researcher' | 'admin' | null; // For pre-selection
  isAuthenticated: boolean;
  // ... existing fields
}
```

### API Changes

```typescript
// Login Request (Optional enhancement)
interface LoginRequest {
  email: string;
  password: string;
  preferred_role?: string; // Optional role hint
}

// Login Response (Enhanced)
interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    role: string;
    role_metadata?: {
      label: string;
      description: string;
      dashboard_route: string;
    };
  };
}
```

## Design Specifications

### Role Cards Design

**Clinician Card:**
- Color: Blue (`bg-blue-50`, `border-blue-200`)
- Icon: Medical/Stethoscope
- Description: "Access patient records, vitals, and AI suggestions"
- Selected: `bg-blue-100 border-blue-400`

**Researcher Card:**
- Color: Purple (`bg-purple-50`, `border-purple-200`)
- Icon: Chart/Graph
- Description: "View analytics, metrics, and research data"
- Selected: `bg-purple-100 border-purple-400`

**Admin Card:**
- Color: Indigo (`bg-indigo-50`, `border-indigo-200`)
- Icon: Settings/Gear
- Description: "System controls and user management"
- Selected: `bg-indigo-100 border-indigo-400`

### Role Badge Design

```typescript
// Small badge for header
<RoleBadge role="clinician" size="sm" />
// Output: [👨‍⚕️ Clinician]

// Large badge for profile
<RoleBadge role="researcher" size="lg" />
// Output: [📊 Researcher - View analytics and research data]
```

## User Experience Flow

### Login Flow with Role Selection

1. **User arrives at login page**
   - Sees three role cards
   - Can click to select a role (optional)
   - Sees role-specific description

2. **User enters credentials**
   - Email and password fields
   - Selected role (if any) is highlighted

3. **User clicks "Sign In"**
   - Form validates
   - Login request sent (with optional role hint)
   - Backend validates credentials AND role match

4. **After successful login**
   - User redirected to role-appropriate dashboard
   - Role badge shown in header
   - Welcome message with role name

### Error Handling

- **Role Mismatch:** "This account does not have [selected role] access"
- **Invalid Credentials:** Standard error message
- **No Role Selected:** Login works, uses user's default role

## Testing Plan

### Test Cases

1. **Role Selection**
   - ✅ Select clinician → Login → Redirects to `/dashboard`
   - ✅ Select researcher → Login → Redirects to `/researcher/dashboard`
   - ✅ Select admin → Login → Redirects to `/admin/controls`
   - ✅ No selection → Login → Uses user's actual role

2. **Role Mismatch**
   - ✅ Select clinician but user is researcher → Error message
   - ✅ Select admin but user is clinician → Error message

3. **Visual Feedback**
   - ✅ Selected role card highlights
   - ✅ Role badge appears in header after login
   - ✅ Welcome message shows correct role

4. **Access Control**
   - ✅ Clinician cannot access researcher dashboard
   - ✅ Researcher cannot access admin controls
   - ✅ Admin can access all dashboards

## Implementation Priority

### High Priority (Must Have)
1. ✅ Role selection UI on login page
2. ✅ Role badges in header
3. ✅ Role-based redirects (already working)
4. ✅ Visual role indicators

### Medium Priority (Should Have)
1. Role-specific welcome messages
2. Role metadata endpoint
3. Role descriptions and previews

### Low Priority (Nice to Have)
1. Role switcher for testing
2. Remember role preference
3. Role-based login page theming

## Files to Create/Modify

### New Files
1. `app/frontend/components/auth/RoleSelector.tsx`
2. `app/frontend/components/auth/RoleBadge.tsx`
3. `app/frontend/components/auth/RoleSwitcher.tsx` (Optional)

### Modified Files
1. `app/frontend/app/login/page.tsx` - Add role selection
2. `app/frontend/store/authStore.ts` - Add role state
3. `app/frontend/lib/auth.ts` - Add role utilities
4. `app/frontend/components/layout/TopHeader.tsx` - Add role badge
5. `app/backend/api/routes/auth.py` - Optional role validation
6. `app/backend/schemas/auth.py` - Add role metadata

## Success Criteria

✅ **User can visually select their role before login**
✅ **Role badges clearly indicate user type**
✅ **Login experience is role-aware and personalized**
✅ **Visual feedback confirms role selection**
✅ **Error handling for role mismatches**
✅ **Consistent role indicators throughout the app**

## Next Steps

1. **Review this plan** - Confirm approach and priorities
2. **Design mockups** - Create visual designs for role cards
3. **Implement Phase 1** - Enhanced login UI with role selection
4. **Test thoroughly** - All role combinations and edge cases
5. **Iterate** - Based on user feedback

---

**Would you like me to proceed with implementing Option 1 (Enhanced Login with Role Selection)?**

This will provide:
- Clear visual role distinction
- Better UX for role-based access
- Professional appearance
- Easy to test and demonstrate

