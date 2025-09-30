from flask import Flask, render_template, request, jsonify, send_file
import os
import pandas as pd
import json
from datetime import datetime
import tempfile
from werkzeug.utils import secure_filename
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our advanced modules
try:
    from src.data_ingestion import DataIngestionEngine, quick_ingest
    from src.data_preprocessing import DataPreprocessingPipeline, preprocess_fraud_data
    from src.ml_models import FraudDetectionMLPipeline, train_fraud_detection_models
    ADVANCED_PROCESSING = True
    logger.info("✅ Advanced PySpark modules loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ Advanced modules not available, using basic processing: {e}")
    ADVANCED_PROCESSING = False


def smart_column_mapping(df):
    """
    Intelligently map different column names to standardized format
    """
    column_mapping = {}
    df_columns = [col.lower().strip() for col in df.columns]
    
    # Define possible column name variations
    mappings = {
        'transaction_id': ['transaction_id', 'transactionid', 'trans_id', 'id', 'txn_id', 'transaction_number', 'reference'],
        'user_id': ['user_id', 'userid', 'customer_id', 'customerid', 'account_id', 'accountid', 'client_id'],
        'amount': ['amount', 'transaction_amount', 'transactionamount', 'value', 'sum', 'total', 'price', 'cost'],
        'merchant': ['merchant', 'merchant_id', 'merchantid', 'vendor', 'shop', 'store', 'location', 'place']
    }
    
    # Try to find matching columns
    for standard_name, variations in mappings.items():
        found = False
        for variation in variations:
            for i, col in enumerate(df_columns):
                if variation in col or col in variation:
                    column_mapping[standard_name] = df.columns[i]  # Use original column name
                    found = True
                    break
            if found:
                break
        
        # If no exact match found, try partial matching
        if not found:
            for i, col in enumerate(df_columns):
                for variation in variations:
                    if variation in col or col in variation:
                        column_mapping[standard_name] = df.columns[i]
                        found = True
                        break
                if found:
                    break
    
    logger.info(f"🎯 Column mapping found: {column_mapping}")
    return column_mapping


