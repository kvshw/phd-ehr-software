# Starting the Backend Server

## Quick Start

1. **Get Database Password from Supabase:**
   - Go to: https://supabase.com/dashboard/project/gzlfyxwsffubglatvcau/settings/database
   - Copy the database password
   - Update `.env` file: Replace `[YOUR-PASSWORD]` in `DATABASE_URL` with your actual password

2. **Start the Backend:**
   ```bash
   cd app/backend
   source .venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Or use Docker:**
   ```bash
   cd devops
   docker compose up backend
   ```

## Login Credentials

- **Email:** `admin@ehr.com`
- **Password:** `admin@123`

The password hash has been fixed in the database!

