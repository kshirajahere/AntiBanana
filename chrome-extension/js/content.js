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
 * Add "Detect with AntiBanana" button to received images and videos
 */
function addDetectButtonsToImages() {
    // WhatsApp Web media selectors (images and videos)
    const mediaSelectors = [
        'img[src*="blob:"]',  // Blob images in messages
        'video[src*="blob:"]', // Blob videos in messages
        'img[data-plain-text]', // Message images
        'div[data-id] img', // Images in message containers
        'div[data-id] video', // Videos in message containers
        '._2fJvx img', // Media viewer images
        '._2fJvx video' // Media viewer videos
    ];
    
    mediaSelectors.forEach(selector => {
        const mediaElements = document.querySelectorAll(selector);
        mediaElements.forEach(media => {
            if (!media.hasAttribute('data-antibanana-processed')) {
                addDetectButton(media);
            }
        });
    });
}

/**
 * Add detect button overlay to a specific image or video
 */
function addDetectButton(media) {
    // Mark as processed
    media.setAttribute('data-antibanana-processed', 'true');
    
    const isVideo = media.tagName.toLowerCase() === 'video';
    
    // Find parent container
    let container = media.closest('div[data-id]') || media.parentElement;
    if (!container) return;
    
    // Make container relative if not already
    const position = window.getComputedStyle(container).position;
    if (position === 'static') {
        container.style.position = 'relative';
    }
    
    // Create detect button
    const detectBtn = document.createElement('button');
    detectBtn.className = 'antibanana-detect-btn';
    detectBtn.innerHTML = isVideo ? '🍌 Detect Video' : '🍌 Detect';
    detectBtn.title = isVideo ? 'Detect video with AntiBanana' : 'Detect with AntiBanana';
    
    // Add click handler
    detectBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        detectMedia(media, detectBtn, isVideo);
    });
    
    // Position button over image (TOP-RIGHT corner)
    detectBtn.style.position = 'absolute';
    detectBtn.style.top = '8px';
    detectBtn.style.right = '8px';
    detectBtn.style.zIndex = '1001'; // Higher than protect toggle
    
    container.appendChild(detectBtn);
}

/**
 * Detect if media (image/video) is a deepfake
 */
