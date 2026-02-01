#!/bin/bash

echo "=========================================="
echo "Course Management App - Status"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Load .env if exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

BACKEND_PORT=${BACKEND_PORT:-8000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}

# Check backend
BACKEND_SERVICE_NAME="course-management-backend"
echo "Backend Status:"
if [ -f "/tmp/${BACKEND_SERVICE_NAME}.pid" ]; then
    BACKEND_PID=$(cat /tmp/${BACKEND_SERVICE_NAME}.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "  Status: ${GREEN}Running${NC}"
        echo "  PID: $BACKEND_PID"
        echo "  Port: $BACKEND_PORT"
        echo "  URL: http://localhost:$BACKEND_PORT"
        
        # Check if actually responding
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:$BACKEND_PORT/docs | grep -q "200"; then
            echo -e "  Health: ${GREEN}✓ Responding${NC}"
        else
            echo -e "  Health: ${YELLOW}⚠ Not responding${NC}"
        fi
    else
        echo -e "  Status: ${RED}Stopped${NC} (stale PID file)"
    fi
else
    echo -e "  Status: ${RED}Stopped${NC}"
fi

echo ""

# Check frontend
FRONTEND_SERVICE_NAME="course-management-frontend"
echo "Frontend Status:"
if [ -f "/tmp/${FRONTEND_SERVICE_NAME}.pid" ]; then
    FRONTEND_PID=$(cat /tmp/${FRONTEND_SERVICE_NAME}.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "  Status: ${GREEN}Running${NC}"
        echo "  PID: $FRONTEND_PID"
        echo "  Port: $FRONTEND_PORT"
        echo "  URL: http://localhost:$FRONTEND_PORT"
        
        # Check if actually responding
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:$FRONTEND_PORT | grep -q "200"; then
            echo -e "  Health: ${GREEN}✓ Responding${NC}"
        else
            echo -e "  Health: ${YELLOW}⚠ Not responding${NC}"
        fi
    else
        echo -e "  Status: ${RED}Stopped${NC} (stale PID file)"
    fi
else
    echo -e "  Status: ${RED}Stopped${NC}"
fi

echo ""

# Check database
echo "Database Status:"
if [ ! -z "$DATABASE_URL" ]; then
    if psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1; then
        echo -e "  Connection: ${GREEN}✓ Connected${NC}"
    else
        echo -e "  Connection: ${RED}✗ Failed${NC}"
    fi
else
    echo -e "  Configuration: ${YELLOW}⚠ DATABASE_URL not set${NC}"
fi

echo ""
