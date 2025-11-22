# AntiBanana Chrome Extension - Changelog

## Latest Updates

### 🎥 Video Detection Support
Added comprehensive video deepfake detection to both popup and WhatsApp integration.

#### Changes Made:

**1. popup.html**
- Updated detect tab file input to accept both images and videos: `accept="image/*,video/*"`
- Changed upload area text to "Click or drag media here"
- Updated checkbox labels to indicate image-only features (C2PA, XAI)
- Changed button text to "Analyze Media"

**2. popup.js - Video Detection Logic**
- Modified `handleDetect()` to detect video file type
- Added conditional endpoint routing:
  - Images → `/detect` endpoint
  - Videos → `/detect-video` endpoint
- Added `num_samples: 5` parameter for video analysis
- Updated `displayDetectResult()` to accept `isVideo` parameter
- Added video-specific result display:
  - Shows "Real Video" vs "Real Image"
  - Displays frames analyzed count
  - Shows fake frames detected count
- Fixed drag-and-drop handler to accept videos in detect tab only

**3. content.js - WhatsApp Video Detection**
- Renamed `addDetectButtonsToImages()` to handle videos too
- Added video selectors:
  - `video[src*="blob:"]`
  - `div[data-id] video`
  - `._2fJvx video`
- Renamed `addDetectButton()` to detect media type (image/video)
- Added video-specific button text: "🍌 Detect Video"
- Renamed `detectImage()` → `detectMedia()` with video support
- Added video detection logic:
  - Routes to `/detect-video` endpoint
  - Sends `num_samples: 5` parameter
  - Handles video blob fetching
- Renamed `fetchImageAsBlob()` → `fetchMediaAsBlob()`
- Updated result display to show video-specific information:
  - Frames analyzed
  - Fake frames detected
  - "Real Video" label
- Added console logging throughout for debugging

---

### 🛡️ WhatsApp Protect Toggle Improvements
Fixed visibility issues and improved robustness of protect toggle.

#### Changes Made:

**1. content.js - Protect Toggle Fixes**
- Enhanced `observeAttachmentPanel()` with multiple selector strategies:
  - `div[data-animate-media-preview]`
  - `div[data-testid="media-preview-composer"]`
  - `div[class*="media-preview"]`
  - `div[class*="_2XgAp"]`
  - `span[data-testid="image-preview"]`
  - `span[data-testid="video-preview"]`
- Added extensive console logging for debugging
- Enhanced media detection to find videos too

**2. addProtectToggle() - Complete Rewrite**
- Replaced CSS-based styling with inline styles for guaranteed visibility
- Added explicit positioning:
  ```javascript
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 1000;
  background: rgba(0, 0, 0, 0.85);
  ```
- Implemented multiple insertion strategies with fallbacks:
  1. Insert before first child
  2. Append to container
  3. Insert in parent element
- Added automatic container positioning (sets `position: relative` if needed)
- Enhanced toggle UI:
  - Larger checkbox (40x20px)
  - Better contrast with dark background
  - Backdrop blur effect
  - White text with shield emoji
  - Status spinner with animation
- Added comprehensive error handling and logging
- Updated to handle both images and videos

**3. protectAndReplaceImage() - Media Support**
- Now detects both `img` and `video` elements
- Logs media type being protected
- Enhanced error reporting

---

### 📋 Documentation
Created comprehensive endpoint reference documentation.

#### New Files:

**1. ENDPOINTS.md**
Complete backend API reference including:
- All 7 endpoints with full documentation
- Request/response formats with examples
- CORS configuration details
- Error handling patterns
- Testing instructions
- Extension usage guide
- WhatsApp integration details

**2. This CHANGELOG.md**
Detailed record of all changes made.

---

## Summary of Endpoints

| Endpoint | Method | Purpose | Form Data |
|----------|--------|---------|-----------|
| `/health` | GET | Health check | None |
| `/detect` | POST | Image detection | `file`, `c2pa`, `enable_xai`, `xai_methods` |
| `/detect-video` | POST | Video detection | `file`, `num_samples` |
| `/detect-audio` | POST | Audio detection | `file` |
| `/protect` | POST | Image protection | `file`, `strength` |
| `/c2pa` | POST | C2PA verification | `file` |
| `/explain` | POST | XAI explanations | `file`, `methods`, `quick_mode` |

---

## Technical Details

### Backend Configuration
- **URL**: `http://localhost:5000`
- **Port**: 5000
- **CORS**: Enabled for all origins
- **Host**: `0.0.0.0` (accessible from any interface)

### Extension Structure
```
chrome-extension/
├── manifest.json          # Chrome extension config
├── popup.html            # Main popup UI
├── js/
│   ├── popup.js         # Popup logic (all 4 tabs)
│   ├── content.js       # WhatsApp integration (detect + protect)
│   └── background.js    # Service worker
├── css/
│   ├── styles.css       # Popup styles
│   └── whatsapp.css     # WhatsApp overlay styles
├── icons/               # Extension icons (16, 48, 128)
├── ENDPOINTS.md         # API documentation
└── CHANGELOG.md         # This file
```

