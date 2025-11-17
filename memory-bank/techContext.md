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
- **Type**: PostgreSQL 14+
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

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
- PostgreSQL 14+
- Docker & Docker Compose

### Environment Variables
```
# Backend
DATABASE_URL=postgresql://user:pass@localhost/ehr_db
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=...
MINIO_SECRET_KEY=...

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
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

