#!/bin/bash

echo "=========================================="
echo "Stopping Course Management App"
echo "=========================================="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Stop backend
BACKEND_SERVICE_NAME="course-management-backend"
if [ -f "/tmp/${BACKEND_SERVICE_NAME}.pid" ]; then
    BACKEND_PID=$(cat /tmp/${BACKEND_SERVICE_NAME}.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        sleep 2
        
        # Force kill if still running
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "Force stopping backend..."
            kill -9 $BACKEND_PID
        fi
        
        rm /tmp/${BACKEND_SERVICE_NAME}.pid
        echo -e "${GREEN}✓${NC} Backend stopped"
    else
        echo -e "${YELLOW}⚠${NC}  Backend process not found"
        rm /tmp/${BACKEND_SERVICE_NAME}.pid
    fi
else
    echo -e "${YELLOW}⚠${NC}  Backend PID file not found"
fi

# Stop frontend
FRONTEND_SERVICE_NAME="course-management-frontend"
if [ -f "/tmp/${FRONTEND_SERVICE_NAME}.pid" ]; then
    FRONTEND_PID=$(cat /tmp/${FRONTEND_SERVICE_NAME}.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        
        # Force kill if still running
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "Force stopping frontend..."
            kill -9 $FRONTEND_PID
        fi
        
        rm /tmp/${FRONTEND_SERVICE_NAME}.pid
        echo -e "${GREEN}✓${NC} Frontend stopped"
    else
        echo -e "${YELLOW}⚠${NC}  Frontend process not found"
        rm /tmp/${FRONTEND_SERVICE_NAME}.pid
    fi
else
    echo -e "${YELLOW}⚠${NC}  Frontend PID file not found"
fi

echo ""
echo -e "${GREEN}All services stopped${NC}"
echo ""
