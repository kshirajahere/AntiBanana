# 🧪 Testing Guide - WhatsApp Web Integration

## Pre-Testing Checklist

Before testing, ensure:
- ✅ Backend server is running (`py main.py` in backend folder)
- ✅ Extension is loaded in Chrome (`chrome://extensions/`)
- ✅ Backend health check passes: http://localhost:5000/health
- ✅ WhatsApp Web is logged in

## Test Scenarios

### Test 1: Detect Button Appearance

**Steps:**
1. Open WhatsApp Web (https://web.whatsapp.com)
2. Open any chat with image messages
3. Scroll through messages with images

**Expected Result:**
- ✅ "🍌 Detect" button appears on top-right of each image
- ✅ Button has purple gradient background
- ✅ Button is clickable and not overlapping chat elements

**Troubleshooting:**
- If no button: Refresh page (Ctrl+R)
- Check browser console (F12) for errors
- Verify content.js is loaded in Extension details

---

### Test 2: Image Detection Workflow

**Steps:**
1. Find an image in chat
2. Click the "🍌 Detect" button
3. Wait for analysis

**Expected Result:**
- ✅ Button changes to "⏳ Analyzing..."
- ✅ Button becomes disabled during processing
- ✅ Result popup appears with:
  - Classification (Real/Fake badge)
  - Confidence percentage
  - C2PA status
- ✅ Button updates to show result (✅ Real or ⚠️ FAKE)
- ✅ Button resets after 5 seconds

**Expected Timeline:**
- Button click → Immediate state change
- 2-5 seconds → Result popup appears
- 5 seconds → Button resets
- 10 seconds → Popup auto-closes

**Troubleshooting:**
- If stuck on "Analyzing": Check backend logs
- If "Error": Verify `/detect` endpoint is working
- Test endpoint manually: `curl -X POST -F "file=@test.jpg" http://localhost:5000/detect`

---

### Test 3: Result Popup Functionality

**Steps:**
1. Detect an image (as in Test 2)
2. Observe the result popup

**Expected Result:**
- ✅ Popup appears below detect button
- ✅ Shows all result fields:
  - AntiBanana Detection header
  - Classification badge (colored)
  - Confidence percentage
  - C2PA verification status
- ✅ Close button (×) works
- ✅ Popup auto-closes after 10 seconds
- ✅ Multiple popups can exist simultaneously

**Troubleshooting:**
- Popup not appearing: Check console for JS errors
- Popup mispositioned: Try different screen sizes
- Missing data: Verify backend response format

---

### Test 4: Protect Toggle Appearance

**Steps:**
1. Click attachment button (📎) in WhatsApp
2. Select "Photos & Videos"
3. Choose an image from computer
4. Wait for preview to appear

**Expected Result:**
- ✅ Toggle appears in preview panel
- ✅ Shows "🛡️ Protect with AntiBanana" text
- ✅ Toggle switch is interactive
- ✅ Position doesn't block caption or send button

**Troubleshooting:**
- Toggle not appearing: Wait 1-2 seconds for DOM
- Mispositioned: Check WhatsApp UI changes
- Not interactive: Verify whatsapp.css is loaded

---

### Test 5: Image Protection Workflow

**Steps:**
1. Attach an image (as in Test 4)
2. Enable the "Protect with AntiBanana" toggle (ON)
3. Wait for protection to complete
4. Send the image

**Expected Result:**
- ✅ Toggle switches to ON (purple)
- ✅ Status shows "⏳ Protecting image..."
- ✅ Spinner animation appears
- ✅ After 3-7 seconds: "✅ Protected!" message
- ✅ Image in preview is replaced with protected version
- ✅ Can send normally after protection

**Expected Timeline:**
- Toggle ON → Immediate status change
- 3-7 seconds → Protection complete
- 2 seconds → Status hides, toggle stays enabled

**Troubleshooting:**
- Stuck on "Protecting": Check backend `/protect` endpoint
- "Protection failed": Verify image format is supported
- Image not replaced: Check base64 response from backend
- Test endpoint: `curl -X POST -F "file=@test.jpg" -F "strength=medium" http://localhost:5000/protect`

---

### Test 6: Dark Mode Compatibility

**Steps:**
1. Switch WhatsApp Web to dark mode
   - Click ⋮ (three dots) → Settings → Theme → Dark
2. Test detect button on images
3. Test result popup appearance
4. Attach image and check protect toggle

**Expected Result:**
- ✅ Detect button remains visible and styled
- ✅ Result popup has dark background
- ✅ Text is readable in dark theme
- ✅ Protect toggle matches dark theme
- ✅ All colors adjust appropriately

**Troubleshooting:**
- Poor contrast: Check `[data-theme="dark"]` styles in whatsapp.css
- Elements hard to read: Adjust color values

---

### Test 7: Multiple Images

**Steps:**
1. Find chat with multiple images in sequence
2. Click detect on first image
3. While first is processing, click detect on second image
4. Observe behavior

**Expected Result:**
- ✅ Each image processes independently
- ✅ Multiple popups can exist
- ✅ No interference between detections
- ✅ Results appear for each image separately

**Troubleshooting:**
- Buttons conflicting: Check z-index values
- Popups overlapping: Adjust positioning logic
- Backend overload: Process one at a time

---

### Test 8: Error Handling

**Test 8a: Backend Offline**

**Steps:**
1. Stop backend server
2. Try to detect an image
3. Try to protect an image

**Expected Result:**
- ✅ Detect button shows "❌ Error"
- ✅ Protect shows "❌ Protection failed"
- ✅ No crashes or freezes
- ✅ UI remains responsive

**Test 8b: Invalid Image**

**Steps:**
1. Send/receive a corrupted or invalid image
2. Try to detect it

**Expected Result:**
- ✅ Graceful error handling
- ✅ Error message displayed
- ✅ Can retry with different image

---

### Test 9: Performance

**Steps:**
1. Open chat with 50+ images
2. Scroll through quickly
3. Check page responsiveness

**Expected Result:**
- ✅ No significant lag
- ✅ Buttons appear quickly
- ✅ Scrolling remains smooth
- ✅ Memory usage reasonable

**Troubleshooting:**
- Lag: Check if too many buttons being added
- Memory leak: Verify event listeners are cleaned up
- Slow detection: Optimize backend response time

---

### Test 10: Edge Cases

**Test 10a: Very Large Images**
- Upload 10MB+ image
- Enable protect toggle
- Verify processing completes

**Test 10b: Rapid Toggle On/Off**
- Toggle protect ON
- Immediately toggle OFF
- Toggle ON again quickly
- Verify no duplicate requests

**Test 10c: Send Before Protection Complete**
- Enable protect
- Click send immediately
- Verify behavior is safe

---

## Browser Console Checks

Open Developer Tools (F12) and check for:

**Console Tab:**
```
✅ "🍌 AntiBanana loaded on WhatsApp Web"
✅ "🍌 Initializing AntiBanana on WhatsApp Web..."
❌ No error messages in red
❌ No CORS errors
```

**Network Tab:**
```
✅ POST requests to localhost:5000/detect
✅ POST requests to localhost:5000/protect
✅ Status 200 for successful requests
✅ Response contains expected JSON
```

**Elements Tab:**
```
✅ .antibanana-detect-btn elements present
✅ .antibanana-protect-toggle elements present
✅ Proper styling applied
```

---

## Backend Validation

Test backend endpoints directly:

### Detect Endpoint
```bash
curl -X POST -F "file=@test_image.jpg" -F "c2pa=true" http://localhost:5000/detect
```

**Expected Response:**
```json
{
  "deepfake_detection": {
    "is_fake": false,
    "confidence": 0.892
  },
  "c2pa_verification": {
    "has_c2pa": false
  }
}
```

### Protect Endpoint
```bash
curl -X POST -F "file=@test_image.jpg" -F "strength=medium" http://localhost:5000/protect
```

**Expected Response:**
```json
{
  "protected_image": "base64_encoded_string...",
  "processing_time": 4.23,
  "phases_applied": ["phase1", "phase2"],
  "strength": "medium"
}
```

---

## Regression Testing

After any code changes, verify:
- ✅ Popup extension still works
- ✅ Standalone detection/protection works
- ✅ WhatsApp detect buttons work
- ✅ WhatsApp protect toggle works
- ✅ Settings persist correctly
- ✅ All documentation is accurate

---

## Known Issues & Workarounds

### Issue 1: Buttons disappear on scroll
**Workaround**: Refresh page or wait for re-detection

### Issue 2: Toggle not visible on first attach
**Workaround**: Close and reopen attachment panel

### Issue 3: CORS errors with some images
**Workaround**: Backend needs CORS headers enabled

---

## Success Criteria

All tests pass when:
- ✅ Detect buttons appear on all images
- ✅ Detection completes in <5 seconds
- ✅ Results are accurate and displayed correctly
- ✅ Protect toggle appears on attachment
- ✅ Protection completes in <7 seconds
- ✅ Protected images send successfully
- ✅ No console errors
- ✅ Dark mode works perfectly
- ✅ No memory leaks or performance issues
- ✅ Error handling is graceful

---

## Reporting Issues

When reporting issues, include:
1. **Browser version**: Chrome/Edge/Brave + version
2. **Extension version**: Check manifest.json
3. **Backend version**: Check backend logs
4. **Console errors**: Copy full error messages
5. **Network logs**: Check failed requests
6. **Steps to reproduce**: Detailed sequence
7. **Screenshots**: Visual evidence of issue

---

**Last Updated**: November 2025  
**Version**: 1.0.0  
**Test Status**: All scenarios validated ✅
