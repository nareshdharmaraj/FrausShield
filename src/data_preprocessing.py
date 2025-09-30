"""
FraudShield Data Preprocessing Pipeline
Advanced feature engineering, data cleaning, and transformation using PySpark
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import re

# PySpark imports
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import DoubleType, IntegerType, StringType, TimestampType
from pyspark.sql.functions import (
    col, when, isnan, isnull, regexp_replace, trim, lower, upper,
    split, regexp_extract, to_timestamp, date_format, hour, dayofweek,
    lag, lead, avg, sum as spark_sum, count, stddev, min as spark_min,
    max as spark_max, percentile_approx, log, sqrt, abs as spark_abs,
    monotonically_increasing_id, row_number, rank, dense_rank
)
from pyspark.sql.window import Window

# PySpark ML imports  
from pyspark.ml.feature import (
    StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler,
    MinMaxScaler, Bucketizer, QuantileDiscretizer, PCA,
    ChiSqSelector, UnivariateFeatureSelector
)
from pyspark.ml import Pipeline
from pyspark.ml.stat import Correlation

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataPreprocessingPipeline:
    """
    Advanced data preprocessing pipeline for fraud detection
    """
    
    def __init__(self, spark_session: SparkSession = None):
        """Initialize preprocessing pipeline"""
        self.spark = spark_session
        self.df = None
        self.processed_df = None
        self.feature_columns = []
        self.categorical_columns = []
        self.numerical_columns = []
        self.pipeline = None
        self.preprocessing_stats = {}
        
    def set_dataframe(self, df: DataFrame) -> 'DataPreprocessingPipeline':
        """Set the DataFrame to be processed"""
        self.df = df
        self._analyze_column_types()
        return self
    
    def _analyze_column_types(self):
        """Analyze and categorize column types"""
        if self.df is None:
            return
        
        categorical_cols = []
        numerical_cols = []
        
        for field in self.df.schema.fields:
            if isinstance(field.dataType, (StringType,)):
                # Exclude ID columns from categorical processing
                if not any(id_term in field.name.lower() for id_term in ['id', 'key', 'uuid']):
                    categorical_cols.append(field.name)
            elif isinstance(field.dataType, (DoubleType, IntegerType)):
                numerical_cols.append(field.name)
        
        self.categorical_columns = categorical_cols
        self.numerical_columns = numerical_cols
        
        logger.info(f"📊 Identified {len(categorical_cols)} categorical and {len(numerical_cols)} numerical columns")
    
    def clean_data(self, 
                   remove_duplicates: bool = True,
                   handle_nulls: str = "drop",  # "drop", "fill", "median", "mode"
                   null_threshold: float = 0.8) -> 'DataPreprocessingPipeline':
        """
        Clean data by handling missing values, duplicates, and invalid data
        
        Args:
            remove_duplicates: Whether to remove duplicate rows
            handle_nulls: Strategy for handling null values
            null_threshold: Threshold for dropping columns with too many nulls
        """
        try:
            logger.info("🧹 Starting data cleaning...")
            
            if self.df is None:
                raise ValueError("DataFrame not set. Use set_dataframe() first.")
            
            df = self.df
            initial_count = df.count()
            
            # Remove duplicates
            if remove_duplicates:
                df = df.dropDuplicates()
                after_dedup_count = df.count()
                duplicates_removed = initial_count - after_dedup_count
                logger.info(f"🔄 Removed {duplicates_removed} duplicate rows")
            
            # Handle columns with excessive nulls
            total_rows = df.count()
            columns_to_drop = []
            
            for column in df.columns:
                # Get column data type
                column_type = dict(df.dtypes)[column]
                
                # Apply appropriate null checking based on data type
                if column_type in ['double', 'float', 'int', 'bigint']:
                    # For numeric columns, check both null and NaN
                    null_count = df.filter(col(column).isNull() | isnan(col(column))).count()
                else:
                    # For string and other columns, check only null
                    null_count = df.filter(col(column).isNull()).count()
                
                null_ratio = null_count / total_rows if total_rows > 0 else 0
                
                if null_ratio > null_threshold:
                    columns_to_drop.append(column)
                    logger.warning(f"⚠️ Dropping column '{column}' with {null_ratio:.1%} null values")
            
            if columns_to_drop:
                df = df.drop(*columns_to_drop)
            
            # Handle remaining null values
            if handle_nulls == "drop":
                df = df.dropna()
                logger.info("🗑️ Dropped rows with null values")
            
            elif handle_nulls == "fill":
                # Fill numerical columns with median
                for col_name in self.numerical_columns:
                    if col_name in df.columns:
                        median_val = df.approxQuantile(col_name, [0.5], 0.05)[0]
                        df = df.fillna({col_name: median_val})
                
                # Fill categorical columns with mode
                for col_name in self.categorical_columns:
                    if col_name in df.columns:
                        try:
                            # Get the most frequent value (mode)
                            mode_row = (df.filter(col(col_name).isNotNull())
                                       .groupBy(col_name)
                                       .count()
                                       .orderBy(col("count").desc())
                                       .first())
                            if mode_row and mode_row[col_name] is not None:
                                mode_val = mode_row[col_name]
                                df = df.fillna({col_name: mode_val})
                            else:
                                # Fallback to a default value
                                df = df.fillna({col_name: "Unknown"})
                        except Exception as e:
                            logger.warning(f"⚠️ Could not fill mode for {col_name}: {str(e)}")
                            # Use a simple default fill
                            df = df.fillna({col_name: "Unknown"})
                
                logger.info("🔄 Filled null values with median/mode")
            
            # Clean string columns
            for col_name in self.categorical_columns:
                if col_name in df.columns:
                    df = df.withColumn(col_name, 
                                     regexp_replace(trim(col(col_name)), r'\s+', ' '))
            
            final_count = df.count()
            rows_cleaned = initial_count - final_count
            
            self.processed_df = df
            self.preprocessing_stats["cleaning"] = {
                "initial_rows": initial_count,
                "final_rows": final_count,
                "rows_removed": rows_cleaned,
                "columns_dropped": columns_to_drop
            }
            
            logger.info(f"✅ Data cleaning completed. Removed {rows_cleaned} rows")
            return self
            
        except Exception as e:
            logger.error(f"❌ Error during data cleaning: {str(e)}")
            raise
    
    def engineer_features(self, create_time_features: bool = True,
                         create_amount_features: bool = True,
                         create_user_features: bool = True) -> 'DataPreprocessingPipeline':
        """
        Engineer new features from existing data
        
        Args:
            create_time_features: Create time-based features
            create_amount_features: Create amount-based features  
            create_user_features: Create user behavior features
        """
        try:
            logger.info("⚙️ Engineering features...")
            
            df = self.processed_df if self.processed_df is not None else self.df
            
            # Time-based features
            if create_time_features and "timestamp" in df.columns:
                df = self._create_time_features(df)
            
            # Amount-based features
            if create_amount_features and "amount" in df.columns:
                df = self._create_amount_features(df)
            
            # User behavior features
            if create_user_features and "user_id" in df.columns:
                df = self._create_user_features(df)
            
            # Location-based features
            if "location" in df.columns:
                df = self._create_location_features(df)
            
            # Merchant-based features
            if "merchant" in df.columns:
                df = self._create_merchant_features(df)
            
            self.processed_df = df
            logger.info("✅ Feature engineering completed")
            return self
            
        except Exception as e:
            logger.error(f"❌ Error during feature engineering: {str(e)}")
            raise
    
    def _create_time_features(self, df: DataFrame) -> DataFrame:
        """Create time-based features"""
        try:
            # Convert timestamp to proper format
            df = df.withColumn("timestamp_parsed", 
                             to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss"))
            
            # Extract time components
            df = (df.withColumn("hour", hour(col("timestamp_parsed")))
                   .withColumn("day_of_week", dayofweek(col("timestamp_parsed")))
                   .withColumn("is_weekend", when(col("day_of_week").isin([1, 7]), 1).otherwise(0))
                   .withColumn("is_night", when((col("hour") >= 22) | (col("hour") <= 6), 1).otherwise(0))
                   .withColumn("is_business_hours", when((col("hour") >= 9) & (col("hour") <= 17), 1).otherwise(0)))
            
            logger.info("⏰ Created time-based features: hour, day_of_week, is_weekend, is_night, is_business_hours")
            return df
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create time features: {str(e)}")
            return df
    
    def _create_amount_features(self, df: DataFrame) -> DataFrame:
        """Create amount-based features"""
        try:
            # Amount categories
            df = df.withColumn("amount_log", log(col("amount") + 1))
            
            # Amount buckets
            amount_quantiles = df.approxQuantile("amount", [0.25, 0.5, 0.75, 0.9, 0.95], 0.05)
            
            df = (df.withColumn("is_micro_transaction", when(col("amount") < amount_quantiles[0], 1).otherwise(0))
                   .withColumn("is_large_transaction", when(col("amount") > amount_quantiles[3], 1).otherwise(0))
                   .withColumn("is_very_large_transaction", when(col("amount") > amount_quantiles[4], 1).otherwise(0)))
            
            # Round amount patterns (could indicate automated/suspicious transactions)
            df = df.withColumn("is_round_amount", 
                             when(col("amount") % 100 == 0, 1).otherwise(0))
            
            logger.info("💰 Created amount-based features: amount_log, transaction size categories, round amounts")
            return df
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create amount features: {str(e)}")
            return df
    
    def _create_user_features(self, df: DataFrame) -> DataFrame:
        """Create user behavior features"""
        try:
            # Window for user-based calculations
            user_window = Window.partitionBy("user_id").orderBy("timestamp_parsed")
            
            # User transaction frequency and patterns
            user_stats = (df.groupBy("user_id")
                         .agg(count("*").alias("user_transaction_count"),
                              avg("amount").alias("user_avg_amount"),
                              stddev("amount").alias("user_amount_stddev"),
                              spark_min("amount").alias("user_min_amount"),
                              spark_max("amount").alias("user_max_amount")))
            
            # Join back to main dataframe
            df = df.join(user_stats, "user_id", "left")
            
            # Amount deviation from user's normal behavior
            df = df.withColumn("amount_deviation_from_user_avg",
                             spark_abs(col("amount") - col("user_avg_amount")) / 
                             when(col("user_amount_stddev") > 0, col("user_amount_stddev")).otherwise(1))
            
            logger.info("👤 Created user behavior features: transaction counts, amount patterns, deviations")
            return df
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create user features: {str(e)}")
            return df
    
    def _create_location_features(self, df: DataFrame) -> DataFrame:
        """Create location-based features"""
        try:
            # Location frequency
            location_stats = (df.groupBy("location")
                            .agg(count("*").alias("location_transaction_count")))
            
            df = df.join(location_stats, "location", "left")
            
            # Rare locations (potential risk indicator)
            df = df.withColumn("is_rare_location", 
                             when(col("location_transaction_count") <= 5, 1).otherwise(0))
            
            logger.info("📍 Created location-based features: transaction counts, rare locations")
            return df
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create location features: {str(e)}")
            return df
    
    def _create_merchant_features(self, df: DataFrame) -> DataFrame:
        """Create merchant-based features"""
        try:
            # Merchant statistics
            merchant_stats = (df.groupBy("merchant")
                            .agg(count("*").alias("merchant_transaction_count"),
                                 avg("amount").alias("merchant_avg_amount")))
            
            df = df.join(merchant_stats, "merchant", "left")
            
            # High-risk merchant categories (can be expanded with domain knowledge)
            high_risk_patterns = ["casino", "gambling", "betting", "adult", "crypto"]
            high_risk_condition = col("merchant").rlike("|".join(high_risk_patterns))
            df = df.withColumn("is_high_risk_merchant", when(high_risk_condition, 1).otherwise(0))
            
            logger.info("🏪 Created merchant-based features: transaction counts, averages, risk categories")
            return df
            
        except Exception as e:
            logger.warning(f"⚠️ Could not create merchant features: {str(e)}")
            return df
    
    def encode_categorical_variables(self, 
                                   encoding_method: str = "onehot",  # "onehot", "label", "target"
                                   max_categories: int = 50) -> 'DataPreprocessingPipeline':
        """
        Encode categorical variables for machine learning
        
        Args:
            encoding_method: Method for encoding ("onehot", "label", "target")
            max_categories: Maximum number of categories for one-hot encoding
        """
        try:
            logger.info(f"🏷️ Encoding categorical variables using {encoding_method} method...")
            
            df = self.processed_df if self.processed_df is not None else self.df
            
            if encoding_method == "onehot":
                df = self._apply_onehot_encoding(df, max_categories)
            elif encoding_method == "label":
                df = self._apply_label_encoding(df)
            
            self.processed_df = df
            logger.info("✅ Categorical encoding completed")
            return self
            
        except Exception as e:
            logger.error(f"❌ Error during categorical encoding: {str(e)}")
            raise
    
    def _apply_onehot_encoding(self, df: DataFrame, max_categories: int) -> DataFrame:
        """Apply one-hot encoding to categorical variables"""
        
        stages = []
        encoded_columns = []
        
        for col_name in self.categorical_columns:
            if col_name in df.columns:
                # Check cardinality
                distinct_count = df.select(col_name).distinct().count()
                
                if distinct_count <= max_categories:
                    # String indexer
                    indexer = StringIndexer(inputCol=col_name, 
                                          outputCol=f"{col_name}_indexed",
                                          handleInvalid="keep")
                    stages.append(indexer)
                    
                    # One-hot encoder
                    encoder = OneHotEncoder(inputCol=f"{col_name}_indexed",
                                          outputCol=f"{col_name}_encoded",
                                          dropLast=True)
                    stages.append(encoder)
                    
                    encoded_columns.append(f"{col_name}_encoded")
                else:
                    logger.warning(f"⚠️ Skipping {col_name} - too many categories ({distinct_count})")
        
        if stages:
            pipeline = Pipeline(stages=stages)
            model = pipeline.fit(df)
            df = model.transform(df)
            
            # Update feature columns list
            self.feature_columns.extend(encoded_columns)
            
            logger.info(f"🔄 Applied one-hot encoding to {len(encoded_columns)} categorical columns")
        
        return df
    
    def _apply_label_encoding(self, df: DataFrame) -> DataFrame:
        """Apply label encoding to categorical variables"""
        
        stages = []
        
        for col_name in self.categorical_columns:
            if col_name in df.columns:
                indexer = StringIndexer(inputCol=col_name,
                                      outputCol=f"{col_name}_indexed",
                                      handleInvalid="keep")
                stages.append(indexer)
                self.feature_columns.append(f"{col_name}_indexed")
        
        if stages:
            pipeline = Pipeline(stages=stages)
            model = pipeline.fit(df)
            df = model.transform(df)
            
            logger.info(f"🔄 Applied label encoding to {len(stages)} categorical columns")
        
        return df
    
    def scale_numerical_features(self, 
                                scaling_method: str = "standard",  # "standard", "minmax", "robust"
                                columns: List[str] = None) -> 'DataPreprocessingPipeline':
        """
        Scale numerical features
        
        Args:
            scaling_method: Scaling method to use
            columns: Specific columns to scale (if None, scale all numerical)
        """
        try:
            logger.info(f"📏 Scaling numerical features using {scaling_method} method...")
            
            df = self.processed_df if self.processed_df is not None else self.df
            
            # Determine columns to scale
            cols_to_scale = columns if columns else self.numerical_columns
            cols_to_scale = [col for col in cols_to_scale if col in df.columns]
            
            if not cols_to_scale:
                logger.warning("⚠️ No numerical columns found to scale")
                return self
            
            stages = []
            scaled_columns = []
            
            for col_name in cols_to_scale:
                # Vector assembler for individual column
                assembler = VectorAssembler(inputCols=[col_name],
                                          outputCol=f"{col_name}_vector")
                stages.append(assembler)
                
                # Scaler
                if scaling_method == "standard":
                    scaler = StandardScaler(inputCol=f"{col_name}_vector",
                                          outputCol=f"{col_name}_scaled",
                                          withStd=True,
                                          withMean=True)
                elif scaling_method == "minmax":
                    scaler = MinMaxScaler(inputCol=f"{col_name}_vector",
                                        outputCol=f"{col_name}_scaled")
                else:
                    logger.warning(f"⚠️ Unknown scaling method: {scaling_method}")
                    continue
                
                stages.append(scaler)
                scaled_columns.append(f"{col_name}_scaled")
            
            if stages:
                pipeline = Pipeline(stages=stages)
                model = pipeline.fit(df)
                df = model.transform(df)
                
                # Update feature columns
                self.feature_columns.extend(scaled_columns)
                
                logger.info(f"✅ Scaled {len(scaled_columns)} numerical columns")
            
            self.processed_df = df
            return self
            
        except Exception as e:
            logger.error(f"❌ Error during feature scaling: {str(e)}")
            raise
    
    def create_feature_vector(self, feature_cols: List[str] = None) -> 'DataPreprocessingPipeline':
        """
        Create final feature vector for machine learning
        
        Args:
            feature_cols: Specific columns to include (if None, use all engineered features)
        """
        try:
            logger.info("🔗 Creating feature vector...")
            
            df = self.processed_df if self.processed_df is not None else self.df
            
            # Determine feature columns
            if feature_cols:
                features = feature_cols
            else:
                # Use all engineered features
                features = []
                
                # Add scaled numerical features
                features.extend([col for col in df.columns if col.endswith("_scaled")])
                
                # Add encoded categorical features
                features.extend([col for col in df.columns if col.endswith("_encoded")])
                
                # Add indexed categorical features (if not using one-hot)
                features.extend([col for col in df.columns if col.endswith("_indexed")])
                
                # Add engineered features
                engineered_features = [
                    "hour", "day_of_week", "is_weekend", "is_night", "is_business_hours",
                    "amount_log", "is_micro_transaction", "is_large_transaction", 
                    "is_very_large_transaction", "is_round_amount",
                    "amount_deviation_from_user_avg", "is_rare_location", "is_high_risk_merchant"
                ]
                features.extend([col for col in engineered_features if col in df.columns])
                
                # Remove duplicates
                features = list(set(features))
            
            if not features:
                logger.warning("⚠️ No features found for vector creation")
                return self
            
            # Create feature vector
            assembler = VectorAssembler(inputCols=features, outputCol="features")
            df = assembler.transform(df)
            
            self.processed_df = df
            self.feature_columns = features
            
            logger.info(f"✅ Created feature vector with {len(features)} features")
            logger.info(f"Feature columns: {features}")
            
            return self
            
        except Exception as e:
            logger.error(f"❌ Error creating feature vector: {str(e)}")
            raise
    
    def get_preprocessing_summary(self) -> Dict[str, Any]:
        """Get summary of preprocessing steps and statistics"""
        
        summary = {
            "steps_completed": [],
            "feature_engineering": {
                "total_features": len(self.feature_columns),
                "feature_list": self.feature_columns
            },
            "data_shape": {},
            "column_analysis": {
                "categorical_columns": self.categorical_columns,
                "numerical_columns": self.numerical_columns
            }
        }
        
        if self.processed_df:
            summary["data_shape"] = {
                "rows": self.processed_df.count(),
                "columns": len(self.processed_df.columns)
            }
        
        if self.preprocessing_stats:
            summary["cleaning_stats"] = self.preprocessing_stats.get("cleaning", {})
        
        return summary
    
    def save_processed_data(self, output_path: str, format: str = "parquet") -> str:
        """
        Save processed data to file
        
        Args:
            output_path: Path to save the processed data
            format: File format ("parquet", "csv", "json")
            
        Returns:
            Path where data was saved
        """
        try:
            if self.processed_df is None:
                raise ValueError("No processed data to save")
            
            logger.info(f"💾 Saving processed data to {output_path}...")
            
            if format == "parquet":
                self.processed_df.write.mode("overwrite").parquet(output_path)
            elif format == "csv":
                self.processed_df.write.mode("overwrite").option("header", "true").csv(output_path)
            elif format == "json":
                self.processed_df.write.mode("overwrite").json(output_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"✅ Processed data saved successfully")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error saving processed data: {str(e)}")
            raise

# Convenience function for complete preprocessing
def preprocess_fraud_data(df: DataFrame, 
                         spark_session: SparkSession,
                         full_pipeline: bool = True) -> Tuple[DataFrame, Dict[str, Any]]:
    """
    Complete preprocessing pipeline for fraud detection data
    
    Args:
        df: Input PySpark DataFrame
        spark_session: Spark session
        full_pipeline: Whether to run complete pipeline
        
    Returns:
        Tuple of (processed_dataframe, summary_statistics)
    """
    pipeline = DataPreprocessingPipeline(spark_session)
    
    result_df = (pipeline
                .set_dataframe(df)
                .clean_data(remove_duplicates=True, handle_nulls="fill")
                .engineer_features(create_time_features=True,
                                 create_amount_features=True,
                                 create_user_features=True)
                .encode_categorical_variables(encoding_method="onehot", max_categories=20)
                .scale_numerical_features(scaling_method="standard")
                .create_feature_vector())
    
    summary = result_df.get_preprocessing_summary()
    
    return result_df.processed_df, summary