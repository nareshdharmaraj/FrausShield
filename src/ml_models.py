"""
FraudShield Machine Learning Models
Advanced fraud detection using supervised and unsupervised ML algorithms
"""

import logging
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
import os

# Type imports for better IDE support
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Import types only for type checking, not runtime
    from pyspark.sql import DataFrame, SparkSession
else:
    # Use Any for runtime to avoid import errors
    DataFrame = SparkSession = Any

# Core imports with error handling
try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False
    joblib = None

# PySpark imports with error handling
try:
    from pyspark.sql import DataFrame as PySparkDataFrame, SparkSession as PySparkSession
    from pyspark.sql.functions import col, when, lit
    from pyspark.sql.types import DoubleType
    
    # PySpark ML imports
    from pyspark.ml.classification import (
        LogisticRegression, RandomForestClassifier, 
        GBTClassifier, DecisionTreeClassifier
    )
    from pyspark.ml.clustering import KMeans
    from pyspark.ml.feature import VectorAssembler, StandardScaler
    from pyspark.ml.evaluation import (
        BinaryClassificationEvaluator, 
        MulticlassClassificationEvaluator
    )
    from pyspark.ml.tuning import ParamGridBuilder, CrossValidator
    from pyspark.ml import Pipeline
    from pyspark.ml.stat import Correlation
    
    PYSPARK_AVAILABLE = True
except ImportError as e:
    PYSPARK_AVAILABLE = False
    # Create runtime fallbacks
    PySparkDataFrame = PySparkSession = object

