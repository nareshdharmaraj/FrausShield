"""
FraudShield Data Ingestion Module
Advanced PySpark data loading, validation, and exploration
"""

import os
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import pandas as pd
import numpy as np

# PySpark imports
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, 
    IntegerType, TimestampType, BooleanType
)
from pyspark.sql.functions import (
    col, count, sum as spark_sum, avg, min as spark_min, 
    max as spark_max, when, isnan, isnull, desc, asc
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionEngine:
    """
    Advanced data ingestion engine using PySpark for scalable processing
    """
    
    def __init__(self, app_name: str = "FraudShield-DataIngestion"):
        """Initialize Spark session and data ingestion engine"""
        self.app_name = app_name
        self.spark = None
        self.schema = None
        self.df = None
        self.validation_results = {}
        
        # Define expected schema for fraud detection
        self.expected_schema = StructType([
            StructField("transaction_id", StringType(), False),
            StructField("user_id", StringType(), False),
            StructField("amount", DoubleType(), False),
            StructField("timestamp", StringType(), True),
            StructField("merchant", StringType(), True),
            StructField("location", StringType(), True),
            StructField("payment_method", StringType(), True),
            StructField("account_type", StringType(), True),
            StructField("transaction_type", StringType(), True)
        ])
        
    def initialize_spark(self) -> SparkSession:
        """Initialize Spark session with optimized configuration"""
        try:
            if self.spark is None:
                self.spark = (SparkSession.builder
                             .appName(self.app_name)
                             .config("spark.sql.adaptive.enabled", "true")
                             .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
                             .config("spark.sql.adaptive.skewJoin.enabled", "true")
                             .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
                             .config("spark.sql.execution.arrow.pyspark.enabled", "true")
                             .getOrCreate())
                
                # Set log level to reduce noise
                self.spark.sparkContext.setLogLevel("WARN")
                
                logger.info(f"✅ Spark session initialized: {self.spark.version}")
            
            return self.spark
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Spark session: {str(e)}")
            raise
    
    def load_csv_data(self, file_path: str, infer_schema: bool = True) -> DataFrame:
        """
        Load CSV data with advanced options and validation
        
        Args:
            file_path: Path to CSV file
            infer_schema: Whether to infer schema automatically
            
        Returns:
            PySpark DataFrame
        """
        try:
            if self.spark is None:
                self.initialize_spark()
            
            logger.info(f"📁 Loading data from: {file_path}")
            
            # Load data with advanced options
            df_reader = (self.spark.read
                        .option("header", "true")
                        .option("inferSchema", str(infer_schema).lower())
                        .option("multiline", "true")
                        .option("escape", '"')
                        .option("timestampFormat", "yyyy-MM-dd HH:mm:ss"))
            
            # Apply schema if available
            if not infer_schema and self.schema:
                df_reader = df_reader.schema(self.schema)
            
            self.df = df_reader.csv(file_path)
            
            # Basic info
            row_count = self.df.count()
            col_count = len(self.df.columns)
            
            logger.info(f"✅ Data loaded successfully: {row_count} rows, {col_count} columns")
            
            return self.df
            
        except Exception as e:
            logger.error(f"❌ Error loading CSV data: {str(e)}")
            raise
    
    def validate_schema(self, df: DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame schema against expected structure
        
        Args:
            df: PySpark DataFrame to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            validation_results = {
                "is_valid": True,
                "missing_columns": [],
                "extra_columns": [],
                "type_mismatches": [],
                "recommendations": []
            }
            
            actual_columns = set(df.columns)
            expected_columns = {field.name for field in self.expected_schema.fields}
            
            # Check for missing required columns
            required_columns = {"transaction_id", "user_id", "amount"}
            missing_required = required_columns - actual_columns
            
            if missing_required:
                validation_results["is_valid"] = False
                validation_results["missing_columns"] = list(missing_required)
                validation_results["recommendations"].append(
                    f"❌ Missing required columns: {', '.join(missing_required)}"
                )
            
            # Check for missing optional columns
            missing_optional = expected_columns - actual_columns - missing_required
            if missing_optional:
                validation_results["missing_columns"].extend(missing_optional)
                validation_results["recommendations"].append(
                    f"⚠️ Missing optional columns: {', '.join(missing_optional)}"
                )
            
            # Check for extra columns
            extra_columns = actual_columns - expected_columns
            if extra_columns:
                validation_results["extra_columns"] = list(extra_columns)
                validation_results["recommendations"].append(
                    f"ℹ️ Extra columns found: {', '.join(extra_columns)}"
                )
            
            # Validate data types for key columns
            schema_dict = {field.name: field.dataType for field in df.schema.fields}
            
            type_checks = {
                "amount": (DoubleType, "Should be numeric for calculations"),
                "transaction_id": (StringType, "Should be string identifier"),
                "user_id": (StringType, "Should be string identifier")
            }
            
            for col_name, (expected_type, message) in type_checks.items():
                if col_name in schema_dict:
                    actual_type = type(schema_dict[col_name])
                    if not isinstance(schema_dict[col_name], expected_type):
                        validation_results["type_mismatches"].append({
                            "column": col_name,
                            "expected": expected_type.__name__,
                            "actual": actual_type.__name__,
                            "message": message
                        })
                        validation_results["recommendations"].append(
                            f"⚠️ {col_name}: {message}"
                        )
            
            # Overall validation status
            if validation_results["missing_columns"] or validation_results["type_mismatches"]:
                logger.warning("⚠️ Schema validation completed with issues")
            else:
                logger.info("✅ Schema validation passed")
            
            self.validation_results = validation_results
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Error during schema validation: {str(e)}")
            raise
    
    def generate_data_profile(self, df: DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive data profile with statistics and quality metrics
        
        Args:
            df: PySpark DataFrame to profile
            
        Returns:
            Dictionary with data profile information
        """
        try:
            logger.info("📊 Generating data profile...")
            
            profile = {
                "basic_info": {},
                "column_stats": {},
                "data_quality": {},
                "sample_data": {},
                "recommendations": []
            }
            
            # Basic information
            row_count = df.count()
            col_count = len(df.columns)
            
            profile["basic_info"] = {
                "total_rows": row_count,
                "total_columns": col_count,
                "schema": [{"name": field.name, "type": str(field.dataType)} 
                          for field in df.schema.fields]
            }
            
            # Column-wise statistics
            for column in df.columns:
                col_type = dict(df.dtypes)[column]
                col_stats = {"type": col_type}
                
                # Null count and percentage
                null_count = df.filter(col(column).isNull()).count()
                null_percentage = (null_count / row_count) * 100 if row_count > 0 else 0
                
                col_stats.update({
                    "null_count": null_count,
                    "null_percentage": round(null_percentage, 2),
                    "non_null_count": row_count - null_count
                })
                
                # Type-specific statistics
                if col_type in ['double', 'float', 'int', 'bigint']:
                    # Numerical statistics
                    stats = df.select(
                        spark_min(column).alias("min"),
                        spark_max(column).alias("max"),
                        avg(column).alias("mean")
                    ).collect()[0]
                    
                    col_stats.update({
                        "min": float(stats["min"]) if stats["min"] is not None else None,
                        "max": float(stats["max"]) if stats["max"] is not None else None,
                        "mean": float(stats["mean"]) if stats["mean"] is not None else None
                    })
                
                elif col_type == 'string':
                    # String statistics
                    distinct_count = df.select(column).distinct().count()
                    col_stats.update({
                        "distinct_count": distinct_count,
                        "distinct_percentage": round((distinct_count / row_count) * 100, 2) if row_count > 0 else 0
                    })
                    
                    # Top values for categorical columns
                    if distinct_count <= 50:  # Categorical threshold
                        top_values = (df.groupBy(column)
                                    .count()
                                    .orderBy(desc("count"))
                                    .limit(10)
                                    .collect())
                        
                        col_stats["top_values"] = [
                            {"value": row[column], "count": row["count"]} 
                            for row in top_values
                        ]
                
                profile["column_stats"][column] = col_stats
            
            # Data quality assessment
            profile["data_quality"] = self._assess_data_quality(df, profile["column_stats"])
            
            # Sample data
            sample_size = min(10, row_count)
            if sample_size > 0:
                sample_data = df.limit(sample_size).toPandas().to_dict('records')
                profile["sample_data"] = sample_data
            
            # Generate recommendations
            profile["recommendations"] = self._generate_recommendations(profile)
            
            logger.info("✅ Data profile generated successfully")
            return profile
            
        except Exception as e:
            logger.error(f"❌ Error generating data profile: {str(e)}")
            raise
    
    def _assess_data_quality(self, df: DataFrame, column_stats: Dict) -> Dict[str, Any]:
        """Assess overall data quality"""
        quality_issues = []
        quality_score = 100
        
        for column, stats in column_stats.items():
            # High null percentage
            if stats["null_percentage"] > 20:
                quality_issues.append(f"High null percentage in {column}: {stats['null_percentage']:.1f}%")
                quality_score -= 10
            
            # Low distinct values for non-ID columns
            if (stats["type"] == "string" and 
                "distinct_percentage" in stats and 
                stats["distinct_percentage"] < 1 and
                column not in ["payment_method", "merchant", "location"]):
                quality_issues.append(f"Low distinct values in {column}: {stats['distinct_percentage']:.1f}%")
                quality_score -= 5
        
        return {
            "score": max(0, quality_score),
            "issues": quality_issues,
            "assessment": "Good" if quality_score >= 80 else "Fair" if quality_score >= 60 else "Poor"
        }
    
    def _generate_recommendations(self, profile: Dict) -> List[str]:
        """Generate actionable recommendations based on data profile"""
        recommendations = []
        
        # Check for missing required columns
        if self.validation_results.get("missing_columns"):
            recommendations.append("🔧 Add missing required columns or map existing columns")
        
        # Check data quality issues
        quality_issues = profile["data_quality"]["issues"]
        if quality_issues:
            recommendations.append("🧹 Address data quality issues before processing")
        
        # Check for numerical columns that should be amounts
        for column, stats in profile["column_stats"].items():
            if "amount" in column.lower() and stats["type"] == "string":
                recommendations.append(f"💰 Convert {column} to numerical type for calculations")
        
        # Check for potential categorical columns
        for column, stats in profile["column_stats"].items():
            if (stats["type"] == "string" and 
                "distinct_count" in stats and 
                stats["distinct_count"] <= 20 and
                stats["distinct_count"] > 1):
                recommendations.append(f"🏷️ Consider {column} as categorical variable for encoding")
        
        return recommendations
    
    def detect_anomalies(self, df: DataFrame) -> Dict[str, Any]:
        """
        Detect potential anomalies in the dataset
        
        Args:
            df: PySpark DataFrame to analyze
            
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            logger.info("🔍 Detecting anomalies...")
            
            anomalies = {
                "statistical_outliers": {},
                "business_rule_violations": [],
                "data_inconsistencies": []
            }
            
            # Statistical outliers for numerical columns
            numerical_columns = [field.name for field in df.schema.fields 
                               if isinstance(field.dataType, (DoubleType, IntegerType))]
            
            for column in numerical_columns:
                if df.filter(col(column).isNotNull()).count() > 0:
                    # Calculate quartiles and IQR
                    quartiles = df.approxQuantile(column, [0.25, 0.75], 0.05)
                    if len(quartiles) == 2:
                        q1, q3 = quartiles
                        iqr = q3 - q1
                        lower_bound = q1 - 1.5 * iqr
                        upper_bound = q3 + 1.5 * iqr
                        
                        outlier_count = df.filter(
                            (col(column) < lower_bound) | (col(column) > upper_bound)
                        ).count()
                        
                        if outlier_count > 0:
                            anomalies["statistical_outliers"][column] = {
                                "count": outlier_count,
                                "lower_bound": lower_bound,
                                "upper_bound": upper_bound,
                                "percentage": round((outlier_count / df.count()) * 100, 2)
                            }
            
            # Business rule violations
            if "amount" in df.columns:
                # Negative amounts
                negative_amounts = df.filter(col("amount") < 0).count()
                if negative_amounts > 0:
                    anomalies["business_rule_violations"].append({
                        "rule": "Negative transaction amounts",
                        "count": negative_amounts,
                        "description": "Transaction amounts should be positive"
                    })
                
                # Zero amounts
                zero_amounts = df.filter(col("amount") == 0).count()
                if zero_amounts > 0:
                    anomalies["business_rule_violations"].append({
                        "rule": "Zero transaction amounts",
                        "count": zero_amounts,
                        "description": "Zero amount transactions may be invalid"
                    })
                
                # Extremely high amounts (> 99.9th percentile)
                high_threshold = df.approxQuantile("amount", [0.999], 0.05)[0]
                extreme_amounts = df.filter(col("amount") > high_threshold).count()
                if extreme_amounts > 0:
                    anomalies["business_rule_violations"].append({
                        "rule": "Extremely high amounts",
                        "count": extreme_amounts,
                        "threshold": high_threshold,
                        "description": "Unusually high transaction amounts"
                    })
            
            # Data inconsistencies
            if "user_id" in df.columns:
                # Check for duplicate transaction IDs
                if "transaction_id" in df.columns:
                    total_transactions = df.count()
                    unique_transactions = df.select("transaction_id").distinct().count()
                    if total_transactions != unique_transactions:
                        anomalies["data_inconsistencies"].append({
                            "issue": "Duplicate transaction IDs",
                            "count": total_transactions - unique_transactions,
                            "description": "Transaction IDs should be unique"
                        })
            
            logger.info("✅ Anomaly detection completed")
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Error during anomaly detection: {str(e)}")
            raise
    
    def export_summary_report(self, profile: Dict, anomalies: Dict, output_path: str) -> str:
        """
        Export comprehensive data summary report
        
        Args:
            profile: Data profile dictionary
            anomalies: Anomaly detection results
            output_path: Path to save the report
            
        Returns:
            Path to the saved report
        """
        try:
            report_content = []
            
            # Header
            report_content.append("# FraudShield Data Ingestion Report")
            report_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report_content.append("")
            
            # Basic Information
            report_content.append("## 📊 Dataset Overview")
            basic_info = profile["basic_info"]
            report_content.append(f"- **Total Rows**: {basic_info['total_rows']:,}")
            report_content.append(f"- **Total Columns**: {basic_info['total_columns']}")
            report_content.append("")
            
            # Schema Information
            report_content.append("## 🏗️ Schema Information")
            for field in basic_info["schema"]:
                report_content.append(f"- **{field['name']}**: {field['type']}")
            report_content.append("")
            
            # Data Quality Assessment
            report_content.append("## 🎯 Data Quality Assessment")
            quality = profile["data_quality"]
            report_content.append(f"- **Overall Score**: {quality['score']}/100 ({quality['assessment']})")
            if quality["issues"]:
                report_content.append("- **Issues Found**:")
                for issue in quality["issues"]:
                    report_content.append(f"  - {issue}")
            report_content.append("")
            
            # Anomalies
            report_content.append("## 🚨 Anomaly Detection Results")
            
            if anomalies["statistical_outliers"]:
                report_content.append("### Statistical Outliers")
                for column, stats in anomalies["statistical_outliers"].items():
                    report_content.append(f"- **{column}**: {stats['count']} outliers ({stats['percentage']:.1f}%)")
            
            if anomalies["business_rule_violations"]:
                report_content.append("### Business Rule Violations")
                for violation in anomalies["business_rule_violations"]:
                    report_content.append(f"- **{violation['rule']}**: {violation['count']} cases")
            
            if anomalies["data_inconsistencies"]:
                report_content.append("### Data Inconsistencies")
                for inconsistency in anomalies["data_inconsistencies"]:
                    report_content.append(f"- **{inconsistency['issue']}**: {inconsistency['count']} cases")
            
            report_content.append("")
            
            # Recommendations
            if profile["recommendations"]:
                report_content.append("## 💡 Recommendations")
                for rec in profile["recommendations"]:
                    report_content.append(f"- {rec}")
            
            # Save report
            report_text = "\n".join(report_content)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            logger.info(f"✅ Data report saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error generating report: {str(e)}")
            raise
    
    def cleanup(self):
        """Clean up Spark session"""
        if self.spark:
            self.spark.stop()
            logger.info("🧹 Spark session stopped")

# Convenience function for quick data ingestion
def quick_ingest(file_path: str, output_dir: str = "results") -> Dict[str, Any]:
    """
    Quick data ingestion with validation and profiling
    
    Args:
        file_path: Path to CSV file
        output_dir: Directory to save results
        
    Returns:
        Dictionary with ingestion results
    """
    engine = DataIngestionEngine()
    
    try:
        # Load data
        df = engine.load_csv_data(file_path)
        
        # Validate schema
        validation = engine.validate_schema(df)
        
        # Generate profile
        profile = engine.generate_data_profile(df)
        
        # Detect anomalies
        anomalies = engine.detect_anomalies(df)
        
        # Generate report
        os.makedirs(output_dir, exist_ok=True)
        report_path = os.path.join(output_dir, f"data_ingestion_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
        engine.export_summary_report(profile, anomalies, report_path)
        
        results = {
            "validation": validation,
            "profile": profile,
            "anomalies": anomalies,
            "report_path": report_path,
            "spark_df": df
        }
        
        return results
        
    finally:
        engine.cleanup()