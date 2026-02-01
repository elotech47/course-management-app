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
    export $(cat .env | grep -v '^#' | xargs)
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

echo "Running database migrations..."
alembic upgrade head

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
VITE_API_URL="http://localhost:$BACKEND_PORT" npm run build

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

# Serve frontend with a simple HTTP server
echo "Starting frontend server on port $FRONTEND_PORT..."

# Check if 'serve' is installed
if ! command -v serve &> /dev/null; then
    echo "Installing 'serve' package globally..."
    npm install -g serve
fi

nohup serve -s dist -l $FRONTEND_PORT > ../logs/frontend.log 2>&1 &
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
