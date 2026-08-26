@echo off
title HTF Supply and Demand Zone Scanner Terminal
color 0B

echo ======================================================================
echo    HTF SUPPLY ^& DEMAND ZONE SCANNER PRO TERMINAL
echo    Institutional Multi-Timeframe Confluence Analytics Engine
echo ======================================================================
echo.

cd /d "%~dp0"

echo [1/3] Starting FastAPI Backend Server on http://127.0.0.1:8000 ...
start "HTF-Backend" /min cmd /c "python -m uvicorn app.main:app --port 8000"

timeout /t 3 /nobreak > nul

echo [2/3] Starting React + Vite Frontend Terminal on http://localhost:5173 ...
cd frontend
start "HTF-Frontend" /min cmd /c "npm run dev"

timeout /t 3 /nobreak > nul

echo [3/3] Opening Terminal UI in Default Browser ...
start http://localhost:5173

echo.
echo ======================================================================
echo  TERMINAL RUNNING SUCCESSFULLY!
echo  - Interactive UI: http://localhost:5173
echo  - API Swagger Docs: http://127.0.0.1:8000/docs
echo  To stop all services, run 'stop_terminal.bat'
echo ======================================================================
pause
