# Database Migration Order

## ⚠️ Important: Run Migrations in This Order

To avoid errors, run the SQL scripts in this specific order:

### Step 1: Basic EHR Tables (If not already done)
**File**: `scripts/create_ehr_tables.sql`
- Creates: clinical_notes, problems, medications, allergies
- Adds history fields to patients table
- **Run this FIRST** if you haven't already

### Step 2: Comprehensive EHR Enhancements (Optional)
**File**: `scripts/create_ehr_enhancements.sql`
- Creates: visits, tasks, alerts, clinical_decisions, care_plans, reports
- Enhances: users, patients, adaptations tables
- **Run this if you want full EHR features**

### Step 3: Finnish EHR Fields (RECOMMENDED - Use This One!)
**File**: `scripts/create_all_finnish_ehr_tables.sql` ⭐
- **This is the COMPLETE script** that creates everything needed
- Creates visits table if it doesn't exist
- Adds all Finnish-specific fields
- Creates Kela reimbursements, municipalities, language preferences
- **Use this script for Finnish features**

### Alternative: Just Finnish Fields (If tables already exist)
**File**: `scripts/create_finnish_ehr_fields.sql`
- Only adds Finnish fields to existing tables
- **Will fail if visits table doesn't exist**
- Use only if you've already run create_ehr_enhancements.sql

---

## 🚀 Quick Start (Finnish Features)

**If you want Finnish features and haven't run any migrations:**

1. Run: `scripts/create_ehr_tables.sql` (basic tables)
2. Run: `scripts/create_all_finnish_ehr_tables.sql` (Finnish features + visits)

**OR (simpler):**

1. Run: `scripts/create_all_finnish_ehr_tables.sql` (creates everything)

---

## ✅ Verification

After running migrations, verify tables exist:

```sql
-- Check if visits table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_name IN ('visits', 'kela_reimbursements', 'municipalities');

-- Check if Finnish fields were added
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'patients' 
AND column_name IN ('henkilotunnus', 'kela_card_number', 'municipality_code');
```

---

## 🔧 Troubleshooting

### Error: "relation 'visits' does not exist"
**Solution**: Run `scripts/create_all_finnish_ehr_tables.sql` which creates the visits table first.

### Error: "relation 'medications' does not exist"
**Solution**: Run `scripts/create_ehr_tables.sql` first, then the Finnish migration.

### Error: "constraint already exists"
**Solution**: This is OK - the script uses `IF NOT EXISTS` and `DROP IF EXISTS` to handle this.

---

**Last Updated**: 2025-01-XX