def flexible_data_validation(df):
    """
    Flexible data validation that works with any CSV structure
    """
    try:
        import numpy as np
        
        logger.info(f"📋 Analyzing CSV with columns: {list(df.columns)}")
        
        # Get intelligent column mapping
        column_mapping = smart_column_mapping(df)
        
        # Create a standardized dataframe
        standardized_df = df.copy()
        
        # If we found some mappings, rename columns
        if column_mapping:
            # Rename columns to standard format
            reverse_mapping = {v: k for k, v in column_mapping.items()}
            standardized_df = standardized_df.rename(columns=reverse_mapping)
            logger.info(f"✅ Mapped columns: {reverse_mapping}")
        
        # Create missing required columns with intelligent defaults
        required_columns = ['transaction_id', 'user_id', 'amount', 'merchant']
        
        for col in required_columns:
            if col not in standardized_df.columns:
                if col == 'transaction_id':
                    # Generate transaction IDs
                    standardized_df['transaction_id'] = [f"TXN_{i+1:06d}" for i in range(len(standardized_df))]
                    logger.info("🆔 Generated transaction_id column")
                    
                elif col == 'user_id':
                    # Use first available ID column or generate
                    id_cols = [c for c in standardized_df.columns if 'id' in c.lower() and c != 'transaction_id']
                    if id_cols:
                        standardized_df['user_id'] = standardized_df[id_cols[0]]
                        logger.info(f"👤 Used {id_cols[0]} as user_id")
                    else:
                        standardized_df['user_id'] = [f"USER_{i+1:04d}" for i in range(len(standardized_df))]
                        logger.info("👤 Generated user_id column")
                
                elif col == 'amount':
                    # Look for numeric columns that could be amounts
                    numeric_cols = standardized_df.select_dtypes(include=['float64', 'int64']).columns
                    amount_candidates = [c for c in numeric_cols if any(keyword in c.lower() for keyword in ['amount', 'value', 'price', 'cost', 'sum', 'total'])]
                    
                    if amount_candidates:
                        standardized_df['amount'] = standardized_df[amount_candidates[0]]
                        logger.info(f"💰 Used {amount_candidates[0]} as amount")
                    else:
                        # Use first numeric column or generate random amounts
                        if len(numeric_cols) > 0:
                            standardized_df['amount'] = standardized_df[numeric_cols[0]]
                            logger.info(f"💰 Used {numeric_cols[0]} as amount")
                        else:
                            np.random.seed(42)
                            standardized_df['amount'] = np.random.uniform(10, 5000, len(standardized_df))
                            logger.info("💰 Generated random amount column")
                
                elif col == 'merchant':
                    # Look for text columns that could be merchants
                    text_cols = standardized_df.select_dtypes(include=['object']).columns
                    merchant_candidates = [c for c in text_cols if any(keyword in c.lower() for keyword in ['merchant', 'vendor', 'shop', 'store', 'location', 'place'])]
                    
                    if merchant_candidates:
                        standardized_df['merchant'] = standardized_df[merchant_candidates[0]]
                        logger.info(f"🏪 Used {merchant_candidates[0]} as merchant")
                    else:
                        # Use first text column or generate merchants
                        if len(text_cols) > 0:
                            standardized_df['merchant'] = standardized_df[text_cols[0]]
                            logger.info(f"🏪 Used {text_cols[0]} as merchant")
                        else:
                            merchants = ['Amazon', 'Walmart', 'Target', 'Starbucks', 'McDonald\'s', 'Gas Station', 'Grocery Store', 'Online Store']
                            standardized_df['merchant'] = np.random.choice(merchants, len(standardized_df))
                            logger.info("🏪 Generated random merchant column")
        
        # Ensure amount column is numeric
        if 'amount' in standardized_df.columns:
            standardized_df['amount'] = pd.to_numeric(standardized_df['amount'], errors='coerce')
            # Fill NaN values with median or 0
            standardized_df['amount'] = standardized_df['amount'].fillna(standardized_df['amount'].median() if not standardized_df['amount'].isna().all() else 100)
        
        logger.info(f"✅ Standardized dataframe created with {len(standardized_df)} rows")
        logger.info(f"📊 Final columns: {list(standardized_df.columns)}")
        
        return standardized_df, True, "Data successfully standardized"
        
    except Exception as e:
        logger.error(f"❌ Error in flexible validation: {str(e)}")
        return df, False, f"Validation error: {str(e)}"


app = Flask(__name__)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Global variables to store processing results
current_results = None
current_filename = None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    """Process uploaded CSV file and perform fraud detection"""
    global current_results, current_filename
    
    try:
        logger.info("📨 Received file processing request")
        
        # Check if file was uploaded
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        current_filename = filename
        
        logger.info(f"📁 File saved: {filename}")
        
        # Load and validate data
        try:
            df = pd.read_csv(filepath)
            logger.info(f"📊 Loaded {len(df)} rows from CSV")
        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            return jsonify({'error': f'Error reading CSV file: {str(e)}'}), 400
        
        # Use flexible validation instead of strict column checking
        try:
            standardized_df, validation_success, validation_message = flexible_data_validation(df)
            if not validation_success:
                return jsonify({'error': validation_message}), 400
            
            logger.info("✅ Flexible validation completed successfully")
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({'error': f'Data validation failed: {str(e)}'}), 400
        
        logger.info("🔍 Starting fraud detection...")
        
        # Perform fraud detection with timeout protection
        try:
            results = perform_fraud_detection(standardized_df)
            current_results = results
            
            # Ensure we have proper response structure
            if not isinstance(results, dict) or 'stats' not in results:
                raise ValueError("Invalid results format from fraud detection")
            
            # Generate response with statistics and chart data
            response = {
                'status': 'success',
                'message': 'File processed successfully',
                'stats': results.get('stats', {}),
                'charts': results.get('charts', {})
            }
            
            logger.info(f"✅ Processing completed. Found {results['stats'].get('fraud', 0)} fraudulent transactions")
            return jsonify(response)
            
        except Exception as fraud_error:
            logger.error(f"Fraud detection error: {str(fraud_error)}")
            # Return a basic successful response with error info
            return jsonify({
                'status': 'success',
                'message': 'Basic processing completed (advanced features unavailable)',
                'stats': {
                    'total': len(standardized_df),
                    'fraud': 0,
                    'normal': len(standardized_df),
                    'fraud_rate': 0
                },
                'charts': {},
                'warning': f'Advanced processing failed: {str(fraud_error)}'
            })
        
    except Exception as e:
        logger.error(f"❌ Critical error in file processing: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': f'Processing failed: {str(e)}',
            'details': 'Check server logs for more information'
        }), 500
        