async function detectMedia(media, button, isVideo = false) {
    const originalText = button.innerHTML;
    button.innerHTML = isVideo ? '⏳ Analyzing Video...' : '⏳ Analyzing...';
    button.disabled = true;
    
    try {
        // Get media as blob
        const blob = await fetchMediaAsBlob(media.src, isVideo);
        
        // Prepare form data
        const formData = new FormData();
        const filename = isVideo ? 'whatsapp-video.mp4' : 'whatsapp-image.jpg';
        formData.append('file', blob, filename);
        
        let endpoint = '/detect';
        
        if (isVideo) {
            endpoint = '/detect-video';
            formData.append('num_samples', '5'); // Analyze 5 frames
        } else {
            formData.append('c2pa', 'true');
            formData.append('enable_xai', 'false'); // Faster without XAI
        }
        
        const response = await fetch(`${BACKEND_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) throw new Error(`Detection failed: ${response.statusText}`);
        
        const result = await response.json();
        
        // Show result
        showDetectionResult(result, button, isVideo);
        
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
 * Fetch media (image/video) as blob (handling CORS and blob URLs)
 */
async function fetchMediaAsBlob(src, isVideo = false) {
    console.log(`[AntiBanana] Fetching ${isVideo ? 'video' : 'image'} from:`, src);
    
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
 * Show detection result as a popup notification (matches frontend design)
 */
function showDetectionResult(result, button, isVideo = false) {
    console.log('[AntiBanana] Detection result:', result);
    
    // Handle different response structures
    let detection, isFake, confidence, manipulationType, processingTime;
    
    if (isVideo && result.video_deepfake_detection) {
        detection = result.video_deepfake_detection;
        isFake = detection.is_fake;
        confidence = (detection.confidence * 100).toFixed(1);
        manipulationType = detection.manipulation_type || 'Unknown';
        processingTime = detection.processing_time ? detection.processing_time.toFixed(2) : 'N/A';
    } else if (result.deepfake_detection) {
        detection = result.deepfake_detection;
        isFake = detection.is_fake;
        confidence = (detection.confidence * 100).toFixed(1);
        manipulationType = detection.manipulation_type || 'Unknown';
        processingTime = detection.processing_time ? detection.processing_time.toFixed(2) : 'N/A';
    } else if (result.deepfake) {
        // Handle alternative response format
        const deepfakeResult = Array.isArray(result.deepfake) ? result.deepfake[0] : result.deepfake;
        if (typeof deepfakeResult === 'object' && deepfakeResult.label) {
            isFake = deepfakeResult.label.toLowerCase().includes('fake');
            confidence = (deepfakeResult.score * 100).toFixed(1);
        } else {
            const match = String(deepfakeResult).match(/Fake|Real/);
            isFake = match && match[0] === 'Fake';
            const scoreMatch = String(deepfakeResult).match(/\d+\.\d+/);
            confidence = scoreMatch ? (parseFloat(scoreMatch[0]) * 100).toFixed(1) : '0';
        }
        manipulationType = result.manipulation_type || 'Unknown';
        processingTime = result.processing_time || 'N/A';
    } else {
        console.error('[AntiBanana] Unexpected response format:', result);
        button.innerHTML = '❌ Error';
        button.style.backgroundColor = '#ef4444';
        setTimeout(() => {
            button.innerHTML = '🍌 Detect';
            button.disabled = false;
            button.style.backgroundColor = '';
        }, 3000);
        return;
    }
    
    // Update button
    button.innerHTML = isFake ? '⚠️ FAKE' : '✅ Real';
    button.style.backgroundColor = isFake ? '#ef4444' : '#10b981';
    button.style.color = 'white';
    
    // Create result popup
    const popup = document.createElement('div');
    popup.className = 'antibanana-result-popup';
    
    let detailsHTML = '';
    if (isVideo && result.frame_results) {
        const fakeFrames = result.frame_results.filter(f => f.is_fake).length;
        const totalFrames = result.frame_results.length;
        const fakePercentage = ((fakeFrames / totalFrames) * 100).toFixed(1);
        detailsHTML = `
            <div class="antibanana-popup-detail">
                <strong>Total Frames:</strong> ${totalFrames}
            </div>
            <div class="antibanana-popup-detail">
                <strong>Fake Frames:</strong> ${fakeFrames} (${fakePercentage}%)
            </div>
            <div class="antibanana-popup-detail">
                <strong>Real Frames:</strong> ${totalFrames - fakeFrames}
            </div>
        `;
    } else {
        detailsHTML = `
            <div class="antibanana-popup-detail">
                <strong>Manipulation Type:</strong> ${manipulationType}
            </div>
            <div class="antibanana-popup-detail">
                <strong>Processing Time:</strong> ${processingTime}s
            </div>
        `;
    }
    
    popup.innerHTML = `
        <div class="antibanana-popup-header" style="background: ${isFake ? '#ef4444' : '#10b981'}; color: white;">
            <span class="antibanana-popup-icon">${isFake ? '⚠️' : '✅'}</span>
            <strong>AntiBanana Detection ${isVideo ? '(Video)' : ''}</strong>
            <button class="antibanana-popup-close" style="color: white;">×</button>
        </div>
        <div class="antibanana-popup-body">
            <div class="antibanana-result-item" style="margin-bottom: 12px;">
                <span style="font-weight: 600;">Classification:</span>
                <span class="antibanana-badge ${isFake ? 'fake' : 'real'}" style="padding: 6px 12px; border-radius: 6px; font-weight: 600;">
                    ${isFake ? '⚠️ Deepfake Detected' : (isVideo ? '✅ Authentic Video' : '✅ Authentic Image')}
                </span>
            </div>
            <div class="antibanana-result-item" style="margin-bottom: 8px;">
                <span style="font-weight: 600;">Confidence Score:</span>
                <div style="flex: 1; margin-left: 12px;">
                    <div style="width: 100%; background: #e5e7eb; height: 8px; border-radius: 4px; overflow: hidden;">
                        <div style="width: ${confidence}%; height: 100%; background: ${isFake ? '#ef4444' : '#10b981'}; transition: width 0.3s ease;"></div>
                    </div>
                    <span style="font-size: 12px; color: #6b7280; margin-top: 2px; display: block; text-align: right;">${confidence}%</span>
                </div>
            </div>
            ${detailsHTML}
            ${result.c2pa_verification ? `
                <div class="antibanana-result-item" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;">
                    <span style="font-weight: 600;">C2PA Status:</span>
                    <span class="antibanana-badge ${result.c2pa_verification.has_c2pa ? 'real' : 'fake'}" style="padding: 4px 10px; border-radius: 6px;">
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
 * Observe attachment panel for image/video uploads
 */
function observeAttachmentPanel() {
    console.log('[AntiBanana] Starting attachment panel observer...');
    
    // Watch for attachment panel to appear
    const targetNode = document.body;
    
    const config = { childList: true, subtree: true };
    
    const callback = (mutationsList) => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                // Multiple selectors for WhatsApp attachment panels (structure changes often)
                const selectors = [
                    'div[data-animate-media-preview]',
                    'div[data-testid="media-preview-composer"]',
                    'div[class*="media-preview"]',
                    'div[class*="_2XgAp"]', // WhatsApp media container class
                    'span[data-testid="image-preview"]',
                    'span[data-testid="video-preview"]'
                ];
                
                selectors.forEach(selector => {
                    const previews = document.querySelectorAll(selector);
                    previews.forEach(preview => {
                        if (!preview.hasAttribute('data-antibanana-protect-added')) {
                            console.log('[AntiBanana] Found attachment preview:', selector);
                            addProtectToggle(preview);
                        }
                    });
                });
                
                // Also check for image/video in send area
                const mediaElements = document.querySelectorAll('div[role="application"] img, div[role="application"] video');
                mediaElements.forEach(media => {
                    const container = media.closest('div[data-animate-media-preview]') || 
                                    media.closest('div[role="application"]') ||
                                    media.closest('span[data-testid]') ||
                                    media.parentElement;
                    if (container && !container.hasAttribute('data-antibanana-protect-added')) {
                        console.log('[AntiBanana] Found media in send area:', media.tagName);
                        addProtectToggle(container);
                    }
                });
            }
        }
    };
    
    const attachmentObserver = new MutationObserver(callback);
    attachmentObserver.observe(targetNode, config);
}

/**
 * Add protect toggle to image/video attachment preview
 */
function addProtectToggle(container) {
    container.setAttribute('data-antibanana-protect-added', 'true');
    console.log('[AntiBanana] Adding protect toggle to container');
    
    // Create toggle container - MORE VISIBLE
    const toggleContainer = document.createElement('div');
    toggleContainer.className = 'antibanana-protect-toggle';
    toggleContainer.style.cssText = `
        position: absolute;
        bottom: 50px;
        left: 10px;
        z-index: 999;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 14px 18px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
        cursor: pointer;
        transition: all 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.3);
    `;
    
    toggleContainer.innerHTML = `
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="font-size: 24px;">🛡️</div>
            <div>
                <div style="color: white; font-size: 15px; font-weight: 700; margin-bottom: 2px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                    Protect & Send
                </div>
                <div style="color: rgba(255, 255, 255, 0.9); font-size: 11px; font-weight: 500;">
                    Click to add watermark
                </div>
            </div>
            <label style="position: relative; display: inline-block; width: 48px; height: 26px; margin-left: 8px;">
                <input type="checkbox" class="antibanana-toggle-input" ${protectionEnabled ? 'checked' : ''}
                       style="opacity: 0; width: 0; height: 0;">
                <span style="position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(255, 255, 255, 0.3); transition: 0.3s; border-radius: 26px;">
                    <span style="position: absolute; content: ''; height: 20px; width: 20px; left: 3px; bottom: 3px; background-color: white; transition: 0.3s; border-radius: 50%;"></span>
                </span>
            </label>
        </div>
        <div class="antibanana-toggle-status" style="display: none; margin-top: 10px; color: white; font-size: 13px; font-weight: 600;">
            <span class="antibanana-spinner" style="display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.6s linear infinite;"></span>
            <span class="antibanana-status-text" style="margin-left: 8px;">Protecting...</span>
        </div>
    `;
    
    // Hover effect
    toggleContainer.addEventListener('mouseenter', () => {
        toggleContainer.style.transform = 'translateY(-2px)';
        toggleContainer.style.boxShadow = '0 8px 24px rgba(16, 185, 129, 0.6)';
    });
    
    toggleContainer.addEventListener('mouseleave', () => {
        toggleContainer.style.transform = 'translateY(0)';
        toggleContainer.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.5)';
    });
    
    // Try multiple insertion strategies
    const insertStrategies = [
        () => container.insertBefore(toggleContainer, container.firstChild),
        () => container.appendChild(toggleContainer),
        () => {
            const parent = container.parentElement;
            if (parent) {
                parent.style.position = 'relative';
                parent.insertBefore(toggleContainer, container);
            }
        }
    ];
    
    let inserted = false;
    for (const strategy of insertStrategies) {
        try {
            strategy();
            inserted = true;
            console.log('[AntiBanana] Protect toggle inserted successfully');
            break;
        } catch (e) {
            console.log('[AntiBanana] Insert strategy failed:', e);
        }
    }
    
    if (!inserted) {
        console.error('[AntiBanana] Failed to insert protect toggle');
        return;
    }
    
    // Make sure container is positioned
    if (window.getComputedStyle(container).position === 'static') {
        container.style.position = 'relative';
    }
    
    // Handle toggle change
    const checkbox = toggleContainer.querySelector('.antibanana-toggle-input');
    const slider = toggleContainer.querySelector('span span');
    
    // Update slider visual when checked
    checkbox.addEventListener('change', (e) => {
        protectionEnabled = e.target.checked;
        console.log('[AntiBanana] Protection toggle changed:', protectionEnabled);
        
        // Update slider position
        if (protectionEnabled) {
            slider.style.transform = 'translateX(22px)';
            slider.style.backgroundColor = '#ffffff';
        } else {
            slider.style.transform = 'translateX(0)';
            slider.style.backgroundColor = '#ffffff';
        }
        
        if (protectionEnabled) {
            // Find the image or video in this container
            const img = container.querySelector('img');
            const video = container.querySelector('video');
            const media = img || video;
            
            if (media) {
                console.log('[AntiBanana] Protecting media:', media.tagName);
                protectAndReplaceImage(media, toggleContainer);
            } else {
                console.warn('[AntiBanana] No media found in container');
            }
        }
    });
    
    // Make whole container clickable
    toggleContainer.addEventListener('click', (e) => {
        if (e.target !== checkbox && !checkbox.disabled) {
            checkbox.checked = !checkbox.checked;
            checkbox.dispatchEvent(new Event('change'));
        }
    });
}

/**
 * Protect image before sending and replace with protected version
 */
async function protectAndReplaceImage(media, toggleContainer) {
    const statusDiv = toggleContainer.querySelector('.antibanana-toggle-status');
    const statusText = statusDiv.querySelector('.antibanana-status-text');
    const checkbox = toggleContainer.querySelector('.antibanana-toggle-input');
    
    statusDiv.style.display = 'flex';
    checkbox.disabled = true;
    
    try {
        // Only images can be protected (not videos yet)
        if (media.tagName.toLowerCase() !== 'img') {
            throw new Error('Only images can be protected currently');
        }
        
        // Get image as blob
        const blob = await fetchMediaAsBlob(media.src, false);
        
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
        
        if (!result.protected_image) {
            throw new Error('No protected image received');
        }
        
        // Replace image with protected version
        const protectedImageDataUrl = `data:image/png;base64,${result.protected_image}`;
        media.src = protectedImageDataUrl;
        
        console.log('[AntiBanana] Image replaced with protected version');
        
        // Show success with download option
        statusText.innerHTML = `✅ Protected! <button class="antibanana-download-btn" style="margin-left: 8px; padding: 4px 8px; background: white; color: #10b981; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 600;">⬇ Download</button>`;
        statusDiv.querySelector('.antibanana-spinner').style.display = 'none';
        
        // Add download handler
        const downloadBtn = statusDiv.querySelector('.antibanana-download-btn');
        downloadBtn.addEventListener('click', () => {
            // Create download link
            const link = document.createElement('a');
            link.href = protectedImageDataUrl;
            link.download = `protected_${Date.now()}.png`;
            link.click();
            console.log('[AntiBanana] Protected image downloaded');
        });
        
        // Keep success message visible
        setTimeout(() => {
            statusDiv.style.display = 'none';
            checkbox.disabled = false;
        }, 10000); // 10 seconds to allow download
        
    } catch (error) {
        console.error('Protection error:', error);
        statusText.textContent = `❌ ${error.message}`;
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
