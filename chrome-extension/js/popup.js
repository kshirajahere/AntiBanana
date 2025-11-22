// Configuration
let BACKEND_URL = 'http://localhost:5000';

// State
let currentTab = 'detect';
let selectedFiles = {
    detect: null,
    protect: null,
    c2pa: null,
    explain: null
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    checkServerStatus();
    initializeTabs();
    initializeUploads();
    initializeButtons();
    initializeSettings();
});

// Load settings from storage
function loadSettings() {
    chrome.storage.sync.get(['backendUrl'], (result) => {
        if (result.backendUrl) {
            BACKEND_URL = result.backendUrl;
            document.getElementById('backendUrl').value = BACKEND_URL;
        }
    });
}

// Save settings to storage
function initializeSettings() {
    document.getElementById('saveSettings').addEventListener('click', () => {
        const url = document.getElementById('backendUrl').value;
        chrome.storage.sync.set({ backendUrl: url }, () => {
            BACKEND_URL = url;
            showAlert('Settings saved successfully', 'success');
            checkServerStatus();
        });
    });
}

// Check server status
async function checkServerStatus() {
    const statusIndicator = document.getElementById('serverStatus');
    const statusText = statusIndicator.querySelector('.status-text');
    
    try {
        const response = await fetch(`${BACKEND_URL}/health`, {
            method: 'GET',
            signal: AbortSignal.timeout(5000)
        });
        
        if (response.ok) {
            statusIndicator.classList.add('connected');
            statusIndicator.classList.remove('error');
            statusText.textContent = 'Connected';
        } else {
            throw new Error('Server error');
        }
    } catch (error) {
        statusIndicator.classList.add('error');
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'Offline';
    }
}

// Tab management
function initializeTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;
            switchTab(tabName);
        });
    });
}

function switchTab(tabName) {
    currentTab = tabName;
    
    // Update buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });
    
    // Update panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === tabName);
    });
}

// Upload handling
function initializeUploads() {
    const uploads = ['detect', 'protect', 'c2pa', 'explain'];
    
    uploads.forEach(type => {
        const uploadArea = document.getElementById(`${type}Upload`);
        const fileInput = document.getElementById(`${type}File`);
        const btn = document.getElementById(`${type}Btn`);
        
        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());
        
        // File selection
        fileInput.addEventListener('change', (e) => {
            handleFileSelect(e.target.files[0], type);
        });
        
        // Drag and drop
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
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                handleFileSelect(file, type);
            }
        });
    });
}

function handleFileSelect(file, type) {
    if (!file) return;
    
    selectedFiles[type] = file;
    const uploadArea = document.getElementById(`${type}Upload`);
    const btn = document.getElementById(`${type}Btn`);
    
    uploadArea.classList.add('has-file');
    uploadArea.querySelector('p').textContent = `✓ ${file.name}`;
    btn.disabled = false;
}

// Button handlers
function initializeButtons() {
    document.getElementById('detectBtn').addEventListener('click', handleDetect);
    document.getElementById('protectBtn').addEventListener('click', handleProtect);
    document.getElementById('c2paBtn').addEventListener('click', handleC2PA);
    document.getElementById('explainBtn').addEventListener('click', handleExplain);
}

// Detect handler
async function handleDetect() {
    const file = selectedFiles.detect;
    if (!file) return;
    
    const btn = document.getElementById('detectBtn');
    const resultContainer = document.getElementById('detectResult');
    const resultContent = document.getElementById('detectResultContent');
    
    setLoading(btn, true);
    resultContainer.hidden = true;
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const includeC2PA = document.getElementById('detectC2PA').checked;
        const enableXAI = document.getElementById('detectXAI').checked;
        
        formData.append('c2pa', includeC2PA ? 'true' : 'false');
        formData.append('enable_xai', enableXAI ? 'true' : 'false');
        
        if (enableXAI) {
            formData.append('xai_methods', 'GradCAM++,IntegratedGradients');
        }
        
        const response = await fetch(`${BACKEND_URL}/detect`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Detection failed');
        
        const result = await response.json();
        displayDetectResult(result, resultContent);
        resultContainer.hidden = false;
        
    } catch (error) {
        showAlert(`Detection failed: ${error.message}`, 'error');
    } finally {
        setLoading(btn, false);
    }
}

