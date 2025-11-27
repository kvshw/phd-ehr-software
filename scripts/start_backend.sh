#!/bin/bash
# Script to start the backend server

PROJECT_ROOT="$(dirname "$0")/.."
cd "$PROJECT_ROOT/app/backend"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

# Set PYTHONPATH so imports work
export PYTHONPATH="$PROJECT_ROOT/app/backend:$PYTHONPATH"

# Load environment variables from project root
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | xargs)
fi

# Start the server
echo "Starting backend server on http://localhost:8000"
echo "Press Ctrl+C to stop"
uvicorn main:app --reload --host 0.0.0.0 --port 8000

