# Create Clinician Account - Quick Guide

## You're Right - No Default Clinician Account!

There is **no default clinician account** created automatically. You need to create one.

---

## Quick Method: Create Clinician Account

### **Step 1: Create User (as Admin)**

Run this command from the **project root directory**:

```bash
cd /Users/kavee/Projects/PhD/Medical\ EHR\ Software

# Create a clinician user
python3 scripts/create_admin_user.py --email clinician@ehr.com --password clinician@123
```

**Note:** This script creates an "admin" user by default, but we'll change the role in the next step.

### **Step 2: Change Role to Clinician**

After creating the user, update the role in Supabase:

1. **Go to Supabase SQL Editor:**
   - https://supabase.com/dashboard/project/gzlfyxwsffubglatvcau/editor

2. **Run this SQL:**
   ```sql
   UPDATE users 
   SET role = 'clinician' 
   WHERE email = 'clinician@ehr.com';
   ```

3. **Verify it worked:**
   ```sql
   SELECT email, role FROM users WHERE email = 'clinician@ehr.com';
   ```

### **Step 3: Login**

Now you can login with:
- **Email:** `clinician@ehr.com`
- **Password:** `clinician@123`
- **Role:** Select "Clinician" on the login page

---

## Alternative: Create Directly via SQL

If you prefer to create the clinician user directly:

### **Step 1: Generate Password Hash**

```bash
cd /Users/kavee/Projects/PhD/Medical\ EHR\ Software

# Generate password hash
python3 -c "import sys; sys.path.insert(0, 'app/backend'); from core.security import get_password_hash; print(get_password_hash('clinician@123'))"
```

### **Step 2: Insert User in Supabase**

1. Go to: https://supabase.com/dashboard/project/gzlfyxwsffubglatvcau/editor

2. Run this SQL (replace `YOUR_HASH_HERE` with the hash from Step 1):
   ```sql
   INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
   VALUES (
       gen_random_uuid(),
       'clinician@ehr.com',
       'YOUR_HASH_HERE',  -- Replace with hash from Step 1
       'clinician',
       NOW(),
       NOW()
   )
   ON CONFLICT (email) DO NOTHING;
   ```

---

## Check Existing Users

To see what users already exist:

1. **Go to Supabase SQL Editor:**
   - https://supabase.com/dashboard/project/gzlfyxwsffubglatvcau/editor

2. **Run this SQL:**
   ```sql
   SELECT id, email, role, created_at 
   FROM users 
   ORDER BY created_at DESC;
   ```

This will show you all existing users and their roles.

---

## Recommended: Create All Test Users

Create accounts for all three roles:

```bash
cd /Users/kavee/Projects/PhD/Medical\ EHR\ Software

# Create Admin
python3 scripts/create_admin_user.py --email admin@ehr.com --password admin@123

# Create Clinician
python3 scripts/create_admin_user.py --email clinician@ehr.com --password clinician@123

# Create Researcher
python3 scripts/create_admin_user.py --email researcher@ehr.com --password researcher@123
```

Then update roles in Supabase:

```sql
-- Update clinician role
UPDATE users SET role = 'clinician' WHERE email = 'clinician@ehr.com';

-- Update researcher role
UPDATE users SET role = 'researcher' WHERE email = 'researcher@ehr.com';

-- Admin is already correct, no need to update
```

---

## Test Credentials Summary

After creating users, you'll have:

| Role | Email | Password |
|------|-------|----------|
| **Admin** | `admin@ehr.com` | `admin@123` |
| **Clinician** | `clinician@ehr.com` | `clinician@123` |
| **Researcher** | `researcher@ehr.com` | `researcher@123` |

---

## Quick Commands (Copy-Paste)

**Create clinician account:**

```bash
# 1. Create user
cd /Users/kavee/Projects/PhD/Medical\ EHR\ Software
python3 scripts/create_admin_user.py --email clinician@ehr.com --password clinician@123

# 2. Update role in Supabase SQL Editor:
# UPDATE users SET role = 'clinician' WHERE email = 'clinician@ehr.com';

# 3. Login at: http://localhost:3000/login
#    Email: clinician@ehr.com
#    Password: clinician@123
#    Role: Select "Clinician"
```

---

## Troubleshooting

### **"User already exists" error:**
- The user was already created
- Just update the role: `UPDATE users SET role = 'clinician' WHERE email = 'clinician@ehr.com';`

### **"Module not found" error:**
- Make sure you're in the project root directory
- Make sure backend dependencies are installed

### **Login still fails:**
- Check that the role was updated correctly
- Verify password is correct
- Make sure you select "Clinician" role on the login page

---

**That's it!** Once you create the clinician account, you can login and test the hybrid AI models! 🚀