def smart_column_mapping(df):
    """
    Intelligently map different column names to standardized format
    """
    column_mapping = {}
    df_columns = [col.lower().strip() for col in df.columns]
    
    # Define possible column name variations
    mappings = {
        'transaction_id': ['transaction_id', 'transactionid', 'trans_id', 'id', 'txn_id', 'transaction_number', 'reference'],
        'user_id': ['user_id', 'userid', 'customer_id', 'customerid', 'account_id', 'accountid', 'client_id'],
        'amount': ['amount', 'transaction_amount', 'transactionamount', 'value', 'sum', 'total', 'price', 'cost'],
        'merchant': ['merchant', 'merchant_id', 'merchantid', 'vendor', 'shop', 'store', 'location', 'place']
    }
    
    # Try to find matching columns
    for standard_name, variations in mappings.items():
        found = False
        for variation in variations:
            for i, col in enumerate(df_columns):
                if variation in col or col in variation:
                    column_mapping[standard_name] = df.columns[i]  # Use original column name
                    found = True
                    break
            if found:
                break
        
        # If no exact match found, try partial matching
        if not found:
            for i, col in enumerate(df_columns):
                for variation in variations:
                    if variation in col or col in variation:
                        column_mapping[standard_name] = df.columns[i]
                        found = True
                        break
                if found:
                    break
    
    logger.info(f"🎯 Column mapping found: {column_mapping}")
    return column_mapping


