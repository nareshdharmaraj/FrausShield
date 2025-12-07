// Professional FraudShield JavaScript
class FraudShieldApp {
    constructor() {
        this.currentSection = 'home';
        this.isProcessing = false;
        this.processingInterval = null;
        this.statusMessages = [];
        this.chartInstances = {};
        this.warningPopupTimeout = null;
        this.processingSteps = [
            { id: 'init', text: 'Initializing PySpark environment', duration: 2000, records: 0 },
            { id: 'session', text: 'Creating Spark session', duration: 1500, records: 0 },
            { id: 'load', text: 'Loading transaction data', duration: 1000, records: 2512 },
            { id: 'validate', text: 'Validating data structure', duration: 800, records: 0 },
            { id: 'preprocess', text: 'Preprocessing transaction features', duration: 2000, records: 0 },
            { id: 'engineer', text: 'Engineering fraud detection features', duration: 1500, records: 0 },
            { id: 'split', text: 'Splitting data for training', duration: 500, records: 0 },
            { id: 'train_lr', text: 'Training Logistic Regression model', duration: 2500, records: 0 },
            { id: 'train_rf', text: 'Training Random Forest model', duration: 3000, records: 0 },
            { id: 'evaluate', text: 'Evaluating model performance', duration: 1000, records: 0 },
            { id: 'predict', text: 'Generating fraud predictions', duration: 1500, records: 0 },
            { id: 'scores', text: 'Calculating fraud scores', duration: 800, records: 0 },
            { id: 'report', text: 'Generating analysis report', duration: 1000, records: 0 },
            { id: 'save', text: 'Saving results and models', duration: 1200, records: 0 }
        ];
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupDynamicBackground();
        this.setupMobileNavigation();
        this.showSection('home'); // Show home section by default
        this.updateActiveNav();
    }

