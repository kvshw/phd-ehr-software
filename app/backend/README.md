# Backend API - EHR Research Platform

FastAPI backend for the Self-Adaptive AI-Assisted EHR Research Platform.

## Structure

```
backend/
├── main.py                 # Application entry point
├── core/                   # Core functionality
│   ├── config.py          # Configuration settings
│   ├── database.py        # Database connection
│   ├── security.py        # JWT and password hashing
│   └── dependencies.py    # Dependency injection
├── models/                 # SQLAlchemy models
│   └── user.py            # User model
├── schemas/                # Pydantic schemas
│   └── auth.py            # Authentication schemas
├── services/               # Business logic
│   └── auth_service.py    # Authentication service
└── api/                    # API routes
    └── routes/
        └── auth.py        # Authentication endpoints
```

## Authentication Endpoints

### POST `/api/v1/auth/login`
Login with email and password. Returns JWT access and refresh tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

### POST `/api/v1/auth/register` (Admin only)
Create a new user. Requires admin authentication.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "role": "clinician"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "clinician"
}
```

### POST `/api/v1/auth/refresh`
Refresh access token using refresh token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

### GET `/api/v1/auth/me`
Get current user information. Requires authentication.

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "clinician"
}
```

## Role-Based Access Control

Three user roles:
- **clinician**: Access to patient dashboard
- **researcher**: Access to analytics dashboard
- **admin**: Full system access, can create users

### Using RBAC in Routes

```python
from core.dependencies import require_admin, require_clinician, require_researcher

@router.get("/admin-only")
async def admin_endpoint(current_user = Depends(require_admin)):
    # Only admins can access
    pass

@router.get("/clinician-endpoint")
async def clinician_endpoint(current_user = Depends(require_clinician)):
    # Clinicians and admins can access
    pass
```

## Environment Variables

Required environment variables (set in `.env`):
- `DATABASE_URL`: PostgreSQL connection string (from Supabase)
- `JWT_SECRET_KEY`: Secret key for JWT signing
- `JWT_ALGORITHM`: JWT algorithm (default: HS256)
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key

## Running

```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

