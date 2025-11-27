# Scripts Directory

Utility scripts for the EHR Research Platform.

## Creating Users

### Option 1: Python Script (Recommended)

Use the Python script to create an admin user:

```bash
cd scripts
python3 create_admin_user.py --email admin@example.com --password your-secure-password
```

**Requirements:**
- Backend dependencies installed
- DATABASE_URL set in .env file
- Access to the Supabase database

### Option 2: Supabase SQL Editor

1. Go to your Supabase project: https://supabase.com/dashboard/project/gzlfyxwsffubglatvcau
2. Navigate to SQL Editor
3. First, generate a password hash:
```bash
   python3 -c "from passlib.context import CryptContext; pwd = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd.hash('your-password'))"
   ```
4. Use the SQL from `create_user.sql` and replace the hash

### Option 3: API Endpoint (After First Admin is Created)

Once you have an admin user, you can use the API:

```bash
# Login as admin first to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "your-password"}'

# Use the access_token to create new users
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "email": "clinician@example.com",
    "password": "password123",
    "role": "clinician"
  }'
```

## Quick Start

1. **Create first admin user:**
```bash
   python3 scripts/create_admin_user.py --email admin@test.com --password admin123
   ```

2. **Login at:** http://localhost:3000/login

3. **Create more users via API** (after logging in as admin)
