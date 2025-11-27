-- Fix the admin password hash
-- The password "admin@123" needs to be properly hashed with bcrypt

-- First, you need to generate the hash. Use one of these methods:

-- Method 1: If you have Python with passlib installed:
-- python3 -c "from passlib.context import CryptContext; pwd = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd.hash('admin@123'))"

-- Method 2: Use an online bcrypt generator (search "bcrypt hash generator")
-- Password: admin@123
-- Rounds: 12 (default)

-- Method 3: Install bcrypt and run:
-- pip install bcrypt
-- python3 -c "import bcrypt; print(bcrypt.hashpw(b'admin@123', bcrypt.gensalt()).decode())"

-- Then update the user with the hash:
UPDATE users 
SET password_hash = '$2b$12$YOUR_GENERATED_HASH_HERE'
WHERE email = 'admin@ehr.com';

-- To verify:
SELECT email, role, LEFT(password_hash, 20) as hash_preview FROM users WHERE email = 'admin@ehr.com';