function displayDetectResult(result, container) {
    let html = '';
    
    // Basic detection result
    if (result.deepfake_detection) {
        const detection = result.deepfake_detection;
        const isFake = detection.is_fake;
        const confidence = (detection.confidence * 100).toFixed(1);
        
        html += `
            <div class="result-item">
                <span class="result-label">Classification:</span>
                <span class="result-badge ${isFake ? 'badge-fake' : 'badge-real'}">
                    ${isFake ? '⚠️ Fake' : '✓ Real'}
                </span>
            </div>
            <div class="result-item">
                <span class="result-label">Confidence:</span>
                <div style="flex: 1; margin-left: 20px;">
                    <div class="progress-bar">
                        <div class="progress-fill ${isFake ? 'fake' : ''}" style="width: ${confidence}%"></div>
                    </div>
                    <div style="text-align: right; margin-top: 4px; font-size: 12px; color: #6b7280;">
                        ${confidence}%
                    </div>
                </div>
            </div>
        `;
    }
    
    // C2PA verification
    if (result.c2pa_verification) {
        const c2pa = result.c2pa_verification;
        html += `
            <div class="result-item">
                <span class="result-label">C2PA Status:</span>
                <span class="result-badge ${c2pa.has_c2pa ? 'badge-success' : 'badge-warning'}">
                    ${c2pa.has_c2pa ? '✓ Verified' : '⚠️ No C2PA'}
                </span>
            </div>
        `;
        
        if (c2pa.has_c2pa && c2pa.claims) {
            html += `<div class="result-item">
                <span class="result-label">Claims Found:</span>
                <span class="result-value">${c2pa.claims}</span>
            </div>`;
        }
    }
    
    // XAI Explanations
    if (result.xai_explanations && result.xai_explanations.visualizations) {
        html += '<div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e5e7eb;">';
        html += '<div style="font-weight: 600; margin-bottom: 8px; color: #374151;">XAI Visualizations:</div>';
        
        Object.entries(result.xai_explanations.visualizations).forEach(([method, imgData]) => {
            html += `
                <div style="margin-bottom: 12px;">
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">${method}</div>
                    <img src="data:image/png;base64,${imgData}" class="result-image" alt="${method}">
                </div>
            `;
        });
        html += '</div>';
    }
    
    container.innerHTML = html;
}

// Protect handler
async function handleProtect() {
    const file = selectedFiles.protect;
    if (!file) return;
    
    const btn = document.getElementById('protectBtn');
    const resultContainer = document.getElementById('protectResult');
    const resultContent = document.getElementById('protectResultContent');
    
    setLoading(btn, true);
    resultContainer.hidden = true;
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('strength', document.getElementById('protectStrength').value);
        
        const response = await fetch(`${BACKEND_URL}/protect`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Protection failed');
        
        const result = await response.json();
        displayProtectResult(result, resultContent);
        resultContainer.hidden = false;
        
    } catch (error) {
        showAlert(`Protection failed: ${error.message}`, 'error');
    } finally {
        setLoading(btn, false);
    }
}

function displayProtectResult(result, container) {
    const html = `
        <div class="result-item">
            <span class="result-label">Status:</span>
            <span class="result-badge badge-success">✓ Protected</span>
        </div>
        <div class="result-item">
            <span class="result-label">Strength:</span>
            <span class="result-value">${result.strength.toUpperCase()}</span>
        </div>
        <div class="result-item">
            <span class="result-label">Processing Time:</span>
            <span class="result-value">${result.processing_time.toFixed(2)}s</span>
        </div>
        <div class="result-item">
            <span class="result-label">Phases Applied:</span>
            <span class="result-value">${result.phases_applied.join(', ')}</span>
        </div>
        <img src="data:image/png;base64,${result.protected_image}" class="result-image" alt="Protected Image">
        <button class="btn btn-secondary download-btn" onclick="downloadProtectedImage('${result.protected_image}')">
            ⬇️ Download Protected Image
        </button>
    `;
    container.innerHTML = html;
}

