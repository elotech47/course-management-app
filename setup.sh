#!/bin/bash

# Course Management System - Setup Script

echo "====================================="
echo "Course Management System Setup"
echo "====================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi
echo "✓ Python 3 found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi
echo "✓ Node.js found: $(node --version)"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed and running."
fi

echo ""
echo "====================================="
echo "Backend Setup"
echo "====================================="
echo ""

cd backend


# Activate virtual environment
echo "Activating virtual environment..."
workon mlEnv

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your configuration before starting the server"
else
    echo "✓ .env file already exists"
fi

# Create database tables
echo "Setting up database tables..."
python -c "from app.db import models; from app.db.database import engine; models.Base.metadata.create_all(bind=engine)" 2>/dev/null || echo "⚠️  Database tables creation skipped. Make sure to configure DATABASE_URL in .env"

echo ""
echo "====================================="
echo "Frontend Setup"
echo "====================================="
echo ""

cd ../frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "VITE_API_URL=http://localhost:8000" > .env
else
    echo "✓ .env file already exists"
fi

cd ..

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your database and email settings in backend/.env"
echo ""
echo "2. Start the backend server:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open your browser to http://localhost:3000"
echo ""
echo "For detailed instructions, see README.md"
echo ""
