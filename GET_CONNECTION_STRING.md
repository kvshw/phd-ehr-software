# How to Get the Correct Database Connection String

## Steps:

1. **Go to Supabase Dashboard:**
   - https://supabase.com/dashboard/project/gzlfyxwsffubglatvcau/settings/database

2. **Click "Connect to your project" button**

3. **In the modal that opens:**
   - Make sure "Type" is set to **"URI"**
   - Make sure "Source" is set to **"Primary Database"**
   - **IMPORTANT**: Change "Method" from "Direct connection" to **"Session pooler"**

4. **Copy the connection string** from the text area
   - It should look like: `postgresql://postgres.gzlfyxwsffubglatvcau:[YOUR_PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres`

5. **Replace `[YOUR_PASSWORD]` with your actual password:**
   - Your password is: `Kavishwa@123`
   - **URL-encode the `@` symbol** as `%40`
   - So it becomes: `Kavishwa%40123`

6. **Update your `.env` file:**
   ```env
   DATABASE_URL=postgresql://postgres.gzlfyxwsffubglatvcau:Kavishwa%40123@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

7. **Restart the backend:**
   ```bash
   pkill -f "uvicorn main:app"
   cd app/backend
   source .venv/bin/activate
   PYTHONPATH=. uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Why Session Pooler?

The direct connection shows "Not IPv4 compatible" warning. The Session Pooler works with IPv4 networks and is the recommended method for most applications.

