# 🛡️ FraudShield - AI-Powered Fraud Detection System📊 Financial Fraud Detection using PySpark

🔹 Project Overview

**Enterprise-grade fraud detection system using advanced machine learning and big data processing with PySpark.**

Financial fraud is a growing challenge in today’s digital economy. Banks and fintech companies face millions of daily transactions, and fraudulent activities are often hidden among legitimate ones.

## 🏗️ Project Structure

This project leverages PySpark (Apache Spark for Python) and Machine Learning to:

```

fraud-detect/Analyze transaction data at scale.

├── 📁 src/                     # Core application modules

│   ├── data_ingestion.py       # PySpark data loading & validationDetect anomalies and fraudulent transactions.

│   ├── data_preprocessing.py   # Feature engineering pipeline  

│   └── ml_models.py           # ML models & fraud detectionProvide actionable insights for fintech security and compliance.

├── 📁 data/                   # Dataset files

│   ├── bank_transactions_data.csv🔹 Problem Statement

│   ├── sample_transactions.csv

│   └── test_bank.csvDetect anomalies in financial transactions using ML algorithms in Spark to improve financial security and regulatory compliance.

├── 📁 tests/                  # Integration tests

│   └── test_integration.py    # End-to-end system tests🔹 Input Format

├── 📁 templates/              # Web interface

│   └── index.html            # Main dashboardInput: Bank transactions stored in CSV files.

├── 📁 static/                 # Frontend assets

│   ├── css/style.css         # StylingExample schema:

│   └── js/app.js             # JavaScript functionality

├── 📁 docs/                   # Documentationtransaction_id | user_id | amount | timestamp | merchant | location | payment_method

│   ├── PROJECT_SUMMARY.md     # Technical architecture

│   ├── COMPLETION_REPORT.md   # Project status🔹 Expected Output

│   ├── SETUP.md              # Installation guide

│   └── TYPE_FIXING_REPORT.md  # Technical fixes logTransactions classified as NORMAL or FRAUD.

├── 📁 results/                # Analysis outputs

├── 📁 uploads/                # Temporary file uploadsExample output:

├── app.py                     # Main Flask application

└── requirements.txt           # Python dependenciestransaction_id	user_id	amount	merchant	prediction

```12345	U01	5000	XYZ Store	FRAUD

67890	U02	200	ABC Market	NORMAL

## 🚀 Quick Start



### Prerequisites🔹 Tech Stack

- Python 3.8+ Languages & Frameworks:

- 4GB+ RAM (for PySpark)Python

- Java 8+ (for Spark)PySpark – Big Data processing & MLlib

Pandas – Data manipulation for small datasets

### InstallationMatplotlib / Seaborn – Visualization

Machine Learning (Spark MLlib)

1. **Clone and setup:**Supervised Models: Logistic Regression, Random Forest Classifier

   ```bashUnsupervised Models: Isolation Forest, KMeans (for anomaly detection)

   git clone https://github.com/nareshdharmaraj/FrausShield.git

   cd fraud-detectEnvironment:

   python -m venv .venvVirtualenv (.venv) – dependency isolation

   .venv\Scripts\activate  # WindowsJava JDK – required by Spark

   pip install -r requirements.txtIDE: VS Code

   ```

Optional (Web UI)

2. **Run the application:**Flask – backend web framework

   ```bashHTML/CSS/js – simple UI for file upload

   python app.pyPlotly/Matplotlib – visualization in web reports

   ```

🔹 Project Workflow

3. **Access the dashboard:**1. Data Ingestion

   Open http://localhost:5000 in your browserLoad raw CSV file into a PySpark DataFrame.

Validate schema and column types.

## 🧪 Testing

2. Data Preprocessing

Run the integration test to verify all components:Handle missing values (drop or impute).

Convert categorical fields:

```bashmerchant, location, payment_method → encoded using StringIndexer or OneHotEncoding.

cd testsNormalize continuous fields (like amount).

python test_integration.py

```3. Exploratory Data Analysis (EDA)

