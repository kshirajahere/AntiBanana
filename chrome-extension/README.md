# 🍌 AntiBanana Chrome Extension

A powerful browser extension for detecting deepfakes, protecting images, verifying C2PA provenance, and generating AI explainability visualizations. **Now with WhatsApp Web integration!**

## 📁 Project Structure

```
chrome-extension/
├── manifest.json              # Extension configuration
├── popup.html                # Main popup interface
├── INSTALLATION.md           # Detailed installation guide
├── WHATSAPP_INTEGRATION.md   # WhatsApp Web guide
├── README.md                 # This file
├── css/
│   ├── styles.css           # UI styling with modern gradients
│   └── whatsapp.css         # WhatsApp Web integration styles
├── js/
│   ├── popup.js             # Main popup logic
│   ├── content.js           # WhatsApp Web content script
│   └── background.js        # Background service worker
└── icons/
    ├── icon16.png           # 16x16 toolbar icon
    ├── icon48.png           # 48x48 extension management icon
    ├── icon128.png          # 128x128 Chrome Web Store icon
    └── generate_icons.py    # Icon generator script
```

## ✨ Features

### 🔍 Deepfake Detection
- Upload images for AI-powered deepfake analysis
- Real-time confidence scoring
- Optional C2PA verification
- XAI explanations with visual heatmaps
- **NEW: Detect images directly in WhatsApp Web chats!**

### 🛡️ Image Protection (MMHI)
- Protect images against deepfake generation
- Three strength levels: Medium, High, Extreme
- Download protected images instantly
- Multiple protection phases applied
- **NEW: Protect images before sending in WhatsApp Web!**

### 📜 C2PA Provenance Verification
- Verify content credentials and chain of custody
- Detailed manifest inspection
- Detect tampered or unverified content

### 💡 Explainability Analysis
- LIME, SHAP, and Grad-CAM visualizations
- Multiple explanation methods
- Quick mode for faster processing
- Visual heatmaps showing decision factors

### 💬 WhatsApp Web Integration
- **Detect Button**: Click "🍌 Detect" on any received image
- **Protect Toggle**: Enable protection before sending images
- **Real-time Results**: Instant popup with detection results
- **Dark Mode**: Full support for WhatsApp's dark theme
- 📖 **[Full WhatsApp Guide](WHATSAPP_INTEGRATION.md)**

## 🚀 Quick Start

### 1. Start the Backend Server
```bash
cd ../backend
py main.py
```

Backend should be running on: `http://localhost:5000`

### 2. Install Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **"Load unpacked"**
4. Select the `chrome-extension` folder
5. Extension is now installed!

📖 **For detailed instructions, see [INSTALLATION.md](INSTALLATION.md)**

## 🎨 UI Preview

The extension features a modern, gradient-based interface with:
- **Tab Navigation**: Detect, Protect, C2PA, Explain
- **Drag & Drop**: Easy image uploads
- **Real-time Status**: Server connection indicator
- **Smooth Animations**: Professional transitions and effects
- **Responsive Design**: Optimized popup layout
- **Result Visualization**: Charts, badges, and image overlays

## 🔧 Configuration

### Backend URL
Default: `http://localhost:5000`

To change:
1. Open the extension popup
2. Scroll to the bottom Settings section
3. Update the Backend URL field
4. Click **Save**

### Permissions
The extension requires:
- `activeTab`: For context menu on images
- `storage`: For saving settings
- `host_permissions`: For connecting to localhost backend

## 🛠️ Development

### Modifying the Extension

1. Edit files in the `chrome-extension` folder
2. Go to `chrome://extensions/`
3. Click the **Reload** button (🔄) on AntiBanana card
4. Test your changes

### Regenerating Icons

```bash
cd icons
py generate_icons.py
```

Requires: `pip install pillow`

### Debugging

**View Console Logs:**
1. Right-click extension popup
2. Select **Inspect**
3. Open **Console** tab

**Check Background Script:**
1. Go to `chrome://extensions/`
2. Click **"Service worker"** link under AntiBanana
3. View background script logs

## 📡 API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Server status check |
| `/detect` | POST | Deepfake detection with optional C2PA & XAI |
| `/protect` | POST | Image protection with MMHI |
| `/c2pa` | POST | C2PA provenance verification |
| `/explain` | POST | Generate explainability visualizations |

## 🎯 Browser Support

- ✅ Google Chrome (v88+)
- ✅ Microsoft Edge (Chromium-based)
- ✅ Brave Browser
- ✅ Opera (Chromium-based)
- ❌ Firefox (uses different extension format)

## 📦 Dependencies

**Frontend (Extension):**
- None! Pure vanilla JavaScript, HTML, CSS

**Backend (Required):**
- Flask server running on port 5000
- All Python dependencies from `backend/requirements.txt`

## 🐛 Troubleshooting

### Extension won't load?
- Ensure Developer mode is enabled
- Check for manifest.json errors in Extensions page
- Verify all files are present in the folder

### Can't connect to backend?
- Check if backend is running: `http://localhost:5000/health`
- Verify port 5000 is not blocked
- Update Backend URL in Settings if using different port

### Images not processing?
- Check browser console for errors (Right-click popup → Inspect)
- Ensure image file is valid format (JPG, PNG, etc.)
- Check backend terminal for error logs

## 📄 License

Part of the AntiBanana project.

## 🙏 Credits

- **UI Design**: Modern gradient theme with smooth animations
- **Icons**: Custom generated with PIL
- **Backend Integration**: Flask REST API
- **Detection Models**: Multiple deepfake detection algorithms

---

**Version**: 1.0.0  
**Manifest Version**: 3  
**Last Updated**: November 2025

Happy detecting! 🍌🔍
