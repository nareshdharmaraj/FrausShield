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
    
    // Start automatic connection checking
    checkConnectionOnLoad();
    startConnectionMonitoring();
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
    
    // Modal click outside to close
    window.addEventListener('click', function(event) {
        const modal = document.getElementById('downloadModal');
        if (event.target === modal) {
            closeDownloadModal();
        }
    });
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
// Connection monitoring functions
async function checkConnectionOnLoad() {
    console.log('🔌 Checking initial connection...');
    showConnectionStatus('checking', '🔄', 'Checking connection...');
    
    try {
        const response = await fetch('/health', { 
            method: 'GET',
            timeout: 5000 
        });
        
        if (response.ok) {
            showConnectionStatus('success', '✅', 'Server connected successfully');
            setTimeout(() => hideConnectionStatus(), 3000); // Hide after 3 seconds
            return true;
        } else {
            showConnectionStatus('warning', '⚠️', 'Server responded but may have issues');
            setTimeout(() => hideConnectionStatus(), 5000);
            return false;
        }
    } catch (error) {
        console.error('Connection check failed:', error);
        showConnectionStatus('error', '❌', 'Cannot connect to server - please check if it\'s running');
        // Don't auto-hide error status
        return false;
    }
}

function startConnectionMonitoring() {
    // Check connection every 30 seconds
    setInterval(async () => {
        try {
            const response = await fetch('/health', { 
                method: 'GET',
                timeout: 3000 
            });
            
            if (!response.ok) {
                showConnectionStatus('warning', '⚠️', 'Connection issues detected');
                setTimeout(() => hideConnectionStatus(), 5000);
            }
        } catch (error) {
            console.error('Background connection check failed:', error);
            showConnectionStatus('error', '❌', 'Connection lost - please refresh the page');
            // Don't auto-hide connection lost status
        }
    }, 30000); // Check every 30 seconds
}

function showConnectionStatus(type, icon, message) {
    const statusBanner = document.getElementById('connectionStatus');
    const statusIcon = document.getElementById('statusIcon');
    const statusText = document.getElementById('statusText');
    const mainContent = document.querySelector('.main');
    
    if (statusBanner && statusIcon && statusText) {
        // Update content
        statusIcon.textContent = icon;
        statusText.textContent = message;
        
        // Remove existing type classes
        statusBanner.classList.remove('success', 'error', 'warning');
        
        // Add new type class
        if (type !== 'checking') {
            statusBanner.classList.add(type);
        }
        
        // Show banner
        statusBanner.classList.add('show');
        
        // Adjust main content spacing
        if (mainContent) {
            mainContent.classList.add('with-status');
        }
        
        console.log(`📡 Connection status: ${type} - ${message}`);
    }
}

function hideConnectionStatus() {
    const statusBanner = document.getElementById('connectionStatus');
    const mainContent = document.querySelector('.main');
    
    if (statusBanner) {
        statusBanner.classList.remove('show');
        
        // Remove main content spacing adjustment after animation
        setTimeout(() => {
            if (mainContent) {
                mainContent.classList.remove('with-status');
            }
        }, 500); // Match CSS transition duration
    }
}

// Loading Screen Control Functions
class LoadingManager {
    constructor() {
        this.pageLoader = document.getElementById('pageLoader');
        this.processingInterface = null;
        this.loadingSteps = [
            { id: 'system', text: 'Initializing fraud detection system...' },
            { id: 'security', text: 'Loading security protocols...' },
            { id: 'algorithms', text: 'Preparing ML algorithms...' },
            { id: 'interface', text: 'Finalizing user interface...' }
        ];
        this.currentStep = 0;
        this.loadingProgress = 0;
        this.isProcessing = false;
        this.processCancelled = false;
    }

    showPageLoader() {
        if (this.pageLoader) {
            this.pageLoader.style.display = 'flex';
            this.startPageLoading();
        }
    }

    hidePageLoader() {
        if (this.pageLoader) {
            this.pageLoader.style.display = 'none';
        }
    }

