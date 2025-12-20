@echo off
REM Simple test runner for MediConnect

echo ========================================
echo   MediConnect Test Suite
echo ========================================
echo.

REM Set PYTHONPATH to include backend directory
set PYTHONPATH=%CD%

echo Running tests from: %CD%
echo PYTHONPATH: %PYTHONPATH%
echo.

REM Run pytest
python -m pytest -v --tb=short

echo.
echo ========================================
echo   Test Run Complete
echo ========================================
pause
