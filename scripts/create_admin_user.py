#!/usr/bin/env python3
"""
Script to create the first admin user
Run this to create an initial admin user for the system
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "app" / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.user import User
from core.security import get_password_hash
from core.config import settings
import uuid

def create_admin_user(email: str, password: str):
    """Create an admin user"""
    if not settings.DATABASE_URL:
        print("ERROR: DATABASE_URL not set in environment variables")
        print("Please set DATABASE_URL in your .env file")
        return False
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if user already exists
        from sqlalchemy import select
        stmt = select(User).where(User.email == email)
        existing_user = db.execute(stmt).scalar_one_or_none()
        
        if existing_user:
            print(f"User with email {email} already exists!")
            return False
        
        # Create admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=hashed_password,
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Role: admin")
        print(f"   ID: {admin_user.id}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to create user: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--password", required=True, help="Admin password")
    
    args = parser.parse_args()
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = create_admin_user(args.email, args.password)
    sys.exit(0 if success else 1)

