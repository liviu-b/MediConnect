@echo off
REM Appointment Reminder Script Runner
REM This script runs the appointment reminder system

echo ========================================
echo MediConnect - Appointment Reminders
echo ========================================
echo.

cd /d "%~dp0backend"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo No virtual environment found, using system Python...
)

echo.
echo Running reminder script...
echo.

python send_appointment_reminders.py

echo.
echo ========================================
echo Script completed!
echo ========================================
pause
