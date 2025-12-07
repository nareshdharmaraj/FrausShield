from flask import Flask, render_template, request, jsonify
import os
import json

app = Flask(__name__)

@app.route('/')
def home():
    """Main page"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_file():
    """Simple test endpoint for the frontend"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Simple mock response
        return jsonify({
            'status': 'success',
            'message': 'File processed successfully (test mode)',
            'fraud_count': 42,
            'total_count': 1000,
            'accuracy': 99.7,
            'unique_merchants': 25,
            'processing_time': 2.5,
            'predictions': [
                {
                    'transaction_id': 'TXN001',
                    'amount': 1250.00,
                    'merchant': 'Test Store',
                    'fraud_probability': 0.95,
                    'is_fraud': True
                },
                {
                    'transaction_id': 'TXN002', 
                    'amount': 450.00,
                    'merchant': 'Coffee Shop',
                    'fraud_probability': 0.12,
                    'is_fraud': False
                }
            ]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check"""
    return jsonify({'status': 'healthy', 'mode': 'test'})

if __name__ == '__main__':
    print("🚀 FraudShield Test Server Starting...")
    print("📊 Web Interface: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)