#!/usr/bin/env python3
"""
Quick script to hash a password
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "app" / "backend"
sys.path.insert(0, str(backend_path))

from core.security import get_password_hash

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 hash_password.py <password>")
        sys.exit(1)
    
    password = sys.argv[1]
    hashed = get_password_hash(password)
    print(f"Password: {password}")
    print(f"Hash: {hashed}")
    print(f"\nSQL Update Command:")
    print(f"UPDATE users SET password_hash = '{hashed}' WHERE email = 'admin@ehr.com';")

