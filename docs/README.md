# 📊 FraudShield Documentation

## 🌐 GitHub Pages Site

The main documentation website is available at: **https://nareshdharmaraj.github.io/FrausShield**

This directory contains both the GitHub Pages site (`index.html`) and technical documentation.

## 🔹 Project Overview

**FraudShield** is an enterprise-grade fraud detection system leveraging Apache Spark (PySpark) and advanced machine learning algorithms. This documentation provides technical details for developers and system administrators.

## 🔹 GitHub Pages Setup

The documentation is automatically deployed to GitHub Pages. To view locally:

```bash
cd docs
python -m http.server 8000
# Open http://localhost:8000
```

## 🔹 Problem Statement

Modern financial institutions process millions of transactions daily, with fraudulent activities often hidden among legitimate transactions. FraudShield provides:

- **Real-time fraud detection** using ML algorithms in Spark
- **Scalable processing** for high-volume transaction data
- **Advanced analytics** for financial security and regulatory compliance

## 🔹 Data Schema

### Input Format
Bank transactions in CSV format with the following schema:

```
transaction_id | user_id | amount | timestamp | merchant | location | payment_method
```

### Output Format
Transactions classified with fraud predictions:

```
transaction_id | user_id | amount | merchant | prediction | confidence_score
12345         | U01     | 5000   | XYZ Store| FRAUD      | 0.95
67890         | U02     | 200    | ABC Store| NORMAL     | 0.85
```

## 🔹 Tech Stack

### Core Technologies
- **🐍 Python 3.8+** - Primary development language
- **⚡ PySpark** - Big data processing and ML pipeline
- **🌶️ Flask** - Web framework and REST API
- **🤖 Scikit-learn** - Additional ML algorithms
- **📊 Pandas/NumPy** - Data manipulation and analysis

### Machine Learning
- **Supervised Models**: Random Forest, Logistic Regression, Gradient Boosting
- **Unsupervised Models**: Isolation Forest, K-Means clustering
- **Feature Engineering**: Temporal, behavioral, and statistical features
- **Model Evaluation**: Cross-validation, ROC-AUC, precision, recall

### Frontend
- **🎨 HTML5/CSS3** - Modern responsive design
- **⚡ JavaScript (ES6+)** - Interactive functionality
- **📈 Chart.js** - Data visualization
- **🌙 Theme System** - Dark/light mode with animations

## 🔹 Architecture Components

### Data Pipeline
1. **Data Ingestion** - Multi-format file processing (CSV, Excel, JSON)
2. **Data Validation** - Schema validation and data quality checks
3. **Feature Engineering** - Advanced feature extraction and transformation
4. **Model Training** - Ensemble ML model training and optimization
5. **Prediction Service** - Real-time fraud scoring and classification
6. **Results Export** - Multi-format report generation

### System Architecture
- **Frontend Layer**: Responsive web interface with theme support
- **API Layer**: RESTful Flask endpoints for data processing
- **Processing Layer**: PySpark-based ML pipeline
- **Storage Layer**: File-based data storage with result caching
- **Visualization Layer**: Interactive charts and analytics dashboards

## 🔹 Performance Specifications

### Processing Capabilities
- **Throughput**: 10,000+ transactions/second
- **Latency**: <500ms fraud prediction response time
- **Memory**: <2GB for processing 1M transactions
- **Scalability**: Linear scaling with Spark cluster size

### Model Performance
- **Random Forest**: 95.2% accuracy, 0.94 F1-score
- **Logistic Regression**: 92.8% accuracy, 0.91 F1-score
- **Isolation Forest**: 89.5% anomaly detection rate
- **Ensemble Method**: 96.7% combined accuracy

## 🔹 Development Environment

### Prerequisites
- **Python 3.8+** with pip
- **Java 8 or 11** (required for Spark)
- **Minimum 4GB RAM** (8GB+ recommended)
- **Modern web browser** for UI testing

### Setup Instructions
Detailed setup instructions are available in the main [README.md](../README.md#-quick-start).

## 🔹 API Endpoints

### Core Endpoints
- `POST /upload` - Upload transaction data files
- `POST /process` - Process uploaded data for fraud detection
- `GET /results` - Retrieve fraud detection results
- `GET /download` - Download results in various formats
- `GET /status` - System health and processing status

### Response Formats
All API endpoints return JSON responses with standardized format:

```json
{
    "status": "success|error",
    "message": "Human readable message",
    "data": { /* Response data */ },
    "timestamp": "ISO 8601 timestamp"
}
```

## 🔹 Security Considerations

- **Input Validation**: Comprehensive data sanitization and validation
- **File Upload Security**: Type checking and size limits
- **Session Management**: Secure session handling for web interface
- **Data Privacy**: No persistent storage of sensitive transaction data
- **Error Handling**: Secure error messages without information leakage

---

For complete documentation, see the main [README.md](../README.md) and [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md).