### WhatsApp Integration Features
1. **Detect Buttons**: Automatically added to all received images/videos
2. **Protect Toggle**: Appears on attachment preview before sending
3. **Result Popups**: Show detection results with confidence scores
4. **Video Support**: Handles video files with frame-by-frame analysis

---

## Testing Checklist

### Extension Popup
- [x] Detect tab accepts images
- [x] Detect tab accepts videos  
- [x] Video detection shows frame analysis
- [x] C2PA checkbox disabled for videos
- [x] XAI checkbox disabled for videos
- [x] Protect tab works for images
- [x] C2PA tab verifies provenance
- [x] Explain tab generates visualizations

### WhatsApp Web
- [x] Detect buttons appear on received images
- [x] Detect buttons appear on received videos
- [x] Video button shows "Detect Video" text
- [x] Protect toggle appears on attachment preview
- [x] Protect toggle has correct styling
- [x] Toggle works with images
- [x] Toggle works with videos
- [x] Result popups display correctly
- [x] Video results show frame analysis

### Backend Integration
- [x] `/detect` endpoint works
- [x] `/detect-video` endpoint works
- [x] `/protect` endpoint works
- [x] `/c2pa` endpoint works
- [x] `/explain` endpoint works
- [x] CORS allows extension requests
- [x] Error handling works properly

---

## Known Issues & Limitations

### WhatsApp Web DOM Changes
WhatsApp Web frequently updates its DOM structure. The extension uses multiple selector strategies to maintain compatibility, but may require updates if WhatsApp makes major changes.

**Current Selectors**:
- Media messages: `img[src*="blob:"]`, `video[src*="blob:"]`
- Message containers: `div[data-id]`, `div[role="application"]`
- Attachment preview: Multiple data-testid and class-based selectors

### Video Processing Time
Video detection analyzes multiple frames (default: 5), which takes longer than image detection:
- Image: ~1-3 seconds
- Video: ~5-15 seconds (depending on `num_samples`)

**Optimization Tips**:
- Reduce `num_samples` for faster results
- Use quick_mode in XAI for faster explanations
- Disable XAI for routine detections

### Browser Compatibility
- Tested on Chrome/Edge (Manifest V3)
- Firefox requires Manifest V2 (not included)
- Safari requires different extension format

---

## Future Enhancements

### Potential Features
1. **Real-time video stream analysis** - Detect during video calls
2. **Batch processing** - Analyze multiple files at once
3. **History tracking** - Save detection results
4. **Confidence threshold settings** - Customize sensitivity
5. **Automatic protection** - Auto-protect before sending
6. **Platform expansion** - Support for Facebook, Instagram, Twitter
7. **Offline mode** - Local model inference without backend

### Performance Improvements
1. **Caching** - Store recent detection results
2. **Progressive loading** - Show partial results while processing
3. **Web Workers** - Offload processing to background threads
4. **Model optimization** - Quantize models for faster inference

---

## Version History

### v1.1.0 (Current)
- ✅ Added video detection support
- ✅ Fixed WhatsApp protect toggle visibility
- ✅ Enhanced error logging
- ✅ Created comprehensive documentation

### v1.0.0 (Initial Release)
- ✅ Chrome extension with 4-tab popup
- ✅ WhatsApp Web integration
- ✅ Image deepfake detection
- ✅ MMHI protection watermarking
- ✅ C2PA provenance verification
- ✅ XAI explanations (LIME, SHAP, Grad-CAM)

---

## Support & Debugging

### Enable Console Logging
The extension includes extensive console logging. To debug:

1. **Popup Console**:
   - Right-click extension icon → "Inspect"
   - View popup.js logs

2. **WhatsApp Web Console**:
   - Open WhatsApp Web
   - Press F12 to open DevTools
   - Look for "[AntiBanana]" prefixed logs

3. **Background Worker**:
   - Go to `chrome://extensions/`
   - Click "Service worker" link
   - View background.js logs

### Common Issues

**Problem**: Protect toggle not appearing
- **Solution**: Check console for selector match logs, WhatsApp may have updated DOM

**Problem**: Detection fails with CORS error
- **Solution**: Verify backend CORS is enabled and server is running

**Problem**: Video detection times out
- **Solution**: Reduce `num_samples` parameter or use shorter videos

**Problem**: Extension not loading
- **Solution**: Check manifest.json permissions, reload extension in chrome://extensions/

---

## Credits
- **Backend**: Flask, PyTorch, Transformers, LIME, SHAP, Grad-CAM
- **Frontend**: Chrome Extension API, Vanilla JavaScript
- **Icons**: Unicode emojis (🍌, 🛡️, 📜, 💡, 🔍)

---

## License
See main project LICENSE file.
