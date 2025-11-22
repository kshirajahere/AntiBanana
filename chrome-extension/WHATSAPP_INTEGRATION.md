# 🍌 AntiBanana WhatsApp Web Integration

## Overview

AntiBanana now integrates seamlessly with WhatsApp Web, allowing you to:
- **Detect deepfakes** in received images with a single click
- **Protect images** before sending them to prevent deepfake generation

## Features

### 🔍 Detect Images in Chat

When you receive images in WhatsApp Web, a **"🍌 Detect"** button will appear in the top-right corner of each image.

**How to use:**
1. Open any chat with images
2. Look for the **"🍌 Detect"** button on images
3. Click it to analyze the image
4. View results instantly in a popup showing:
   - Classification (Real/Fake)
   - Confidence percentage
   - C2PA verification status

### 🛡️ Protect Images Before Sending

When you attach an image to send, a protection toggle will appear.

**How to use:**
1. Click the attachment button (📎) in WhatsApp
2. Select an image to send
3. Toggle **"🛡️ Protect with AntiBanana"** ON
4. The image will be protected automatically
5. Send the protected image normally

**Protection Levels:**
- Default: Medium strength protection
- Adds MMHI adversarial perturbations
- Prevents AI deepfake generation

## Installation

### Prerequisites
1. **Backend server running** on `http://localhost:5000`
2. **Chrome extension installed** (see main [INSTALLATION.md](INSTALLATION.md))

### Enable WhatsApp Web Integration

The WhatsApp integration is automatically enabled when you install the extension. No additional steps needed!

Just:
1. Install the AntiBanana extension
2. Visit https://web.whatsapp.com
3. Look for the detect buttons and protect toggles

## How It Works

### For Received Images

```
1. You receive an image in chat
2. AntiBanana adds a "Detect" button overlay
3. Click button → Image sent to backend
4. Get real-time results in a popup
5. Results show: Real/Fake, Confidence, C2PA
```

### For Sending Images

```
1. You attach an image to send
2. Toggle "Protect with AntiBanana" appears
3. Enable toggle → Image protected automatically
4. Protected image replaces original
5. Send protected image to recipient
```

## UI Elements

### Detect Button
- **Location**: Top-right corner of received images
- **Appearance**: Purple gradient button with 🍌 icon
- **States**:
  - `🍌 Detect` - Ready to analyze
  - `⏳ Analyzing...` - Processing
  - `✅ Real` - Authentic image detected
  - `⚠️ FAKE` - Deepfake detected
  - `❌ Error` - Analysis failed

### Result Popup
- **Shows**: Classification, confidence %, C2PA status
- **Auto-closes**: After 10 seconds
- **Manual close**: Click × button
- **Position**: Below the detect button

### Protect Toggle
- **Location**: In attachment preview panel
- **Appearance**: Toggle switch with shield icon
- **States**:
  - OFF - Normal send
  - ON - Protect before sending
  - Processing - Shows spinner with status

## Configuration

### Backend URL
The extension uses your configured backend URL from Settings:
- Default: `http://localhost:5000`
- Change in extension popup → Settings section

### Protection Strength
Currently set to "medium" by default. Can be modified in `content.js`:

```javascript
formData.append('strength', 'medium'); // Options: medium, high, extreme
```

## Technical Details

### Permissions Required
- `https://web.whatsapp.com/*` - Access WhatsApp Web
- `downloads` - Handle protected image downloads

### Content Script
- **File**: `js/content.js`
- **Runs on**: https://web.whatsapp.com
- **Purpose**: Inject detect buttons and protect toggles

### Styling
- **File**: `css/whatsapp.css`
- **Supports**: Light and dark themes
- **Responsive**: Works on all screen sizes

## Troubleshooting

### Detect buttons not appearing?

**Solution:**
1. Reload WhatsApp Web (Ctrl/Cmd + R)
2. Check extension is enabled at `chrome://extensions/`
3. Verify backend is running
4. Look in browser console (F12) for errors

### Protection not working?

**Solution:**
1. Ensure backend `/protect` endpoint is available
2. Check image format is supported (JPG, PNG)
3. Verify toggle is enabled before sending
4. Check backend logs for errors

### Backend connection issues?

**Solution:**
1. Verify backend is running: http://localhost:5000/health
2. Check CORS is enabled in backend
3. Update backend URL in extension settings
4. Check browser console for network errors

### Images not loading in results?

**Solution:**
1. Check backend returns base64 encoded images
2. Verify API response format matches expected structure
3. Check browser console for CORS errors

## Privacy & Security

- **All processing** happens on your configured backend server
- **No data** is sent to external servers
- **Images** are processed locally or on your backend
- **No tracking** or analytics

## Limitations

- Only works on **WhatsApp Web** (not mobile app)
- Requires **active internet connection** to backend
- **CORS restrictions** may apply to some images
- Protection only applies to **newly attached** images

## API Endpoints Used

| Endpoint | Purpose | Parameters |
|----------|---------|-----------|
| `/detect` | Analyze image for deepfakes | file, c2pa, enable_xai |
| `/protect` | Add MMHI protection | file, strength |

## Performance

- **Detect**: ~2-5 seconds per image
- **Protect**: ~3-7 seconds per image
- **Network**: Depends on backend response time
- **UI**: Non-blocking, responsive interactions

## Dark Mode Support

✅ Full support for WhatsApp's dark mode
- Buttons adapt to theme
- Popups match WhatsApp colors
- Toggles adjust contrast automatically

## Browser Compatibility

- ✅ Chrome/Chromium
- ✅ Edge
- ✅ Brave
- ✅ Opera
- ❌ Firefox (different extension format)

## Known Issues

1. **Blob URL images**: May have CORS restrictions
2. **Multiple images**: Process one at a time for best results
3. **Large images**: May take longer to process
4. **WhatsApp updates**: May require extension updates

## Future Enhancements

- [ ] Batch detection for multiple images
- [ ] Customizable protection strength in UI
- [ ] Detection history/cache
- [ ] Automatic detection option
- [ ] Group chat statistics

## Support

If you encounter issues:
1. Check browser console (F12 → Console tab)
2. Check backend logs
3. Reload extension at `chrome://extensions/`
4. Restart WhatsApp Web

## Version

**WhatsApp Integration**: v1.0.0  
**Last Updated**: November 2025  
**Compatible with**: WhatsApp Web (Current version)

---

Happy chatting with confidence! 🍌🔍
