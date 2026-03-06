#!/bin/bash

set -e

echo "=========================================="
echo "Course Management App - Production Deploy"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables from .env file
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} Loading environment variables from .env file..."
    export $(grep -v '^#' .env | sed 's/[[:space:]]*#.*$//' | grep -v '^$' | xargs)
else
    echo -e "${RED}✗${NC} .env file not found!"
    echo "Please create a .env file based on env.example"
    echo "cp env.example .env"
    echo "Then edit .env with your configuration"
    exit 1
fi

# Set default ports if not specified
BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}
POSTGRES_PORT=${POSTGRES_PORT:-5432}

# Ensure logs directory exists (used by backend and frontend processes)
mkdir -p logs

echo ""
echo "Configuration:"
echo "  Backend Port:   $BACKEND_PORT"
echo "  Frontend Port:  $FRONTEND_PORT"
echo "  Database Port:  $POSTGRES_PORT"
echo ""

# Check if ports are available
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${YELLOW}⚠${NC}  Port $port is already in use by another process"
        echo "   Please either:"
        echo "   1. Stop the process using port $port, or"
        echo "   2. Change ${service}_PORT in your .env file"
        return 1
    fi
    return 0
}

echo "Checking port availability..."
PORT_CHECK_FAILED=0
check_port $BACKEND_PORT "BACKEND" || PORT_CHECK_FAILED=1
check_port $FRONTEND_PORT "FRONTEND" || PORT_CHECK_FAILED=1

if [ $PORT_CHECK_FAILED -eq 1 ]; then
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if PostgreSQL is running
echo ""
echo "Checking PostgreSQL connection..."
if ! psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${RED}✗${NC} Cannot connect to PostgreSQL"
    echo "Please ensure PostgreSQL is running and DATABASE_URL is correct"
    exit 1
fi
echo -e "${GREEN}✓${NC} PostgreSQL is accessible"

# Backend setup
echo ""
echo "=========================================="
echo "Setting up Backend"
echo "=========================================="

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing/updating Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# PostgreSQL 15+ revokes CREATE on schema public; grant to app user so create_all works
echo "Ensuring database user has schema permissions..."
DB_NAME="${POSTGRES_DB:-course_management}"
DB_USER="${POSTGRES_USER:-course_admin}"
if ! sudo -u postgres psql -d "$DB_NAME" -c "GRANT CREATE ON SCHEMA public TO $DB_USER; GRANT USAGE ON SCHEMA public TO $DB_USER; GRANT ALL ON SCHEMA public TO $DB_USER;" 2>/dev/null; then
    echo -e "${RED}✗${NC} Could not grant schema permissions (PostgreSQL 15+ restricts public schema)."
    echo "Run this once as a superuser, then run ./deploy.sh again:"
    echo "  sudo -u postgres psql -d $DB_NAME -c \"GRANT CREATE, USAGE ON SCHEMA public TO $DB_USER; GRANT ALL ON SCHEMA public TO $DB_USER;\""
    exit 1
fi

echo "Creating database tables..."
python -c "from app.db import models; from app.db.database import engine; models.Base.metadata.create_all(bind=engine)"

echo -e "${GREEN}✓${NC} Backend setup complete"

# Check if backend service file exists
BACKEND_SERVICE_NAME="course-management-backend"
if [ -f "/tmp/${BACKEND_SERVICE_NAME}.pid" ]; then
    OLD_PID=$(cat /tmp/${BACKEND_SERVICE_NAME}.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Stopping existing backend process (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
fi

echo "Starting backend server on port $BACKEND_PORT..."
nohup uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --workers 4 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > /tmp/${BACKEND_SERVICE_NAME}.pid
echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"

cd ..

# Frontend setup
echo ""
echo "=========================================="
echo "Setting up Frontend"
echo "=========================================="

cd frontend

echo "Installing/updating Node.js dependencies..."
npm install

echo "Building frontend for production..."
# Use VITE_API_URL from .env if set, otherwise default to localhost
VITE_API_URL=${VITE_API_URL:-"http://localhost:$BACKEND_PORT"}
echo "  Using API URL: $VITE_API_URL"
VITE_API_URL=$VITE_API_URL npm run build

echo -e "${GREEN}✓${NC} Frontend build complete"

# Check if frontend service is running
FRONTEND_SERVICE_NAME="course-management-frontend"
if [ -f "/tmp/${FRONTEND_SERVICE_NAME}.pid" ]; then
    OLD_PID=$(cat /tmp/${FRONTEND_SERVICE_NAME}.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Stopping existing frontend process (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
fi

# Serve production build using vite preview (lightweight, built-in)
echo "Starting frontend server on port $FRONTEND_PORT..."

# Verify dist folder exists (vite preview serves from dist)
if [ ! -d "dist" ]; then
    echo -e "${RED}✗${NC} dist folder not found"
    echo "Please run the build first"
    exit 1
fi
echo "  Serving from: $(pwd)/dist (vite preview)"

nohup npm run preview -- --port $FRONTEND_PORT --host 0.0.0.0 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/${FRONTEND_SERVICE_NAME}.pid
echo -e "${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"

cd ..

# Create logs directory if it doesn't exist
mkdir -p logs

echo ""
echo "=========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Application URLs:"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  Backend:  http://localhost:$BACKEND_PORT"
echo "  API Docs: http://localhost:$BACKEND_PORT/docs"
echo ""
echo "Process IDs:"
echo "  Backend:  $BACKEND_PID (log: logs/backend.log)"
echo "  Frontend: $FRONTEND_PID (log: logs/frontend.log)"
echo ""
echo "To stop the application, run:"
echo "  ./deploy-stop.sh"
echo ""
echo "To view logs:"
echo "  tail -f logs/backend.log"
echo "  tail -f logs/frontend.log"
echo ""
