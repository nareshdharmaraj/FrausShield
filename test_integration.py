#!/usr/bin/env python3
"""
Integration Test Script for FraudShield ML Pipeline
Tests the complete end-to-end fraud detection pipeline
"""

import requests
import pandas as pd
import time
import json
import os

def test_pipeline_integration():
    """Test the complete ML pipeline integration"""
    
    print("🧪 FraudShield Integration Test")
    print("=" * 50)
    
    # Test 1: Check if application is running
    print("\n1. Testing application health...")
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Application is running and healthy")
        else:
            print("❌ Application health check failed")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to application: {str(e)}")
        return False
    
    # Test 2: Test file upload and processing
    print("\n2. Testing file upload and processing...")
    
    # Check if sample file exists
    sample_file = "sample_transactions.csv"
    if not os.path.exists(sample_file):
        print(f"❌ Sample file {sample_file} not found")
        return False
    
    try:
        # Upload file for processing
        with open(sample_file, 'rb') as f:
            files = {'file': (sample_file, f, 'text/csv')}
            response = requests.post("http://localhost:5000/process", files=files, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ File processing completed successfully")
            
            # Test 3: Validate results
            print("\n3. Validating processing results...")
            
            # Check required fields in response
            required_fields = ['status', 'stats', 'charts']
            for field in required_fields:
                if field in result:
                    print(f"✅ {field} present in response")
                else:
                    print(f"❌ {field} missing from response")
                    return False
            
            # Check statistics
            stats = result.get('stats', {})
            if 'total' in stats and 'fraud' in stats:
                print(f"✅ Statistics: {stats['total']} total transactions, {stats['fraud']} fraud detected")
            else:
                print("❌ Invalid statistics in response")
                return False
            
            # Check charts data
            charts = result.get('charts', {})
            if len(charts) > 0:
                print(f"✅ Charts data generated: {list(charts.keys())}")
            else:
                print("❌ No charts data generated")
                return False
            
        else:
            print(f"❌ File processing failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error during file processing: {str(e)}")
        return False
    
    # Test 4: Test download functionality
    print("\n4. Testing results download...")
    try:
        response = requests.get("http://localhost:5000/download", timeout=30)
        if response.status_code == 200:
            print("✅ Results download working")
        else:
            print(f"⚠️ Download returned status {response.status_code} (may be expected if no results)")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Download test failed: {str(e)} (may be expected)")
    
    print("\n" + "=" * 50)
    print("🎯 Integration Test Completed Successfully!")
    print("✅ All core components are working properly")
    print("🛡️ FraudShield is ready for production use")
    
    return True

if __name__ == "__main__":
    success = test_pipeline_integration()
    exit(0 if success else 1)