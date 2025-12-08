@echo off
REM EventPulse Development Server Launcher (Simple)
REM Starts both backend and frontend in separate windows

echo.
echo  ========================================
echo   EventPulse Development Servers
echo  ========================================
echo.

REM Start backend in new window
echo Starting Backend (FastAPI) on http://localhost:8000...
start "EventPulse Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000"

REM Wait a moment for backend to initialize
timeout /t 2 /nobreak > nul

REM Start frontend in new window
echo Starting Frontend (React) on http://localhost:3000...
start "EventPulse Frontend" cmd /k "cd src\ui\frontend && npm start"

echo.
echo  Both servers are starting in separate windows.
echo  Close this window or the server windows to stop.
echo.
