# Finnish EHR System Adaptation Plan

## 🎯 Goal
Adapt the EHR system to align with Finnish healthcare standards and practices, making it more relevant for a Finnish university PhD project while maintaining existing functionality.

---

## 🇫🇮 Key Finnish Healthcare Features to Integrate

### 1. Kela Card Integration (CRITICAL)
**Status**: ❌ Missing

**What is Kela Card:**
- Personal health insurance card issued to residents
- Proof of entitlement to National Health Insurance benefits
- Enables direct reimbursements at pharmacies and clinics
- Contains personal identification number (henkilötunnus)

**Implementation:**
- [ ] Kela Card number field in patient registration
- [ ] Kela Card number validation (format: YYMMDD-XXXX)
- [ ] Kela eligibility verification
- [ ] Direct reimbursement calculation
- [ ] Kela card scanning/input interface
- [ ] Kela reimbursement tracking

**Database Changes:**
```sql
ALTER TABLE patients
ADD COLUMN kela_card_number VARCHAR(20),
ADD COLUMN kela_eligible BOOLEAN DEFAULT TRUE,
ADD COLUMN municipality_code VARCHAR(10), -- For public healthcare eligibility
ADD COLUMN municipality_name VARCHAR(255);
```

**Files to Create:**
- `app/backend/services/kela_service.py` - Kela integration logic
- `app/frontend/components/patient-registration/KelaCardInput.tsx`
- `app/frontend/lib/kelaService.ts`

---

### 2. Kanta Services Integration
**Status**: ❌ Missing

**What is Kanta:**
- Finland's national eHealth platform
- Provides access to electronic health records
- Prescription management
- Laboratory results and imaging
- Patient access via OmaKanta portal

**Implementation:**
- [ ] Kanta-compatible data formats
- [ ] HL7 FHIR standards compliance
- [ ] Data export to Kanta format
- [ ] Prescription integration (ePrescription)
- [ ] Lab result integration
- [ ] Imaging report integration

**Files to Create:**
- `app/backend/services/kanta_service.py` - Kanta integration
- `app/backend/services/fhir_service.py` - FHIR format conversion
- `app/frontend/components/kanta/KantaIntegration.tsx`

---

### 3. Finnish Personal Identity Number (Henkilötunnus)
**Status**: ❌ Missing

**Format:** YYMMDD-XXXX (e.g., 120345-1234)
- First 6 digits: Date of birth (DDMMYY)
- Separator: - or +
- Last 4 digits: Individual number + check digit

**Implementation:**
- [ ] Henkilötunnus field in patient registration
- [ ] Format validation
- [ ] Check digit validation
- [ ] Age calculation from henkilötunnus
- [ ] Gender inference from henkilötunnus

**Database Changes:**
```sql
ALTER TABLE patients
ADD COLUMN henkilotunnus VARCHAR(11) UNIQUE, -- Finnish personal ID
ADD COLUMN date_of_birth DATE; -- Can be derived from henkilötunnus
```

**Files to Create:**
- `app/backend/utils/finnish_id_validator.py` - Validation logic
- `app/frontend/components/patient-registration/HenkilotunnusInput.tsx`

---

### 4. Public vs Private Healthcare Distinction
**Status**: ❌ Missing

**Finnish System:**
- Public healthcare: Municipality-based, accessible to registered residents
- Private healthcare: Direct payment with Kela reimbursement
- Service type affects billing and reimbursement

**Implementation:**
- [ ] Service type selection (public/private)
- [ ] Municipality registration check
- [ ] Public healthcare eligibility verification
- [ ] Billing adjustment based on service type
- [ ] Reimbursement calculation

**Database Changes:**
```sql
ALTER TABLE visits
ADD COLUMN service_type VARCHAR(20) DEFAULT 'public', -- public, private
ADD COLUMN municipality_code VARCHAR(10),
ADD COLUMN kela_reimbursement_amount DECIMAL(10,2);
```

---

### 5. ePrescription System (Finnish Standards)
**Status**: ⚠️ Basic medication tracking exists

**Finnish ePrescription:**
- Electronic prescription orders
- Integration with National Prescription Centre
- Medication reconciliation
- Refill requests

**Enhancements:**
- [ ] ePrescription format compliance
- [ ] Prescription refill tracking
- [ ] Medication reconciliation
- [ ] Prescription history from Kanta
- [ ] Prescriber identification (HETI number)

**Database Changes:**
```sql
ALTER TABLE medications
ADD COLUMN prescription_id VARCHAR(100), -- ePrescription ID
ADD COLUMN heti_number VARCHAR(20), -- Prescriber HETI number
ADD COLUMN refill_count INTEGER DEFAULT 0,
ADD COLUMN refill_authorized BOOLEAN DEFAULT FALSE;
```

