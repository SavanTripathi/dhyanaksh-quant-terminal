@echo off
title Stopping HTF Zone Scanner Terminal
color 0C

echo ======================================================================
echo    Stopping HTF Supply ^& Demand Zone Scanner Services...
echo ======================================================================
echo.

echo Terminating Uvicorn Backend Processes...
taskkill /f /im python.exe /fi "WINDOWTITLE eq HTF-Backend*" 2>nul
taskkill /f /im node.exe /fi "WINDOWTITLE eq HTF-Frontend*" 2>nul

echo.
echo All background terminal services terminated cleanly.
echo.
pause
