#!/bin/bash

# Start backend server
echo "Starting backend server..."
cd backend
workon mlEnv
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Backend started with PID: $BACKEND_PID"
echo "API available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"

# Start frontend server
echo ""
echo "Starting frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Frontend started with PID: $FRONTEND_PID"
echo "Application available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
wait
