# Login Troubleshooting Guide

## Issue: "Login failed. Please check your credentials."

### Quick Fix Steps

1. **Check if backend is running:**
   ```bash
   docker compose -f devops/docker-compose.yml ps backend
   ```

2. **Check backend logs for errors:**
   ```bash
   docker compose -f devops/docker-compose.yml logs backend --tail 50
   ```

3. **Verify you have a user account:**
   - If you don't have a user, create one using the script below

## Creating a User Account

### Option 1: Create Admin User (Recommended)

```bash
# Make sure you're in the project root
cd /Users/kavee/Projects/PhD/Medical\ EHR\ Software

# Create an admin user
python3 scripts/create_admin_user.py --email admin@ehr.com --password admin@123
```

### Option 2: Create via Supabase SQL Editor

1. Go to: https://supabase.com/dashboard/project/gzlfyxwsffubglatvcau/editor
2. Run this SQL (replace password hash):

```sql
-- First, generate password hash using Python:
-- python3 -c "from app.backend.core.security import get_password_hash; print(get_password_hash('your-password'))"

INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'admin@ehr.com',
    '$2b$12$YOUR_HASHED_PASSWORD_HERE',  -- Replace with actual hash
    'admin',
    NOW(),
    NOW()
)
ON CONFLICT (email) DO NOTHING;
```

### Option 3: Check Existing Users

Run this in Supabase SQL Editor to see all users:

```sql
SELECT id, email, role, created_at 
FROM users 
ORDER BY created_at DESC;
```

## Test Credentials

According to `START_BACKEND.md`:
- **Email:** `admin@ehr.com`
- **Password:** `admin@123`

**If these don't work**, the user might not exist. Create it using Option 1 above.

## Common Issues

### 1. Backend Not Running
- **Symptom:** Network error or connection refused
- **Fix:** `docker compose -f devops/docker-compose.yml restart backend`

### 2. Database Connection Error
- **Symptom:** Backend logs show database connection errors
- **Fix:** Check `.env` file has correct `DATABASE_URL` with password

### 3. User Doesn't Exist
- **Symptom:** "Incorrect email or password" error
- **Fix:** Create user using `create_admin_user.py` script

### 4. Password Hash Mismatch
- **Symptom:** Login fails even with correct password
- **Fix:** Recreate user with script (it uses correct hashing)

### 5. Role Validation Error
- **Symptom:** "This account does not have [role] access"
- **Fix:** Make sure you selected the correct role on login page, or create a user with that role

## Creating Different Role Users

### Create Clinician User
```bash
python3 scripts/create_admin_user.py --email clinician@ehr.com --password clinician@123
# Then update role in database:
# UPDATE users SET role = 'clinician' WHERE email = 'clinician@ehr.com';
```

### Create Researcher User
```bash
python3 scripts/create_admin_user.py --email researcher@ehr.com --password researcher@123
# Then update role in database:
# UPDATE users SET role = 'researcher' WHERE email = 'researcher@ehr.com';
```

## Verify Login Works

After creating a user, test the login:

1. Go to: http://localhost:3000/login
2. Select role (if using role-based login)
3. Enter email and password
4. Should redirect to appropriate dashboard

## Still Having Issues?

1. **Check browser console** for frontend errors
2. **Check backend logs** for authentication errors
3. **Verify database connection** in `.env` file
4. **Test API directly:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@ehr.com", "password": "admin@123"}'
   ```