---

### 6. Bilingual Support (Finnish/Swedish)
**Status**: ❌ Missing

**Finnish Context:**
- Official languages: Finnish and Swedish
- Many healthcare professionals speak both
- Patient-facing materials should support both

**Implementation:**
- [ ] Language selector (Finnish/Swedish/English)
- [ ] UI translation files
- [ ] Patient document generation in selected language
- [ ] Multilingual form labels
- [ ] Language preference storage

**Files to Create:**
- `app/frontend/locales/fi.json` - Finnish translations
- `app/frontend/locales/sv.json` - Swedish translations
- `app/frontend/lib/i18n.ts` - Internationalization setup

---

### 7. European Health Insurance Card (EHIC) Support
**Status**: ❌ Missing

**For EU/EEA Patients:**
- Temporary visitors from EU/EEA countries
- EHIC verification
- Appropriate billing

**Implementation:**
- [ ] EHIC number field
- [ ] EHIC validation
- [ ] EU country code support
- [ ] Temporary patient flag
- [ ] EHIC expiration tracking

**Database Changes:**
```sql
ALTER TABLE patients
ADD COLUMN ehic_number VARCHAR(20),
ADD COLUMN ehic_country_code VARCHAR(3),
ADD COLUMN ehic_expiry_date DATE,
ADD COLUMN is_temporary_visitor BOOLEAN DEFAULT FALSE;
```

---

### 8. Finnish Healthcare Workflow Adaptations

#### 8.1 Municipality-Based Care
- [ ] Municipality registration verification
- [ ] Primary care center assignment
- [ ] Referral system (terveyskeskus → specialist)

#### 8.2 Finnish Medical Terminology
- [ ] ICD-10-FI codes (Finnish version of ICD-10)
- [ ] ATC codes for medications (already common)
- [ ] Finnish medical terminology database

#### 8.3 Visit Types (Finnish Context)
- [ ] Terveyskeskus visit (primary care)
- [ ] Specialist consultation
- [ ] Emergency department (päivystys)
- [ ] Home visit (kotikäynti)
- [ ] Telemedicine consultation

---

### 9. Finnish Data Protection Compliance

**Requirements:**
- [ ] GDPR compliance (already EU standard)
- [ ] Finnish Data Protection Act compliance
- [ ] Patient consent management
- [ ] Data retention policies
- [ ] Audit trails (already implemented)

---

### 10. OmaKanta Patient Portal Integration

**OmaKanta Features:**
- Patient access to their records
- Prescription viewing
- Lab results viewing
- Appointment booking

**Implementation:**
- [ ] Patient portal interface
- [ ] Secure patient authentication
- [ ] Read-only access to own records
- [ ] Prescription viewing
- [ ] Lab result viewing

**Files to Create:**
- `app/frontend/app/patient-portal/page.tsx`
- `app/frontend/components/patient-portal/OmaKantaView.tsx`

---

## 📋 Implementation Priority

### Phase 1: Core Finnish Features (HIGH PRIORITY)
1. ✅ Kela Card integration
2. ✅ Henkilötunnus (Finnish ID) support
3. ✅ Public/Private healthcare distinction
4. ✅ Municipality registration

### Phase 2: Integration & Standards (MEDIUM PRIORITY)
5. ✅ Kanta Services compatibility
6. ✅ HL7 FHIR standards
7. ✅ ePrescription enhancement
8. ✅ EHIC support

### Phase 3: Localization (MEDIUM PRIORITY)
9. ✅ Bilingual support (Finnish/Swedish)
10. ✅ Finnish medical terminology
11. ✅ ICD-10-FI codes

### Phase 4: Patient Portal (LOW PRIORITY)
12. ✅ OmaKanta-style patient portal
13. ✅ Patient access features

---

## 🗂️ Database Schema Updates

### Enhanced Patient Table (Finnish Fields)
```sql
ALTER TABLE patients
-- Finnish identification
ADD COLUMN henkilotunnus VARCHAR(11) UNIQUE,
ADD COLUMN kela_card_number VARCHAR(20),
ADD COLUMN date_of_birth DATE,

-- Healthcare eligibility
ADD COLUMN kela_eligible BOOLEAN DEFAULT TRUE,
ADD COLUMN municipality_code VARCHAR(10),
ADD COLUMN municipality_name VARCHAR(255),
ADD COLUMN primary_care_center VARCHAR(255),

-- International patients
ADD COLUMN ehic_number VARCHAR(20),
ADD COLUMN ehic_country_code VARCHAR(3),
ADD COLUMN ehic_expiry_date DATE,
ADD COLUMN is_temporary_visitor BOOLEAN DEFAULT FALSE,

-- Contact (Finnish format)
ADD COLUMN phone VARCHAR(20),
ADD COLUMN email VARCHAR(255),
ADD COLUMN address TEXT,
ADD COLUMN postal_code VARCHAR(10),
ADD COLUMN city VARCHAR(100);
```

