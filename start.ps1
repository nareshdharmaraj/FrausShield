# FraudShield Startup Script
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Starting FraudShield with PySpark Support" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Set JAVA_HOME for PySpark
# Try to find JDK installation
$javaHomeLocations = @(
    "C:\Program Files\Java\jdk-17",
    "C:\Program Files\Java\jdk-11",
    "C:\Program Files\Java\jdk1.8.0_*",
    "C:\Program Files\Java\jdk-1.8"
)

$env:JAVA_HOME = $null
foreach ($location in $javaHomeLocations) {
    $found = Get-Item $location -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($found -and (Test-Path "$($found.FullName)\bin\java.exe")) {
        $env:JAVA_HOME = $found.FullName
        break
    }
}

if ($env:JAVA_HOME) {
    Write-Host "Java detected: $env:JAVA_HOME" -ForegroundColor Green
    & "$env:JAVA_HOME\bin\java.exe" -version 2>&1 | Select-Object -First 1 | Write-Host -ForegroundColor Gray
} else {
    Write-Host "Warning: Java not found. PySpark requires Java 8 or higher." -ForegroundColor Yellow
    Write-Host "Please install Java from: https://www.oracle.com/java/technologies/downloads/" -ForegroundColor Yellow
}

# Set Python environment
$pythonPath = "N:\Naresh\Sem 5\SSF\fraud-detect\.venv\Scripts\python.exe"
if (Test-Path $pythonPath) {
    Write-Host "Virtual environment: .venv" -ForegroundColor Green
} else {
    Write-Host "Warning: Virtual environment not found" -ForegroundColor Yellow
    $pythonPath = "python"
}

# Set Spark environment variables
$env:PYSPARK_PYTHON = $pythonPath
$env:PYSPARK_DRIVER_PYTHON = $pythonPath
$env:SPARK_LOCAL_IP = "127.0.0.1"

Write-Host ""
Write-Host "Environment Configuration:" -ForegroundColor Cyan
Write-Host "  JAVA_HOME: $env:JAVA_HOME"
Write-Host "  PYSPARK_PYTHON: $env:PYSPARK_PYTHON"
Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Run app
& $pythonPath app.py
