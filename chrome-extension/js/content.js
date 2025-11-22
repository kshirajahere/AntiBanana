/**
 * AntiBanana WhatsApp Web Content Script
 * Adds deepfake detection and image protection features to WhatsApp Web
 */

console.log('🍌 AntiBanana loaded on WhatsApp Web');

// Configuration
let BACKEND_URL = 'http://localhost:5000';
let protectionEnabled = false;

// Load settings
chrome.storage.sync.get(['backendUrl'], (result) => {
    if (result.backendUrl) {
        BACKEND_URL = result.backendUrl;
    }
});

// Observer to watch for new images
let observer = null;

// Initialize when page is ready
function initialize() {
    console.log('🍌 Initializing AntiBanana on WhatsApp Web...');
    
    // Add detect buttons to existing images
    addDetectButtonsToImages();
    
    // Add protect toggle to attachment panel
    observeAttachmentPanel();
    
    // Watch for new messages with images
    observeMessages();
}

/**
 * Add "Detect with AntiBanana" button to received images
 */
function addDetectButtonsToImages() {
    // WhatsApp Web image selectors
    const imageSelectors = [
        'img[src*="blob:"]',  // Blob images in messages
        'img[data-plain-text]', // Message images
        'div[data-id] img', // Images in message containers
        '._2fJvx img' // Media viewer images
    ];
    
    imageSelectors.forEach(selector => {
        const images = document.querySelectorAll(selector);
        images.forEach(img => {
            if (!img.hasAttribute('data-antibanana-processed')) {
                addDetectButton(img);
            }
        });
    });
}

/**
 * Add detect button overlay to a specific image
 */
function addDetectButton(img) {
    // Mark as processed
    img.setAttribute('data-antibanana-processed', 'true');
    
    // Find parent container
    let container = img.closest('div[data-id]') || img.parentElement;
    if (!container) return;
    
    // Make container relative if not already
    const position = window.getComputedStyle(container).position;
    if (position === 'static') {
        container.style.position = 'relative';
    }
    
    // Create detect button
    const detectBtn = document.createElement('button');
    detectBtn.className = 'antibanana-detect-btn';
    detectBtn.innerHTML = '🍌 Detect';
    detectBtn.title = 'Detect with AntiBanana';
    
    // Add click handler
    detectBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        detectImage(img, detectBtn);
    });
    
    // Position button over image
    detectBtn.style.position = 'absolute';
    detectBtn.style.top = '8px';
    detectBtn.style.right = '8px';
    detectBtn.style.zIndex = '1000';
    
    container.appendChild(detectBtn);
}

/**
 * Detect if image is a deepfake
 */
async function detectImage(img, button) {
    const originalText = button.innerHTML;
    button.innerHTML = '⏳ Analyzing...';
    button.disabled = true;
    
    try {
        // Get image as blob
        const blob = await fetchImageAsBlob(img.src);
        
        // Send to backend
        const formData = new FormData();
        formData.append('file', blob, 'whatsapp-image.jpg');
        formData.append('c2pa', 'true');
        formData.append('enable_xai', 'false'); // Faster without XAI
        
        const response = await fetch(`${BACKEND_URL}/detect`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Detection failed');
        
        const result = await response.json();
        
        // Show result
        showDetectionResult(result, button);
        
    } catch (error) {
        console.error('Detection error:', error);
        button.innerHTML = '❌ Error';
        button.style.backgroundColor = '#ef4444';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.style.backgroundColor = '';
        }, 2000);
    }
}

/**
 * Fetch image as blob (handling CORS and blob URLs)
 */
async function fetchImageAsBlob(src) {
    // If it's a blob URL, fetch directly
    if (src.startsWith('blob:')) {
        const response = await fetch(src);
        return await response.blob();
    }
    
    // Otherwise fetch with CORS mode
    const response = await fetch(src, { mode: 'cors' });
    return await response.blob();
}

/**
 * Show detection result as a popup notification
 */
function showDetectionResult(result, button) {
    const detection = result.deepfake_detection;
    const isFake = detection.is_fake;
    const confidence = (detection.confidence * 100).toFixed(1);
    
    // Update button
    button.innerHTML = isFake ? '⚠️ FAKE' : '✅ Real';
    button.style.backgroundColor = isFake ? '#ef4444' : '#10b981';
    button.style.color = 'white';
    
    // Create result popup
    const popup = document.createElement('div');
    popup.className = 'antibanana-result-popup';
    popup.innerHTML = `
        <div class="antibanana-popup-header">
            <span class="antibanana-popup-icon">${isFake ? '⚠️' : '✅'}</span>
            <strong>AntiBanana Detection</strong>
            <button class="antibanana-popup-close">×</button>
        </div>
        <div class="antibanana-popup-body">
            <div class="antibanana-result-item">
                <span>Classification:</span>
                <span class="antibanana-badge ${isFake ? 'fake' : 'real'}">
                    ${isFake ? 'Deepfake' : 'Real Image'}
                </span>
            </div>
            <div class="antibanana-result-item">
                <span>Confidence:</span>
                <span>${confidence}%</span>
            </div>
            ${result.c2pa_verification ? `
                <div class="antibanana-result-item">
                    <span>C2PA:</span>
                    <span class="antibanana-badge ${result.c2pa_verification.has_c2pa ? 'real' : 'fake'}">
                        ${result.c2pa_verification.has_c2pa ? '✓ Verified' : '✗ No C2PA'}
                    </span>
                </div>
            ` : ''}
        </div>
    `;
    
    // Position popup near the button
    const buttonRect = button.getBoundingClientRect();
    popup.style.position = 'fixed';
    popup.style.top = `${buttonRect.bottom + 10}px`;
    popup.style.right = `${window.innerWidth - buttonRect.right}px`;
    popup.style.zIndex = '10000';
    
    document.body.appendChild(popup);
    
    // Close button
    popup.querySelector('.antibanana-popup-close').addEventListener('click', () => {
        popup.remove();
    });
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
        if (popup.parentElement) {
            popup.remove();
        }
    }, 10000);
    
    // Reset button after 5 seconds
    setTimeout(() => {
        button.innerHTML = '🍌 Detect';
        button.style.backgroundColor = '';
        button.style.color = '';
        button.disabled = false;
    }, 5000);
}

