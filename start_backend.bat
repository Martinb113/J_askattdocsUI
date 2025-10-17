@echo off
echo ========================================
echo Starting Backend Server
echo ========================================
echo.

cd /d "%~dp0backend"

REM Check if venv exists
if not exist "venv" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if database is set up
if not exist "alembic\versions\*.py" (
    echo.
    echo [INFO] First time setup - Running migrations...
    alembic revision --autogenerate -m "Initial schema"
    alembic upgrade head
    echo.
    echo [INFO] Seeding database...
    python scripts\seed_data.py
)

echo.
echo ========================================
echo Backend starting at http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start uvicorn
uvicorn app.main:app --reload

pause
