# AntiBanana Chrome Extension - Installation & Usage Guide

## 🚀 Quick Start

### Prerequisites
1. **Backend Server Running**
   - Navigate to backend directory
   - Install dependencies: `pip install -r requirements.txt`
   - Start server: `python main.py`
   - Verify: Backend should be running on `http://localhost:5000`

2. **Google Chrome or Microsoft Edge**
   - Version 88+ (for Manifest V3 support)

---

## 📦 Installation Steps

### Step 1: Load Extension in Chrome

1. **Open Chrome Extensions Page**
   ```
   chrome://extensions/
   ```
   Or: Menu (⋮) → More Tools → Extensions

2. **Enable Developer Mode**
   - Toggle "Developer mode" switch (top-right corner)

3. **Load Unpacked Extension**
   - Click "Load unpacked" button
   - Navigate to: `AntiBanana/chrome-extension/` folder
   - Click "Select Folder"

4. **Verify Installation**
   - You should see "AntiBanana" card with 🍌 icon
   - Extension should be enabled (toggle is blue)

### Step 2: Pin Extension (Optional)
1. Click the puzzle piece icon (Extensions) in toolbar
2. Find "AntiBanana"
3. Click the pin icon to keep it visible

---

## 🎯 Using the Extension

### Popup Interface (4 Tabs)

#### 1️⃣ Detect Tab
**Purpose**: Analyze images/videos for deepfakes

**Steps**:
1. Click extension icon to open popup
2. Ensure you're on "Detect" tab
3. Upload media:
   - Click upload area, OR
   - Drag and drop image/video
4. Configure options:
   - ☑️ Include C2PA Verification (images only)
   - ☑️ Enable XAI Explanations (images only)
5. Click "Analyze Media" button
6. View results:
   - Classification (Real/Fake)
   - Confidence percentage
   - For videos: Frames analyzed, fake frames detected
   - C2PA verification status
   - XAI visualizations (if enabled)

**Supported Formats**:
- Images: JPG, PNG, WEBP, BMP
- Videos: MP4, AVI, MOV, WEBM

---

#### 2️⃣ Protect Tab
**Purpose**: Add MMHI watermark to protect images

**Steps**:
1. Click "Protect" tab
2. Upload image (drag or click)
3. Select protection strength:
   - Medium (faster, less robust)
   - High (balanced)
   - Extreme (slower, most robust)
4. Click "Protect Image" button
5. Download protected image when ready

**Note**: Protected images look identical but contain invisible watermark.

---

#### 3️⃣ C2PA Tab
**Purpose**: Verify content credentials and provenance

**Steps**:
1. Click "C2PA" tab
2. Upload image with C2PA credentials
3. Click "Verify Provenance" button
4. View results:
   - C2PA status (verified/not found)
   - Claims and manifests
   - Creator information
   - Edit history

**Note**: Only images with embedded C2PA data will show verification.

---

#### 4️⃣ Explain Tab
**Purpose**: Generate AI explainability visualizations

**Steps**:
1. Click "Explain" tab
2. Upload image
3. Select explanation method:
   - All Methods (comprehensive)
   - LIME (highlights important regions)
   - SHAP (shows feature importance)
   - Grad-CAM (visual attention maps)
4. Optional: Enable "Quick Mode" for faster results
5. Click "Generate Explanation" button
6. View heatmaps showing which image regions influenced detection

**Methods Explained**:
- **LIME**: Shows which image parts are most important
- **SHAP**: Feature importance from game theory
- **Grad-CAM**: CNN attention visualization
- **Integrated Gradients**: Attribution-based explanation

---

### WhatsApp Web Integration

#### Auto-Detect Received Media
Extension automatically adds detect buttons to images/videos in WhatsApp.

**Usage**:
1. Open https://web.whatsapp.com
2. Wait for extension to load (see console logs)
3. Received images/videos will have "🍌 Detect" button (top-right)
4. Click button to analyze
5. Results appear in popup overlay
6. Button changes color:
   - 🟢 Green = Real
   - 🔴 Red = Fake
   - ⚪ Gray = Error

**Supported Elements**:
- Images in messages
- Videos in messages
- Media viewer images/videos
- Blob URLs and regular URLs

---

#### Protect Before Sending
Extension adds protect toggle to attachment preview.

**Usage**:
1. Click attachment button in WhatsApp
2. Select image/video to send
3. In preview screen, look for protect toggle (top-left)
4. Toggle "🛡️ Protect with AntiBanana" switch ON
5. Wait for protection to complete (shows "✅ Protected!")
6. Image is automatically replaced with protected version
7. Send as normal

**Features**:
- Automatic image replacement
- Visual feedback (spinner, status text)
- Error handling (shows error message)
- Works with multiple images

**Troubleshooting**:
- If toggle doesn't appear, check console for "[AntiBanana]" logs
- WhatsApp's DOM changes frequently; extension uses multiple selectors
- Refresh page if needed

---

## ⚙️ Configuration

### Change Backend URL
If backend is not running on default `localhost:5000`:

1. Open extension popup
2. Scroll to bottom
3. Find "Backend URL" input field
4. Enter new URL (e.g., `http://192.168.1.100:5000`)
5. Click "Save" button
6. Status indicator will update

**Status Indicators**:
- 🟢 Connected (backend reachable)
- 🔴 Error (backend not responding)
- ⚪ Checking (testing connection)

---

## 🐛 Troubleshooting

### Extension Not Loading
**Problem**: Extension doesn't appear after loading
- **Solution**: Check for errors in `chrome://extensions/`
- **Solution**: Ensure all files are in correct structure
- **Solution**: Reload extension (click refresh icon)