/**
 * Observe attachment panel for image uploads
 */
function observeAttachmentPanel() {
    // Watch for attachment panel to appear
    const targetNode = document.body;
    
    const config = { childList: true, subtree: true };
    
    const callback = (mutationsList) => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                // Check for attachment preview
                const attachmentPreviews = document.querySelectorAll('div[data-animate-media-preview]');
                attachmentPreviews.forEach(preview => {
                    if (!preview.hasAttribute('data-antibanana-protect-added')) {
                        addProtectToggle(preview);
                    }
                });
                
                // Also check for image preview containers
                const imagePreviews = document.querySelectorAll('div[role="application"] img');
                imagePreviews.forEach(img => {
                    const container = img.closest('div[data-animate-media-preview]') || 
                                    img.closest('div[role="application"]');
                    if (container && !container.hasAttribute('data-antibanana-protect-added')) {
                        addProtectToggle(container);
                    }
                });
            }
        }
    };
    
    const attachmentObserver = new MutationObserver(callback);
    attachmentObserver.start = () => attachmentObserver.observe(targetNode, config);
    attachmentObserver.start();
}

/**
 * Add protect toggle to image attachment preview
 */
function addProtectToggle(container) {
    container.setAttribute('data-antibanana-protect-added', 'true');
    
    // Create toggle container
    const toggleContainer = document.createElement('div');
    toggleContainer.className = 'antibanana-protect-toggle';
    toggleContainer.innerHTML = `
        <label class="antibanana-toggle-label">
            <input type="checkbox" class="antibanana-toggle-input" ${protectionEnabled ? 'checked' : ''}>
            <span class="antibanana-toggle-slider"></span>
            <span class="antibanana-toggle-text">
                <span class="antibanana-toggle-icon">🛡️</span>
                Protect with AntiBanana
            </span>
        </label>
        <div class="antibanana-toggle-status" style="display: none;">
            <span class="antibanana-spinner"></span>
            <span class="antibanana-status-text">Protecting image...</span>
        </div>
    `;
    
    // Find appropriate location to insert
    const insertLocation = container.querySelector('footer') || 
                          container.querySelector('div[role="button"]')?.parentElement ||
                          container;
    
    if (insertLocation) {
        insertLocation.insertBefore(toggleContainer, insertLocation.firstChild);
    } else {
        container.appendChild(toggleContainer);
    }
    
    // Handle toggle change
    const checkbox = toggleContainer.querySelector('.antibanana-toggle-input');
    checkbox.addEventListener('change', (e) => {
        protectionEnabled = e.target.checked;
        
        if (protectionEnabled) {
            // Find the image in this container
            const img = container.querySelector('img');
            if (img) {
                protectAndReplaceImage(img, toggleContainer);
            }
        }
    });
}

/**
 * Protect image before sending
 */
async function protectAndReplaceImage(img, toggleContainer) {
    const statusDiv = toggleContainer.querySelector('.antibanana-toggle-status');
    const checkbox = toggleContainer.querySelector('.antibanana-toggle-input');
    
    statusDiv.style.display = 'flex';
    checkbox.disabled = true;
    
    try {
        // Get image as blob
        const blob = await fetchImageAsBlob(img.src);
        
        // Send to backend for protection
        const formData = new FormData();
        formData.append('file', blob, 'whatsapp-image.jpg');
        formData.append('strength', 'medium'); // Can be made configurable
        
        const response = await fetch(`${BACKEND_URL}/protect`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error('Protection failed');
        
        const result = await response.json();
        
        // Replace image with protected version
        img.src = `data:image/png;base64,${result.protected_image}`;
        
        // Show success
        statusDiv.querySelector('.antibanana-status-text').textContent = '✅ Protected!';
        statusDiv.querySelector('.antibanana-spinner').style.display = 'none';
        
        setTimeout(() => {
            statusDiv.style.display = 'none';
            checkbox.disabled = false;
        }, 2000);
        
    } catch (error) {
        console.error('Protection error:', error);
        statusDiv.querySelector('.antibanana-status-text').textContent = '❌ Protection failed';
        statusDiv.querySelector('.antibanana-spinner').style.display = 'none';
        
        setTimeout(() => {
            statusDiv.style.display = 'none';
            checkbox.disabled = false;
            checkbox.checked = false;
            protectionEnabled = false;
        }, 3000);
    }
}

/**
 * Observe new messages being added
 */
function observeMessages() {
    const targetNode = document.querySelector('#main') || document.body;
    
    const config = { childList: true, subtree: true };
    
    const callback = (mutationsList) => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                // Throttle to avoid excessive processing
                setTimeout(() => {
                    addDetectButtonsToImages();
                }, 500);
            }
        }
    };
    
    observer = new MutationObserver(callback);
    observer.observe(targetNode, config);
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
} else {
    initialize();
}

// Re-initialize when navigating in WhatsApp Web
window.addEventListener('load', () => {
    setTimeout(initialize, 2000); // Wait for WhatsApp to fully load
});
