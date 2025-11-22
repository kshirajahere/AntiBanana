// Background script for AntiBanana Chrome Extension
// Handles extension lifecycle and background tasks

console.log('AntiBanana extension loaded');

// Listen for extension installation
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('AntiBanana extension installed');
        
        // Set default settings
        chrome.storage.sync.set({
            backendUrl: 'http://localhost:5000'
        });
        
        // Open welcome page or instructions
        chrome.tabs.create({
            url: chrome.runtime.getURL('popup.html')
        });
    } else if (details.reason === 'update') {
        console.log('AntiBanana extension updated');
    }
});

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'checkServer') {
        // Can be used for server health checks from background
        fetch(request.url + '/health')
            .then(response => response.json())
            .then(data => sendResponse({ status: 'ok', data }))
            .catch(error => sendResponse({ status: 'error', error: error.message }));
        return true; // Keep message channel open for async response
    }
});

// Optional: Add context menu items for quick access
chrome.runtime.onInstalled.addListener(() => {
    if (chrome.contextMenus) {
        chrome.contextMenus.create({
            id: 'antibanana-detect',
            title: 'Detect with AntiBanana',
            contexts: ['image']
        });
    }
});

// Handle context menu clicks
if (chrome.contextMenus) {
    chrome.contextMenus.onClicked.addListener((info, tab) => {
        if (info.menuItemId === 'antibanana-detect') {
            // Could implement image detection from context menu
            console.log('Context menu clicked on image:', info.srcUrl);
        }
    });
}
