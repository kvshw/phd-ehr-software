# Next Steps: Implementation Roadmap

## 🎯 Current Status

✅ **Planning Complete:**
- Comprehensive EHR enhancement plan
- Finnish healthcare adaptation plan
- Database migration scripts ready
- Finnish ID validator created

✅ **Database Ready:**
- Migration scripts prepared
- All table schemas defined

⏳ **Ready to Implement:**
- Backend models and APIs
- Frontend components
- Integration with existing features

---

## 🚀 Phase 1: Foundation (Week 1) - START HERE

### Step 1.1: Run Database Migrations (30 minutes)
**Priority**: CRITICAL - Do this first!

```bash
# In Supabase SQL Editor, run in this order:
1. scripts/create_ehr_tables.sql (if not already done)
2. scripts/create_all_finnish_ehr_tables.sql (Finnish features + visits)
```

**Verification:**
```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('visits', 'kela_reimbursements', 'municipalities', 'user_language_preferences');

-- Check Finnish fields added
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'patients' 
AND column_name IN ('henkilotunnus', 'kela_card_number', 'municipality_code');
```

### Step 1.2: Update Backend Models (2-3 hours)
**Priority**: HIGH

**Files to Create/Modify:**

1. **Enhanced User Model**
   - File: `app/backend/models/user.py`
   - Add: specialty, first_name, last_name, title, department, heti_number, preferences

2. **Enhanced Patient Model**
   - File: `app/backend/models/patient.py`
   - Add: All Finnish fields (henkilotunnus, kela_card_number, municipality, etc.)

3. **Visit Model** (NEW)
   - File: `app/backend/models/visit.py`
   - Complete visit/encounter management

4. **Task Model** (NEW)
   - File: `app/backend/models/task.py`
   - Task management system

5. **Alert Model** (NEW)
   - File: `app/backend/models/alert.py`
   - Alert system

**Action Items:**
- [ ] Update User model with Finnish fields
- [ ] Update Patient model with Finnish fields
- [ ] Create Visit model
- [ ] Create Task model
- [ ] Create Alert model
- [ ] Update `app/backend/models/__init__.py` to export new models

### Step 1.3: Create Backend Schemas (1-2 hours)
**Priority**: HIGH

**Files to Create:**

1. `app/backend/schemas/visit.py` - Visit request/response schemas
2. `app/backend/schemas/task.py` - Task schemas
3. `app/backend/schemas/alert.py` - Alert schemas
4. Update `app/backend/schemas/patient.py` - Add Finnish fields
5. Update `app/backend/schemas/user.py` - Add Finnish fields

**Action Items:**
- [ ] Create visit schemas
- [ ] Create task schemas
- [ ] Create alert schemas
- [ ] Update patient schemas
- [ ] Update user schemas

---

## 🚀 Phase 2: Core Features (Week 1-2)

### Step 2.1: Patient Registration Enhancement (3-4 hours)
**Priority**: HIGH - High visibility feature

**What to Build:**
- Multi-step registration wizard
- Henkilötunnus input with validation
- Kela Card input
- Municipality selector
- Auto-fill date of birth from henkilötunnus

**Files to Create:**
- `app/frontend/app/patients/register/page.tsx`
- `app/frontend/components/patient-registration/RegistrationWizard.tsx`
- `app/frontend/components/patient-registration/HenkilotunnusInput.tsx`
- `app/frontend/components/patient-registration/KelaCardInput.tsx`
- `app/frontend/lib/finnishIdService.ts` - Frontend validation

**Backend:**
- Update `app/backend/api/routes/patients.py` - Add Finnish field handling
- Create `app/backend/services/finnish_id_service.py` - Use existing validator

**Action Items:**
- [ ] Create registration wizard component
- [ ] Integrate Finnish ID validator
- [ ] Add Kela card input
- [ ] Add municipality selector
- [ ] Update patient creation API

### Step 2.2: Visit Management (4-5 hours)
**Priority**: HIGH - Core workflow feature

**What to Build:**
- Create visit/encounter
- Visit history list
- Visit details view
- Finnish visit types (terveyskeskus, erikoislääkäri, päivystys)
- Public/Private service selection

**Files to Create:**
- `app/backend/api/routes/visits.py` - Visit CRUD API
- `app/backend/services/visit_service.py` - Visit business logic
- `app/frontend/components/patient-detail/VisitsSection.tsx`
- `app/frontend/lib/visitService.ts`
- `app/frontend/components/visits/VisitForm.tsx`
- `app/frontend/components/visits/ServiceTypeSelector.tsx`

**Action Items:**
- [ ] Create visit API endpoints
- [ ] Create visit service
- [ ] Create visits section component
- [ ] Add visit form
- [ ] Integrate into patient detail page

