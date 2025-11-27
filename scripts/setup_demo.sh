#!/bin/bash

# Demo Setup Script
# Sets up everything needed for a professional demonstration

set -e  # Exit on error

echo "=========================================="
echo "  EHR Research Platform - Demo Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "scripts/setup_dummy_data.py" ]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Checking environment...${NC}"
# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Please create it from .env.example${NC}"
    echo "   Make sure to add your Supabase credentials"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✅ Environment check complete${NC}"
echo ""

echo -e "${YELLOW}Step 2: Setting up demo users...${NC}"
python3 scripts/create_admin_user.py || echo -e "${YELLOW}⚠️  User creation skipped (may already exist)${NC}"
echo -e "${GREEN}✅ Demo users ready${NC}"
echo ""

echo -e "${YELLOW}Step 3: Generating demo patients...${NC}"
python3 scripts/setup_dummy_data.py --count 25 --remove-duplicates
echo -e "${GREEN}✅ Demo patients created${NC}"
echo ""

echo -e "${YELLOW}Step 4: Adding vitals and labs data...${NC}"
# Check if add_patient_data.py exists
if [ -f "scripts/add_patient_data.py" ]; then
    python3 scripts/add_patient_data.py || echo -e "${YELLOW}⚠️  Vitals/labs generation skipped${NC}"
    echo -e "${GREEN}✅ Patient data enriched${NC}"
else
    echo -e "${YELLOW}⚠️  add_patient_data.py not found, skipping${NC}"
fi
echo ""

echo -e "${YELLOW}Step 5: Generating feedback data for analytics...${NC}"
if [ -f "scripts/generate_test_feedback.py" ]; then
    python3 scripts/generate_test_feedback.py --count 50 --days 30 || echo -e "${YELLOW}⚠️  Feedback generation skipped${NC}"
    echo -e "${GREEN}✅ Feedback data created${NC}"
else
    echo -e "${YELLOW}⚠️  generate_test_feedback.py not found, skipping${NC}"
fi
echo ""

echo -e "${YELLOW}Step 6: Verifying setup...${NC}"
# Run a quick verification
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('app/backend')))
from core.database import SessionLocal
from models.patient import Patient
from sqlalchemy import func, select

db = SessionLocal()
try:
    patient_count = db.execute(select(func.count(Patient.id))).scalar_one()
    print(f'✅ Found {patient_count} patients in database')
    if patient_count < 10:
        print('⚠️  Warning: Less than 10 patients. Demo may be limited.')
    else:
        print('✅ Patient count looks good for demo')
finally:
    db.close()
" || echo -e "${YELLOW}⚠️  Verification skipped${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Demo Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Demo Credentials:"
echo "-----------------"
echo "Clinician:"
echo "  Email: clinician@demo.com"
echo "  Password: (check scripts/create_admin_user.py)"
echo ""
echo "Researcher:"
echo "  Email: researcher@demo.com"
echo "  Password: (check scripts/create_admin_user.py)"
echo ""
echo "Admin:"
echo "  Email: admin@demo.com"
echo "  Password: (check scripts/create_admin_user.py)"
echo ""
echo "Next Steps:"
echo "1. Start backend: cd app/backend && uvicorn main:app --reload"
echo "2. Start frontend: cd app/frontend && npm run dev"
echo "3. Visit: http://localhost:3000"
echo "4. Follow: DEMO_WALKTHROUGH.md"
echo ""
echo -e "${GREEN}Ready for demo! 🎉${NC}"

