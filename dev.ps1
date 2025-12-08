#!/usr/bin/env pwsh
# EventPulse Development Server Launcher
# Starts both backend (FastAPI) and frontend (React) servers

Write-Host "🚀 Starting EventPulse Development Servers..." -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "❌ Virtual environment not found. Run: python -m venv .venv" -ForegroundColor Red
    exit 1
}

# Check if node_modules exists
if (-not (Test-Path ".\src\ui\frontend\node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location ".\src\ui\frontend"
    npm install
    Pop-Location
}

Write-Host "🔧 Starting Backend (FastAPI) on http://localhost:8000" -ForegroundColor Green
Write-Host "🎨 Starting Frontend (React) on http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host ""

# Start backend in background job
$backend = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & .\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000
}

# Start frontend in background job
$frontend = Start-Job -ScriptBlock {
    Set-Location "$using:PWD\src\ui\frontend"
    npm start
}

# Wait and stream output
try {
    while ($true) {
        # Get backend output
        Receive-Job -Job $backend -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "[API] $_" -ForegroundColor Blue
        }
        
        # Get frontend output  
        Receive-Job -Job $frontend -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host "[UI] $_" -ForegroundColor Magenta
        }
        
        # Check if jobs are still running
        if ($backend.State -eq "Failed" -or $frontend.State -eq "Failed") {
            Write-Host "❌ A server crashed. Check the output above." -ForegroundColor Red
            break
        }
        
        Start-Sleep -Milliseconds 500
    }
}
finally {
    Write-Host "`n🛑 Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backend, $frontend -ErrorAction SilentlyContinue
    Remove-Job -Job $backend, $frontend -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Servers stopped." -ForegroundColor Green
}