### Step 2.3: Dashboard Adaptations (4-5 hours)
**Priority**: HIGH - High impact for MAPE-K

**What to Build:**
- Dashboard-level MAPE-K adaptations
- Widget ordering
- Widget visibility
- Role-based dashboard layouts

**Files to Create/Modify:**
- `app/backend/services/adaptation_service.py` - Add dashboard adaptation logic
- `app/backend/services/dashboard_adaptation_service.py` - Dashboard-specific logic
- `app/frontend/store/adaptationStore.ts` - Global adaptation state
- `app/frontend/components/dashboard/AdaptiveDashboard.tsx`
- `app/frontend/components/dashboard/AdaptiveWidget.tsx`
- Update `app/frontend/app/dashboard/page.tsx` - Apply adaptations

**Action Items:**
- [ ] Extend adaptation service for dashboard
- [ ] Create adaptation store
- [ ] Create adaptive dashboard component
- [ ] Apply adaptations to dashboard
- [ ] Test widget ordering/visibility

---

## 🚀 Phase 3: Finnish Features (Week 2-3)

### Step 3.1: Finnish ID Integration (2-3 hours)
**Priority**: MEDIUM - Finnish-specific

**What to Build:**
- Integrate Finnish ID validator into patient registration
- Auto-fill date of birth and gender
- Format validation in frontend

**Files to Modify:**
- `app/frontend/components/patient-registration/HenkilotunnusInput.tsx` (use validator)
- `app/backend/api/routes/patients.py` - Validate on backend
- `app/frontend/lib/finnishIdService.ts` - Frontend validation wrapper

**Action Items:**
- [ ] Integrate validator into registration form
- [ ] Add auto-fill functionality
- [ ] Add format validation
- [ ] Test with sample Finnish IDs

### Step 3.2: Kela Service (Mock) (2-3 hours)
**Priority**: MEDIUM - Finnish-specific

**What to Build:**
- Mock Kela service for research (no real API calls)
- Eligibility checking
- Reimbursement calculation
- Direct reimbursement processing

**Files to Create:**
- `app/backend/services/kela_service.py` - Mock Kela integration
- `app/frontend/lib/kelaService.ts` - Frontend service
- `app/frontend/components/kela/KelaCardVerification.tsx`

**Action Items:**
- [ ] Create mock Kela service
- [ ] Implement eligibility checking
- [ ] Implement reimbursement calculation
- [ ] Create Kela card verification component

### Step 3.3: Bilingual Support (3-4 hours)
**Priority**: MEDIUM - Important for Finnish context

**What to Build:**
- Set up i18n (internationalization)
- Finnish translations
- Swedish translations
- Language selector

**Files to Create:**
- `app/frontend/locales/fi.json` - Finnish translations
- `app/frontend/locales/sv.json` - Swedish translations
- `app/frontend/lib/i18n.ts` - i18n setup
- `app/frontend/components/layout/LanguageSelector.tsx`

**Dependencies:**
```bash
cd app/frontend
npm install next-i18next react-i18next i18next
```

**Action Items:**
- [ ] Install i18n libraries
- [ ] Set up i18n configuration
- [ ] Create translation files
- [ ] Add language selector
- [ ] Translate key UI components

---

## 🚀 Phase 4: Enhanced Workflows (Week 3-4)

### Step 4.1: Task Management (4-5 hours)
**Priority**: MEDIUM - Useful for daily operations

**What to Build:**
- Create tasks
- Assign tasks
- Task completion tracking
- Task list view
- Task dashboard widget

**Files to Create:**
- `app/backend/api/routes/tasks.py`
- `app/backend/services/task_service.py`
- `app/frontend/components/tasks/TaskManager.tsx`
- `app/frontend/components/dashboard/TaskSidebar.tsx`
- `app/frontend/lib/taskService.ts`

**Action Items:**
- [ ] Create task API
- [ ] Create task service
- [ ] Create task manager component
- [ ] Add task sidebar to dashboard
- [ ] Integrate with patient detail page

### Step 4.2: Alert System (3-4 hours)
**Priority**: MEDIUM - Important for patient safety

**What to Build:**
- Create alerts
- Alert acknowledgment
- Alert center/notification bell
- Alert filtering

**Files to Create:**
- `app/backend/api/routes/alerts.py`
- `app/backend/services/alert_service.py`
- `app/frontend/components/alerts/AlertCenter.tsx`
- `app/frontend/components/layout/NotificationBell.tsx`
- `app/frontend/lib/alertService.ts`

**Action Items:**
- [ ] Create alert API
- [ ] Create alert service
- [ ] Create alert center component
- [ ] Add notification bell to header
- [ ] Integrate with patient workflows

### Step 4.3: Role-Based UI (4-5 hours)
**Priority**: HIGH - High impact for usability