# Scikit-learn for additional algorithms
try:
    from sklearn.ensemble import IsolationForest
    from sklearn.cluster import DBSCAN
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split
    import pandas as pd
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    pd = np = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudDetectionMLPipeline:
    """
    Comprehensive ML pipeline for fraud detection using both supervised and unsupervised methods
    """
    
    def __init__(self, spark_session: "SparkSession"):
        """Initialize ML pipeline with Spark session"""
        if not PYSPARK_AVAILABLE:
            raise ImportError("PySpark is required for FraudDetectionMLPipeline")
            
        self.spark = spark_session
        self.models = {}
        self.model_performance = {}
        self.feature_importance = {}
        self.best_model = None
        self.best_model_name = None
        self.training_data = None
        self.test_data = None
        
    def prepare_data_for_ml(self, df: "DataFrame", 
                           target_column: str = "is_fraud",
                           train_ratio: float = 0.8) -> Tuple["DataFrame", "DataFrame"]:
        """
        Prepare data for machine learning by creating target labels and splitting
        
        Args:
            df: Input DataFrame with features
            target_column: Name of target column to create
            train_ratio: Ratio for train/test split
            
        Returns:
            Tuple of (training_data, test_data)
        """
        try:
            logger.info("🎯 Preparing data for ML training...")
            
            # Create fraud labels if they don't exist
            if target_column not in df.columns:
                # Use existing prediction column or create labels based on advanced rules
                if "prediction" in df.columns:
                    df = df.withColumn(target_column, col("prediction").cast("double"))
                else:
                    df = self._create_fraud_labels(df, target_column)
            
            # Ensure we have required columns
            required_cols = ["features", target_column]
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            # Split data
            train_df, test_df = df.randomSplit([train_ratio, 1 - train_ratio], seed=42)
            
            train_count = train_df.count()
            test_count = test_df.count()
            fraud_count = df.filter(col(target_column) == 1).count()
            
            logger.info(f"📊 Data split: {train_count} train, {test_count} test samples")
            logger.info(f"🚨 Fraud rate: {(fraud_count / df.count() * 100):.2f}%")
            
            self.training_data = train_df
            self.test_data = test_df
            
            return train_df, test_df
            
        except Exception as e:
            logger.error(f"❌ Error preparing data for ML: {str(e)}")
            raise
    
    def _create_fraud_labels(self, df: "DataFrame", target_column: str) -> "DataFrame":
        """Create fraud labels based on advanced business rules"""
        
        # Get available columns
        available_cols = df.columns
        
        # Start with basic amount-based rules (always available)
        amount_quantile = df.approxQuantile("amount", [0.99], 0.05)[0]
        fraud_conditions = (
            # Very high amounts (top 1%)
            (col("amount") > amount_quantile) |
            
            # Very low amounts (suspicious)
            (col("amount") < 1)
        )
        
        # Add time-based rules if hour column exists
        if "hour" in available_cols:
            fraud_conditions = fraud_conditions | (
                ((col("hour") < 6) | (col("hour") > 22)) & (col("amount") > 1000)
            )
        
        # Add weekend rules if available
        if "is_weekend" in available_cols:
            fraud_conditions = fraud_conditions | (
                (col("is_weekend") == 1) & (col("amount") > 5000)
            )
        
        # Add user behavior rules if available
        if "amount_deviation_from_user_avg" in available_cols:
            fraud_conditions = fraud_conditions | (
                col("amount_deviation_from_user_avg") > 3
            )
        
        # Add location rules if available
        if "is_rare_location" in available_cols:
            fraud_conditions = fraud_conditions | (
                (col("is_rare_location") == 1) & (col("amount") > 1000)
            )
        
        # Add merchant rules if available
        if "is_high_risk_merchant" in available_cols:
            fraud_conditions = fraud_conditions | (
                col("is_high_risk_merchant") == 1
            )
        
        # Add round amount rules if available
        if "is_round_amount" in available_cols:
            fraud_conditions = fraud_conditions | (
                (col("is_round_amount") == 1) & (col("amount") > 10000)
            )
        
        df = df.withColumn(target_column, when(fraud_conditions, 1.0).otherwise(0.0))
        
        return df
    
    def train_supervised_models(self, train_df: "DataFrame", 
                               target_column: str = "is_fraud") -> Dict[str, Any]:
        """
        Train multiple supervised ML models for fraud detection
        
        Args:
            train_df: Training DataFrame
            target_column: Target column name
            
        Returns:
            Dictionary with trained models and performance metrics
        """
        try:
            logger.info("🤖 Training supervised ML models...")
            
            models_config = {
                "logistic_regression": {
                    "model": LogisticRegression(
                        featuresCol="features",
                        labelCol=target_column,
                        maxIter=100,
                        regParam=0.01
                    ),
                    "param_grid": ParamGridBuilder() \
                        .addGrid(LogisticRegression.regParam, [0.01, 0.1, 0.5]) \
                        .addGrid(LogisticRegression.elasticNetParam, [0.0, 0.5, 1.0]) \
                        .build()
                },
                
                "random_forest": {
                    "model": RandomForestClassifier(
                        featuresCol="features",
                        labelCol=target_column,
                        numTrees=50,
                        maxDepth=10,
                        seed=42
                    ),
                    "param_grid": ParamGridBuilder() \
                        .addGrid(RandomForestClassifier.numTrees, [20, 50, 100]) \
                        .addGrid(RandomForestClassifier.maxDepth, [5, 10, 15]) \
                        .build()
                },
                
                "gradient_boosting": {
                    "model": GBTClassifier(
                        featuresCol="features",
                        labelCol=target_column,
                        maxIter=50,
                        maxDepth=6,
                        seed=42
                    ),
                    "param_grid": ParamGridBuilder() \
                        .addGrid(GBTClassifier.maxIter, [20, 50, 100]) \
                        .addGrid(GBTClassifier.maxDepth, [4, 6, 8]) \
                        .build()
                },
                
                "decision_tree": {
                    "model": DecisionTreeClassifier(
                        featuresCol="features",
                        labelCol=target_column,
                        maxDepth=10,
                        seed=42
                    ),
                    "param_grid": ParamGridBuilder() \
                        .addGrid(DecisionTreeClassifier.maxDepth, [5, 10, 15, 20]) \
                        .build()
                }
            }
            
            # Train each model
            for model_name, config in models_config.items():
                logger.info(f"📈 Training {model_name}...")
                
                try:
                    # Create evaluator
                    evaluator = BinaryClassificationEvaluator(
                        labelCol=target_column,
                        rawPredictionCol="rawPrediction",
                        metricName="areaUnderROC"
                    )
                    
                    # Cross-validation for hyperparameter tuning
                    cv = CrossValidator(
                        estimator=config["model"],
                        estimatorParamMaps=config["param_grid"],
                        evaluator=evaluator,
                        numFolds=3,
                        seed=42
                    )
                    
                    # Fit model
                    cv_model = cv.fit(train_df)
                    best_model = cv_model.bestModel
                    
                    # Store model
                    self.models[model_name] = {
                        "model": best_model,
                        "cv_model": cv_model,
                        "evaluator": evaluator
                    }
                    
                    logger.info(f"✅ {model_name} trained successfully")
                    
                except Exception as e:
                    logger.error(f"❌ Error training {model_name}: {str(e)}")
                    continue
            
            logger.info(f"🎯 Trained {len(self.models)} supervised models")
            return self.models
            
        except Exception as e:
            logger.error(f"❌ Error in supervised model training: {str(e)}")
            raise
    
    def train_unsupervised_models(self, df: "DataFrame") -> Dict[str, Any]:
        """
        Train unsupervised models for anomaly detection
        
        Args:
            df: DataFrame with features
            
        Returns:
            Dictionary with trained unsupervised models
        """
        try:
            logger.info("🔍 Training unsupervised anomaly detection models...")
            
            unsupervised_models = {}
            
            # KMeans clustering for anomaly detection
            try:
                logger.info("📊 Training KMeans clustering...")
                
                # Determine optimal k using elbow method (simplified)
                k_values = [2, 3, 4, 5, 8, 10]
                best_k = 5  # Default
                
                for k in k_values:
                    kmeans = KMeans(
                        featuresCol="features",
                        predictionCol="cluster",
                        k=k,
                        seed=42
                    )
                    
                    model = kmeans.fit(df)
                    # Could implement proper elbow method here
                    
                    if k == 5:  # Use k=5 for demonstration
                        unsupervised_models["kmeans"] = {
                            "model": model,
                            "k": k,
                            "type": "clustering"
                        }
                        break
                
                logger.info(f"✅ KMeans clustering trained with k={best_k}")
                
            except Exception as e:
                logger.error(f"❌ Error training KMeans: {str(e)}")
            
            # Isolation Forest using scikit-learn (if available)
            if SKLEARN_AVAILABLE:
                try:
                    logger.info("🌲 Training Isolation Forest...")
                    
                    # Convert to pandas for sklearn
                    pandas_df = df.select("features").toPandas()
                    
                    # Extract feature vectors (assuming they're DenseVectors)
                    if len(pandas_df) > 0:
                        # Convert Spark vectors to numpy arrays
                        features_array = np.array([
                            row.features.toArray() if hasattr(row.features, 'toArray') 
                            else np.array(row.features) 
                            for row in pandas_df.itertuples()
                        ])
                        
                        # Train Isolation Forest
                        isolation_forest = IsolationForest(
                            contamination=0.1,  # Expect 10% anomalies
                            random_state=42,
                            n_estimators=100
                        )
                        
                        isolation_forest.fit(features_array)
                        
                        unsupervised_models["isolation_forest"] = {
                            "model": isolation_forest,
                            "type": "anomaly_detection",
                            "contamination": 0.1
                        }
                        
                        logger.info("✅ Isolation Forest trained successfully")
                
                except Exception as e:
                    logger.error(f"❌ Error training Isolation Forest: {str(e)}")
            
            self.unsupervised_models = unsupervised_models
            logger.info(f"🎯 Trained {len(unsupervised_models)} unsupervised models")
            
            return unsupervised_models
            
        except Exception as e:
            logger.error(f"❌ Error in unsupervised model training: {str(e)}")
            raise
    
    def evaluate_models(self, test_df: "DataFrame", 
                       target_column: str = "is_fraud") -> Dict[str, Dict[str, float]]:
        """
        Evaluate all trained models on test data
        
        Args:
            test_df: Test DataFrame
            target_column: Target column name
            
        Returns:
            Dictionary with performance metrics for each model
        """
        try:
            logger.info("📊 Evaluating model performance...")
            
            performance_results = {}
            
            # Evaluate supervised models
            for model_name, model_info in self.models.items():
                try:
                    logger.info(f"🔍 Evaluating {model_name}...")
                    
                    model = model_info["model"]
                    evaluator = model_info["evaluator"]
                    
                    # Make predictions
                    predictions = model.transform(test_df)
                    
                    # Calculate metrics
                    auc_roc = evaluator.evaluate(predictions)
                    
                    # Additional metrics
                    accuracy_evaluator = MulticlassClassificationEvaluator(
                        labelCol=target_column,
                        predictionCol="prediction",
                        metricName="accuracy"
                    )
                    
                    precision_evaluator = MulticlassClassificationEvaluator(
                        labelCol=target_column,
                        predictionCol="prediction",
                        metricName="weightedPrecision"
                    )
                    
                    recall_evaluator = MulticlassClassificationEvaluator(
                        labelCol=target_column,
                        predictionCol="prediction",
                        metricName="weightedRecall"
                    )
                    
                    accuracy = accuracy_evaluator.evaluate(predictions)
                    precision = precision_evaluator.evaluate(predictions)
                    recall = recall_evaluator.evaluate(predictions)
                    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
                    
                    performance_results[model_name] = {
                        "auc_roc": round(auc_roc, 4),
                        "accuracy": round(accuracy, 4),
                        "precision": round(precision, 4),
                        "recall": round(recall, 4),
                        "f1_score": round(f1_score, 4)
                    }
                    
                    logger.info(f"✅ {model_name} - AUC: {auc_roc:.4f}, Accuracy: {accuracy:.4f}")
                    
                except Exception as e:
                    logger.error(f"❌ Error evaluating {model_name}: {str(e)}")
                    continue
            
            # Find best model
            if performance_results:
                best_model_name = max(performance_results.keys(), 
                                    key=lambda x: performance_results[x]["auc_roc"])
                self.best_model_name = best_model_name
                self.best_model = self.models[best_model_name]["model"]
                
                logger.info(f"🏆 Best model: {best_model_name} (AUC: {performance_results[best_model_name]['auc_roc']:.4f})")
            
            self.model_performance = performance_results
            return performance_results
            
        except Exception as e:
            logger.error(f"❌ Error evaluating models: {str(e)}")
            raise
    
    def extract_feature_importance(self) -> Dict[str, List[Tuple[str, float]]]:
        """Extract feature importance from tree-based models"""
        try:
            importance_results = {}
            
            for model_name, model_info in self.models.items():
                model = model_info["model"]
                
                # Extract feature importance for tree-based models
                if hasattr(model, 'featureImportances'):
                    importances = model.featureImportances.toArray()
                    
                    # Create feature importance list (assuming feature names are indices)
                    feature_importance = [
                        (f"feature_{i}", float(importance)) 
                        for i, importance in enumerate(importances)
                    ]
                    
                    # Sort by importance
                    feature_importance.sort(key=lambda x: x[1], reverse=True)
                    
                    importance_results[model_name] = feature_importance[:10]  # Top 10
                    
                    logger.info(f"📋 Extracted feature importance for {model_name}")
            
            self.feature_importance = importance_results
            return importance_results
            
        except Exception as e:
            logger.error(f"❌ Error extracting feature importance: {str(e)}")
            return {}
    
    def predict_fraud(self, df: "DataFrame", 
                     model_name: str = None) -> "DataFrame":
        """
        Make fraud predictions on new data
        
        Args:
            df: DataFrame with features
            model_name: Specific model to use (if None, use best model)
            
        Returns:
            DataFrame with predictions and probabilities
        """
        try:
            # Use specified model or best model
            if model_name and model_name in self.models:
                model = self.models[model_name]["model"]
                used_model = model_name
            elif self.best_model:
                model = self.best_model
                used_model = self.best_model_name
            else:
                raise ValueError("No trained model available for prediction")
            
            logger.info(f"🔮 Making predictions using {used_model}...")
            
            # Make predictions
            predictions = model.transform(df)
            
            # Add fraud probability (for models that support it)
            if hasattr(model, 'probability'):
                # Extract probability of fraud (class 1)
                predictions = predictions.withColumn(
                    "fraud_probability",
                    col("probability").getItem(1).cast(DoubleType())
                )
            
            logger.info("✅ Predictions completed")
            return predictions
            
        except Exception as e:
            logger.error(f"❌ Error making predictions: {str(e)}")
            raise
    
    def save_models(self, output_dir: str) -> Dict[str, str]:
        """
        Save trained models to disk
        
        Args:
            output_dir: Directory to save models
            
        Returns:
            Dictionary with model names and their saved paths
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            saved_paths = {}
            
            # Save PySpark models
            for model_name, model_info in self.models.items():
                model_path = os.path.join(output_dir, f"{model_name}_spark_model")
                try:
                    model_info["model"].write().overwrite().save(model_path)
                    saved_paths[model_name] = model_path
                    logger.info(f"💾 Saved {model_name} to {model_path}")
                except Exception as e:
                    logger.error(f"❌ Error saving {model_name}: {str(e)}")
            
            # Save sklearn models (if any)
            if hasattr(self, 'unsupervised_models'):
                for model_name, model_info in self.unsupervised_models.items():
                    if model_info["type"] == "anomaly_detection":
                        model_path = os.path.join(output_dir, f"{model_name}_sklearn_model.pkl")
                        try:
                            joblib.dump(model_info["model"], model_path)
                            saved_paths[model_name] = model_path
                            logger.info(f"💾 Saved {model_name} to {model_path}")
                        except Exception as e:
                            logger.error(f"❌ Error saving {model_name}: {str(e)}")
            
            # Save performance metrics
            metrics_path = os.path.join(output_dir, "model_performance.json")
            if self.model_performance:
                import json
                with open(metrics_path, 'w') as f:
                    json.dump(self.model_performance, f, indent=2)
                saved_paths["performance_metrics"] = metrics_path
            
            logger.info(f"✅ Saved {len(saved_paths)} models and metrics")
            return saved_paths
            
        except Exception as e:
            logger.error(f"❌ Error saving models: {str(e)}")
            raise
    
    def get_model_summary(self) -> Dict[str, Any]:
        """Get comprehensive summary of all models and their performance"""
        
        summary = {
            "models_trained": list(self.models.keys()),
            "best_model": self.best_model_name,
            "performance_metrics": self.model_performance,
            "feature_importance": self.feature_importance,
            "training_info": {
                "training_samples": self.training_data.count() if self.training_data else 0,
                "test_samples": self.test_data.count() if self.test_data else 0,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        if hasattr(self, 'unsupervised_models'):
            summary["unsupervised_models"] = list(self.unsupervised_models.keys())
        
        return summary

# Convenience function for complete ML pipeline
def train_fraud_detection_models(df: "DataFrame", 
                                spark_session: "SparkSession",
                                target_column: str = "is_fraud",
                                save_models: bool = True,
                                output_dir: str = "models") -> Tuple[FraudDetectionMLPipeline, Dict[str, Any]]:
    """
    Complete ML pipeline for fraud detection
    
    Args:
        df: Preprocessed DataFrame with features
        spark_session: Spark session
        target_column: Target column name
        save_models: Whether to save trained models
        output_dir: Directory to save models
        
    Returns:
        Tuple of (ML pipeline object, model summary)
    """
    try:
        # Initialize ML pipeline
        ml_pipeline = FraudDetectionMLPipeline(spark_session)
        
        # Prepare data
        train_df, test_df = ml_pipeline.prepare_data_for_ml(df, target_column)
        
        # Train supervised models
        supervised_models = ml_pipeline.train_supervised_models(train_df, target_column)
        
        # Train unsupervised models
        unsupervised_models = ml_pipeline.train_unsupervised_models(df)
        
        # Evaluate models
        performance = ml_pipeline.evaluate_models(test_df, target_column)
        
        # Extract feature importance
        feature_importance = ml_pipeline.extract_feature_importance()
        
        # Save models if requested
        if save_models:
            saved_paths = ml_pipeline.save_models(output_dir)
            logger.info(f"💾 Models saved to: {output_dir}")
        
        # Get summary
        summary = ml_pipeline.get_model_summary()
        
        logger.info("🎯 ML pipeline training completed successfully")
        
        return ml_pipeline, summary
        
    except Exception as e:
        logger.error(f"❌ Error in ML pipeline: {str(e)}")
        raise