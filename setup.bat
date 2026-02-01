@echo off
REM Course Management System - Setup Script for Windows

echo =====================================
echo Course Management System Setup
echo =====================================
echo.

echo Checking prerequisites...

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3 is not installed. Please install Python 3.9 or higher.
    exit /b 1
)
echo Python found

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed. Please install Node.js 18 or higher.
    exit /b 1
)
echo Node.js found

echo.
echo =====================================
echo Backend Setup
echo =====================================
echo.

cd backend

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo Please edit backend\.env with your configuration before starting the server
) else (
    echo .env file already exists
)

echo.
echo =====================================
echo Frontend Setup
echo =====================================
echo.

cd ..\frontend

REM Install dependencies
echo Installing Node.js dependencies...
call npm install

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    echo VITE_API_URL=http://localhost:8000 > .env
) else (
    echo .env file already exists
)

cd ..

echo.
echo =====================================
echo Setup Complete!
echo =====================================
echo.
echo Next steps:
echo.
echo 1. Configure your database and email settings in backend\.env
echo.
echo 2. Start the backend server:
echo    cd backend
echo    venv\Scripts\activate
echo    uvicorn app.main:app --reload --port 8000
echo.
echo 3. In a new terminal, start the frontend:
echo    cd frontend
echo    npm run dev
echo.
echo 4. Open your browser to http://localhost:3000
echo.
echo For detailed instructions, see README.md
echo.

pause
