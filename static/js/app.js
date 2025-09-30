// Global variables
let uploadedFile = null;
let processedData = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const processBtn = document.getElementById('processBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const resultsSection = document.getElementById('results'); // Fixed: changed from 'resultsSection' to 'results'

// Initialize event listeners
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeAnimations();
});

function initializeEventListeners() {
    // File upload events
    uploadArea.addEventListener('click', () => fileInput.click());
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    fileInput.addEventListener('change', handleFileSelect);
    
    // Process button
    if (processBtn) {
        processBtn.addEventListener('click', processFile);
    }
    
    // Download button
    const downloadBtn = document.getElementById('downloadBtn');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadResults);
    }
}

function initializeAnimations() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 200);
    });
}

// File handling functions
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleFile(file) {
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
        showAlert('Please select a CSV file.', 'error');
        return;
    }
    
    // Validate file size (50MB limit)
    if (file.size > 50 * 1024 * 1024) {
        showAlert('File size must be less than 50MB.', 'error');
        return;
    }
    
    uploadedFile = file;
    fileName.textContent = file.name;
    fileName.style.display = 'block';
    
    // Enable process button
    if (processBtn) {
        processBtn.disabled = false;
        processBtn.classList.remove('btn-outline');
        processBtn.classList.add('btn-primary');
    }
    
    showAlert(`File "${file.name}" uploaded successfully!`, 'success');
}

// Test server connection
async function testConnection() {
    try {
        const response = await fetch('/health', { 
            method: 'GET',
            timeout: 5000 
        });
        
        if (response.ok) {
            showAlert('✅ Server connection is working', 'success');
            return true;
        } else {
            showAlert('⚠️ Server responded but may have issues', 'warning');
            return false;
        }
    } catch (error) {
        showAlert('❌ Cannot connect to server - please check if it\'s running', 'error');
        return false;
    }
}

// Test response format
async function testResponse() {
    try {
        console.log('🧪 Testing response format...');
        const response = await fetch('/test-response');
        const data = await response.json();
        console.log('🧪 Test response data:', data);
        
        // Try to display the test results
        displayResults(data);
        showAlert('✅ Test response successful - check console', 'success');
    } catch (error) {
        console.error('❌ Test response failed:', error);
        showAlert('❌ Test response failed: ' + error.message, 'error');
    }
}

// Processing functions
async function processFile() {
    if (!uploadedFile) {
        showAlert('Please select a file first.', 'error');
        return;
    }
    
    // Show progress
    progressContainer.style.display = 'block';
    processBtn.disabled = true;
    processBtn.innerHTML = '<div class="spinner"></div>Processing...';
    
    // Start progress animation
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 2;
        if (progress <= 90) {
            updateProgress(progress);
        }
    }, 500);
    
    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', uploadedFile);
        
        // Upload and process file with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
        
        console.log('🚀 Starting file processing...');
        
        const response = await fetch('/process', {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        clearInterval(progressInterval);
        
        console.log('📡 Response received:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Processing result:', result);
        
        // Update progress to 100%
        updateProgress(100);
        
        // Show results
        setTimeout(() => {
            displayResults(result);
        }, 500);
        
    } catch (error) {
        clearInterval(progressInterval);
        console.error('❌ Processing error:', error);
        
        let errorMessage = '';
        if (error.name === 'AbortError') {
            errorMessage = 'Processing timed out. Please try with a smaller file or check your connection.';
        } else if (error.message === 'Failed to fetch') {
            errorMessage = 'Connection error - server may be down. Please refresh the page and try again.';
        } else {
            errorMessage = `Error processing file: ${error.message}`;
        }
        
        showAlert(errorMessage, 'error');
        resetProcessing();
    }
}

function updateProgress(percentage) {
    progressFill.style.width = percentage + '%';
}

function displayResults(data) {
    console.log('🎯 Displaying results with data:', data);
    
    // Hide progress
    progressContainer.style.display = 'none';
    console.log('✅ Progress hidden');
    
    // Show results section
    if (resultsSection) {
        resultsSection.style.display = 'block';
        resultsSection.classList.add('slide-up');
        console.log('✅ Results section shown');
    } else {
        console.error('❌ Results section not found!');
        return;
    }
    
    // Update statistics
    if (data.stats) {
        updateStatistics(data.stats);
        console.log('✅ Statistics updated:', data.stats);
    } else {
        console.error('❌ No stats data found');
    }
    
    // Create charts
    if (data.charts) {
        createCharts(data.charts);
        console.log('✅ Charts created');
    } else {
        console.log('⚠️ No chart data available');
    }
    
    // Reset process button
    resetProcessing();
    
    // Scroll to results
    if (resultsSection) {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
        console.log('✅ Scrolled to results');
    }
}

