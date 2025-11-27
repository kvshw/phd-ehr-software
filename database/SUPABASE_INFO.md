# Supabase Database Information

## Project Details
- **Project Name**: ehr-research-platform
- **Project ID**: gzlfyxwsffubglatvcau
- **Organization**: PhD (nichfiwbjsrzhdrcoopx)
- **Region**: us-east-1
- **Status**: ACTIVE_HEALTHY

## Connection Information
- **Supabase URL**: https://gzlfyxwsffubglatvcau.supabase.co
- **Database Host**: db.gzlfyxwsffubglatvcau.supabase.co
- **Database Version**: PostgreSQL 17.6.1.048

## API Keys
- **Anon Key**: Available in `.env.example`
- **Service Role Key**: Get from Supabase Dashboard (Settings > API)

## Database Schema

### Tables Created
1. **users** - User authentication and roles
2. **patients** - Patient records
3. **vitals** - Time-series vital signs
4. **labs** - Laboratory results
5. **imaging** - Medical imaging metadata
6. **suggestions** - AI-generated suggestions
7. **user_actions** - User behavior logging
8. **adaptations** - MAPE-K adaptation plans

### Migrations Applied
All migrations have been applied via Supabase MCP:
- `create_users_table`
- `create_patients_table`
- `create_vitals_table`
- `create_labs_table`
- `create_imaging_table`
- `create_suggestions_table`
- `create_user_actions_table`
- `create_adaptations_table`

## TypeScript Types
TypeScript types have been generated and saved to:
- `app/frontend/lib/supabase-types.ts`

## Accessing the Database

### Via Supabase Client (Recommended)
```typescript
import { createClient } from '@supabase/supabase-js'
import { Database } from './lib/supabase-types'

const supabase = createClient<Database>(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)
```

### Via Direct PostgreSQL Connection
Use the connection string in `.env.example` for direct database access (e.g., for migrations, admin tools).

## Next Steps
1. Get Service Role Key from Supabase Dashboard
2. Update `.env` file with actual credentials
3. Configure Row Level Security (RLS) policies as needed
4. Set up database backups

