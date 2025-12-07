@echo off
REM ====================================================================
REM FraudShield - Complete Startup Script
REM ====================================================================
REM This script starts:
REM   1. Backend Flask Server (Terminal 1)
REM   2. Spark Web UI Browser Tab
REM   3. Frontend Web Interface Browser Tab
REM ====================================================================

echo.
echo ========================================
echo    FraudShield Startup Manager
echo ========================================
echo.
echo Starting all services...
echo.

REM Start Backend in new PowerShell window
echo [1/3] Starting Backend Server...
start "FraudShield Backend" powershell -NoExit -Command "cd '%~dp0'; Write-Host ''; Write-Host '========================================' -ForegroundColor Cyan; Write-Host '   FraudShield Backend Server' -ForegroundColor Green; Write-Host '========================================' -ForegroundColor Cyan; Write-Host ''; .\start.ps1"

REM Wait for backend to initialize
echo [2/3] Waiting for server initialization...
timeout /t 8 /nobreak >nul

REM Open Spark Web UI in browser
echo [3/3] Opening Spark Web UI...
start http://localhost:4040
timeout /t 2 /nobreak >nul

REM Open Frontend Web Interface in browser
echo [4/4] Opening Frontend Web Interface...
start http://localhost:5000

echo.
echo ========================================
echo    All Services Started!
echo ========================================
echo.
echo   Backend:     Running in separate window
echo   Spark UI:    http://localhost:4040
echo   Frontend:    http://localhost:5000
echo.
echo   Processing Spark UI will be at:
echo   http://localhost:4041
echo.
echo Press any key to exit this window...
pause >nul
