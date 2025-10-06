#!/usr/bin/env python3
"""
Test script to verify data extraction endpoint
"""

import requests
import json

def test_data_extraction():
    """Test the /extract_data endpoint with actual CSV"""
    
    url = 'http://127.0.0.1:5000/extract_data'
    
    # Test with the actual bank transactions CSV
    csv_file_path = 'data/bank_transactions_data.csv'
    
    try:
        with open(csv_file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Data extraction successful!")
            print(f"📊 Total transactions: {len(data.get('transactions', []))}")
            print(f"📋 CSV rows: {data.get('summary', {}).get('total_rows', 0)}")
            print(f"📂 Columns: {data.get('summary', {}).get('columns', [])}")
            
            # Extract unique locations and merchants
            locations = set()
            merchants = set()
            
            for transaction in data.get('transactions', []):
                if 'Location' in transaction:
                    locations.add(transaction['Location'])
                if 'MerchantID' in transaction:
                    merchants.add(transaction['MerchantID'])
            
            print(f"📍 Unique locations found: {len(locations)}")
            print(f"🏪 Unique merchants found: {len(merchants)}")
            
            # Show sample data
            if locations:
                print(f"📍 Sample locations: {list(locations)[:10]}")
            if merchants:
                print(f"🏪 Sample merchants: {list(merchants)[:10]}")
                
            return True
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing data extraction endpoint...")
    success = test_data_extraction()
    if success:
        print("🎉 All tests passed!")
    else:
        print("💥 Tests failed!")