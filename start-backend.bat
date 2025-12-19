@echo off
echo ========================================
echo Starting MediConnect Backend Server
echo ========================================
echo.

cd /d "%~dp0backend"

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    echo.
    py -m venv venv
    if errorlevel 1 (
        python -m venv venv
    )
    echo.
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting backend server on http://localhost:8000
echo API Documentation will be available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000

pause