    startPageLoading() {
        this.loadingProgress = 0;
        this.currentStep = 0;
        this.updatePageLoader();
        
        const loadingInterval = setInterval(() => {
            this.loadingProgress += Math.random() * 15 + 5; // Random increment between 5-20
            
            if (this.loadingProgress >= 25 * (this.currentStep + 1) && this.currentStep < this.loadingSteps.length - 1) {
                this.activateNextStep();
            }
            
            if (this.loadingProgress >= 100) {
                this.loadingProgress = 100;
                this.updatePageLoader();
                
                setTimeout(() => {
                    this.hidePageLoader();
                    clearInterval(loadingInterval);
                }, 800);
                return;
            }
            
            this.updatePageLoader();
        }, 200);
    }

    updatePageLoader() {
        const progressRing = document.querySelector('.progress-ring-fill');
        const progressText = document.querySelector('.progress-text');
        const loadingPercent = document.getElementById('loadingPercent');
        const techStatus = document.querySelector('#techStatus');
        
        if (progressRing) {
            const circumference = 2 * Math.PI * 45; // radius = 45
            const offset = circumference - (this.loadingProgress / 100) * circumference;
            progressRing.style.strokeDashoffset = offset;
        }
        
        if (progressText) {
            progressText.textContent = `${Math.round(this.loadingProgress)}%`;
        }
        
        if (loadingPercent) {
            loadingPercent.textContent = Math.round(this.loadingProgress);
        }
        
        if (techStatus && this.currentStep < this.loadingSteps.length) {
            techStatus.textContent = this.loadingSteps[this.currentStep].text;
        }
    }

    activateNextStep() {
        const steps = document.querySelectorAll('.step');
        if (steps[this.currentStep]) {
            steps[this.currentStep].classList.add('completed');
        }
        
        this.currentStep++;
        
        if (this.currentStep < steps.length) {
            steps[this.currentStep].classList.add('active');
        }
    }

    showProcessingInterface() {
        // Create processing interface if it doesn't exist
        if (!this.processingInterface) {
            this.createProcessingInterface();
        }
        
        if (this.processingInterface) {
            this.processingInterface.style.display = 'flex';
            this.isProcessing = true;
            this.processCancelled = false;
            this.startProcessingAnimation();
            console.log('🚀 Processing interface displayed');
        } else {
            console.error('❌ Could not show processing interface - element not found');
        }
    }

    hideProcessingInterface() {
        if (this.processingInterface) {
            this.processingInterface.style.display = 'none';
        }
        this.isProcessing = false;
    }