### Backend Connection Failed
**Problem**: "Backend not reachable" error
- **Solution**: Verify backend is running: `curl http://localhost:5000/health`
- **Solution**: Check firewall isn't blocking port 5000
- **Solution**: Try different backend URL
- **Solution**: Check CORS is enabled in backend

### WhatsApp Buttons Not Appearing
**Problem**: Detect buttons don't show on images
- **Solution**: Refresh WhatsApp Web page
- **Solution**: Check console for extension logs (F12)
- **Solution**: Verify extension permissions include `*://web.whatsapp.com/*`
- **Solution**: Clear browser cache and reload

### Protect Toggle Not Visible
**Problem**: Toggle doesn't appear on attachment preview
- **Solution**: Open console and look for "[AntiBanana] Found attachment preview" logs
- **Solution**: WhatsApp may have changed DOM structure - check selectors in content.js
- **Solution**: Try uploading different image format
- **Solution**: Reload extension and WhatsApp page

### Video Detection Very Slow
**Problem**: Video analysis takes too long
- **Solution**: Use shorter videos (< 30 seconds)
- **Solution**: Backend processes 5 frames by default - this is normal
- **Solution**: Avoid using XAI with videos
- **Solution**: Upgrade backend hardware (GPU recommended)

### Results Not Displaying
**Problem**: Detection completes but no results shown
- **Solution**: Check browser console for errors
- **Solution**: Verify backend response format matches expected JSON
- **Solution**: Try with different image/video file
- **Solution**: Check backend logs for errors

---

## 🔍 Advanced Usage

### Developer Console Debugging

**Popup Console**:
```
1. Right-click extension icon
2. Click "Inspect"
3. Go to Console tab
4. Look for logs from popup.js
```

**WhatsApp Content Script Console**:
```
1. Open WhatsApp Web
2. Press F12 (DevTools)
3. Go to Console tab  
4. Look for "[AntiBanana]" prefixed logs
```

**Background Worker Console**:
```
1. Go to chrome://extensions/
2. Find AntiBanana extension
3. Click "Service worker" link
4. View background.js logs
```

---

### Keyboard Shortcuts (Future Feature)
Currently not implemented, but you can add:
- `Ctrl+Shift+D`: Open detect tab
- `Ctrl+Shift+P`: Open protect tab
- `Alt+D`: Detect current image on page

---

## 📊 Performance Tips

### Faster Detection
- Disable XAI for routine checks (adds 2-5 seconds)
- Use Quick Mode in Explain tab
- Resize large images before upload
- Use Medium protection strength unless needed

### Better Accuracy
- Enable all XAI methods for comprehensive analysis
- Use High/Extreme protection for important images
- Cross-reference with C2PA verification
- Check multiple frames for videos

### Resource Management
- Close extension popup when not in use
- Extension only runs on WhatsApp Web (no background overhead)
- Backend can be stopped when not needed

---

## 🔒 Security & Privacy

### What Data is Sent?
- **Only uploaded files** are sent to backend
- Files are sent via HTTP POST (local network only by default)
- No data is stored permanently
- No telemetry or analytics

### Network Traffic
- All requests go to `localhost:5000` (your own machine)
- CORS is required for cross-origin requests
- Use HTTPS in production deployments

### Permissions Required
- `activeTab`: Access current tab for WhatsApp integration
- `storage`: Save backend URL preference
- `downloads`: Download protected images (future feature)
- `host_permissions`: Access backend API and WhatsApp Web

---

## 🎓 Best Practices

### When to Detect
✅ Suspicious images/videos from unknown sources  
✅ Social media content with unusual characteristics  
✅ Profile pictures that seem too perfect  
✅ News images/videos before sharing  

❌ Don't over-rely on automated detection  
❌ High confidence ≠ 100% certain  
❌ Use as one tool among many  

### When to Protect
✅ Original photos before posting publicly  
✅ Personal content you want to track  
✅ Professional work (art, photography)  
✅ Sensitive documents (with appropriate encryption too)

❌ Don't protect images you don't own  
❌ Protection is invisible but not encryption  
❌ Check platform compatibility first  

---

## 📞 Support

### Getting Help
1. Check this guide first
2. Review ENDPOINTS.md for API details
3. Check CHANGELOG.md for recent changes
4. Look at console logs for errors
5. Verify backend is running correctly

### Common Error Messages

**"Backend not reachable"**
- Backend server is not running
- Wrong backend URL configured
- Firewall blocking connection

**"Detection failed"**
- Invalid file format
- Backend processing error
- Network timeout (try smaller file)

**"Protection failed"**
- Image format not supported
- Backend protection service error
- Insufficient memory

---

## 🔄 Updating the Extension

When new version is released:

1. Download updated extension folder
2. Go to `chrome://extensions/`
3. Find AntiBanana extension
4. Click refresh icon (🔄)
5. Or: Remove and re-add extension

**Note**: Settings (backend URL) are preserved in Chrome storage.

---

## 📝 License & Credits

See main PROJECT.md for comprehensive documentation.

---

## 🌟 Tips & Tricks

1. **Batch Processing**: Open multiple tabs with extension popup for parallel processing
2. **Quick Detection**: Disable C2PA and XAI for 3x faster results
3. **Video Sampling**: 5 frames is good balance; increase for longer videos
4. **Protection Levels**: Medium for social media, Extreme for legal documents
5. **XAI Interpretation**: Red areas in heatmaps = suspicious regions
6. **WhatsApp Workflow**: Detect received → Protect before send → Share safely

---

**Version**: 1.1.0  
**Last Updated**: 2024  
**Compatibility**: Chrome 88+, Edge 88+
