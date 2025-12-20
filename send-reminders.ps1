# Appointment Reminder Script Runner (PowerShell)
# This script runs the appointment reminder system

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "MediConnect - Appointment Reminders" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to backend directory
Set-Location -Path "$PSScriptRoot\backend"

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Host "No virtual environment found, using system Python..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Running reminder script..." -ForegroundColor Green
Write-Host ""

# Run the reminder script
python send_appointment_reminders.py

$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "Script completed successfully!" -ForegroundColor Green
} else {
    Write-Host "Script completed with errors!" -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

# Keep window open
Read-Host -Prompt "Press Enter to exit"
