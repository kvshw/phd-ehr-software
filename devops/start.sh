#!/bin/bash
# Quick start script for Docker Compose

set -e

echo "🚀 Starting EHR Platform with Docker Compose..."
echo ""

# Check if .env file exists
if [ ! -f "../.env" ]; then
    echo "⚠️  Warning: .env file not found in project root"
    echo "   Make sure to create .env file with required variables"
    echo ""
fi

# Check for docker compose command (V2) or docker-compose (V1)
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ Error: docker compose or docker-compose not found"
    echo "   Please install Docker Desktop or Docker Compose"
    exit 1
fi

# Start services
echo "📦 Starting all services..."
$DOCKER_COMPOSE up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check backend health
echo "🔍 Checking backend health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check logs with: $DOCKER_COMPOSE logs backend"
        exit 1
    fi
    echo "   Waiting for backend... ($i/30)"
    sleep 2
done

echo ""
echo "✅ All services started!"
echo ""
echo "📍 Services:"
echo "   - Backend API:    http://localhost:8000"
echo "   - Frontend:       http://localhost:3000"
echo "   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "📋 Useful commands:"
echo "   - View logs:      $DOCKER_COMPOSE logs -f [service-name]"
echo "   - Stop services:  $DOCKER_COMPOSE down"
echo "   - Restart:        $DOCKER_COMPOSE restart [service-name]"
echo ""