**What to Build:**
- Doctor-specific layout
- Nurse-specific layout
- Specialty-based templates
- Role-based dashboard customization

**Files to Create:**
- `app/backend/services/role_adaptation_service.py`
- `app/frontend/components/adaptation/RoleBasedLayout.tsx`
- `app/frontend/components/adaptation/DoctorLayout.tsx`
- `app/frontend/components/adaptation/NurseLayout.tsx`
- Update `app/frontend/app/dashboard/page.tsx` - Apply role layouts

**Action Items:**
- [ ] Create role adaptation service
- [ ] Create doctor layout component
- [ ] Create nurse layout component
- [ ] Apply role-based layouts
- [ ] Test with different roles

---

## 🚀 Phase 5: Polish & Integration (Week 4+)

### Step 5.1: Clinical Decisions (3-4 hours)
**Priority**: LOW - Nice to have

**What to Build:**
- Decision tracking
- Decision workflow
- Decision audit trail

### Step 5.2: Care Plans (3-4 hours)
**Priority**: LOW - Nice to have

**What to Build:**
- Care plan creation
- Care plan templates
- Care plan progress tracking

### Step 5.3: Reports (4-5 hours)
**Priority**: LOW - Nice to have

**What to Build:**
- Report generation
- Report templates
- Report sharing

---

## 📋 Immediate Next Steps (Do Today)

### 1. Run Database Migration (30 min)
```sql
-- In Supabase SQL Editor
-- Run: scripts/create_all_finnish_ehr_tables.sql
```

### 2. Test Finnish ID Validator (15 min)
```bash
cd app/backend
python3 utils/finnish_id_validator.py
```

### 3. Update Patient Model (1 hour)
- Add Finnish fields to `app/backend/models/patient.py`
- Update `app/backend/schemas/patient.py`

### 4. Create Visit Model (1 hour)
- Create `app/backend/models/visit.py`
- Create `app/backend/schemas/visit.py`

---

## 🎯 Recommended Implementation Order

### Week 1 Focus:
1. ✅ Database migration
2. ✅ Backend models (User, Patient, Visit)
3. ✅ Patient registration enhancement
4. ✅ Visit management API

### Week 2 Focus:
1. ✅ Dashboard adaptations
2. ✅ Finnish ID integration
3. ✅ Bilingual support setup
4. ✅ Visit management UI

### Week 3 Focus:
1. ✅ Task management
2. ✅ Alert system
3. ✅ Role-based UI
4. ✅ Kela service (mock)

### Week 4+ Focus:
1. ✅ Polish and testing
2. ✅ Additional features
3. ✅ Documentation
4. ✅ Demo preparation

---

## 🔧 Development Workflow

### For Each Feature:
1. **Backend First**: Create model → schema → service → API
2. **Frontend Second**: Create service → component → integrate
3. **Test**: Test with sample data
4. **Document**: Update relevant docs

### Testing Checklist:
- [ ] Backend API works (test with Postman/curl)
- [ ] Frontend component renders
- [ ] Data saves correctly
- [ ] No console errors
- [ ] Works with existing features
- [ ] Finnish features work correctly

---

## 📝 Quick Reference

### Key Files to Modify:
- `app/backend/models/` - Database models
- `app/backend/schemas/` - API schemas
- `app/backend/api/routes/` - API endpoints
- `app/backend/services/` - Business logic
- `app/frontend/components/` - UI components
- `app/frontend/lib/` - Frontend services
- `app/frontend/app/` - Pages

### Key Commands:
```bash
# Backend
cd app/backend
uvicorn main:app --reload

# Frontend
cd app/frontend
npm run dev

# Test Finnish ID validator
python3 app/backend/utils/finnish_id_validator.py
```

---

## 🎓 For PhD Research

**As you implement, document:**
- Research contributions
- Finnish healthcare adaptations
- MAPE-K enhancements
- User experience improvements
- Technical achievements

**Update:**
- `memory-bank/progress.md` - Track what's done
- `memory-bank/activeContext.md` - Current work
- `memory-bank/systemPatterns.md` - New patterns

---

## ✅ Success Criteria

**Phase 1 Complete When:**
- [ ] Database migrations run successfully
- [ ] All backend models created
- [ ] Patient registration includes Finnish fields
- [ ] Visit management works

**Phase 2 Complete When:**
- [ ] Dashboard adaptations work
- [ ] Finnish ID validation works
- [ ] Bilingual support functional
- [ ] Visit management UI complete

**Phase 3 Complete When:**
- [ ] Task management works
- [ ] Alert system functional
- [ ] Role-based UI implemented
- [ ] Kela service (mock) working

---

**Status**: Ready to Start Implementation  
**Next Action**: Run database migration, then start with backend models  
**Estimated Time**: 4-6 weeks for full implementation

