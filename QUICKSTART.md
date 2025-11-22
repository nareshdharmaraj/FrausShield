# Quick Start Guide

## Prerequisites
1. **Java 8 or higher** (Required for PySpark)
   - Download from: https://www.oracle.com/java/technologies/downloads/
   - Verify installation: `java -version`

2. **Python 3.8+**
   - Python 3.10 or higher recommended

## Installation

### Method 1: Using PowerShell Script (Recommended)
```powershell
# Simply run the startup script
.\run_app.ps1
```

This script will:
- Auto-detect Java and set JAVA_HOME
- Activate the virtual environment
- Set required environment variables
- Start the Flask application with PySpark support

### Method 2: Manual Setup
```powershell
# Set JAVA_HOME (adjust path to your Java installation)
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Set Spark environment variables
$env:PYSPARK_PYTHON = ".\.venv\Scripts\python.exe"
$env:PYSPARK_DRIVER_PYTHON = ".\.venv\Scripts\python.exe"

# Run the application
python app.py
```

## Accessing the Application

Once started, you can access:
- **Web Interface**: http://localhost:5000
- **Spark Web UI**: http://localhost:4040 (available after first processing)

## Verifying PySpark

When the application starts successfully, you should see:
```
✅ PySpark modules loaded successfully

================================================================================
🚀 FRAUDSHIELD v3.0 - Fraud Detection System
================================================================================

📊 Application URLs:
   ├─ Web Interface:  http://localhost:5000
   └─ Spark Web UI:   http://localhost:4040 (available after first processing)

🔍 Ready to detect fraudulent transactions!
================================================================================
```

If you see warnings about PySpark not being available:
1. Ensure Java is installed: `java -version`
2. Ensure JAVA_HOME is set
3. Reinstall dependencies: `pip install -r requirements.txt`

## Viewing Spark Jobs

1. Start the application using `run_app.ps1`
2. Upload a CSV file through the web interface
3. Open http://localhost:4040 to see:
   - Jobs and stages
   - Task execution details
   - DAG visualization
   - Storage and executors

The terminal will also show detailed progress with:
- Data loading statistics
- Preprocessing steps
- Model training progress
- Evaluation metrics
- Analysis report

## Troubleshooting

### "JAVA_HOME not set" error
Set JAVA_HOME to your Java installation directory:
```powershell
$env:JAVA_HOME = "C:\Program Files\Java\jdk-17"
```

### "PySpark modules not available" warning
Install PySpark:
```powershell
pip install pyspark
```

### Spark Web UI not showing jobs
Ensure you're using the `run_app.ps1` script or manually set all environment variables as shown in Method 2.
