@echo off
echo ========================================
echo Starting MediConnect Backend Server
echo ========================================
echo.

cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo.
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo.
) else (
    call venv\Scripts\activate.bat
)

echo Starting backend server on http://localhost:8000
echo API Documentation will be available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000

pause