### Enhanced Visit Table (Finnish Context)
```sql
ALTER TABLE visits
ADD COLUMN service_type VARCHAR(20) DEFAULT 'public',
ADD COLUMN visit_type_fi VARCHAR(50), -- terveyskeskus, erikoislääkäri, päivystys, etc.
ADD COLUMN municipality_code VARCHAR(10),
ADD COLUMN kela_reimbursement_amount DECIMAL(10,2),
ADD COLUMN referral_from VARCHAR(255),
ADD COLUMN referral_to VARCHAR(255);
```

---

## 🔧 Technical Implementation

### Backend Services

1. **Kela Service**
   - File: `app/backend/services/kela_service.py`
   - Functions:
     - Validate Kela card number
     - Check eligibility
     - Calculate reimbursements
     - Process direct reimbursements

2. **Finnish ID Validator**
   - File: `app/backend/utils/finnish_id_validator.py`
   - Functions:
     - Validate henkilötunnus format
     - Validate check digit
     - Extract birth date
     - Extract gender

3. **Kanta Service**
   - File: `app/backend/services/kanta_service.py`
   - Functions:
     - Export to Kanta format
     - Import from Kanta
     - FHIR conversion
     - Prescription integration

4. **Municipality Service**
   - File: `app/backend/services/municipality_service.py`
   - Functions:
     - Verify municipality registration
     - Get primary care center
     - Check public healthcare eligibility

### Frontend Components

1. **Kela Card Input**
   - File: `app/frontend/components/patient-registration/KelaCardInput.tsx`
   - Features: Scan/input, validation, eligibility check

2. **Henkilötunnus Input**
   - File: `app/frontend/components/patient-registration/HenkilotunnusInput.tsx`
   - Features: Format validation, auto-fill date of birth

3. **Service Type Selector**
   - File: `app/frontend/components/visits/ServiceTypeSelector.tsx`
   - Features: Public/Private selection, billing adjustment

4. **Language Selector**
   - File: `app/frontend/components/layout/LanguageSelector.tsx`
   - Features: FI/SV/EN selection, persist preference

---

## 🌍 Localization Files

### Finnish Translations
File: `app/frontend/locales/fi.json`
```json
{
  "common": {
    "patient": "Potilas",
    "doctor": "Lääkäri",
    "nurse": "Sairaanhoitaja",
    "visit": "Käynti",
    "medication": "Lääke",
    "diagnosis": "Diagnoosi"
  },
  "kela": {
    "card_number": "Kela-kortin numero",
    "eligible": "Oikeutettu",
    "reimbursement": "Korvaus"
  }
}
```

### Swedish Translations
File: `app/frontend/locales/sv.json`
```json
{
  "common": {
    "patient": "Patient",
    "doctor": "Läkare",
    "nurse": "Sjuksköterska",
    "visit": "Besök",
    "medication": "Medicin",
    "diagnosis": "Diagnos"
  }
}
```

---

## 📝 Integration Checklist

### Must Have (For Finnish Context)
- [ ] Kela Card number field and validation
- [ ] Henkilötunnus support
- [ ] Public/Private service distinction
- [ ] Municipality registration
- [ ] Finnish/Swedish language support
- [ ] Basic Kanta compatibility

### Should Have
- [ ] EHIC support
- [ ] ePrescription enhancement
- [ ] OmaKanta-style patient portal
- [ ] ICD-10-FI codes

### Nice to Have
- [ ] Full Kanta integration (requires API access)
- [ ] Real-time Kela reimbursement processing
- [ ] Municipality database integration

---

## 🔄 Migration Strategy

### Step 1: Database Updates
1. Run `scripts/create_finnish_ehr_fields.sql` (to be created)
2. Migrate existing patient data
3. Add default values for new fields

### Step 2: Backend Implementation
1. Add Finnish ID validator
2. Add Kela service (mock for research)
3. Add municipality service
4. Update patient registration API

### Step 3: Frontend Implementation
1. Add Kela card input component
2. Add henkilötunnus input
3. Add language selector
4. Update patient registration form

### Step 4: Testing
1. Test with Finnish test data
2. Validate henkilötunnus formats
3. Test bilingual interface
4. Verify Kela card validation

---

## 🎓 For PhD Research

**Emphasize:**
- System adapted to Finnish healthcare context
- Kela Card integration demonstrates real-world applicability
- Bilingual support shows internationalization
- Municipality-based care reflects Finnish public health system
- Research platform uses Finnish standards while maintaining flexibility

---

**Last Updated**: 2025-01-XX  
**Status**: Planning Complete - Ready for Implementation

