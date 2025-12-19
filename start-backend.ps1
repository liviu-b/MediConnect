# MediConnect Backend Startup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting MediConnect Backend Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$backendPath = Join-Path $PSScriptRoot "backend"
Set-Location $backendPath

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host ""
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    pip install -r requirements.txt
    Write-Host ""
} else {
    & "venv\Scripts\Activate.ps1"
}

Write-Host "Starting backend server on http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation will be available at http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
