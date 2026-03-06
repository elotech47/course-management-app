#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | sed 's/[[:space:]]*#.*$//' | grep -v '^$' | xargs)
else
    echo -e "${RED}✗${NC} .env file not found!"
    exit 1
fi

FRONTEND_PORT=${FRONTEND_PORT:-3000}
FRONTEND_SERVICE_NAME="course-management-frontend"

echo "Restarting frontend server..."

# Stop existing frontend process
if [ -f "/tmp/${FRONTEND_SERVICE_NAME}.pid" ]; then
    OLD_PID=$(cat /tmp/${FRONTEND_SERVICE_NAME}.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Stopping existing frontend process (PID: $OLD_PID)..."
        kill $OLD_PID
        sleep 2
    fi
    rm -f /tmp/${FRONTEND_SERVICE_NAME}.pid
fi

cd frontend

# Check if dist folder exists
if [ ! -d "dist" ]; then
    echo -e "${RED}✗${NC} dist folder not found. Please run ./deploy.sh to build first."
    exit 1
fi

# Check if 'serve' is installed
if ! command -v serve &> /dev/null; then
    echo "Installing 'serve' package globally..."
    npm install -g serve
fi

# Get absolute path to dist folder
DIST_PATH=$(pwd)/dist
echo "  Serving from: $DIST_PATH"
echo "  Port: $FRONTEND_PORT"

# Start frontend server with proper cache headers
# - No cache for HTML files (to get fresh bundle references)
# - Long cache for assets (they have hashes in filenames)
nohup serve -s "$DIST_PATH" -l $FRONTEND_PORT \
  --single \
  --no-clipboard \
  > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/${FRONTEND_SERVICE_NAME}.pid

echo -e "${GREEN}✓${NC} Frontend restarted (PID: $FRONTEND_PID)"
echo ""
echo "To view logs:"
echo "  tail -f logs/frontend.log"

cd ..
