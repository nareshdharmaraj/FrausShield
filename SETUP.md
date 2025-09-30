# FraudShield - Financial Fraud Detection

## Virtual Environment Setup

### Create and activate virtual environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Project Structure
```
fraud-detect/
├── src/                    # Core application modules
├── templates/              # HTML templates for Flask
├── static/                # CSS, JS, and images
│   ├── css/
│   └── js/
├── uploads/               # Uploaded CSV files
├── results/               # Generated prediction results
├── bank_transactions_data.csv
├── requirements.txt
├── app.py                # Main Flask application
└── README.md
```

## Running the Application

### Development Mode
```bash
python app.py
```

### Production Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Environment Variables (Optional)
Create a `.env` file for configuration:
```
FLASK_ENV=development
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=50MB
```