    createProcessingInterface() {
        this.processingInterface = document.getElementById('processingInterface');
        if (!this.processingInterface) {
            console.error('Processing interface element not found');
            return;
        }
        
        // Set up cancel button
        const cancelBtn = this.processingInterface.querySelector('.btn-cancel');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.cancelProcessing());
        }
        
        console.log('✅ Processing interface created and ready');
    }

    startProcessingAnimation() {
        let progress = 0;
        let currentStage = 0;
        const stages = [
            'Initializing fraud detection...',
            'Analyzing transaction patterns...',
            'Applying ML algorithms...',
            'Generating fraud reports...',
            'Finalizing results...'
        ];
        
        const metrics = {
            records: 0,
            patterns: 0,
            flags: 0
        };
        
        const processingInterval = setInterval(() => {
            if (this.processCancelled) {
                clearInterval(processingInterval);
                return;
            }
            
            // Update progress
            progress += Math.random() * 8 + 2; // Random increment between 2-10
            if (progress > 100) progress = 100;
            
            // Update stage
            const stageProgress = Math.floor(progress / 20);
            if (stageProgress > currentStage && currentStage < stages.length - 1) {
                currentStage = stageProgress;
                this.updateProcessingStage(currentStage, stages[currentStage]);
            }
            
            // Update metrics (simulated)
            metrics.records = Math.min(metrics.records + Math.floor(Math.random() * 50 + 10), 1000);
            metrics.patterns = Math.min(metrics.patterns + Math.floor(Math.random() * 5 + 1), 25);
            metrics.flags = Math.min(metrics.flags + Math.floor(Math.random() * 3), 15);
            
            this.updateProcessingProgress(progress, metrics);
            
            // Add processing log
            this.addProcessingLog(`Processing batch ${Math.floor(metrics.records / 100)}... ${Math.round(progress)}% complete`);
            
            if (progress >= 100) {
                this.completeProcessing();
                clearInterval(processingInterval);
            }
        }, 300);
    }

    updateProcessingProgress(percentage, metrics) {
        const progressCircle = document.querySelector('.progress-circle-fill');
        const progressText = document.querySelector('.progress-percent');
        const metricElements = document.querySelectorAll('.metric-value');
        
        if (progressCircle) {
            const circumference = 2 * Math.PI * 60; // radius = 60
            const offset = circumference - (percentage / 100) * circumference;
            progressCircle.style.strokeDashoffset = offset;
        }
        
        if (progressText) {
            progressText.textContent = `${Math.round(percentage)}%`;
        }
        
        if (metricElements.length >= 3) {
            metricElements[0].textContent = metrics.records.toLocaleString();
            metricElements[1].textContent = metrics.patterns;
            metricElements[2].textContent = metrics.flags;
        }
    }

    updateProcessingStage(stageIndex, stageText) {
        const stages = document.querySelectorAll('.stage');
        
        // Mark previous stages as completed
        for (let i = 0; i < stageIndex; i++) {
            if (stages[i]) {
                stages[i].classList.remove('active');
                stages[i].classList.add('completed');
            }
        }
        
        // Mark current stage as active
        if (stages[stageIndex]) {
            stages[stageIndex].classList.add('active');
        }
    }

    addProcessingLog(message) {
        const logContainer = document.querySelector('.processing-log');
        if (logContainer) {
            const logItem = document.createElement('div');
            logItem.className = 'log-item';
            logItem.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
            
            logContainer.appendChild(logItem);
            
            // Keep only last 5 log items
            const logItems = logContainer.querySelectorAll('.log-item');
            if (logItems.length > 5) {
                logContainer.removeChild(logItems[0]);
            }
            
            logContainer.scrollTop = logContainer.scrollHeight;
        }
    }

    completeProcessing() {
        this.isProcessing = false;
        
        // Mark all stages as completed
        const stages = document.querySelectorAll('.stage');
        stages.forEach(stage => {
            stage.classList.remove('active');
            stage.classList.add('completed');
        });
        
        // Update button text
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.innerHTML = '✅ Analysis Completed';
            processBtn.disabled = false;
        }
        
        this.addProcessingLog('Analysis completed successfully!');
        
        // Hide processing interface after 2 seconds
        setTimeout(() => {
            this.hideProcessingInterface();
        }, 2000);
    }

    cancelProcessing() {
        this.processCancelled = true;
        this.isProcessing = false;
        
        // Reset processing interface
        const progressCircle = document.querySelector('.progress-circle-fill');
        const progressText = document.querySelector('.progress-percent');
        
        if (progressCircle) {
            progressCircle.style.strokeDashoffset = 377; // Reset to 0%
        }
        
        if (progressText) {
            progressText.textContent = '0%';
        }
        
        // Reset stages
        const stages = document.querySelectorAll('.stage');
        stages.forEach(stage => {
            stage.classList.remove('active', 'completed');
        });
        
        // Update button
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.innerHTML = 'Process File';
            processBtn.disabled = false;
        }
        
        this.addProcessingLog('Processing cancelled by user');
        
        setTimeout(() => {
            this.hideProcessingInterface();
        }, 1000);
    }
}

// Initialize loading manager
const loadingManager = new LoadingManager();

// Show page loader when document loads
document.addEventListener('DOMContentLoaded', function() {
    loadingManager.showPageLoader();
});

// Legacy function for backward compatibility (if needed elsewhere)
async function testConnection() {
    return await checkConnectionOnLoad();
}

// Processing functions
async function processFile() {
    if (!uploadedFile) {
        showAlert('Please select a file first.', 'error');
        return;
    }
    
    // First, let's read and process the file to extract data for user input
    console.log('📊 Reading file for user input preparation...');
    await prepareUserInput();
}

async function prepareUserInput() {
    try {
        // Create FormData for initial file reading
        const formData = new FormData();
        formData.append('file', uploadedFile);
        
        console.log('🔍 Extracting data from file...', uploadedFile.name);
        
        // Get basic file data without full processing
        const response = await fetch('/extract_data', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to read file data');
        }
        
        const data = await response.json();
        console.log('📋 File data extracted:', data);
        console.log('📊 Transactions found:', data.transactions?.length || 0);
        console.log('📂 CSV columns:', data.summary?.columns || []);
        
        // Store the data temporarily
        processedData = data;
        
        // Show user input modal
        showUserInputModal();
        
    } catch (error) {
        console.error('❌ Error preparing user input:', error);
        showAlert('Error reading file. Please try again.', 'error');
    }
}