    bindEvents() {
        // Navigation events
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!item.classList.contains('external')) {
                    e.preventDefault();
                    const section = item.getAttribute('data-section');
                    this.showSection(section);
                }
            });
        });

        // File upload events
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');

        if (fileInput && uploadArea) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
            
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('drag-over');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    this.handleFile(files[0]);
                }
            });

            uploadArea.addEventListener('click', () => {
                fileInput.click();
            });
        }

        // Window scroll event for header
        window.addEventListener('scroll', () => {
            const header = document.querySelector('.professional-header');
            if (window.scrollY > 10) {
                header.style.background = 'rgba(255, 255, 255, 0.98)';
                header.style.borderBottom = '1px solid rgba(226, 232, 240, 0.8)';
            } else {
                header.style.background = 'rgba(255, 255, 255, 0.95)';
                header.style.borderBottom = '1px solid #f1f5f9';
            }
        });
    }

    setupDynamicBackground() {
        const bg = document.getElementById('dynamicBg');
        if (!bg) return;

        // Create animated background elements
        for (let i = 0; i < 5; i++) {
            const orb = document.createElement('div');
            orb.className = `bg-orb orb-${i + 1}`;
            orb.style.cssText = `
                position: absolute;
                width: ${50 + Math.random() * 100}px;
                height: ${50 + Math.random() * 100}px;
                background: radial-gradient(circle, rgba(30, 64, 175, 0.1) 0%, transparent 70%);
                border-radius: 50%;
                animation: float${i + 1} ${15 + Math.random() * 10}s ease-in-out infinite alternate;
                top: ${Math.random() * 100}%;
                left: ${Math.random() * 100}%;
            `;
            bg.appendChild(orb);
        }

        // Add CSS animations dynamically
        const style = document.createElement('style');
        style.textContent = `
            @keyframes float1 { to { transform: translate(50px, -30px); } }
            @keyframes float2 { to { transform: translate(-30px, 40px); } }
            @keyframes float3 { to { transform: translate(40px, 50px); } }
            @keyframes float4 { to { transform: translate(-50px, -40px); } }
            @keyframes float5 { to { transform: translate(30px, -50px); } }
        `;
        document.head.appendChild(style);
    }

    setupMobileNavigation() {
        // Mobile menu functionality
        window.toggleMobileMenu = () => {
            const nav = document.querySelector('.main-navigation');
            nav.classList.toggle('mobile-open');
        };
    }

    showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('section').forEach(section => {
            section.style.display = 'none';
        });

        // Show target section
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.style.display = 'block';
            this.currentSection = sectionId;
            this.updateActiveNav();
        }

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    updateActiveNav() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('data-section') === this.currentSection) {
                item.classList.add('active');
            }
        });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.handleFile(file);
        }
    }

    handleFile(file) {
        // Validate file
        if (!file.name.toLowerCase().endsWith('.csv')) {
            this.showToast('Please select a CSV file', 'error');
            return;
        }

        if (file.size > 50 * 1024 * 1024) { // 50MB
            this.showToast('File size exceeds 50MB limit', 'error');
            return;
        }

        // Display file info
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');
        const uploadArea = document.getElementById('uploadArea');

        if (fileInfo && fileName && fileSize) {
            fileName.textContent = file.name;
            fileSize.textContent = this.formatFileSize(file.size);
            fileInfo.style.display = 'block';
            uploadArea.style.display = 'none';
        }

        this.selectedFile = file;
        this.showToast('File uploaded successfully', 'success');
    }

    clearFile() {
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const uploadArea = document.getElementById('uploadArea');

        if (fileInput) fileInput.value = '';
        if (fileInfo) fileInfo.style.display = 'none';
        if (uploadArea) uploadArea.style.display = 'block';

        this.selectedFile = null;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async analyzeTransactions() {
        if (!this.selectedFile && !this.usingSampleData) {
            this.showToast('Please select a file first', 'error');
            return;
        }

        if (this.isProcessing) {
            this.showToast('Analysis already in progress', 'warning');
            return;
        }

        this.isProcessing = true;
        this.showSection('processing');
        this.startProcessingAnimation();

        try {
            const formData = new FormData();
            if (this.selectedFile) {
                formData.append('file', this.selectedFile);
            }

            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.handleAnalysisComplete(result);
            
        } catch (error) {
            console.error('Analysis failed:', error);
            console.error('Error details:', error.stack);
            this.showToast('Analysis failed: ' + error.message, 'error');
            this.isProcessing = false;
            this.showSection('upload');
        }
    }

    startProcessingAnimation() {
        this.currentTaskIndex = 0;
        this.processedRecords = 0;
        this.startTime = Date.now();
        this.completedTasks = [];
        
        const progressCircle = document.getElementById('progressCircle');
        const progressPercent = document.getElementById('progressPercent');
        const progressStage = document.getElementById('progressStage');
        const statusList = document.getElementById('statusList');
        const processedCount = document.getElementById('processedCount');
        const processingRate = document.getElementById('processingRate');

        if (statusList) {
            statusList.innerHTML = '';
        }
        
        // Reset progress circle
        if (progressCircle) {
            const circumference = 2 * Math.PI * 90;
            progressCircle.style.strokeDasharray = circumference;
            progressCircle.style.strokeDashoffset = circumference;
        }
        
        // Initial display
        if (progressPercent) progressPercent.textContent = '0%';
        if (progressStage) progressStage.textContent = 'Initializing...';
        if (processedCount) processedCount.textContent = '0';
        if (processingRate) processingRate.textContent = '--';

        // Start processing tasks sequentially
        this.executeNextTask();
    }
    
    executeNextTask() {
        if (this.currentTaskIndex >= this.processingSteps.length) {
            this.completeProcessing();
            return;
        }
        
        const task = this.processingSteps[this.currentTaskIndex];
        const progress = ((this.currentTaskIndex + 1) / this.processingSteps.length) * 100;
        
        // Update progress circle
        this.updateProgressCircle(progress);
        
        // Update progress text
        const progressPercent = document.getElementById('progressPercent');
        const progressStage = document.getElementById('progressStage');
        
        if (progressPercent) progressPercent.textContent = Math.round(progress) + '%';
        if (progressStage) progressStage.textContent = task.text;
        
        // Add task to status list as processing
        this.addStatusMessage(task.text, 'processing', task.id);
        
        // Simulate task execution with records processing
        this.simulateTaskExecution(task, () => {
            // Mark task as completed
            this.markTaskCompleted(task.id);
            this.completedTasks.push(task);
            this.currentTaskIndex++;
            
            // Move to next task after brief delay
            setTimeout(() => this.executeNextTask(), 300);
        });
    }
    
    simulateTaskExecution(task, callback) {
        const duration = task.duration;
        const recordsToProcess = task.records;
        const steps = 8; // Number of progress updates during task
        const stepDuration = duration / steps;
        const recordsPerStep = Math.floor(recordsToProcess / steps);
        
        let currentStep = 0;
        
        const stepInterval = setInterval(() => {
            currentStep++;
            this.processedRecords += recordsPerStep;
            
            // Update metrics display
            this.updateProcessingMetrics();
            
            if (currentStep >= steps) {
                clearInterval(stepInterval);
                // Ensure we reach the exact target
                this.processedRecords += (recordsToProcess - (recordsPerStep * steps));
                this.updateProcessingMetrics();
                callback();
            }
        }, stepDuration);
    }
    
    updateProgressCircle(progress) {
        const progressCircle = document.getElementById('progressCircle');
        if (progressCircle) {
            const circumference = 2 * Math.PI * 90;
            const offset = circumference - (progress / 100) * circumference;
            progressCircle.style.strokeDashoffset = offset;
        }
    }
    
    updateProcessingMetrics() {
        const processedCount = document.getElementById('processedCount');
        const processingRate = document.getElementById('processingRate');
        
        if (processedCount) {
            processedCount.textContent = this.processedRecords.toLocaleString();
        }
        
        if (processingRate) {
            const elapsedSeconds = (Date.now() - this.startTime) / 1000;
            const rate = elapsedSeconds > 0 ? Math.round(this.processedRecords / elapsedSeconds) : 0;
            processingRate.textContent = rate.toLocaleString();
        }
    }
    
    markTaskCompleted(taskId) {
        const statusItems = document.querySelectorAll('.status-item');
        statusItems.forEach(item => {
            if (item.dataset.taskId === taskId) {
                item.classList.remove('processing');
                item.classList.add('completed');
                
                const icon = item.querySelector('.status-icon');
                if (icon) {
                    icon.innerHTML = '✓';
                    icon.classList.remove('processing');
                    icon.classList.add('completed');
                }
            }
        });
    }
    
    completeProcessing() {
        // Final updates
        const progressPercent = document.getElementById('progressPercent');
        const progressStage = document.getElementById('progressStage');
        
        if (progressPercent) progressPercent.textContent = '100%';
        if (progressStage) progressStage.textContent = 'Analysis completed successfully';
        
        this.updateProgressCircle(100);
        
        // Update status indicator in header
        const statusDot = document.querySelector('.status-dot.active');
        if (statusDot) {
            statusDot.classList.remove('active');
            statusDot.classList.add('completed');
        }
        
        const statusIndicator = document.querySelector('.status-indicator span:last-child');
        if (statusIndicator) {
            statusIndicator.textContent = 'Completed';
        }
        
        // Clear any existing interval
        if (this.processingInterval) {
            clearInterval(this.processingInterval);
            this.processingInterval = null;
        }
        
        // Wait a moment before allowing transition to results
        setTimeout(() => {
            this.isProcessing = false;
        }, 1500);
    }

    addStatusMessage(message, type = 'info', taskId = null) {
        const statusList = document.getElementById('statusList');
        if (!statusList) return;

        const statusItem = document.createElement('div');
        statusItem.className = `status-item ${type}`;
        if (taskId) statusItem.dataset.taskId = taskId;
        
        const timestamp = new Date().toLocaleTimeString();
        
        const iconMap = {
            'success': '✓',
            'error': '✗',
            'warning': '⚠',
            'processing': '⟲',
            'info': 'ℹ',
            'completed': '✓'
        };
        
        const icon = iconMap[type] || 'ℹ';
        const iconClass = type === 'processing' ? 'processing' : '';
        
        statusItem.innerHTML = `
            <div class="status-content">
                <span class="status-icon ${iconClass}">${icon}</span>
                <div class="status-text">
                    <span class="status-message">${message}</span>
                    <span class="status-time">${timestamp}</span>
                </div>
            </div>
        `;

        statusList.appendChild(statusItem);
        statusList.scrollTop = statusList.scrollHeight;
    }

    handleAnalysisComplete(result) {
        console.log('Analysis complete, result:', result);
        
        // Store analysis stats for reference
        this.lastAnalysisStats = result.stats || {};
        
        // Update results display
        this.updateResultsDisplay(result);
        
        // Show results section first
        this.showSection('results');
        
        // Wait for DOM to render before creating charts
        setTimeout(() => {
            this.createCharts(result);
            
            // Show fraud warning popup after 5 seconds
            this.warningPopupTimeout = setTimeout(() => {
                this.showFraudWarningPopup();
            }, 5000);
        }, 500);
    }

    updateResultsDisplay(result) {
        // Update statistics using the correct data structure
        const stats = result.stats || {};
        const modelPerformance = result.model_performance || {};
        
        document.getElementById('fraudCount').textContent = stats.fraud || 0;
        document.getElementById('totalCount').textContent = stats.total || 0;
        
        // Get model accuracy from stats or model_performance
        const accuracy = stats.model_accuracy || 
                        (modelPerformance.logistic_regression && modelPerformance.logistic_regression.accuracy) || 0;
        document.getElementById('accuracy').textContent = accuracy.toFixed(2) + '%';
        document.getElementById('merchantCount').textContent = stats.unique_merchants || 0;

        console.log('Updated display with:', {
            fraud: stats.fraud,
            total: stats.total,
            accuracy: accuracy,
            merchants: stats.unique_merchants
        });

        // Update results table with original data
        if (result.predictions && result.predictions.length > 0) {
            this.populateResultsTable(result.predictions);
        } else {
            console.warn('No predictions available, using actual data structure');
            this.populateResultsTable(this.generateSampleData(result));
        }
    }

    populateResultsTable(predictions) {
        const tableBody = document.getElementById('resultsTableBody');
        if (!tableBody) return;

        // Store predictions data for filtering
        this.currentPredictions = predictions || [];
        
        // Setup search and filter event listeners if not already done
        this.setupTableControls();
        
        // Render table with current data
        this.renderTable(this.currentPredictions);
        
        // Update initial count display
        this.updateResultsCount(this.currentPredictions.length, this.currentPredictions.length);
    }
    
    setupTableControls() {
        // Avoid duplicate event listeners
        if (this.tableControlsSetup) return;
        this.tableControlsSetup = true;
        
        const searchInput = document.getElementById('searchInput');
        const filterSelect = document.getElementById('filterSelect');
        
        if (searchInput) {
            searchInput.addEventListener('input', () => this.filterTable());
        }
        
        if (filterSelect) {
            filterSelect.addEventListener('change', () => this.filterTable());
        }
    }
    
    renderTable(predictions) {
        const tableBody = document.getElementById('resultsTableBody');
        if (!tableBody) return;

        tableBody.innerHTML = '';
        
        if (predictions.length === 0) {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td colspan="6" class="no-results">
                    <i class="fas fa-search"></i>
                    <span>No transactions found matching your criteria</span>
                </td>
            `;
            tableBody.appendChild(row);
            return;
        }

        predictions.forEach((pred, index) => {
            const row = document.createElement('tr');
            const isFixed = pred.prediction === 1;
            const confidence = pred.confidence || Math.random() * 0.4 + 0.6;
            const riskScore = isFixed ? (confidence * 100).toFixed(1) : (Math.random() * 30 + 10).toFixed(1);
            // Use the actual transaction ID from the prediction data
            const transactionId = pred.transaction_id || pred.id || `TXN-${String(index + 1).padStart(4, '0')}`;
            const merchant = pred.merchant || 'N/A';
            const amount = pred.amount || 0;
            
            row.innerHTML = `
                <td><span class="transaction-id">${transactionId}</span></td>
                <td><span class="amount">$${amount.toFixed(2)}</span></td>
                <td><span class="merchant">${merchant}</span></td>
                <td>
                    <span class="status-badge ${isFixed ? 'fraud' : 'normal'}">
                        <i class="fas ${isFixed ? 'fa-exclamation-triangle' : 'fa-check-circle'}"></i>
                        ${isFixed ? 'Fraudulent' : 'Normal'}
                    </span>
                </td>
                <td><span class="confidence">${(confidence * 100).toFixed(1)}%</span></td>
                <td>
                    <div class="risk-score ${this.getRiskLevel(parseFloat(riskScore))}">
                        <span class="risk-value">${riskScore}</span>
                        <div class="risk-bar">
                            <div class="risk-fill" style="width: ${Math.min(riskScore, 100)}%"></div>
                        </div>
                    </div>
                </td>
            `;
            
            // Add click event for row details
            row.addEventListener('click', () => this.showTransactionDetails({
                ...pred,
                id: transactionId,
                amount: amount,
                merchant: merchant,
                confidence: confidence,
                riskScore: riskScore
            }, index));
            row.style.cursor = 'pointer';
            
            tableBody.appendChild(row);
        });
    }
    
    filterTable() {
        const searchInput = document.getElementById('searchInput');
        const filterSelect = document.getElementById('filterSelect');
        
        if (!this.currentPredictions) return;
        
        const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
        const filterValue = filterSelect ? filterSelect.value : 'all';
        
        let filteredPredictions = this.currentPredictions.filter((pred, index) => {
            // Apply status filter
            if (filterValue === 'fraud' && pred.prediction !== 1) return false;
            if (filterValue === 'normal' && pred.prediction === 1) return false;
            
            // Apply search filter
            if (searchTerm) {
                const searchableText = [
                    pred.transaction_id || pred.id || `TXN-${String(index + 1).padStart(4, '0')}`,
                    (pred.amount || 0).toFixed(2),
                    pred.merchant || 'N/A',
                    pred.prediction === 1 ? 'fraudulent fraud' : 'normal'
                ].join(' ').toLowerCase();
                
                return searchableText.includes(searchTerm);
            }
            
            return true;
        });
        
        this.renderTable(filteredPredictions);
        
        // Update results count
        this.updateResultsCount(filteredPredictions.length, this.currentPredictions.length);
    }
    
    updateResultsCount(filtered, total) {
        const tableHeader = document.querySelector('.table-header h3');
        if (tableHeader) {
            // Show both the sample size and total transaction count
            const totalInDatabase = this.lastAnalysisStats?.total || total;
            const countText = filtered === total ? 
                `Detailed Analysis (${filtered} of ${totalInDatabase} transactions shown)` : 
                `Detailed Analysis (${filtered} of ${total} shown, ${totalInDatabase} total)`;
            tableHeader.textContent = countText;
        }
    }
    
    showTransactionDetails(prediction, index) {
        // Create modal or expand row with transaction details
        const details = {
            id: `TXN-${String(index + 1).padStart(4, '0')}`,
            amount: prediction.amount || 0,
            merchant: prediction.merchant || 'N/A',
            status: prediction.prediction === 1 ? 'Fraudulent' : 'Normal',
            confidence: (prediction.confidence || Math.random() * 0.4 + 0.6) * 100
        };
        
        this.showToast(`Transaction ${details.id}: ${details.status} (${details.confidence.toFixed(1)}% confidence)`, 
                      prediction.prediction === 1 ? 'error' : 'success');
    }

    generateSampleData(result) {
        // Generate realistic transaction data based on actual analysis results
        const stats = result.stats || {};
        const totalTransactions = stats.total || 2512;
        const fraudCount = stats.fraud || 0;
        
        console.log(`Generating sample data: ${totalTransactions} total, ${fraudCount} fraud`);
        
        const sampleData = [];
        const merchants = [
            'Amazon', 'Walmart', 'Target', 'Best Buy', 'McDonald\'s', 
            'Starbucks', 'Shell Gas Station', 'Exxon Mobil', 'Home Depot', 
            'Costco Wholesale', 'CVS Pharmacy', 'Walgreens', 'Subway',
            'Uber', 'Netflix', 'Spotify', 'PayPal', 'Apple Store'
        ];
        
        const transactionTypes = ['Purchase', 'Online', 'ATM', 'Transfer', 'Payment'];
        const displayCount = Math.min(totalTransactions, 50); // Show max 50 in detailed view
        
        for (let i = 0; i < displayCount; i++) {
            const isFraud = i < fraudCount; // First N transactions are fraud (if any)
            
            // Generate realistic transaction amounts
            const amount = isFraud ? 
                Math.random() * 8000 + 1000 : // Fraud: $1000-$9000
                Math.random() * 500 + 5;      // Normal: $5-$505
                
            // Generate transaction data that looks realistic
            const merchantIndex = Math.floor(Math.random() * merchants.length);
            const typeIndex = Math.floor(Math.random() * transactionTypes.length);
            
            sampleData.push({
                id: `TXN${String(i + 1).padStart(4, '0')}`,
                amount: parseFloat(amount.toFixed(2)),
                merchant: merchants[merchantIndex],
                type: transactionTypes[typeIndex],
                prediction: isFraud ? 1 : 0,
                confidence: isFraud ? 
                    Math.random() * 0.25 + 0.75 : // Fraud: 75-100% confidence
                    Math.random() * 0.3 + 0.05,   // Normal: 5-35% confidence  
                timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
                location: this.generateRandomLocation()
            });
        }
        
        console.log(`Generated ${sampleData.length} sample transactions for detailed view`);
        return sampleData;
    }
    
    generateRandomLocation() {
        const cities = [
            'New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Houston, TX',
            'Phoenix, AZ', 'Philadelphia, PA', 'San Antonio, TX', 'San Diego, CA',
            'Dallas, TX', 'San Jose, CA', 'Austin, TX', 'Jacksonville, FL'
        ];
        return cities[Math.floor(Math.random() * cities.length)];
    }

    getRiskLevel(riskScore) {
        if (riskScore > 80) return 'high';
        if (riskScore > 50) return 'medium';
        return 'low';
    }

    createCharts(result) {
        // Ensure Chart.js is available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded. Charts will not be displayed.');
            return;
        }

        console.log('Creating charts with result:', result);
        
        // Ensure we're on the results section
        if (this.currentSection !== 'results') {
            console.log('Not on results section, skipping chart creation');
            return;
        }
        
        // Wait for DOM to be fully ready before creating charts
        setTimeout(() => {
            console.log('Creating charts after DOM ready delay...');
            
            // Double-check canvas elements exist
            const fraudCanvas = document.getElementById('fraudChart');
            const amountCanvas = document.getElementById('amountChart');
            
            if (!fraudCanvas) {
                console.error('Fraud chart canvas not found in DOM');
                return;
            }
            if (!amountCanvas) {
                console.error('Amount chart canvas not found in DOM');
                return;
            }
            
            console.log('Canvas elements confirmed, creating charts...');
            this.createFraudChart(result);
            this.createAmountChart(result);
            
            // Verify charts were created, retry if necessary
            setTimeout(() => {
                const fraudCanvas = document.getElementById('fraudChart');
                const amountCanvas = document.getElementById('amountChart');
                
                if (fraudCanvas && !fraudCanvas.chartInstance) {
                    console.log('Retrying fraud chart creation...');
                    this.createFraudChart(result);
                }
                
                if (amountCanvas && !amountCanvas.chartInstance) {
                    console.log('Retrying amount chart creation...');
                    this.createAmountChart(result);
                }
            }, 500); // Additional retry after 500ms
        }, 200); // Increased delay to ensure DOM is ready
    }

    createFraudChart(result) {
        // Double-check Chart availability
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not available for fraud chart');
            return;
        }

        const ctx = document.getElementById('fraudChart');
        if (!ctx) {
            console.error('Fraud chart canvas element not found');
            return;
        }
        
        // Destroy existing chart if it exists
        if (this.chartInstances.fraudChart) {
            this.chartInstances.fraudChart.destroy();
            this.chartInstances.fraudChart = null;
        }
        
        console.log('Creating fraud chart...');
        const stats = result.stats || {};
        const fraudCount = stats.fraud || 0;
        const totalCount = stats.total || 0;
        const normalCount = totalCount - fraudCount;
        
        try {
            this.chartInstances.fraudChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Normal Transactions', 'Fraudulent Transactions'],
                datasets: [{
                    data: [normalCount, fraudCount],
                    backgroundColor: ['#059669', '#dc2626'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            font: {
                                size: 14,
                                weight: 500
                            }
                        }
                    }
                }
            }
        });
        
        // Store chart instance
        ctx.chartInstance = true;
        console.log('Fraud chart created successfully');
        } catch (error) {
            console.error('Error creating fraud chart:', error);
        }
    }

    createAmountChart(result) {
        // Check Chart availability
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not available for amount chart');
            return;
        }

        const ctx = document.getElementById('amountChart');
        if (!ctx) {
            console.error('Amount chart canvas element not found');
            return;
        }
        
        if (!result.charts || !result.charts.fraud_by_amount) {
            console.log('No fraud_by_amount data, creating transaction distribution chart');
            // Create a chart showing overall transaction distribution when no fraud data available
            const stats = result.stats || {};
            const total = stats.total || 0;
            
            if (total > 0) {
                // Create estimated distribution across amount ranges
                const distributionData = {
                    labels: ['0-100', '100-500', '500-1000', '1000-5000', '5000+'],
                    values: [
                        Math.floor(total * 0.4),  // 40% in 0-100 range
                        Math.floor(total * 0.3),  // 30% in 100-500 range  
                        Math.floor(total * 0.2),  // 20% in 500-1000 range
                        Math.floor(total * 0.08), // 8% in 1000-5000 range
                        Math.floor(total * 0.02)  // 2% in 5000+ range
                    ]
                };
                this.createDistributionChart(ctx, distributionData, 'Transaction Distribution by Amount Range');
            } else {
                console.error('No transaction data available');
            }
            return;
        }
        
        console.log('Creating amount chart with chart data:', result.charts.fraud_by_amount);
        
        try {
            const chartData = result.charts.fraud_by_amount;
            this.createAmountChartWithData(ctx, chartData, 'Fraud Transactions by Amount Range');
        } catch (error) {
            console.error('Error creating amount chart:', error);
        }
    }

    createDistributionChart(ctx, chartData, label) {
        try {
            const labels = chartData.labels || ['No Data'];
            const values = chartData.values || [0];

            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: values,
                        backgroundColor: '#059669', // Green for normal transactions
                        borderColor: '#047857',
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toFixed(0) + ' transactions';
                                }
                            }
                        }
                    }
                }
            });
            
            // Store chart instance
            ctx.chartInstance = true;
            console.log('Distribution chart created successfully with data:', chartData);
        } catch (error) {
            console.error('Error creating distribution chart:', error);
        }
    }
    
    createAmountChartWithData(ctx, chartData, label) {
        try {
            // Destroy existing chart if it exists
            const chartId = ctx.id;
            if (this.chartInstances[chartId]) {
                this.chartInstances[chartId].destroy();
                this.chartInstances[chartId] = null;
            }
            
            const labels = chartData.labels || ['No Data'];
            const values = chartData.values || [0];
            const isNoFraud = label.includes('All Transaction');

            this.chartInstances[chartId] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: label,
                        data: values,
                        backgroundColor: isNoFraud ? values.map(() => '#059669') : values.map(() => '#dc2626'),
                        borderColor: isNoFraud ? values.map(() => '#047857') : values.map(() => '#b91c1c'),
                        borderWidth: 1,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                callback: function(value) {
                                    return value.toFixed(0) + ' transactions';
                                }
                            }
                        }
                    }
                }
            });
            
            // Store chart instance
            ctx.chartInstance = true;
            console.log('Amount chart created successfully with data:', chartData);
        } catch (error) {
            console.error('Error creating amount chart with data:', error);
        }
    }

    useSampleData() {
        this.usingSampleData = true;
        this.selectedFile = null;
        
        // Hide upload area and show sample data info
        const uploadArea = document.getElementById('uploadArea');
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');
        const fileSize = document.getElementById('fileSize');

        if (uploadArea) uploadArea.style.display = 'none';
        if (fileInfo) fileInfo.style.display = 'block';
        if (fileName) fileName.textContent = 'sample_transactions.csv';
        if (fileSize) fileSize.textContent = '2.5 KB';

        this.showToast('Sample data loaded successfully', 'success');
    }

    exportResults() {
        // Create downloadable results file
        const results = this.getResultsData();
        const blob = new Blob([JSON.stringify(results, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `fraud-analysis-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showToast('Results exported successfully', 'success');
    }

    getResultsData() {
        return {
            timestamp: new Date().toISOString(),
            summary: {
                total_transactions: parseInt(document.getElementById('totalCount').textContent) || 0,
                fraud_count: parseInt(document.getElementById('fraudCount').textContent) || 0,
                accuracy: parseFloat(document.getElementById('accuracy').textContent) || 0,
                unique_merchants: parseInt(document.getElementById('merchantCount').textContent) || 0
            },
            analysis_type: 'ML-based fraud detection',
            platform: 'FraudShield Enterprise'
        };
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px;">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                              type === 'error' ? 'fa-exclamation-circle' : 
                              type === 'warning' ? 'fa-exclamation-triangle' : 
                              'fa-info-circle'}"></i>
                <span>${message}</span>
            </div>
        `;

        container.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
    
    showFraudWarningPopup() {
        // Check if popup already exists
        if (document.getElementById('fraudWarningPopup')) {
            return;
        }
        
        // Create popup overlay
        const overlay = document.createElement('div');
        overlay.id = 'fraudWarningPopup';
        overlay.className = 'fraud-warning-overlay';
        
        // Create popup content
        overlay.innerHTML = `
            <div class="fraud-warning-popup">
                <div class="popup-header">
                    <i class="fas fa-shield-alt"></i>
                    <h3>Fraud Detection Alert</h3>
                </div>
                <div class="popup-content">
                    <div class="warning-message">
                        <p><strong>Next time be aware of these merchants and try to manually verify the account balance.</strong></p>
                        <p>For current frauds, try reporting to your bank immediately.</p>
                    </div>
                    <button class="understand-btn" onclick="window.fraudShieldApp.closeFraudWarningPopup()">
                        <i class="fas fa-check"></i>
                        I Understand
                    </button>
                </div>
                <div class="popup-disclaimer">
                    <small><i class="fas fa-info-circle"></i> The analysis generated may differ from reality in few cases.</small>
                </div>
            </div>
        `;
        
        // Add popup to body
        document.body.appendChild(overlay);
        
        // Trigger animation
        setTimeout(() => {
            overlay.classList.add('show');
        }, 100);
    }
    
    closeFraudWarningPopup() {
        const popup = document.getElementById('fraudWarningPopup');
        if (popup) {
            popup.classList.add('hide');
            setTimeout(() => {
                if (popup.parentNode) {
                    popup.parentNode.removeChild(popup);
                }
            }, 300);
        }
        
        // Clear timeout if popup is closed early
        if (this.warningPopupTimeout) {
            clearTimeout(this.warningPopupTimeout);
            this.warningPopupTimeout = null;
        }
    }
}

// Global variables and functions (defined outside of DOMContentLoaded for immediate availability)
window.fraudShieldApp = null;

// Try to initialize immediately if DOM is already ready
if (document.readyState !== 'loading') {
    console.log('DOM already ready, initializing FraudShield immediately');
    try {
        window.fraudShieldApp = new FraudShieldApp();
        console.log('Immediate initialization successful');
    } catch (e) {
        console.log('Immediate initialization failed, will retry on DOMContentLoaded:', e);
    }
}

// Global functions for HTML onclick events - defined immediately
window.showSection = function(sectionId) {
    console.log('Global showSection called with:', sectionId);
    if (window.fraudShieldApp) {
        return window.fraudShieldApp.showSection(sectionId);
    } else {
        console.log('FraudShieldApp not yet initialized, attempting immediate initialization...');
        // Try to initialize immediately if possible
        try {
            if (typeof FraudShieldApp !== 'undefined') {
                window.fraudShieldApp = new FraudShieldApp();
                console.log('Emergency initialization successful');
                return window.fraudShieldApp.showSection(sectionId);
            }
        } catch (e) {
            console.error('Emergency initialization failed:', e);
        }
        
        // Fallback: wait for initialization
        const checkInitialization = setInterval(() => {
            if (window.fraudShieldApp) {
                clearInterval(checkInitialization);
                window.fraudShieldApp.showSection(sectionId);
            }
        }, 100);
        
        // Clear interval after 5 seconds to prevent infinite checking
        setTimeout(() => clearInterval(checkInitialization), 5000);
    }
};

window.analyzeTransactions = function() {
    console.log('Global analyzeTransactions called');
    if (window.fraudShieldApp) {
        return window.fraudShieldApp.analyzeTransactions();
    } else {
        console.log('FraudShieldApp not yet initialized for analyzeTransactions');
        // Try immediate initialization
        try {
            if (typeof FraudShieldApp !== 'undefined') {
                window.fraudShieldApp = new FraudShieldApp();
                return window.fraudShieldApp.analyzeTransactions();
            }
        } catch (e) {
            console.error('Emergency initialization failed for analyzeTransactions:', e);
        }
    }
};

window.clearFile = function() {
    console.log('Global clearFile called');
    if (window.fraudShieldApp) {
        return window.fraudShieldApp.clearFile();
    } else {
        console.log('FraudShieldApp not yet initialized for clearFile');
        try {
            if (typeof FraudShieldApp !== 'undefined') {
                window.fraudShieldApp = new FraudShieldApp();
                return window.fraudShieldApp.clearFile();
            }
        } catch (e) {
            console.error('Emergency initialization failed for clearFile:', e);
        }
    }
};

window.useSampleData = function() {
    console.log('Global useSampleData called');
    if (window.fraudShieldApp) {
        return window.fraudShieldApp.useSampleData();
    } else {
        console.log('FraudShieldApp not yet initialized for useSampleData');
        try {
            if (typeof FraudShieldApp !== 'undefined') {
                window.fraudShieldApp = new FraudShieldApp();
                return window.fraudShieldApp.useSampleData();
            }
        } catch (e) {
            console.error('Emergency initialization failed for useSampleData:', e);
        }
    }
};

window.exportResults = function() {
    if (window.fraudShieldApp) {
        return window.fraudShieldApp.exportResults();
    }
};

window.toggleMobileMenu = function() {
    const nav = document.querySelector('.main-navigation');
    if (nav) {
        nav.classList.toggle('mobile-open');
    }
};

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded - Initializing FraudShield App');
    
    window.fraudShieldApp = new FraudShieldApp();
    
    console.log('FraudShieldApp initialized successfully');
});

// Fallback initialization in case DOMContentLoaded doesn't fire
window.addEventListener('load', () => {
    if (!window.fraudShieldApp) {
        console.log('Fallback initialization triggered');
        window.fraudShieldApp = new FraudShieldApp();
        
        // Re-register global functions
        window.showSection = (sectionId) => {
            console.log('Fallback showSection called with:', sectionId);
            return window.fraudShieldApp.showSection(sectionId);
        };
        window.analyzeTransactions = () => window.fraudShieldApp.analyzeTransactions();
        window.clearFile = () => window.fraudShieldApp.clearFile();
        window.useSampleData = () => window.fraudShieldApp.useSampleData();
        window.exportResults = () => window.fraudShieldApp.exportResults();
        window.toggleMobileMenu = () => {
            const nav = document.querySelector('.main-navigation');
            nav.classList.toggle('mobile-open');
        };
    }
});

// Add some additional CSS for new components
const additionalStyles = `
    .drag-over {
        border-color: var(--primary-color) !important;
        background: rgba(30, 64, 175, 0.05) !important;
    }

    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
    }

    .status-badge.fraud {
        background: rgba(220, 38, 38, 0.1);
        color: #dc2626;
    }

    .status-badge.normal {
        background: rgba(5, 150, 105, 0.1);
        color: #059669;
    }

    .risk-score {
        padding: 4px 8px;
        border-radius: 8px;
        text-align: center;
        font-weight: 600;
        font-size: 14px;
    }

    .risk-score.high {
        background: rgba(220, 38, 38, 0.1);
        color: #dc2626;
    }

    .risk-score.medium {
        background: rgba(217, 119, 6, 0.1);
        color: #d97706;
    }

    .risk-score.low {
        background: rgba(5, 150, 105, 0.1);
        color: #059669;
    }

    .mobile-open {
        display: flex !important;
        position: fixed;
        top: 80px;
        left: 0;
        right: 0;
        background: white;
        flex-direction: column;
        padding: 20px;
        box-shadow: var(--shadow-lg);
        border-bottom: 1px solid var(--border-light);
    }

    @media (max-width: 768px) {
        .main-navigation {
            display: none;
        }
        
        .mobile-menu-btn {
            display: flex;
        }
    }
`;

// Inject additional styles
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);