@echo off
REM ====================================================================
REM FraudShield - Dual Terminal Startup Script
REM ====================================================================
REM This script opens two separate terminals:
REM   Terminal 1: Backend (Flask + PySpark)
REM   Terminal 2: Browser tabs (Spark UI + Frontend)
REM ====================================================================

echo.
echo ========================================
echo    FraudShield Dual Terminal Manager
echo ========================================
echo.

REM Start Backend in PowerShell Terminal 1
echo [1/4] Starting Backend Server in Terminal 1...
start "FraudShield Backend" powershell -NoExit -Command "cd '%~dp0'; Write-Host ''; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host '   FraudShield Backend Server (Terminal 1)' -ForegroundColor Green; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host ''; Write-Host 'Starting Flask + PySpark...' -ForegroundColor Yellow; Write-Host ''; .\start.ps1"

REM Wait for backend initialization
echo [2/4] Waiting for backend initialization (12 seconds)...
timeout /t 12 /nobreak >nul

REM Start Browser Manager in PowerShell Terminal 2
echo [3/4] Opening Browser Manager in Terminal 2...
start "FraudShield Browser" powershell -NoExit -Command "cd '%~dp0'; Write-Host ''; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host '   FraudShield Browser Manager (Terminal 2)' -ForegroundColor Green; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host ''; Write-Host '[1/2] Opening Spark Web UI...' -ForegroundColor Yellow; Start-Process 'http://localhost:4040'; Start-Sleep -Seconds 3; Write-Host '[2/2] Opening Frontend Interface...' -ForegroundColor Yellow; Start-Process 'http://localhost:5000'; Write-Host ''; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host '   All Services Running!' -ForegroundColor Green; Write-Host '============================================================' -ForegroundColor Cyan; Write-Host ''; Write-Host 'Backend Server:      http://localhost:5000' -ForegroundColor White; Write-Host 'Spark Web UI:        http://localhost:4040' -ForegroundColor White; Write-Host 'Processing Spark UI: http://localhost:4041' -ForegroundColor White; Write-Host ''; Write-Host 'Press Ctrl+C to stop monitoring...' -ForegroundColor Gray; Write-Host ''"

echo [4/4] Startup complete!
echo.
echo ========================================
echo    Terminals Opened:
echo ========================================
echo   Terminal 1: Backend Server
echo   Terminal 2: Browser Manager
echo.
echo   Spark UI:    http://localhost:4040
echo   Frontend:    http://localhost:5000
echo.
echo Press any key to exit this launcher...
pause >nul
