@echo off
echo ========================================
echo Starting MediConnect Frontend Server
echo ========================================
echo.

cd /d "%~dp0frontend"

REM Check if node_modules exists
if not exist "node_modules\" (
    echo Node modules not found. Installing dependencies...
    echo This may take a few minutes...
    echo.
    call yarn install
    echo.
)

echo Starting frontend development server...
echo The application will open automatically at http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

call yarn start

pause
