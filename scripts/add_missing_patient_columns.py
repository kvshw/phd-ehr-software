#!/usr/bin/env python3
"""
Add missing patient columns to the database
Run this script to add emergency contact and other missing columns
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import database utilities
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("[ERROR] Error: DATABASE_URL not found in environment variables")
    print("   Please set DATABASE_URL in your .env file")
    sys.exit(1)

def add_missing_columns():
    """Add missing columns to patients table"""
    engine = create_engine(DATABASE_URL)
    
    sql = """
    ALTER TABLE patients
    ADD COLUMN IF NOT EXISTS emergency_contact_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS emergency_contact_phone VARCHAR(20),
    ADD COLUMN IF NOT EXISTS emergency_contact_relation VARCHAR(100),
    ADD COLUMN IF NOT EXISTS registration_status VARCHAR(50) DEFAULT 'complete',
    ADD COLUMN IF NOT EXISTS registration_completed_at TIMESTAMP WITH TIME ZONE,
    ADD COLUMN IF NOT EXISTS insurance_provider VARCHAR(255),
    ADD COLUMN IF NOT EXISTS insurance_id VARCHAR(100);
    """
    
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
        print("[SUCCESS] Successfully added missing columns to patients table")
        return True
    except Exception as e:
        print(f"[ERROR] Error adding columns: {e}")
        return False

if __name__ == "__main__":
    print("[TOOL] Adding missing patient columns...")
    if add_missing_columns():
        print("[SUCCESS] Migration complete!")
        sys.exit(0)
    else:
        print("[ERROR] Migration failed!")
        sys.exit(1)

