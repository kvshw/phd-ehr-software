# Docker Configuration

This directory contains Docker configuration files for the EHR Research Platform.

## Files

- `docker-compose.yml` - Orchestrates all services
- `Dockerfile.frontend` - Next.js frontend container
- `Dockerfile.backend` - FastAPI backend container
- `Dockerfile.model` - Base image for model services
- `.dockerignore` - Files to exclude from Docker builds

## Services

### MinIO (Object Storage)
- Port: 9000 (API), 9001 (Console)
- Default credentials: minioadmin/minioadmin
- Bucket: ehr-images (auto-created)

### Backend API
- Port: 8000
- FastAPI application
- Connects to Supabase database

### Frontend
- Port: 3000
- Next.js application
- Development mode with hot reload

### Model Services
- Vital Risk Service: Port 8001
- Image Analysis Service: Port 8002
- Diagnosis Helper Service: Port 8003

## Usage

### Quick Start (Recommended)
```bash
cd devops
./start.sh
```

This script will:
- Start all services
- Wait for backend to be healthy
- Show service URLs and useful commands

### Start all services manually
```bash
cd devops
docker compose up -d
# or (if using Docker Compose V1)
docker-compose up -d
```

### Start specific services
```bash
docker compose up -d minio backend frontend
```

### View logs
```bash
docker compose logs -f [service-name]
```

### Stop services
```bash
docker compose down
```

### Rebuild containers
```bash
docker compose build --no-cache
docker compose up -d
```

### Access MinIO Console
- URL: http://localhost:9001
- Username: minioadmin
- Password: minioadmin

## Environment Variables

Make sure to create a `.env` file in the project root with all required variables (see `.env.example`).

## Network

All services are connected via the `ehr-network` bridge network, allowing them to communicate using service names as hostnames.

## Volumes

- `minio-data`: Persistent storage for MinIO object storage

## Development vs Production

The Dockerfiles are configured for development with hot reload enabled. For production:
1. Use multi-stage builds
2. Disable hot reload
3. Use production-optimized base images
4. Add health checks
5. Configure proper logging

