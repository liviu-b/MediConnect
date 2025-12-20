@echo off
REM MediConnect Test Runner
REM Run automated tests with coverage

echo ========================================
echo   MediConnect Test Suite
echo ========================================
echo.

cd backend

REM Check if virtual environment exists
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo No virtual environment found. Using global Python.
)

echo.
echo Installing/Updating test dependencies...
pip install -q pytest pytest-asyncio pytest-cov httpx faker

echo.
echo ========================================
echo   Running Tests...
echo ========================================
echo.

REM Run tests based on argument
if "%1"=="" (
    REM Run all tests
    pytest -v --cov=app --cov-report=html --cov-report=term-missing
) else if "%1"=="auth" (
    REM Run auth tests
    pytest -v -m auth tests/test_auth.py
) else if "%1"=="doctors" (
    REM Run doctor tests
    pytest -v -m doctors tests/test_doctors.py
) else if "%1"=="appointments" (
    REM Run appointment tests
    pytest -v -m appointments tests/test_appointments.py
) else if "%1"=="quick" (
    REM Run quick tests (no coverage)
    pytest -v --tb=short
) else if "%1"=="coverage" (
    REM Run with detailed coverage
    pytest -v --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml
    echo.
    echo Opening coverage report...
    start htmlcov\index.html
) else (
    REM Run specific test file
    pytest -v tests/test_%1.py
)

echo.
echo ========================================
echo   Test Run Complete
echo ========================================
echo.

if exist htmlcov (
    echo Coverage report: htmlcov\index.html
    echo.
    choice /C YN /M "Open coverage report in browser"
    if errorlevel 2 goto :end
    if errorlevel 1 start htmlcov\index.html
)

:end
pause
