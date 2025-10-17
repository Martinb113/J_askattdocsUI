@echo off
echo ========================================
echo Starting Frontend Development Server
echo ========================================
echo.

cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist "node_modules" (
    echo [INFO] First time setup - Installing dependencies...
    echo This may take a few minutes...
    npm install
)

echo.
echo ========================================
echo Frontend starting at http://localhost:3000
echo ========================================
echo.
echo Login with:
echo   AT^&T ID: admin
echo   Password: Admin123!
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start development server
npm run dev

pause