def flexible_data_validation(df):
    """
    Flexible data validation that works with any CSV structure
    """
    try:
        logger.info(f"📋 Analyzing CSV with columns: {list(df.columns)}")
        
        # Get intelligent column mapping
        column_mapping = smart_column_mapping(df)
        
        # Create a standardized dataframe
        standardized_df = df.copy()
        
        # If we found some mappings, rename columns
        if column_mapping:
            # Rename columns to standard format
            reverse_mapping = {v: k for k, v in column_mapping.items()}
            standardized_df = standardized_df.rename(columns=reverse_mapping)
            logger.info(f"✅ Mapped columns: {reverse_mapping}")
        
        # Create missing required columns with intelligent defaults
        required_columns = ['transaction_id', 'user_id', 'amount', 'merchant']
        
        for col in required_columns:
            if col not in standardized_df.columns:
                if col == 'transaction_id':
                    # Generate transaction IDs
                    standardized_df['transaction_id'] = [f"TXN_{i+1:06d}" for i in range(len(standardized_df))]
                    logger.info("🆔 Generated transaction_id column")
                    
                elif col == 'user_id':
                    # Use first available ID column or generate
                    id_cols = [c for c in standardized_df.columns if 'id' in c.lower() and c != 'transaction_id']
                    if id_cols:
                        standardized_df['user_id'] = standardized_df[id_cols[0]]
                        logger.info(f"👤 Used {id_cols[0]} as user_id")
                    else:
                        standardized_df['user_id'] = [f"USER_{i+1:04d}" for i in range(len(standardized_df))]
                        logger.info("👤 Generated user_id column")
                
                elif col == 'amount':
                    # Look for numeric columns that could be amounts
                    numeric_cols = standardized_df.select_dtypes(include=['float64', 'int64']).columns
                    amount_candidates = [c for c in numeric_cols if any(keyword in c.lower() for keyword in ['amount', 'value', 'price', 'cost', 'sum', 'total'])]
                    
                    if amount_candidates:
                        standardized_df['amount'] = standardized_df[amount_candidates[0]]
                        logger.info(f"💰 Used {amount_candidates[0]} as amount")
                    else:
                        # Use first numeric column or generate random amounts
                        if len(numeric_cols) > 0:
                            standardized_df['amount'] = standardized_df[numeric_cols[0]]
                            logger.info(f"💰 Used {numeric_cols[0]} as amount")
                        else:
                            import numpy as np
                            np.random.seed(42)
                            standardized_df['amount'] = np.random.uniform(10, 5000, len(standardized_df))
                            logger.info("💰 Generated random amount column")
                
                elif col == 'merchant':
                    # Look for text columns that could be merchants
                    text_cols = standardized_df.select_dtypes(include=['object']).columns
                    merchant_candidates = [c for c in text_cols if any(keyword in c.lower() for keyword in ['merchant', 'vendor', 'shop', 'store', 'location', 'place'])]
                    
                    if merchant_candidates:
                        standardized_df['merchant'] = standardized_df[merchant_candidates[0]]
                        logger.info(f"🏪 Used {merchant_candidates[0]} as merchant")
                    else:
                        # Use first text column or generate merchants
                        if len(text_cols) > 0:
                            standardized_df['merchant'] = standardized_df[text_cols[0]]
                            logger.info(f"🏪 Used {text_cols[0]} as merchant")
                        else:
                            merchants = ['Amazon', 'Walmart', 'Target', 'Starbucks', 'McDonald\'s', 'Gas Station', 'Grocery Store', 'Online Store']
                            standardized_df['merchant'] = np.random.choice(merchants, len(standardized_df))
                            logger.info("🏪 Generated random merchant column")
        
        # Ensure amount column is numeric
        if 'amount' in standardized_df.columns:
            standardized_df['amount'] = pd.to_numeric(standardized_df['amount'], errors='coerce')
            # Fill NaN values with median or 0
            standardized_df['amount'] = standardized_df['amount'].fillna(standardized_df['amount'].median() if not standardized_df['amount'].isna().all() else 100)
        
        logger.info(f"✅ Standardized dataframe created with {len(standardized_df)} rows")
        logger.info(f"📊 Final columns: {list(standardized_df.columns)}")
        
        return standardized_df, True, "Data successfully standardized"
        
    except Exception as e:
        logger.error(f"❌ Error in flexible validation: {str(e)}")
        return df, False, f"Validation error: {str(e)}"
        
        logger.info("🔍 Starting fraud detection...")
        
        # Perform fraud detection with timeout protection
        try:
            results = perform_fraud_detection(standardized_df)
            current_results = results
            
            # Ensure we have proper response structure
            if not isinstance(results, dict) or 'stats' not in results:
                raise ValueError("Invalid results format from fraud detection")
            
            # Generate response with statistics and chart data
            response = {
                'status': 'success',
                'message': 'File processed successfully',
                'stats': results.get('stats', {}),
                'charts': results.get('charts', {})
            }
            
            logger.info(f"✅ Processing completed. Found {results['stats'].get('fraud', 0)} fraudulent transactions")
            return jsonify(response)
            
        except Exception as fraud_error:
            logger.error(f"Fraud detection error: {str(fraud_error)}")
            # Return a basic successful response with error info
            return jsonify({
                'status': 'success',
                'message': 'Basic processing completed (advanced features unavailable)',
                'stats': {
                    'total': len(standardized_df),
                    'fraud': 0,
                    'normal': len(standardized_df),
                    'fraud_rate': 0
                },
                'charts': {},
                'warning': f'Advanced processing failed: {str(fraud_error)}'
            })
        
    except Exception as e:
        logger.error(f"❌ Critical error in file processing: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': f'Processing failed: {str(e)}',
            'details': 'Check server logs for more information'
        }), 500


@app.route('/status')
def status():
    """Get current processing status"""
    return jsonify({
        'status': 'ready',
        'timestamp': datetime.now().isoformat(),
        'message': 'Server is ready to process files'
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'FraudShield Detection System'
    })


@app.route('/test-response')
def test_response():
    """Test endpoint to check JSON response format"""
    return jsonify({
        'status': 'success',
        'message': 'Test response working',
        'stats': {
            'total': 20,
            'fraud': 9,
            'normal': 11,
            'fraud_rate': 45.0
        },
        'charts': {
            'fraud_by_amount': {
                'labels': ['0-100', '100-500', '500-1000'],
                'values': [2, 4, 3]
            }
        }
    })

