# Quick Start: Testing Feedback Analytics

## 🚀 Fastest Way to Test (5 minutes)

### Step 1: Generate Test Data
```bash
python3 scripts/generate_test_feedback.py --count 50 --days 30
```

### Step 2: View Analytics
Open: **http://localhost:3000/feedback/analytics**

### Step 3: Explore
- Check overview stats
- View timeline chart
- See learning events (if >10 feedback)
- Export data

---

## 📊 What You'll See

After generating 50 feedback items:
- **Total Feedback:** 50
- **Acceptance Rate:** ~55% (27-28 accepted)
- **Actions Breakdown:**
  - Accept: ~28
  - Ignore: ~15
  - Not Relevant: ~7
- **Timeline Chart:** Shows feedback over 30 days
- **Learning Events:** Will appear if you have 10+ feedback

---

## 🎯 Best Testing Strategy for PhD

### For Initial Testing:
```bash
# Small dataset to verify everything works
python3 scripts/generate_test_feedback.py --count 20 --days 7
```

### For Demo/Presentation:
```bash
# Realistic dataset
python3 scripts/generate_test_feedback.py --count 100 --days 30
```

### For Research Analysis:
```bash
# Large dataset for statistical analysis
python3 scripts/generate_test_feedback.py --count 200 --days 90
```

---

## ✅ Prerequisites

Make sure you have:
1. ✅ Database tables created (run `scripts/create_feedback_tables.sql` in Supabase)
2. ✅ At least 1 clinician user
3. ✅ At least 1 patient
4. ✅ Some suggestions (script will create sample ones if needed)

---

## 🎬 Demo Script for Professor

1. **Show empty state** (if no feedback yet)
2. **Generate test data:** `python3 scripts/generate_test_feedback.py --count 50`
3. **Refresh analytics page**
4. **Explain:**
   - "This shows how clinicians interact with AI suggestions"
   - "55% acceptance rate indicates good AI performance"
   - "The system learns from feedback and adjusts confidence"
5. **Show learning events** (if triggered)
6. **Export data** to show research capabilities

---

## 📝 Notes

- Test data is **realistic** but **synthetic**
- Distribution matches real-world patterns
- Perfect for PhD research demonstration
- All data can be exported for analysis

**Ready to test!** 🎉

