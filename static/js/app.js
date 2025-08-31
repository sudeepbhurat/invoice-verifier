// Invoice Verifier Frontend JavaScript

class InvoiceVerifier {
    constructor() {
        this.initializeEventListeners();
        this.setupDragAndDrop();
    }

    initializeEventListeners() {
        // File upload form
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleFileUpload(e));
        }

        // Manual entry form
        const manualForm = document.getElementById('manualForm');
        if (manualForm) {
            manualForm.addEventListener('submit', (e) => this.handleManualEntry(e));
        }

        // File input change
        const fileInput = document.getElementById('file');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }
    }

    setupDragAndDrop() {
        const dropArea = document.querySelector('.border-dashed');
        if (!dropArea) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => this.highlight(dropArea), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => this.unhighlight(dropArea), false);
        });

        dropArea.addEventListener('drop', (e) => this.handleDrop(e), false);
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight(elem) {
        elem.classList.add('dragover');
    }

    unhighlight(elem) {
        elem.classList.remove('dragover');
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        const fileInput = document.getElementById('file');
        
        if (fileInput && files.length > 0) {
            fileInput.files = files;
            this.handleFileSelect({ target: fileInput });
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            const dropArea = document.querySelector('.border-dashed');
            if (dropArea) {
                const icon = dropArea.querySelector('.fa-file-pdf');
                const text = dropArea.querySelector('span');
                
                if (icon) icon.className = 'fas fa-file-pdf text-6xl text-blue-600';
                if (text) text.textContent = file.name;
            }
        }
    }

    async handleFileUpload(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const file = formData.get('file');
        
        if (!file) {
            this.showError('Please select a PDF file to upload.');
            return;
        }

        if (!file.name.toLowerCase().endsWith('.pdf')) {
            this.showError('Please select a valid PDF file.');
            return;
        }

        this.showLoading();
        this.hideError();
        this.hideResults();

        try {
            const response = await fetch('/verify', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Upload failed');
            }

            const result = await response.json();
            this.displayResults(result);
        } catch (error) {
            this.showError(`Error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    async handleManualEntry(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = {};
        
        // Convert form data to JSON
        for (let [key, value] of formData.entries()) {
            if (value.trim()) {
                data[key] = value.trim();
            }
        }

        if (Object.keys(data).length === 0) {
            this.showError('Please fill in at least one field.');
            return;
        }

        this.showLoading();
        this.hideError();
        this.hideResults();

        try {
            const response = await fetch('/verify-json', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Verification failed');
            }

            const result = await response.json();
            this.displayResults(result);
        } catch (error) {
            this.showError(`Error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    displayResults(result) {
        const resultsDiv = document.getElementById('results');
        const verdictCard = document.getElementById('verdictCard');
        const scoreText = document.getElementById('scoreText');
        const scoreBar = document.getElementById('scoreBar');
        const extractedFields = document.getElementById('extractedFields');
        const checkResults = document.getElementById('checkResults');

        if (!resultsDiv) return;

        // Display verdict
        this.displayVerdict(verdictCard, result.verdict, result.score);

        // Display score
        this.displayScore(scoreText, scoreBar, result.score);

        // Display extracted fields
        this.displayExtractedFields(extractedFields, result.extracted);

        // Display check results
        this.displayCheckResults(checkResults, result.checks);

        // Show results with animation
        resultsDiv.classList.remove('hidden');
        resultsDiv.classList.add('results-animate');
        
        // Scroll to results
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    displayVerdict(verdictCard, verdict, score) {
        if (!verdictCard) return;

        let icon, bgClass, message;
        
        switch (verdict) {
            case 'PASS':
                icon = 'fas fa-check-circle';
                bgClass = 'verdict-pass';
                message = 'Invoice verification passed successfully!';
                break;
            case 'REVIEW':
                icon = 'fas fa-exclamation-triangle';
                bgClass = 'verdict-review';
                message = 'Invoice requires review - some issues found.';
                break;
            case 'FAIL':
                icon = 'fas fa-times-circle';
                bgClass = 'verdict-fail';
                message = 'Invoice verification failed - multiple issues found.';
                break;
            default:
                icon = 'fas fa-question-circle';
                bgClass = 'bg-gray-500';
                message = 'Verification result unclear.';
        }

        verdictCard.className = `mb-6 p-6 rounded-lg ${bgClass} text-center`;
        verdictCard.innerHTML = `
            <i class="${icon} text-4xl mb-3"></i>
            <h3 class="text-2xl font-bold mb-2">${verdict}</h3>
            <p class="text-lg">${message}</p>
        `;
    }

    displayScore(scoreText, scoreBar, score) {
        if (!scoreText || !scoreBar) return;

        scoreText.textContent = `${score}/100`;

        let scoreClass;
        if (score >= 80) scoreClass = 'score-excellent';
        else if (score >= 60) scoreClass = 'score-good';
        else if (score >= 40) scoreClass = 'score-fair';
        else scoreClass = 'score-poor';

        scoreBar.className = `h-3 rounded-full transition-all duration-500 ${scoreClass}`;
        scoreBar.style.width = `${score}%`;
    }

    displayExtractedFields(container, extracted) {
        if (!container) return;

        const fields = [
            { key: 'gstin', label: 'GSTIN', icon: 'fas fa-id-card' },
            { key: 'invoice_no', label: 'Invoice Number', icon: 'fas fa-hashtag' },
            { key: 'invoice_date', label: 'Invoice Date', icon: 'fas fa-calendar' },
            { key: 'place_of_supply', label: 'Place of Supply', icon: 'fas fa-map-marker-alt' },
            { key: 'hsn', label: 'HSN Code', icon: 'fas fa-barcode' },
            { key: 'taxable_value', label: 'Taxable Value', icon: 'fas fa-rupee-sign' },
            { key: 'total', label: 'Total Amount', icon: 'fas fa-calculator' }
        ];

        container.innerHTML = fields.map(field => {
            const value = extracted[field.key] || 'Not found';
            return `
                <div class="bg-gray-50 p-4 rounded-lg">
                    <div class="flex items-center mb-2">
                        <i class="${field.icon} text-blue-600 mr-2"></i>
                        <span class="font-medium text-gray-700">${field.label}</span>
                    </div>
                    <p class="text-gray-900">${value}</p>
                </div>
            `;
        }).join('');
    }

    displayCheckResults(container, checks) {
        if (!container) return;

        container.innerHTML = checks.map(check => {
            let statusClass, statusIcon;
            
            switch (check.status) {
                case 'PASS':
                    statusClass = 'status-pass';
                    statusIcon = 'fas fa-check-circle text-green-600';
                    break;
                case 'WARN':
                    statusClass = 'status-warn';
                    statusIcon = 'fas fa-exclamation-triangle text-yellow-600';
                    break;
                case 'FAIL':
                    statusClass = 'status-fail';
                    statusIcon = 'fas fa-times-circle text-red-600';
                    break;
                default:
                    statusClass = 'status-info';
                    statusIcon = 'fas fa-info-circle text-blue-600';
            }

            return `
                <div class="bg-white border border-gray-200 rounded-lg p-4">
                    <div class="flex items-start justify-between">
                        <div class="flex items-start space-x-3">
                            <i class="${statusIcon} mt-1"></i>
                            <div class="flex-1">
                                <h4 class="font-medium text-gray-900 mb-1">${check.name}</h4>
                                <p class="text-sm text-gray-600">${check.message}</p>
                                ${check.data ? `<pre class="text-xs text-gray-500 mt-2 bg-gray-50 p-2 rounded">${JSON.stringify(check.data, null, 2)}</pre>` : ''}
                            </div>
                        </div>
                        <span class="status-badge ${statusClass}">${check.status}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    showLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.classList.remove('hidden');
    }

    hideLoading() {
        const loading = document.getElementById('loading');
        if (loading) loading.classList.add('hidden');
    }

    showError(message) {
        const error = document.getElementById('error');
        if (error) {
            error.textContent = message;
            error.classList.remove('hidden');
        }
    }

    hideError() {
        const error = document.getElementById('error');
        if (error) error.classList.add('hidden');
    }

    hideResults() {
        const results = document.getElementById('results');
        if (results) results.classList.add('hidden');
    }

    // Utility function to format currency
    formatCurrency(amount) {
        if (!amount) return 'N/A';
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR'
        }).format(amount);
    }

    // Utility function to validate GSTIN format
    validateGSTINFormat(gstin) {
        const gstinRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/;
        return gstinRegex.test(gstin);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new InvoiceVerifier();
    
    // Add some interactive enhancements
    const cards = document.querySelectorAll('.bg-white.rounded-lg.shadow-lg');
    cards.forEach(card => card.classList.add('card-hover'));
    
    // Add form input enhancements
    const inputs = document.querySelectorAll('input, textarea');
    inputs.forEach(input => input.classList.add('form-input'));
    
    // Add button enhancements
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => button.classList.add('btn-primary'));
});

// Add keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.activeElement.closest('form');
        if (activeForm) {
            activeForm.dispatchEvent(new Event('submit'));
        }
    }
    
    // Escape to hide results
    if (e.key === 'Escape') {
        const results = document.getElementById('results');
        if (results && !results.classList.contains('hidden')) {
            results.classList.add('hidden');
        }
    }
});