function downloadProtectedImage(base64Data) {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${base64Data}`;
    link.download = `protected_${Date.now()}.png`;
    link.click();
}

// C2PA handler
async function handleC2PA() {
    const file = selectedFiles.c2pa;
    if (!file) return;
    
    const btn = document.getElementById('c2paBtn');
    const resultContainer = document.getElementById('c2paResult');
    const resultContent = document.getElementById('c2paResultContent');
    
    setLoading(btn, true);
    resultContainer.hidden = true;
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch(`${BACKEND_URL}/c2pa`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('C2PA verification failed');
        
        const result = await response.json();
        displayC2PAResult(result, resultContent);
        resultContainer.hidden = false;
        
    } catch (error) {
        showAlert(`C2PA verification failed: ${error.message}`, 'error');
    } finally {
        setLoading(btn, false);
    }
}

function displayC2PAResult(result, container) {
    let html = '';
    
    if (result.has_c2pa) {
        html += `
            <div class="result-item">
                <span class="result-label">C2PA Status:</span>
                <span class="result-badge badge-success">✓ C2PA Found</span>
            </div>
            <div class="result-item">
                <span class="result-label">Total Claims:</span>
                <span class="result-value">${result.claims || 0}</span>
            </div>
        `;
        
        if (result.manifest) {
            html += `
                <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #e5e7eb;">
                    <div style="font-weight: 600; margin-bottom: 8px; color: #374151;">Manifest Details:</div>
                    <pre style="background: #f9fafb; padding: 12px; border-radius: 6px; font-size: 11px; overflow-x: auto; max-height: 200px;">${JSON.stringify(result.manifest, null, 2)}</pre>
                </div>
            `;
        }
    } else {
        html += `
            <div class="alert alert-info">
                <strong>No C2PA data found</strong><br>
                ${result.error || 'This image does not contain C2PA provenance information.'}
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Explain handler
async function handleExplain() {
    const file = selectedFiles.explain;
    if (!file) return;
    
    const btn = document.getElementById('explainBtn');
    const resultContainer = document.getElementById('explainResult');
    const resultContent = document.getElementById('explainResultContent');
    
    setLoading(btn, true);
    resultContainer.hidden = true;
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('method', document.getElementById('explainMethod').value);
        formData.append('quick', document.getElementById('explainQuick').checked ? 'true' : 'false');
        
        const response = await fetch(`${BACKEND_URL}/explain`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Explanation generation failed');
        
        const result = await response.json();
        displayExplainResult(result, resultContent);
        resultContainer.hidden = false;
        
    } catch (error) {
        showAlert(`Explanation failed: ${error.message}`, 'error');
    } finally {
        setLoading(btn, false);
    }
}

function displayExplainResult(result, container) {
    let html = '';
    
    if (result.status === 'success' && result.visualizations) {
        html += '<div style="font-weight: 600; margin-bottom: 12px; color: #374151;">Explanation Visualizations:</div>';
        
        Object.entries(result.visualizations).forEach(([method, imgData]) => {
            html += `
                <div style="margin-bottom: 16px;">
                    <div style="font-size: 13px; font-weight: 600; color: #6b7280; margin-bottom: 8px; text-transform: uppercase;">${method}</div>
                    <img src="data:image/png;base64,${imgData}" class="result-image" alt="${method} explanation">
                </div>
            `;
        });
        
        if (result.processing_time) {
            html += `
                <div class="result-item">
                    <span class="result-label">Processing Time:</span>
                    <span class="result-value">${result.processing_time.toFixed(2)}s</span>
                </div>
            `;
        }
    } else {
        html += `
            <div class="alert alert-error">
                ${result.error || 'Failed to generate explanations'}
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Utility functions
function setLoading(button, loading) {
    const text = button.querySelector('.btn-text');
    const spinner = button.querySelector('.spinner');
    
    if (loading) {
        text.hidden = true;
        spinner.hidden = false;
        button.disabled = true;
    } else {
        text.hidden = false;
        spinner.hidden = true;
        button.disabled = false;
    }
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.cssText = 'position: fixed; top: 70px; left: 20px; right: 20px; z-index: 1000; animation: slideDown 0.3s;';
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.animation = 'slideUp 0.3s';
        setTimeout(() => alertDiv.remove(), 300);
    }, 3000);
}

// Make downloadProtectedImage available globally
window.downloadProtectedImage = downloadProtectedImage;