function updateStatistics(stats) {
    document.getElementById('totalTransactions').textContent = stats.total || 0;
    document.getElementById('fraudTransactions').textContent = stats.fraud || 0;
    document.getElementById('normalTransactions').textContent = stats.normal || 0;
    
    const fraudPercentage = stats.total > 0 ? ((stats.fraud / stats.total) * 100).toFixed(2) : 0;
    document.getElementById('fraudPercentage').textContent = fraudPercentage + '%';
}

function createCharts(chartData) {
    // Fraud by Amount Range Chart
    if (chartData.fraud_by_amount) {
        createBarChart('fraudByAmountChart', chartData.fraud_by_amount, 'Fraud by Amount Range');
    }
    
    // Fraud by Merchant Chart
    if (chartData.fraud_by_merchant) {
        createBarChart('fraudByMerchantChart', chartData.fraud_by_merchant, 'Top Merchants with Fraud');
    }
    
    // Fraud Over Time Chart
    if (chartData.fraud_over_time) {
        createLineChart('fraudOverTimeChart', chartData.fraud_over_time, 'Fraud Trends Over Time');
    }
    
    // Fraud by Payment Method Chart
    if (chartData.fraud_by_payment) {
        createPieChart('fraudByPaymentChart', chartData.fraud_by_payment, 'Fraud by Payment Method');
    }
    
    // Data Quality Chart
    if (chartData.data_quality) {
        createDonutChart('dataQualityChart', chartData.data_quality, 'Data Quality Assessment');
    }
    
    // Anomalies Chart
    if (chartData.anomalies) {
        createDonutChart('anomaliesChart', chartData.anomalies, 'Anomaly Detection Results');
    }
    
    // Risk Distribution Chart
    if (chartData.risk_distribution) {
        createBarChart('riskDistributionChart', chartData.risk_distribution, 'Risk Score Distribution');
    }
    
    // Model Performance Chart
    if (chartData.model_performance) {
        createBarChart('modelPerformanceChart', chartData.model_performance, 'ML Model Performance (AUC/Accuracy)');
    }
}

function createBarChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Fraud Count',
                data: data.values,
                backgroundColor: 'rgba(239, 68, 68, 0.8)',
                borderColor: 'rgba(239, 68, 68, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createLineChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Fraud Count',
                data: data.values,
                borderColor: 'rgba(37, 99, 235, 1)',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: { size: 16, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createPieChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(236, 72, 153, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: { size: 16, weight: 'bold' }
                }
            }
        }
    });
}

function createDonutChart(elementId, data, title) {
    const ctx = document.getElementById(elementId);
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(37, 99, 235, 0.8)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: title,
                    font: { size: 16, weight: 'bold' }
                }
            }
        }
    });
}

function downloadResults() {
    if (!processedData) {
        showAlert('No results to download.', 'error');
        return;
    }
    
    // Trigger download
    window.location.href = '/download';
}

function resetProcessing() {
    if (processBtn) {
        processBtn.disabled = false;
        processBtn.innerHTML = '🚀 Analyze Transactions';
        processBtn.classList.remove('btn-outline');
        processBtn.classList.add('btn-primary');
    }
}

// Utility functions
function showAlert(message, type) {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} fade-in`;
    alert.innerHTML = `
        <span>${type === 'success' ? '✅' : '❌'}</span>
        <span>${message}</span>
    `;
    
    // Insert after upload area
    uploadArea.parentNode.insertBefore(alert, uploadArea.nextSibling);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Simulate progress for demo
function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 100) {
            progress = 100;
            clearInterval(interval);
        }
        updateProgress(progress);
    }, 200);
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Header scroll effect
window.addEventListener('scroll', function() {
    const header = document.querySelector('.header');
    if (window.scrollY > 100) {
        header.style.background = 'rgba(255, 255, 255, 0.98)';
    } else {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
    }
});