Transaction distribution by amount, time, merchant.

## 📊 FeaturesOutlier detection using boxplots/histograms.

Correlation analysis (features vs fraud likelihood).

- **🤖 Advanced ML Models:** Isolation Forest, Random Forest, Gradient Boosting

- **⚡ PySpark Processing:** Big data handling and distributed computing4. Model Training

- **📈 Real-time Analytics:** Interactive charts and fraud pattern analysis  If dataset has fraud labels:

- **🔄 Universal CSV Support:** Works with any transaction data formatTrain supervised ML models (Logistic Regression, Random Forest).

- **🎯 High Accuracy:** Multi-factor fraud detection algorithmsEvaluate with Accuracy, Precision, Recall, F1 Score.

- **📱 Responsive UI:** Modern web interface with real-time updatesIf no fraud labels:

Use unsupervised anomaly detection (Isolation Forest, KMeans).

## 💡 UsageIdentify unusual spending patterns.



1. Upload your transaction CSV file5. Prediction & Flagging

2. System automatically detects and maps columnsPredict fraud likelihood for each transaction.

3. View real-time fraud analysis and insightsMark transactions as:

4. Download detailed results and reports0 → NORMAL

1 → FRAUD

## 🔧 Technical Stack

6. Output & Visualization

- **Backend:** Flask, PySpark, scikit-learn, pandasSave results as a CSV with predictions.

- **Frontend:** HTML5, CSS3, JavaScript, Chart.jsCreate visual dashboards:

- **ML Models:** Isolation Forest, Random Forest, Gradient BoostingFraudulent transactions by merchant.

- **Data Processing:** Apache Spark for big data handlingFraud trends over time.

High-risk users/locations.

## 📖 Documentation

🔹 Web Application (Optional but Recommended)

- **[Project Summary](docs/PROJECT_SUMMARY.md)** - Technical architecture detailsIf extended to a Flask-based web UI:

- **[Setup Guide](docs/SETUP.md)** - Detailed installation instructions  Homepage

- **[Completion Report](docs/COMPLETION_REPORT.md)** - Project status and achievementsWelcome message: “Upload your transactions file to detect fraud instantly.”

Upload form for CSV file.

## 🛡️ Security FeaturesProcessing Page

System runs fraud detection pipeline in the backend.

- ✅ Secure file upload validationShows progress/loading animation.

- ✅ Input sanitization and validationResults Page

- ✅ Temporary file cleanupDownload link for processed CSV.

- ✅ Error handling and logging

Summary statistics:

## 📧 SupportTotal transactions

Number of frauds detected

For questions or issues, please check the documentation in the `docs/` folder or review the integration tests.Fraud percentage



---Graphs:

Fraud by merchant (bar chart)

**Built with ❤️ for secure financial transactions**Fraud by amount range (histogram)
Fraud by time (line chart)

🔹 Installation & Setup
1. Clone Repository
git clone https://github.com/nareshdharmaraj/FrausShield

2. Create Virtual Environment
python -m venv .venv
.\.venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Verify PySpark Setup
from pyspark.sql import SparkSession
spark = SparkSession.builder.appName("FraudDetection").getOrCreate()
print("Spark Version:", spark.version)
spark.stop()

🔹 Example Usage
Run fraud detection script:
python fraud_detection.py --input data/transactions.csv --output results/predictions.csv

Run web app (optional):
python app.py

🔹 Future Enhancements

Real-time fraud detection with Spark Streaming + Kafka.
Deploy ML model on AWS EMR / Databricks for large-scale usage.
Interactive dashboards using Streamlit or Dash.
Model explainability (why a transaction is flagged).

🔹 Why This Project Matters
✔️ Scalable fraud detection system for financial institutions.
✔️ Detects anomalies in real-world transaction streams.
✔️ Hands-on application of Big Data + Machine Learning + FinTech Security.

⚡ Built with PySpark, powered by Machine Learning, designed to safeguard financial ecosystems.
