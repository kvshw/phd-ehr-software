-- SQL script to create a user directly in Supabase
-- Run this in the Supabase SQL Editor

-- Create an admin user
-- Replace 'admin@example.com' and 'your-password-here' with your desired credentials
-- The password will need to be hashed using bcrypt

-- First, you need to hash the password. You can use this Python one-liner:
-- python3 -c "from passlib.context import CryptContext; pwd = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd.hash('your-password-here'))"

-- Then insert the user:
INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'admin@example.com',
    '$2b$12$YOUR_HASHED_PASSWORD_HERE',  -- Replace with actual bcrypt hash
    'admin',
    NOW(),
    NOW()
);

-- To create a clinician user:
INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'clinician@example.com',
    '$2b$12$YOUR_HASHED_PASSWORD_HERE',  -- Replace with actual bcrypt hash
    'clinician',
    NOW(),
    NOW()
);

-- To create a researcher user:
INSERT INTO users (id, email, password_hash, role, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    'researcher@example.com',
    '$2b$12$YOUR_HASHED_PASSWORD_HERE',  -- Replace with actual bcrypt hash
    'researcher',
    NOW(),
    NOW()
);

