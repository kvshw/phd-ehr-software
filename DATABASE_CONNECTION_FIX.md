# Database Connection Issue - DNS Resolution Problem

## Problem
The hostname `db.gzlfyxwsffubglatvcau.supabase.co` cannot be resolved by DNS.

## Solutions

### Option 1: Get Connection String from Supabase Dashboard (RECOMMENDED)

1. Go to: https://supabase.com/dashboard/project/gzlfyxwsffubglatvcau/settings/database
2. Scroll to **"Connection string"** section
3. Select **"URI"** format (not "Connection pooling")
4. Copy the connection string - it should look like:
   ```
   postgresql://postgres.[PROJECT_REF]:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with your actual password `Kavishwa@123`
6. **IMPORTANT**: URL-encode the `@` symbol in the password as `%40`
   - So `Kavishwa@123` becomes `Kavishwa%40123`
7. Update `DATABASE_URL` in `.env` file

### Option 2: Use Connection Pooling (Alternative)

If direct connection doesn't work, try the connection pooling URL:
```
postgresql://postgres.gzlfyxwsffubglatvcau:Kavishwa%40123@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### Option 3: Check Network/DNS

If DNS resolution is failing:
1. Check your internet connection
2. Try using a different DNS server (e.g., 8.8.8.8)
3. Check if your firewall is blocking the connection
4. Try from a different network

### Option 4: Use Supabase REST API (Temporary Workaround)

If PostgreSQL connection continues to fail, we can modify the backend to use Supabase REST API via the service role key instead of direct PostgreSQL connections.

## Current DATABASE_URL Format

Make sure your `.env` file has:
```env
DATABASE_URL=postgresql://postgres:Kavishwa%40123@[CORRECT-HOSTNAME]:5432/postgres
```

Where `[CORRECT-HOSTNAME]` should be obtained from the Supabase dashboard.

