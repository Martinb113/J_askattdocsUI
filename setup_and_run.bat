@echo off
setlocal enabledelayedexpansion

echo ========================================
echo AI Chat Application - Complete Setup
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

REM Check PostgreSQL
psql --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] PostgreSQL not found in PATH!
    echo Please install PostgreSQL 15+ from:
    echo https://www.postgresql.org/download/windows/
    echo.
    echo After installation, add to PATH:
    echo C:\Program Files\PostgreSQL\15\bin
    echo.
    pause
    exit /b 1
)

echo [OK] All prerequisites found!
echo.

REM Setup Backend
echo ========================================
echo Setting up Backend...
echo ========================================
cd /d "%~dp0backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo [ACTION REQUIRED] Please edit backend\.env with your PostgreSQL password
    echo Press any key when ready...
    pause >nul
)

echo Installing Python dependencies...
pip install -r requirements.txt --quiet

echo.
echo Checking database...
psql -U postgres -d ai_chat_db -c "SELECT 1;" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Database 'ai_chat_db' not found. Creating...
    psql -U postgres -c "CREATE DATABASE ai_chat_db;"
    if errorlevel 1 (
        echo [ERROR] Failed to create database!
        echo Please create manually: CREATE DATABASE ai_chat_db;
        pause
        exit /b 1
    )
)

echo Running migrations...
alembic revision --autogenerate -m "Initial schema" >nul 2>&1
alembic upgrade head

echo Seeding database...
python scripts\seed_data.py

echo.
echo [OK] Backend setup complete!
echo.

REM Setup Frontend
cd /d "%~dp0frontend"

echo ========================================
echo Setting up Frontend...
echo ========================================

if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

echo Installing Node dependencies...
echo This may take a few minutes...
npm install

echo.
echo [OK] Frontend setup complete!
echo.

REM Summary
cd /d "%~dp0"
echo ========================================
echo Setup Complete! Starting Application...
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Login with:
echo   AT^&T ID: admin
echo   Password: Admin123!
echo.
echo Press Ctrl+C in each window to stop
echo ========================================
echo.
pause

REM Start both services in new windows
start "Backend Server" cmd /k "%~dp0start_backend.bat"
timeout /t 5 /nobreak >nul
start "Frontend Server" cmd /k "%~dp0start_frontend.bat"

echo.
echo Both servers starting...
echo Backend window and Frontend window opened!
echo.
pause
