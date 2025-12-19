@echo off
echo ========================================
echo Starting MediConnect Application
echo ========================================
echo.
echo This will start both backend and frontend servers
echo in separate windows.
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to continue...
pause > nul

REM Start backend in a new window
start "MediConnect Backend" cmd /k "%~dp0start-backend.bat"

REM Wait a few seconds for backend to start
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

REM Start frontend in a new window
start "MediConnect Frontend" cmd /k "%~dp0start-frontend.bat"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Backend window: MediConnect Backend
echo Frontend window: MediConnect Frontend
echo.
echo Close those windows to stop the servers
echo ========================================
echo.
pause
