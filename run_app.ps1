# FraudShield Startup Script
# This script ensures all required environment variables are set

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "🚀 Starting FraudShield with PySpark Support" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Set JAVA_HOME for PySpark
$javaPath = (Get-Command java -ErrorAction SilentlyContinue).Path
if ($javaPath) {
    $env:JAVA_HOME = $javaPath | Split-Path -Parent | Split-Path -Parent
    Write-Host "✅ Java detected: $env:JAVA_HOME" -ForegroundColor Green
    java -version 2>&1 | Select-Object -First 1
} else {
    Write-Host "⚠️  Warning: Java not found. PySpark requires Java 8 or higher." -ForegroundColor Yellow
    Write-Host "   Download from: https://www.oracle.com/java/technologies/downloads/" -ForegroundColor Yellow
    Write-Host ""
}

# Set Python environment
$pythonPath = "N:/Naresh/Sem 5/SSF/fraud-detect/.venv/Scripts/python.exe"
if (Test-Path $pythonPath) {
    Write-Host "✅ Virtual environment: .venv" -ForegroundColor Green
    Write-Host "✅ Python: $pythonPath" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "⚠️  Warning: Virtual environment not found at .venv" -ForegroundColor Yellow
    $pythonPath = "python"
}

# Set Spark environment variables
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
$env:SPARK_LOCAL_IP = "127.0.0.1"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🔧 Environment Configuration:" -ForegroundColor Cyan
Write-Host "   JAVA_HOME:              $env:JAVA_HOME"
Write-Host "   PYSPARK_PYTHON:         $env:PYSPARK_PYTHON"
Write-Host "   PYSPARK_DRIVER_PYTHON:  $env:PYSPARK_DRIVER_PYTHON"
Write-Host "   SPARK_LOCAL_IP:         $env:SPARK_LOCAL_IP"
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment and run app
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath
& "$scriptPath\.venv\Scripts\Activate.ps1"
& $pythonPath "$scriptPath\app.py"
