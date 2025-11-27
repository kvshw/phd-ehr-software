# Technical Context

## Technology Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **State Management**: Zustand or Context API
- **HTTP Client**: Axios
- **Image Viewer**: Custom or library (e.g., react-image-viewer)

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Authentication**: JWT (python-jose, passlib)
- **Database ORM**: SQLAlchemy
- **Validation**: Pydantic
- **CORS**: FastAPI CORS middleware

### Database
- **Type**: Supabase (PostgreSQL 17.6.1)
- **Project ID**: gzlfyxwsffubglatvcau
- **Region**: us-east-1
- **ORM**: SQLAlchemy (backend) / Supabase Client (frontend)
- **Migrations**: Supabase MCP / Alembic (for direct SQL)
- **Connection**: Supabase REST API or direct PostgreSQL connection

### Storage
- **Object Storage**: MinIO (S3-compatible) or AWS S3
- **Purpose**: Medical imaging files

### Model Services
- **Language**: Python 3.11+
- **Framework**: FastAPI for API endpoints
- **ML Libraries**: As needed (scikit-learn, PyTorch, TensorFlow)
- **Communication**: HTTP REST APIs

### DevOps
- **Containerization**: Docker
- **Orchestration**: docker-compose
- **Services**: Frontend, Backend, Database, MinIO, Model Services

## Development Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account (project already created: gzlfyxwsffubglatvcau)
- Docker & Docker Compose (for local services like MinIO)

### Environment Variables
```
# Supabase
SUPABASE_URL=https://gzlfyxwsffubglatvcau.supabase.co
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.gzlfyxwsffubglatvcau.supabase.co:5432/postgres

# Backend
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
BACKEND_PORT=8000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://gzlfyxwsffubglatvcau.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...

# MinIO/S3
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...
```

## Technical Constraints

1. **No Real PHI**: All data must be synthetic
2. **Desktop Only**: No mobile/responsive requirements for MVP
3. **Research Focus**: Performance optimization secondary to transparency
4. **Versioning**: Model services must support version tracking
5. **Logging**: Comprehensive logging for research analysis

## Dependencies

### Backend Core
- fastapi
- uvicorn
- sqlalchemy
- alembic
- python-jose[cryptography]
- passlib[bcrypt]
- pydantic
- python-multipart
- boto3 (for S3/MinIO)

### Frontend Core
- next
- react
- react-dom
- typescript
- tailwindcss
- axios
- zustand (or react context)

## API Design Patterns

### RESTful Endpoints
- `/api/v1/patients` - Patient CRUD
- `/api/v1/vitals` - Vital signs
- `/api/v1/labs` - Lab results
- `/api/v1/imaging` - Image management
- `/api/v1/ai/*` - AI service routing
- `/api/v1/adapt/*` - Adaptation engine
- `/api/v1/logs/*` - Research logging

### Authentication
- JWT tokens in Authorization header
- Token refresh mechanism
- Role-based endpoint access