async function processFileWithUserInput() {
    if (!uploadedFile) {
        showAlert('Please select a file first.', 'error');
        return;
    }
    
    // Show processing interface instead of basic progress
    loadingManager.showProcessingInterface();
    
    // Update process button
    processBtn.disabled = true;
    processBtn.innerHTML = '<div class="spinner"></div>Processing...';
    
    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', uploadedFile);
        
        // Add user input configuration if available
        if (window.userFraudConfig) {
            formData.append('user_config', JSON.stringify(window.userFraudConfig));
        }
        
        // Upload and process file with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minute timeout
        
        console.log('🚀 Starting file processing with user input...');
        
        const response = await fetch('/process', {
            method: 'POST',
            body: formData,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        console.log('📡 Response received:', response.status);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(errorData.error || `HTTP ${response.status}`);
        }
        
        const result = await response.json();
        console.log('✅ Processing result:', result);
        
        // Let the loading manager complete the processing animation
        // Note: The loadingManager.completeProcessing() will be called by the animation
        
        // Show results after animation completes
        setTimeout(() => {
            displayResults(result);
            resetProcessing();
        }, 3000); // Wait for completion animation
        
    } catch (error) {
        console.error('❌ Processing error:', error);
        
        // Cancel the processing animation
        loadingManager.cancelProcessing();
        
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
    
    // Store processed data for downloads
    processedData = data;
    console.log('💾 Processed data stored for downloads');
    
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
    console.log('🔍 Updating statistics with data:', stats);
    
    document.getElementById('totalTransactions').textContent = stats.total || 0;
    document.getElementById('fraudDetected').textContent = stats.fraud || 0;
    document.getElementById('normalTransactions').textContent = stats.normal || 0;
    
    const fraudPercentage = stats.total > 0 ? ((stats.fraud / stats.total) * 100).toFixed(2) : 0;
    document.getElementById('accuracyScore').textContent = fraudPercentage + '%';
    
    console.log('✅ Statistics updated - Total:', stats.total, 'Fraud:', stats.fraud, 'Normal:', stats.normal);
}

function createCharts(chartData) {
    console.log('🎨 Creating charts with data:', chartData);
    
    // Fraud by Amount Range Chart
    if (chartData.fraud_by_amount) {
        createBarChart('fraudAmountChart', chartData.fraud_by_amount, 'Fraud by Amount Range');
    }
    
    // Fraud by Merchant Chart
    if (chartData.fraud_by_merchant) {
        createBarChart('fraudMerchantChart', chartData.fraud_by_merchant, 'Top Merchants with Fraud');
    }
    
    // Fraud Over Time Chart
    if (chartData.fraud_over_time) {
        createLineChart('fraudTimeChart', chartData.fraud_over_time, 'Fraud Trends Over Time');
    }
    
    // Fraud by Payment Method Chart
    if (chartData.fraud_by_payment) {
        createPieChart('fraudPaymentChart', chartData.fraud_by_payment, 'Fraud by Payment Method');
    }
    
    // Data Quality Chart
    if (chartData.data_quality) {
        createDonutChart('dataQualityChart', chartData.data_quality, 'Data Quality Assessment');
    }
    
    // Anomalies Chart
    if (chartData.anomalies) {
        createDonutChart('anomalyChart', chartData.anomalies, 'Anomaly Detection Results');
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
    console.log(`📊 Creating bar chart for ${elementId} with data:`, data);
    
    const ctx = document.getElementById(elementId);
    if (!ctx) {
        console.error(`❌ Canvas element not found: ${elementId}`);
        return;
    }
    
    if (!data || !data.labels || !data.values) {
        console.error(`❌ Invalid data structure for ${elementId}:`, data);
        return;
    }
    
    // Choose colors based on chart type
    let backgroundColor, borderColor;
    if (elementId.includes('risk')) {
        // Risk colors: green, yellow, red
        backgroundColor = [
            'rgba(16, 185, 129, 0.8)',  // Green for low risk
            'rgba(245, 158, 11, 0.8)',  // Yellow for medium risk
            'rgba(239, 68, 68, 0.8)'    // Red for high risk
        ];
        borderColor = [
            'rgba(16, 185, 129, 1)',
            'rgba(245, 158, 11, 1)',
            'rgba(239, 68, 68, 1)'
        ];
    } else if (elementId.includes('performance')) {
        // Performance colors: blue gradient
        backgroundColor = [
            'rgba(37, 99, 235, 0.8)',
            'rgba(59, 130, 246, 0.8)',
            'rgba(96, 165, 250, 0.8)'
        ];
        borderColor = [
            'rgba(37, 99, 235, 1)',
            'rgba(59, 130, 246, 1)',
            'rgba(96, 165, 250, 1)'
        ];
    } else {
        // Default fraud colors
        backgroundColor = 'rgba(239, 68, 68, 0.8)';
        borderColor = 'rgba(239, 68, 68, 1)';
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Count',
                data: data.values,
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createLineChart(elementId, data, title) {
    console.log(`📈 Creating line chart for ${elementId} with data:`, data);
    
    const ctx = document.getElementById(elementId);
    if (!ctx) {
        console.error(`❌ Canvas element not found: ${elementId}`);
        return;
    }
    
    if (!data || !data.labels || !data.values) {
        console.error(`❌ Invalid data structure for ${elementId}:`, data);
        return;
    }
    
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
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createPieChart(elementId, data, title) {
    console.log(`🥧 Creating pie chart for ${elementId} with data:`, data);
    
    const ctx = document.getElementById(elementId);
    if (!ctx) {
        console.error(`❌ Canvas element not found: ${elementId}`);
        return;
    }
    
    if (!data || !data.labels || !data.values) {
        console.error(`❌ Invalid data structure for ${elementId}:`, data);
        return;
    }
    
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
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
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
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: false
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
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
    
    showDownloadModal();
}

function showDownloadModal() {
    const modal = document.getElementById('downloadModal');
    modal.style.display = 'block';
    
    // Reset to format selection step
    document.getElementById('formatSelectionStep').style.display = 'block';
    document.getElementById('previewStep').style.display = 'none';
    document.getElementById('modalTitle').textContent = '📥 Download Results';
}

function closeDownloadModal() {
    const modal = document.getElementById('downloadModal');
    modal.style.display = 'none';
}

let selectedFormat = '';

function selectFormat(format) {
    selectedFormat = format;
    
    // Show loading
    showAlert('Preparing preview...', 'success');
    
    // Generate preview
    generatePreview(format);
}

function generatePreview(format) {
    try {
        // Switch to preview step
        document.getElementById('formatSelectionStep').style.display = 'none';
        document.getElementById('previewStep').style.display = 'block';
        document.getElementById('modalTitle').textContent = `📥 ${format.toUpperCase()} Download Preview`;
        
        const previewTitle = document.getElementById('previewTitle');
        const previewContent = document.getElementById('previewContent');
        
        // Show loading in preview
        previewContent.textContent = 'Loading preview...';
        
        // Fetch actual preview data
        fetch(`/download-preview?format=${format}`)
            .then(response => response.json())
            .then(data => {
                let preview = '';
                
                if (format === 'csv') {
                    preview = generateCSVPreview(data);
                    previewTitle.textContent = '📄 CSV File Preview';
                } else if (format === 'excel') {
                    preview = generateExcelPreview(data);
                    previewTitle.textContent = '📊 Excel File Preview';
                } else if (format === 'pdf') {
                    preview = generatePDFPreview(data);
                    previewTitle.textContent = '📋 PDF Report Preview';
                }
                
                previewContent.textContent = preview;
                
                // Hide loading alert
                setTimeout(() => {
                    const alerts = document.querySelectorAll('.alert');
                    alerts.forEach(alert => alert.remove());
                }, 500);
            })
            .catch(error => {
                console.error('Preview error:', error);
                // Fallback to static preview
                let preview = '';
                const stats = processedData?.stats || { total: 0, fraud: 0, normal: 0 };
                
                if (format === 'csv') {
                    preview = generateCSVPreview({ stats });
                    previewTitle.textContent = '📄 CSV File Preview';
                } else if (format === 'excel') {
                    preview = generateExcelPreview({ stats });
                    previewTitle.textContent = '📊 Excel File Preview';
                } else if (format === 'pdf') {
                    preview = generatePDFPreview({ stats });
                    previewTitle.textContent = '📋 PDF Report Preview';
                }
                
                previewContent.textContent = preview;
                showAlert('Using cached preview data', 'success');
            });
        
    } catch (error) {
        showAlert('Error generating preview: ' + error.message, 'error');
        backToFormatSelection();
    }
}

function generateCSVPreview(data) {
    const stats = data?.stats || { total: 0, fraud: 0, normal: 0 };
    const sampleData = data?.sample_data || [];
    
    let preview = `# =========================================
# 🛡️ FraudShield - AI-Powered Fraud Detection
# Advanced Machine Learning Fraud Analysis
# =========================================
# Report Generated: ${new Date().toLocaleString()}
# Total Transactions: ${stats.total}
# Fraud Detected: ${stats.fraud}
# Normal Transactions: ${stats.normal}
# =========================================

`;

    // Add sample data if available
    if (sampleData.length > 0) {
        const headers = Object.keys(sampleData[0]);
        preview += headers.join(',') + '\n';
        
        sampleData.forEach(row => {
            const values = headers.map(header => row[header] || '');
            preview += values.join(',') + '\n';
        });
        
        preview += `... (${stats.total} total rows)\n`;
    } else {
        preview += `transaction_id,amount,merchant,payment_method,prediction,risk_score
TXN_001,1500.00,Amazon,Credit Card,0,0.25
TXN_002,15000.00,Unknown,Wire Transfer,1,0.89
TXN_003,45.99,Starbucks,Debit Card,0,0.12
... (${stats.total} total rows)
`;
    }

    preview += `
# =========================================
# DISCLAIMER
# This analysis was generated using machine learning
# algorithms and may contain prediction errors.
# Results should be verified by domain experts
# before making critical decisions.
# =========================================`;

    return preview;
}

function generateExcelPreview(data) {
    const stats = data?.stats || { total: 0, fraud: 0, normal: 0 };
    const fraudRate = stats.total > 0 ? ((stats.fraud/stats.total)*100).toFixed(1) : '0.0';
    
    return `📊 Excel File Structure:

Sheet 1: Summary
┌─────────────────────────────────────┐
│ 🛡️ FraudShield Analysis Summary      │
│ Generated: ${new Date().toLocaleDateString()}                │
│                                     │
│ Metric               │ Value        │
│ ─────────────────────│──────────────│
│ Total Transactions   │ ${stats.total.toString().padStart(12)} │
│ Fraud Detected       │ ${stats.fraud.toString().padStart(12)} │
│ Normal Transactions  │ ${stats.normal.toString().padStart(12)} │
│ Fraud Rate %         │ ${fraudRate.padStart(12)} │
└─────────────────────────────────────┘

Sheet 2: Detailed Results
┌─────────────────────────────────────┐
│ transaction_id │ amount │ prediction │
│ ──────────────│────────│────────────│
│ TXN_001       │ 1500.00│ 0 (Normal) │
│ TXN_002       │15000.00│ 1 (Fraud)  │
│ ... (${stats.total} total rows)              │
└─────────────────────────────────────┘

Sheet 3: Disclaimer
Legal disclaimer and usage notes included.`;
}

function generatePDFPreview(data) {
    const stats = data?.stats || { total: 0, fraud: 0, normal: 0 };
    const fraudRate = stats.total > 0 ? ((stats.fraud/stats.total)*100).toFixed(1) : '0.0';
    
    return `📋 PDF Report Structure:

┌─────────────────────────────────────┐
│          FRAUDSHIELD REPORT         │
│    AI-Powered Fraud Detection       │
│                                     │
│ Executive Summary:                  │
│ • ${stats.total} transactions analyzed        │
│ • ${stats.fraud} fraudulent transactions found│
│ • ${fraudRate}% fraud rate                 │
│                                     │
│ Key Insights:                       │
│ • Risk distribution analysis        │
│ • Payment method patterns          │
│ • Amount-based fraud detection     │
│                                     │
│ Charts & Visualizations:           │
│ • Fraud by amount ranges           │
│ • Risk score distribution          │
│ • Model performance metrics        │
│                                     │
│ Detailed Transaction List:          │
│ [Complete transaction data]         │
│                                     │
│ Disclaimer:                         │
│ ML predictions - verify with experts│
└─────────────────────────────────────┘

Note: PDF format provides a comprehensive
professional report with charts and analysis.`;
}

function backToFormatSelection() {
    document.getElementById('previewStep').style.display = 'none';
    document.getElementById('formatSelectionStep').style.display = 'block';
    document.getElementById('modalTitle').textContent = '📥 Download Results';
}

function confirmDownload() {
    if (!selectedFormat) {
        showAlert('No format selected', 'error');
        return;
    }
    
    // Show loading state
    showAlert('Preparing download...', 'success');
    
    // Create a form and submit it to trigger download
    const form = document.createElement('form');
    form.method = 'GET';
    form.action = `/download?format=${selectedFormat}`;
    form.style.display = 'none';
    
    document.body.appendChild(form);
    form.submit();
    document.body.removeChild(form);
    
    // Close modal
    closeDownloadModal();
    
    // Show success message
    setTimeout(() => {
        showAlert('Download started successfully!', 'success');
    }, 1000);
}

function resetProcessing() {
    // Hide processing interface if it's still showing
    if (loadingManager.isProcessing) {
        loadingManager.hideProcessingInterface();
    }
    
    // Reset process button
    if (processBtn) {
        processBtn.disabled = false;
        processBtn.innerHTML = '🚀 Analyze Transactions';
        processBtn.classList.remove('btn-outline');
        processBtn.classList.add('btn-primary');
    }
    
    // Hide old progress container if still visible
    if (progressContainer) {
        progressContainer.style.display = 'none';
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

// User Input Modal Functions
function showUserInputModal() {
    console.log('Opening user input modal...');
    const modal = document.getElementById('userInputModal');
    if (modal) {
        modal.style.display = 'block';
        modal.classList.add('show');
        
        // Scroll to top of modal container to ensure visibility
        modal.scrollTop = 0;
        
        // Prevent body scrolling while modal is open
        document.body.style.overflow = 'hidden';
        
        // Populate checkboxes with data from uploaded file
        populateLocationCheckboxes();
        populateMerchantCheckboxes();
        
        // Focus on modal for better UX
        modal.focus();
    } else {
        console.error('User input modal not found in DOM');
    }
}

function closeUserInputModal() {
    const modal = document.getElementById('userInputModal');
    if (modal) {
        modal.classList.remove('show');
        
        // Restore body scrolling
        document.body.style.overflow = '';
        
        setTimeout(() => {
            modal.style.display = 'none';
        }, 300);
    }
}

function populateLocationCheckboxes() {
    const container = document.getElementById('locationCheckboxes');
    if (!container || !processedData) {
        console.log('❌ No location container or processed data available');
        console.log('Container:', container);
        console.log('ProcessedData:', processedData);
        return;
    }
    
    console.log('🏗️ Populating location checkboxes...');
    console.log('📊 Processed data structure:', processedData);
    
    // Extract unique locations from processed data
    const locations = new Set();
    if (processedData.transactions) {
        console.log(`📋 Found ${processedData.transactions.length} transactions to process`);
        processedData.transactions.forEach(transaction => {
            if (transaction.Location) {
                locations.add(transaction.Location);
                console.log('📍 Found location:', transaction.Location);
            }
        });
    } else {
        console.log('⚠️ No transactions array found in processedData');
    }
    
    console.log(`📍 Total unique locations: ${locations.size}`);
    
    // Clear existing checkboxes
    container.innerHTML = '';
    
    if (locations.size === 0) {
        container.innerHTML = '<p style="color: #666; font-style: italic;">No location data found in the uploaded file.</p>';
        return;
    }
    
    // Create checkbox for each location
    Array.from(locations).sort().forEach(location => {
        const checkboxItem = document.createElement('div');
        checkboxItem.className = 'checkbox-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `location_${location.replace(/\s+/g, '_')}`;
        checkbox.value = location;
        
        const label = document.createElement('label');
        label.htmlFor = checkbox.id;
        label.textContent = location;
        
        checkboxItem.appendChild(checkbox);
        checkboxItem.appendChild(label);
        container.appendChild(checkboxItem);
    });
    
    console.log(`✅ Populated ${locations.size} locations`);
}

function populateMerchantCheckboxes() {
    const container = document.getElementById('merchantCheckboxes');
    if (!container || !processedData) {
        console.log('❌ No merchant container or processed data available');
        console.log('Container:', container);
        console.log('ProcessedData:', processedData);
        return;
    }
    
    console.log('🏗️ Populating merchant checkboxes...');
    
    // Extract unique merchants from processed data
    const merchants = new Set();
    if (processedData.transactions) {
        console.log(`📋 Found ${processedData.transactions.length} transactions to process`);
        processedData.transactions.forEach(transaction => {
            if (transaction.MerchantID) {
                merchants.add(transaction.MerchantID);
                console.log('🏪 Found merchant:', transaction.MerchantID);
            }
        });
    } else {
        console.log('⚠️ No transactions array found in processedData');
    }
    
    console.log(`🏪 Total unique merchants: ${merchants.size}`);
    
    // Clear existing checkboxes
    container.innerHTML = '';
    
    if (merchants.size === 0) {
        container.innerHTML = '<p style="color: #666; font-style: italic;">No merchant data found in the uploaded file.</p>';
        return;
    }
    
    // Create checkbox for each merchant
    Array.from(merchants).sort().forEach(merchant => {
        const checkboxItem = document.createElement('div');
        checkboxItem.className = 'checkbox-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `merchant_${merchant.replace(/\s+/g, '_')}`;
        checkbox.value = merchant;
        
        const label = document.createElement('label');
        label.htmlFor = checkbox.id;
        label.textContent = merchant;
        
        checkboxItem.appendChild(checkbox);
        checkboxItem.appendChild(label);
        container.appendChild(checkboxItem);
    });
    
    console.log(`✅ Populated ${merchants.size} merchants`);
}

function skipUserInput() {
    console.log('User skipped input configuration');
    closeUserInputModal();
    // Continue with default fraud detection
    continueProcessing();
}

function applyUserInput() {
    console.log('🎯 Apply & Analyze button clicked');
    console.log('Applying user input configuration...');
    
    // Get selected locations
    const selectedLocations = [];
    document.querySelectorAll('#locationCheckboxes input[type="checkbox"]:checked').forEach(checkbox => {
        selectedLocations.push(checkbox.value);
    });
    
    // Get selected merchants
    const selectedMerchants = [];
    document.querySelectorAll('#merchantCheckboxes input[type="checkbox"]:checked').forEach(checkbox => {
        selectedMerchants.push(checkbox.value);
    });
    
    console.log('📍 Selected suspicious locations:', selectedLocations);
    console.log('🏪 Selected suspicious merchants:', selectedMerchants);
    
    // Store user selections globally
    window.userFraudConfig = {
        suspiciousLocations: selectedLocations,
        suspiciousMerchants: selectedMerchants
    };
    
    console.log('🔧 User config stored:', window.userFraudConfig);
    
    closeUserInputModal();
    // Continue with enhanced fraud detection
    continueProcessing();
}

function continueProcessing() {
    // This function will handle the actual fraud detection processing
    // It will be called after user input is collected (or skipped)
    console.log('🚀 Continuing with fraud detection processing...');
    console.log('📁 Uploaded file:', uploadedFile);
    console.log('📊 Processed data:', processedData);
    
    if (uploadedFile && processedData) {
        console.log('✅ All required data available, starting processing...');
        // Re-run fraud detection with user input
        processFileWithUserInput();
    } else {
        console.error('❌ Missing required data:');
        console.error('- Uploaded file:', !!uploadedFile);
        console.error('- Processed data:', !!processedData);
        showAlert('Missing required data for processing. Please upload a file first.', 'error');
    }
}

// Add event listeners for user input modal
document.addEventListener('DOMContentLoaded', function() {
    // Modal click outside to close (for user input modal)
    window.addEventListener('click', function(event) {
        const userModal = document.getElementById('userInputModal');
        if (event.target === userModal) {
            closeUserInputModal();
        }
        
        // Also handle download modal
        const downloadModal = document.getElementById('downloadModal');
        if (event.target === downloadModal) {
            closeDownloadModal();
        }
    });
    
    // Handle escape key to close modals
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const userModal = document.getElementById('userInputModal');
            const downloadModal = document.getElementById('downloadModal');
            
            if (userModal && userModal.style.display === 'block') {
                closeUserInputModal();
            } else if (downloadModal && downloadModal.style.display === 'block') {
                closeDownloadModal();
            }
        }
    });
});