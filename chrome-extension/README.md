# 🍌 AntiBanana Chrome Extension

## Professional Deepfake Detection & Protection Suite

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Chrome](https://img.shields.io/badge/chrome-extension-green)
![Platform](https://img.shields.io/badge/platform-WhatsApp%20%7C%20Instagram-orange)

AntiBanana is a powerful Chrome extension that brings advanced deepfake detection and image protection capabilities directly to your browser. Seamlessly integrated with WhatsApp Web and Instagram, it helps you verify the authenticity of images and videos in real-time.

---

## ✨ Features

### 🔍 Deepfake Detection
- **Image Detection**: Analyze images for deepfake manipulation
- **Video Detection**: Comprehensive video analysis with frame sampling
- **Real-time Analysis**: Detect deepfakes directly on WhatsApp Web and Instagram
- **C2PA Verification**: Check for Content Authenticity Initiative provenance data
- **XAI Explanations**: Get explainable AI insights into detection decisions

### 🛡️ Image Protection
- **MMHI Framework**: Multi-layered protection against AI manipulation
- **Adjustable Strength**: Choose between Medium, High, or Extreme protection
- **15-Phase Pipeline**: Advanced protection using state-of-the-art techniques

### 🌐 Platform Support
- **WhatsApp Web**: Add detect buttons to received images and videos
- **Instagram**: Analyze feed images and videos with one click
- **Standalone Popup**: Upload and analyze any media file

### 🎨 Modern UI
- Beautiful, premium design with glassmorphism effects
- Smooth animations and transitions
- Dark mode compatible
- Responsive layout

---

## 📦 Installation

### Prerequisites
1. **Backend Server**: The extension requires the AntiBanana backend server running
   - Default URL: `http://localhost:5000`
   - Configurable in extension settings

### Install Extension

#### Method 1: Load Unpacked (Development)
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable **Developer mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `chrome-extension` folder
5. The extension should now appear in your extensions list

#### Method 2: Chrome Web Store (Future)
*Coming soon when published*

---

## 🚀 Quick Start

### 1. Start the Backend Server

```bash
cd backend
python main.py
```

The server should start on `http://localhost:5000`.

### 2. Configure Extension

1. Click the AntiBanana extension icon in Chrome
2. At the bottom, verify the **Backend URL** is correct
3. Check that the status shows **Connected** (green dot)

### 3. Use on WhatsApp Web

1. Open [WhatsApp Web](https://web.whatsapp.com/)
2. Navigate to a chat with images or videos
3. Hover over any media to see the **🍌 Detect** button
4. Click to analyze - results appear in a popup

### 4. Use on Instagram

1. Open [Instagram](https://www.instagram.com/)
2. Browse your feed or open a post
3. Look for the **🍌 Detect** button on images/videos
4. Click to analyze deepfakes instantly

### 5. Standalone Detection

1. Click the extension icon to open the popup
2. Switch between **Image** or **Video** mode
3. Upload or drag-and-drop your file
4. Click **Analyze Media** to get results

---

## 📖 Usage Guide

### Popup Interface

#### Detect Tab
- **Media Type Selector**: Choose between Image or Video
- **Upload Area**: Click or drag files
- **Options**:
  - Include C2PA Verification
  - Enable XAI Explanations
  - Frame Samples (for videos): 20, 30, or 50 frames
- **Results Display**: Comprehensive detection results with confidence scores

#### Protect Tab
- Upload an image
- Select protection strength (Medium/High/Extreme)
- Download the protected image
- Protected images resist deepfake generation

#### C2PA Tab
- Verify Content Provenance
- Check for Content Authenticity Initiative signatures
- View detailed manifest data

#### Explain Tab
- Generate XAI visualizations
- Choose method: LIME, SHAP, Grad-CAM, or All
- Quick Mode for faster results

### WhatsApp Web Integration

**Detecting Received Media**:
1. Open any chat with images or videos
2. The **🍌 Detect** button appears on each media item
3. Click to analyze
4. Results show in a floating popup

**Protecting Before Sending** *(Coming Soon)*:
1. Click the attachment icon
2. Select an image
3. Toggle "Protect with AntiBanana"
4. Image is protected before sending

### Instagram Integration

**Feed & Post Analysis**:
1. Browse Instagram normally
2. Detect buttons appear on images and videos
3. Click to verify authenticity
4. Results overlay the post

---

## ⚙️ Configuration

### Backend URL
Change the backend server address:
1. Open extension popup
2. Scroll to bottom settings
3. Update **Backend URL**
4. Click **Save**

### Storage
Extension settings are synced across Chrome instances using Chrome Sync.

---

## 🔧 Technical Details

### Architecture

```
┌─────────────────┐
│  Chrome Browser │
└────────┬────────┘
         │
    ┌────┴─────┐
    │Extension │
    └────┬─────┘
         │
    ┌────┴────────────────┬──────────────┐
    │                     │              │
┌───┴────┐        ┌──────┴─────┐  ┌────┴─────┐
│ Popup  │        │  Content   │  │Background│
│ (HTML) │        │  Script    │  │  Script  │
└───┬────┘        └──────┬─────┘  └────┬─────┘
    │                    │              │
    └────────────────────┴──────────────┘
                    │
            ┌───────┴────────┐
            │ Backend Server │
            │ (Flask API)    │
            └────────────────┘
```

### File Structure

```
chrome-extension/
├── manifest.json           # Extension configuration
├── popup.html             # Main popup UI
├── icons/                 # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
├── css/
│   ├── styles.css         # Popup styles
│   └── whatsapp.css       # Content script styles
└── js/
    ├── popup.js           # Popup logic
    ├── content.js         # Content script (WhatsApp/Instagram)
    └── background.js      # Background service worker
```

### API Endpoints Used

- `GET /health` - Check server status
- `POST /detect` - Image deepfake detection
- `POST /detect-video` - Video deepfake detection
- `POST /protect` - Image protection (MMHI)
- `POST /c2pa` - C2PA verification
- `POST /explain` - XAI explanations

---

## 🎯 Features in Detail

### Image Detection
- **Models**: Advanced CNN + Vision Transformer ensemble
- **Speed**: ~2-3 seconds per image
- **Accuracy**: High confidence scoring
- **Output**: Classification, confidence, C2PA status

### Video Detection
- **Frame Sampling**: Intelligent hybrid sampling strategy
- **Parallel Processing**: Multi-threaded frame analysis
- **Lip Sync Analysis**: Audio-visual synchronization check
- **Temporal Consistency**: Frame-to-frame coherence analysis
- **Output**: Overall verdict, fake frame ratio, processing time

### Image Protection (MMHI)
- **15-Phase Pipeline**:
  1. Semantic Decoupling
  2. Frequency Domain Disruption
  3. Latent Space Poisoning
  4. Attention Mechanism Jamming
  5. Adversarial Perturbations
  6. Feature Map Corruption
  7. Gradient Masking
  8. Input Sanitization
  9. Model-Specific Countermeasures
  10. Ensemble Confusion
  11. Metadata Injection
  12. Safety Trigger Injection
  13. Multi-Resolution Disruption
  14. Perceptual Hash Scrambling
  15. Anti-Inversion Block

---

## 🐛 Troubleshooting

### "Offline" Status
**Problem**: Extension shows backend as offline  
**Solution**:
- Ensure backend server is running
- Check backend URL is correct
- Verify no firewall blocking localhost:5000

### Detect Buttons Not Appearing
**Problem**: No detect buttons on WhatsApp/Instagram  
**Solution**:
- Refresh the page (Ctrl+R)
- Check extension is enabled
- Verify you're on supported sites
- Try reloading extension

### Detection Fails
**Problem**: Detection returns an error  
**Solution**:
- Check backend server logs
- Ensure image/video is accessible
- Try re-uploading
- Check CORS settings for Instagram images

### Slow Video Detection
**Problem**: Video analysis takes too long  
**Solution**:
- Reduce number of frame samples (use 20 instead of 50)
- Use shorter videos
- Ensure backend has adequate resources

---

## 🔒 Privacy & Security

- **No Data Storage**: Extension doesn't store your images/videos
- **Direct Communication**: All data sent directly to your backend
- **No Tracking**: No analytics or user tracking
- **Local Processing**: Backend runs on your machine
- **Open Source**: Full transparency in code

---

## 🚧 Limitations

- **CORS Restrictions**: Some Instagram images may fail to load due to CORS policies
- **Backend Required**: Extension needs backend server running
- **File Size Limits**: Large videos may timeout
- **Performance**: Video detection is computationally intensive

---

## 🛣️ Roadmap

- [ ] Support for more platforms (Twitter, Facebook)
- [ ] Inline video player with detection
- [ ] Batch processing multiple files
- [ ] Export detection reports as PDF
- [ ] Browser-based lightweight detection (no backend needed)
- [ ] Real-time streaming video analysis
- [ ] Audio deepfake detection

---

## 📝 License

This project is part of the AntiBanana suite. See main repository for license details.

---

## 🤝 Contributing

Contributions are welcome! Please see the main AntiBanana repository for contribution guidelines.

---

## 📧 Support

For issues, questions, or feature requests, please open an issue in the main repository.

---

## 🙏 Acknowledgments

- Google for Chrome Extension platform
- OpenCV for video processing
- Content Authenticity Initiative for C2PA standards

---

**Made with ❤️ by the AntiBanana Team**

*Protecting authenticity in the age of AI*