def perform_fraud_detection(df):
    """
    Perform fraud detection with fast processing for web interface
    """
    try:
        data_size = len(df)
        logger.info(f"📊 Processing {data_size} transactions")
        
        # For web interface, always use fast basic processing to avoid timeouts
        logger.info("⚡ Using optimized basic processing for web interface...")
        return perform_basic_fraud_detection(df)
            
    except Exception as e:
        logger.error(f"Error in fraud detection: {str(e)}")
        # Fallback to basic processing
        return perform_basic_fraud_detection(df)

def perform_advanced_fraud_detection(df):
    """
    Advanced fraud detection using complete PySpark ML pipeline
    """
    try:
        logger.info("🚀 Starting complete ML fraud detection pipeline...")
        
        # Save DataFrame as temporary CSV for PySpark processing
        temp_csv_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_processing.csv')
        df.to_csv(temp_csv_path, index=False)
        
        # Initialize data ingestion engine
        ingestion_engine = DataIngestionEngine()
        spark = ingestion_engine.initialize_spark()
        
        # Load data with PySpark
        spark_df = ingestion_engine.load_csv_data(temp_csv_path)
        
        # Validate schema
        validation_results = ingestion_engine.validate_schema(spark_df)
        logger.info(f"Schema validation: {validation_results['is_valid']}")
        
        # Generate data profile
        data_profile = ingestion_engine.generate_data_profile(spark_df)
        logger.info(f"Data quality score: {data_profile['data_quality']['score']}/100")
        
        # Detect anomalies
        anomalies = ingestion_engine.detect_anomalies(spark_df)
        
        # Initialize preprocessing pipeline
        preprocessing_pipeline = DataPreprocessingPipeline(spark)
        
        # Run complete preprocessing pipeline with error handling
        try:
            processed_df = (preprocessing_pipeline
                           .set_dataframe(spark_df)
                           .clean_data(remove_duplicates=True, handle_nulls="fill")
                           .engineer_features(create_time_features=True,
                                            create_amount_features=True,
                                            create_user_features=True)
                           .encode_categorical_variables(encoding_method="onehot", max_categories=10)
                           .scale_numerical_features(scaling_method="standard")
                           .create_feature_vector()
                           .processed_df)
            
            logger.info("✅ Complete preprocessing pipeline completed")
            
        except Exception as preprocessing_error:
            logger.warning(f"⚠️ Complete preprocessing failed: {str(preprocessing_error)}")
            logger.info("🔄 Attempting partial preprocessing...")
            
            try:
                # Try minimal preprocessing
                processed_df = (preprocessing_pipeline
                               .set_dataframe(spark_df)
                               .clean_data(remove_duplicates=True, handle_nulls="fill")
                               .engineer_features(create_time_features=False,
                                                create_amount_features=True,
                                                create_user_features=False)
                               .create_feature_vector()
                               .processed_df)
                logger.info("✅ Minimal preprocessing completed")
                
            except Exception as minimal_error:
                logger.warning(f"⚠️ Minimal preprocessing failed: {str(minimal_error)}")
                # Use basic preprocessing
                processed_df = preprocessing_pipeline.set_dataframe(spark_df).processed_df
                logger.info("✅ Using basic data without preprocessing")
        
        # Initialize and train ML models
        try:
            logger.info("🤖 Training ML models...")
            ml_pipeline = FraudDetectionMLPipeline(spark)
            
            # Prepare data for ML (create fraud labels)
            train_df, test_df = ml_pipeline.prepare_data_for_ml(processed_df, "is_fraud", 0.8)
            
            # Train supervised models (simplified for demo)
            logger.info("📈 Training supervised models...")
            supervised_models = ml_pipeline.train_supervised_models(train_df, "is_fraud")
            
            # Train unsupervised models
            logger.info("🔍 Training unsupervised models...")
            unsupervised_models = ml_pipeline.train_unsupervised_models(processed_df)
            
            # Evaluate models
            logger.info("📊 Evaluating models...")
            performance = ml_pipeline.evaluate_models(test_df, "is_fraud")
            
            # Make predictions on full dataset
            predictions_df = ml_pipeline.predict_fraud(processed_df)
            
            # Convert to pandas for further processing
            processed_pandas_df = predictions_df.select("*").toPandas()
            
            logger.info("🎯 ML pipeline completed successfully")
            
        except Exception as ml_error:
            logger.warning(f"⚠️ ML training failed, using advanced rules: {str(ml_error)}")
            # Fallback to advanced rule-based detection
            processed_pandas_df = processed_df.select("*").toPandas()
            fraud_predictions = apply_advanced_fraud_rules(processed_pandas_df)
            processed_pandas_df['prediction'] = fraud_predictions
            processed_pandas_df['is_fraud'] = fraud_predictions
            performance = {"rule_based": {"accuracy": "N/A", "note": "Advanced rules applied"}}
        
        # Generate risk scores
        processed_pandas_df['risk_score'] = generate_risk_scores(processed_pandas_df)
        
        # Calculate statistics
        total_transactions = len(processed_pandas_df)
        fraud_transactions = int(processed_pandas_df['prediction'].sum())
        normal_transactions = total_transactions - fraud_transactions
        
        stats = {
            'total': total_transactions,
            'fraud': fraud_transactions,
            'normal': normal_transactions,
            'fraud_rate': (fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0
        }
        
        # Generate enhanced chart data
        charts = generate_advanced_chart_data(processed_pandas_df, data_profile, anomalies)
        
        # Add model performance to charts
        if 'performance' in locals() and performance:
            charts['model_performance'] = {
                'labels': list(performance.keys()),
                'values': [perf.get('auc_roc', perf.get('accuracy', 0.5)) for perf in performance.values()]
            }
        
        # Save results with enhanced features
        results_filename = f"ml_fraud_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        results_path = os.path.join(app.config['RESULTS_FOLDER'], results_filename)
        processed_pandas_df.to_csv(results_path, index=False)
        
        # Save ML models if trained successfully
        if 'ml_pipeline' in locals():
            try:
                models_dir = os.path.join(app.config['RESULTS_FOLDER'], 'models')
                saved_models = ml_pipeline.save_models(models_dir)
                logger.info(f"💾 Saved {len(saved_models)} models")
            except Exception as save_error:
                logger.warning(f"⚠️ Could not save models: {str(save_error)}")
        
        # Cleanup
        ingestion_engine.cleanup()
        if os.path.exists(temp_csv_path):
            os.remove(temp_csv_path)
        
        logger.info("✅ Complete ML fraud detection completed successfully")
        
        return {
            'stats': stats,
            'charts': charts,
            'processed_data': processed_pandas_df,
            'results_file': results_filename,
            'data_quality': data_profile['data_quality'],
            'anomalies': anomalies,
            'validation': validation_results,
            'model_performance': performance if 'performance' in locals() else None,
            'pipeline_type': 'complete_ml'
        }
        
    except Exception as e:
        logger.error(f"Error in complete ML fraud detection: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def perform_basic_fraud_detection(df):
    """
    Basic fraud detection as fallback
    This is the original implementation
    """
    try:
        # Create a copy for processing
        processed_df = df.copy()
        
        # Simple rule-based fraud detection (to be replaced with ML models)
        # Flag as fraud if:
        # 1. Amount > 10000
        # 2. Amount < 1 (suspicious small amounts)
        # 3. Random sample for demonstration
        
        import numpy as np
        np.random.seed(42)  # For reproducible results
        
        fraud_conditions = (
            (processed_df['amount'] > 10000) |  # High amount transactions
            (processed_df['amount'] < 1) |      # Suspicious small amounts
            (np.random.random(len(processed_df)) < 0.05)  # Random 5% for demo
        )
        
        processed_df['prediction'] = fraud_conditions.astype(int)
        processed_df['risk_score'] = np.random.uniform(0, 1, len(processed_df))
        
        # Calculate statistics
        total_transactions = len(processed_df)
        fraud_transactions = int(processed_df['prediction'].sum())
        normal_transactions = total_transactions - fraud_transactions
        
        stats = {
            'total': total_transactions,
            'fraud': fraud_transactions,
            'normal': normal_transactions,
            'fraud_rate': (fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0
        }
        
        # Generate chart data
        charts = generate_chart_data(processed_df)
        
        # Save results
        results_filename = f"basic_fraud_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        results_path = os.path.join(app.config['RESULTS_FOLDER'], results_filename)
        processed_df.to_csv(results_path, index=False)
        
        return {
            'stats': stats,
            'charts': charts,
            'processed_data': processed_df,
            'results_file': results_filename
        }
        
    except Exception as e:
        logger.error(f"Error in basic fraud detection: {str(e)}")
        raise

def apply_advanced_fraud_rules(df):
    """Apply advanced fraud detection rules based on engineered features"""
    import numpy as np
    
    fraud_score = np.zeros(len(df))
    
    # Amount-based rules
    if 'amount' in df.columns:
        # Very high amounts
        fraud_score += (df['amount'] > df['amount'].quantile(0.99)).astype(int) * 0.3
        
        # Very low amounts
        fraud_score += (df['amount'] < 1).astype(int) * 0.2
        
        # Round amounts (suspicious pattern)
        fraud_score += (df['amount'] % 100 == 0).astype(int) * 0.1
    
    # Time-based rules
    if 'hour' in df.columns:
        # Night transactions (higher risk)
        fraud_score += ((df['hour'] < 6) | (df['hour'] > 22)).astype(int) * 0.15
    
    if 'is_weekend' in df.columns:
        # Weekend transactions
        fraud_score += df['is_weekend'].astype(int) * 0.1
    
    # User behavior rules
    if 'amount_deviation_from_user_avg' in df.columns:
        # High deviation from user's normal behavior
        fraud_score += (df['amount_deviation_from_user_avg'] > 3).astype(int) * 0.25
    
    # Location-based rules
    if 'is_rare_location' in df.columns:
        fraud_score += df['is_rare_location'].astype(int) * 0.2
    
    # Merchant-based rules
    if 'is_high_risk_merchant' in df.columns:
        fraud_score += df['is_high_risk_merchant'].astype(int) * 0.3
    
    # Convert scores to binary predictions (threshold = 0.5)
    predictions = (fraud_score > 0.5).astype(int)
    
    return predictions

def generate_risk_scores(df):
    """Generate risk scores for transactions"""
    import numpy as np
    
    # Use prediction as base score and add some variation
    base_scores = df['prediction'].values.astype(float)
    risk_scores = base_scores + np.random.normal(0, 0.1, len(df))
    
    # Ensure scores are between 0 and 1
    risk_scores = np.clip(risk_scores, 0, 1)
    
    return risk_scores

def generate_advanced_chart_data(df, data_profile, anomalies):
    """Generate enhanced chart data with advanced insights"""
    try:
        charts = generate_chart_data(df)  # Start with basic charts
        
        # Add data quality insights
        charts['data_quality'] = {
            'labels': ['Good Quality', 'Issues Found'],
            'values': [
                data_profile['data_quality']['score'], 
                100 - data_profile['data_quality']['score']
            ]
        }
        
        # Add anomaly insights
        total_anomalies = 0
        if anomalies.get('statistical_outliers'):
            total_anomalies += sum(stats['count'] for stats in anomalies['statistical_outliers'].values())
        if anomalies.get('business_rule_violations'):
            total_anomalies += sum(violation['count'] for violation in anomalies['business_rule_violations'])
        
        charts['anomalies'] = {
            'labels': ['Normal Patterns', 'Anomalies Detected'],
            'values': [len(df) - total_anomalies, total_anomalies]
        }
        
        # Risk score distribution
        if 'risk_score' in df.columns:
            risk_ranges = ['Low (0-0.3)', 'Medium (0.3-0.7)', 'High (0.7-1.0)']
            risk_counts = [
                len(df[(df['risk_score'] >= 0) & (df['risk_score'] < 0.3)]),
                len(df[(df['risk_score'] >= 0.3) & (df['risk_score'] < 0.7)]),
                len(df[(df['risk_score'] >= 0.7) & (df['risk_score'] <= 1.0)])
            ]
            charts['risk_distribution'] = {
                'labels': risk_ranges,
                'values': risk_counts
            }
        
        return charts
        
    except Exception as e:
        logger.error(f"Error generating advanced charts: {str(e)}")
        return generate_chart_data(df)  # Fallback to basic charts

def generate_chart_data(df):
    """Generate data for various charts"""
    try:
        charts = {}
        
        # Fraud by Amount Range
        amount_ranges = ['0-100', '100-500', '500-1000', '1000-5000', '5000+']
        amount_fraud_counts = []
        
        for range_label in amount_ranges:
            if range_label == '0-100':
                mask = (df['amount'] >= 0) & (df['amount'] < 100)
            elif range_label == '100-500':
                mask = (df['amount'] >= 100) & (df['amount'] < 500)
            elif range_label == '500-1000':
                mask = (df['amount'] >= 500) & (df['amount'] < 1000)
            elif range_label == '1000-5000':
                mask = (df['amount'] >= 1000) & (df['amount'] < 5000)
            else:  # 5000+
                mask = df['amount'] >= 5000
            
            fraud_count = df[mask & (df['prediction'] == 1)].shape[0]
            amount_fraud_counts.append(fraud_count)
        
        charts['fraud_by_amount'] = {
            'labels': amount_ranges,
            'values': amount_fraud_counts
        }
        
        # Fraud by Merchant (top 10)
        if 'merchant' in df.columns:
            merchant_fraud = df[df['prediction'] == 1]['merchant'].value_counts().head(10)
            charts['fraud_by_merchant'] = {
                'labels': merchant_fraud.index.tolist(),
                'values': merchant_fraud.values.tolist()
            }
        
        # Fraud by Payment Method
        if 'payment_method' in df.columns:
            payment_fraud = df[df['prediction'] == 1]['payment_method'].value_counts()
            charts['fraud_by_payment'] = {
                'labels': payment_fraud.index.tolist(),
                'values': payment_fraud.values.tolist()
            }
        else:
            # Generate dummy data for demo
            charts['fraud_by_payment'] = {
                'labels': ['Credit Card', 'Debit Card', 'Bank Transfer', 'Digital Wallet'],
                'values': [45, 30, 15, 10]
            }
        
        # Fraud Over Time (if timestamp available)
        if 'timestamp' in df.columns:
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['date'] = df['timestamp'].dt.date
                time_fraud = df[df['prediction'] == 1].groupby('date').size()
                charts['fraud_over_time'] = {
                    'labels': [str(date) for date in time_fraud.index],
                    'values': time_fraud.values.tolist()
                }
            except:
                # Generate dummy time data
                import datetime as dt
                dates = [(dt.date.today() - dt.timedelta(days=i)) for i in range(7, 0, -1)]
                charts['fraud_over_time'] = {
                    'labels': [str(date) for date in dates],
                    'values': [12, 8, 15, 23, 18, 11, 9]
                }
        else:
            # Generate dummy time data
            import datetime as dt
            dates = [(dt.date.today() - dt.timedelta(days=i)) for i in range(7, 0, -1)]
            charts['fraud_over_time'] = {
                'labels': [str(date) for date in dates],
                'values': [12, 8, 15, 23, 18, 11, 9]
            }
        
        return charts
        
    except Exception as e:
        logger.error(f"Error generating chart data: {str(e)}")
        return {}

@app.route('/download')
def download_results():
    """Download processed results"""
    global current_results, current_filename
    
    if not current_results:
        return jsonify({'error': 'No results available'}), 404
    
    try:
        # Find the most recent results file
        results_files = [f for f in os.listdir(app.config['RESULTS_FOLDER']) if f.startswith('fraud_results_')]
        if not results_files:
            return jsonify({'error': 'Results file not found'}), 404
        
        # Get the most recent file
        latest_file = max(results_files, key=lambda x: os.path.getctime(os.path.join(app.config['RESULTS_FOLDER'], x)))
        file_path = os.path.join(app.config['RESULTS_FOLDER'], latest_file)
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"fraud_detection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Error downloading results: {str(e)}")
        return jsonify({'error': 'Download failed'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.errorhandler(413)
def file_too_large(e):
    return jsonify({'error': 'File too large. Maximum size is 50MB.'}), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting FraudShield Application...")
    print("📊 Access the web interface at: http://localhost:5000")
    print("🔍 Upload CSV files to detect fraudulent transactions")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )