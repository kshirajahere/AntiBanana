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
            // For detect tab, accept both images and videos
            if (type === 'detect') {
                if (file && (file.type.startsWith('image/') || file.type.startsWith('video/'))) {
                    handleFileSelect(file, type);
                }
            } else {
                // Other tabs only accept images
                if (file && file.type.startsWith('image/')) {
                    handleFileSelect(file, type);
                }
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
    
    const isVideo = file.type.startsWith('video/');
    const btn = document.getElementById('detectBtn');
    const resultContainer = document.getElementById('detectResult');
    const resultContent = document.getElementById('detectResultContent');
    
    setLoading(btn, true);
    resultContainer.hidden = true;
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        let endpoint = '/detect';
        
        if (isVideo) {
            // Video detection
            endpoint = '/detect-video';
            formData.append('num_samples', '5'); // Analyze 5 frames
        } else {
            // Image detection
            const includeC2PA = document.getElementById('detectC2PA').checked;
            const enableXAI = document.getElementById('detectXAI').checked;
            
            formData.append('c2pa', includeC2PA ? 'true' : 'false');
            formData.append('enable_xai', enableXAI ? 'true' : 'false');
            
            if (enableXAI) {
                formData.append('xai_methods', 'GradCAM++,IntegratedGradients');
            }
        }
        
        const response = await fetch(`${BACKEND_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Detection failed');
        
        const result = await response.json();
        displayDetectResult(result, resultContent, isVideo);
        resultContainer.hidden = false;
        
    } catch (error) {
        showAlert(`Detection failed: ${error.message}`, 'error');
    } finally {
        setLoading(btn, false);
    }
}

function displayDetectResult(result, container, isVideo = false) {
    let html = '';
    
    // Basic detection result
    const detection = result.deepfake_detection || result.video_deepfake_detection;
    if (detection) {
        const isFake = detection.is_fake;
        const confidence = (detection.confidence * 100).toFixed(1);
        const manipulationType = detection.manipulation_type || 'Unknown';
        const processingTime = detection.processing_time ? detection.processing_time.toFixed(2) : 'N/A';
        
        // Header with big status
        html += `
            <div style="padding: 24px; text-align: center; background: ${isFake ? 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)' : 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)'}; border-radius: 8px; margin-bottom: 16px;">
                <div style="font-size: 48px; margin-bottom: 8px;">${isFake ? '⚠️' : '✅'}</div>
                <div style="font-size: 24px; font-weight: 700; color: ${isFake ? '#b91c1c' : '#065f46'}; margin-bottom: 8px;">
                    ${isFake ? 'Deepfake Detected' : (isVideo ? 'Authentic Video' : 'Authentic Image')}
                </div>
                <div style="font-size: 14px; color: #6b7280;">
                    ${isFake ? 'Our AI detected signs of manipulation in this media.' : 'Our AI analysis indicates this is likely authentic without significant manipulation.'}
                </div>
            </div>
        `;
        
        // Confidence score with progress bar
        html += `
            <div class="result-item" style="margin-bottom: 16px;">
                <span class="result-label" style="font-weight: 600; font-size: 14px;">Confidence Score:</span>
                <div style="flex: 1; margin-left: 20px;">
                    <div style="width: 100%; background: #e5e7eb; height: 12px; border-radius: 6px; overflow: hidden;">
                        <div style="width: ${confidence}%; height: 100%; background: ${isFake ? 'linear-gradient(90deg, #ef4444 0%, #dc2626 100%)' : 'linear-gradient(90deg, #10b981 0%, #059669 100%)'}; transition: width 0.5s ease;"></div>
                    </div>
                    <div style="text-align: right; margin-top: 4px; font-size: 14px; font-weight: 600; color: ${isFake ? '#ef4444' : '#10b981'};">${confidence}%</div>
                </div>
            </div>
        `;
        
        // Additional details
        html += `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
                <div style="padding: 12px; background: #f9fafb; border-radius: 6px;">
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Manipulation Type</div>
                    <div style="font-weight: 600; color: #374151;">${manipulationType}</div>
                </div>
                <div style="padding: 12px; background: #f9fafb; border-radius: 6px;">
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Processing Time</div>
                    <div style="font-weight: 600; color: #374151;">${processingTime}s</div>
                </div>
            </div>
        `;
        
        // Video-specific frame analysis
        if (isVideo && result.frame_results) {
            const fakeFrames = result.frame_results.filter(f => f.is_fake).length;
            const totalFrames = result.frame_results.length;
            const fakePercentage = ((fakeFrames / totalFrames) * 100).toFixed(1);
            
            html += `
                <div style="margin-top: 16px; padding: 16px; border: 2px solid ${fakePercentage > 30 ? '#fecaca' : '#d1fae5'}; border-radius: 8px; background: ${fakePercentage > 30 ? '#fef2f2' : '#f0fdf4'};">
                    <div style="font-weight: 600; margin-bottom: 12px; color: #374151;">📊 Frame Analysis</div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">
                        <div style="text-align: center; padding: 8px; background: white; border-radius: 4px;">
                            <div style="font-size: 20px; font-weight: 700; color: #3b82f6;">${totalFrames}</div>
                            <div style="font-size: 11px; color: #6b7280;">Total Frames</div>
                        </div>
                        <div style="text-align: center; padding: 8px; background: white; border-radius: 4px;">
                            <div style="font-size: 20px; font-weight: 700; color: #ef4444;">${fakeFrames}</div>
                            <div style="font-size: 11px; color: #6b7280;">Fake Frames</div>
                        </div>
                        <div style="text-align: center; padding: 8px; background: white; border-radius: 4px;">
                            <div style="font-size: 20px; font-weight: 700; color: #10b981;">${totalFrames - fakeFrames}</div>
                            <div style="font-size: 11px; color: #6b7280;">Real Frames</div>
                        </div>
                    </div>
                    <div style="margin-top: 8px; font-size: 13px; color: #6b7280; text-align: center;">
                        ${fakePercentage}% of frames show signs of manipulation
                    </div>
                </div>
            `;
        }
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
    const strength = result.protection_strength || result.strength || 'medium';
    const processingTime = result.processing_time ? result.processing_time.toFixed(2) : 'N/A';
    const phasesApplied = result.phases_applied || ['Frequency', 'Spatial', 'Adversarial'];
    
    const html = `
        <div style="padding: 24px; text-align: center; background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); border-radius: 8px; margin-bottom: 16px;">
            <div style="font-size: 48px; margin-bottom: 8px;">🛡️</div>
            <div style="font-size: 24px; font-weight: 700; color: #065f46; margin-bottom: 8px;">
                Protection Applied
            </div>
            <div style="font-size: 14px; color: #6b7280;">
                Your image has been protected with an imperceptible watermark
            </div>
        </div>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px;">
            <div style="padding: 12px; background: #f9fafb; border-radius: 6px;">
                <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Protection Strength</div>
                <div style="font-weight: 600; color: #374151; text-transform: uppercase;">${strength}</div>
            </div>
            <div style="padding: 12px; background: #f9fafb; border-radius: 6px;">
                <div style="font-size: 12px; color: #6b7280; margin-bottom: 4px;">Processing Time</div>
                <div style="font-weight: 600; color: #374151;">${processingTime}s</div>
            </div>
        </div>
        
        <div style="padding: 12px; background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 6px; margin-bottom: 16px;">
            <div style="font-size: 12px; color: #6b7280; margin-bottom: 6px;">Protection Phases Applied</div>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                ${phasesApplied.map(phase => `
                    <span style="padding: 4px 10px; background: #10b981; color: white; border-radius: 4px; font-size: 11px; font-weight: 600;">${phase}</span>
                `).join('')}
            </div>
        </div>
        
        <div style="margin-bottom: 16px; padding: 16px; background: #fffbeb; border: 1px solid #fde68a; border-radius: 6px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                <span style="font-size: 20px;">ℹ️</span>
                <span style="font-weight: 600; color: #78350f;">About Protected Images</span>
            </div>
            <div style="font-size: 13px; color: #78350f; line-height: 1.5;">
                • The watermark is invisible to human eyes<br>
                • Protection survives compression & resizing<br>
                • Can be detected by our system to prove ownership<br>
                • No visual quality loss
            </div>
        </div>
        
        <div style="border-radius: 8px; overflow: hidden; margin-bottom: 16px; border: 2px solid #d1fae5;">
            <img src="data:image/png;base64,${result.protected_image}" style="width: 100%; display: block;" alt="Protected Image">
        </div>
        
        <button class="btn btn-primary" onclick="downloadProtectedImage('${result.protected_image}')" style="width: 100%; padding: 12px; font-size: 16px; font-weight: 600;">
            ⬇️ Download Protected Image
        </button>
    `;
    container.innerHTML = html;
}

function downloadProtectedImage(base64Data) {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${base64Data}`;
    link.download = `protected_antibanana_${Date.now()}.png`;
    link.click();
    showAlert('Protected image downloaded successfully!', 'success');
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
