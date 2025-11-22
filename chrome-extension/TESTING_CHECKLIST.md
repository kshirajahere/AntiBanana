# ✅ AntiBanana Extension Testing Checklist

Complete this checklist to verify all features are working correctly.

---

## 🔧 Pre-Testing Setup

- [ ] Backend server is running on `http://localhost:5000`
- [ ] Extension is loaded in Chrome (`chrome://extensions/`)
- [ ] Extension is pinned to toolbar
- [ ] WhatsApp Web is accessible
- [ ] Instagram is accessible (logged in)
- [ ] Test images ready (at least 2-3 different images)
- [ ] Test video ready (short MP4, under 30 seconds recommended)

---

## 1️⃣ Extension Popup - Basic Functionality

### Connection Status
- [ ] Click extension icon
- [ ] Status indicator shows "Connected" with green dot
- [ ] If offline, update Backend URL and click Save
- [ ] Status changes to Connected

### Tab Navigation
- [ ] Click each tab (Detect, Protect, C2PA, Explain)
- [ ] Tab switches correctly
- [ ] Active tab has purple underline
- [ ] Content changes for each tab

---

## 2️⃣ Image Detection (Popup)

### Upload Methods
- [ ] Click on upload area to browse files
- [ ] Select an image file
- [ ] Image name appears with checkmark
- [ ] Drag and drop an image
- [ ] Image is accepted

### Detection Options
- [ ] Toggle "Include C2PA Verification" on/off
- [ ] Toggle "Enable XAI Explanations" on/off
- [ ] Both options persist when toggled

### Run Detection
- [ ] Click "Analyze Media" button
- [ ] Button shows loading spinner
- [ ] Results appear after processing (2-5 seconds)
- [ ] Results show:
  - [ ] Classification (Real/Fake badge)
  - [ ] Confidence percentage with progress bar
  - [ ] C2PA status (if enabled)
  - [ ] XAI visualizations (if enabled)

### Edge Cases
- [ ] Try uploading non-image file → Should show error
- [ ] Try with very large image (>10MB) → Should handle gracefully
- [ ] Try with corrupt image → Should show error message

---

## 3️⃣ Video Detection (Popup)

### Media Type Selection
- [ ] Click "Video" button in media type selector
- [ ] Button turns purple (active)
- [ ] Upload text changes to "Click or drag video here"
- [ ] File hint changes to video formats
- [ ] Video options panel appears

### Frame Sampling
- [ ] Click Frame Samples dropdown
- [ ] Select "20 frames (Fast)"
- [ ] Select "30 frames (Balanced)"
- [ ] Select "50 frames (Thorough)"
- [ ] Selection persists

### Upload and Detect
- [ ] Upload a video file (MP4)
- [ ] Click "Analyze Media"
- [ ] Progress message appears
- [ ] Processing takes longer than images (expected)
- [ ] Results show:
  - [ ] Overall verdict (Real/Fake/Suspicious)
  - [ ] Confidence score
  - [ ] Frames analyzed count
  - [ ] Fake frames detected
  - [ ] Processing time
  - [ ] Video metadata (duration, resolution, FPS)
  - [ ] Lip sync analysis (if available)

### Edge Cases
- [ ] Try very short video (<5 seconds)
- [ ] Try video with no audio
- [ ] Try unsupported format → Should show error

---

## 4️⃣ Image Protection (Popup)

- [ ] Switch to "Protect" tab
- [ ] Upload an image
- [ ] Select "Medium" strength
- [ ] Click "Protect Image"
- [ ] Wait for processing (this may take 30-60 seconds)
- [ ] Results show:
  - [ ] Protected status badge
  - [ ] Strength level
  - [ ] Processing time
  - [ ] Phases applied
  - [ ] Protected image preview
  - [ ] Download button
- [ ] Click download button
- [ ] Protected image downloads successfully

---

## 5️⃣ C2PA Verification (Popup)

- [ ] Switch to "C2PA" tab
- [ ] Upload an image with C2PA data (if available)
- [ ] Click "Verify Provenance"
- [ ] Results show C2PA status
- [ ] If no C2PA: Shows "No C2PA data found"
- [ ] If has C2PA: Shows manifest details

---

## 6️⃣ XAI Explanations (Popup)

- [ ] Switch to "Explain" tab
- [ ] Upload an image
- [ ] Select "All Methods"
- [ ] Toggle "Quick Mode" on
- [ ] Click "Generate Explanation"
- [ ] Wait for processing
- [ ] Results show:
  - [ ] Multiple visualization methods
  - [ ] Heatmap images
  - [ ] Processing time

---

## 7️⃣ WhatsApp Web Integration

### Setup
- [ ] Open https://web.whatsapp.com/
- [ ] Login to WhatsApp
- [ ] Open a chat with image messages
- [ ] Wait for page to fully load

### Image Detection
- [ ] Scroll through chat
- [ ] Locate an image message
- [ ] Look for **🍌 Detect** button on image
- [ ] Button appears in top-right corner
- [ ] Click the button
- [ ] Button shows "⏳ Analyzing..."
- [ ] Result popup appears
- [ ] Popup shows:
  - [ ] AntiBanana header
  - [ ] Verdict badge
  - [ ] Confidence score
  - [ ] Close button (×)
- [ ] Click close button → Popup disappears
- [ ] Wait 5 seconds → Button resets to "🍌 Detect"

### Video Detection
- [ ] Find a video message in chat
- [ ] Look for **🍌 Detect Video** button
- [ ] Click the button
- [ ] Shows "⏳ Analyzing Video..."
- [ ] Result popup appears with video stats
- [ ] Popup shows fake frames detected
- [ ] Button resets after completion

### Multiple Messages
- [ ] Detect multiple different images
- [ ] Each gets its own detect button
- [ ] Buttons don't interfere with each other
- [ ] Results are accurate per image

---

## 8️⃣ Instagram Integration

### Feed Analysis
- [ ] Open https://www.instagram.com/
- [ ] Login to Instagram
- [ ] Scroll through main feed
- [ ] Look for **🍌 Detect** buttons on post images
- [ ] Buttons appear in top-right of images
- [ ] Click button on a post
- [ ] Result popup appears
- [ ] Results show verdict and confidence

### Story/Modal Analysis
- [ ] Click on a post to open modal
- [ ] Look for detect button on modal image
- [ ] Click to analyze
- [ ] Results appear correctly

### Video Posts
- [ ] Find a video post in feed
- [ ] Look for **🍌 Detect Video** button
- [ ] Click to analyze video
- [ ] Results show video statistics

---

## 9️⃣ UI & UX Testing

### Visual Design
- [ ] All buttons have proper styling
- [ ] Purple gradient theme is consistent
- [ ] Icons are properly aligned
- [ ] Text is readable
- [ ] Spacing looks professional
- [ ] No layout shifts or jumps

### Animations
- [ ] Buttons have hover effects
- [ ] Tabs switch smoothly
- [ ] Progress bars animate
- [ ] Popups fade in/out
- [ ] Loading spinners spin

### Responsiveness
- [ ] Resize browser window
- [ ] Extension popup maintains layout
- [ ] Buttons remain accessible
- [ ] Text doesn't overflow

---

## 🔟 Error Handling

### Network Errors
- [ ] Stop backend server
- [ ] Try to detect an image
- [ ] Error message appears
- [ ] Status shows "Offline"
- [ ] Restart server
- [ ] Status returns to "Connected"

### Invalid Files
- [ ] Upload text file as image
- [ ] Error message shown
- [ ] Upload corrupted video
- [ ] Graceful error handling

### Platform Errors
- [ ] Block extension on a site
- [ ] Check for console errors
- [ ] Unblock extension
- [ ] Functionality resumes

---

## Performance Testing

### Speed
- [ ] Image detection completes in < 5 seconds
- [ ] Video detection (20 frames) < 2 minutes
- [ ] Video detection (50 frames) < 5 minutes
- [ ] UI remains responsive during processing

### Resource Usage
- [ ] Check Chrome Task Manager (`Shift+Esc`)
- [ ] Extension memory usage is reasonable
- [ ] No memory leaks after multiple detections

---

## Cross-Browser Testing (Optional)

If testing on different browsers:
- [ ] Test on Chrome
- [ ] Test on Edge (Chromium)
- [ ] Test on Brave

---

## 🎯 Final Verification

- [ ] All core features work
- [ ] No critical bugs found
- [ ] UI is polished
- [ ] Error messages are helpful
- [ ] Documentation is accurate
- [ ] Ready for production use

---

## 📊 Testing Results

**Date**: _______________  
**Tester**: _______________  
**Tests Passed**: _____ / _____  
**Critical Issues**: _____  
**Minor Issues**: _____  

**Overall Status**: ⬜ Pass  ⬜ Fail  ⬜ Needs Work

---

## 🐛 Issues Found

Document any issues discovered during testing:

1. **Issue**: ________________________________
   - **Severity**: Critical / High / Medium / Low
   - **Steps to Reproduce**: ________________________________
   - **Expected**: ________________________________
   - **Actual**: ________________________________

2. **Issue**: ________________________________
   - **Severity**: Critical / High / Medium / Low
   - **Steps to Reproduce**: ________________________________
   - **Expected**: ________________________________
   - **Actual**: ________________________________

---

## ✅ Sign-Off

By completing this checklist, I verify that the AntiBanana Chrome Extension has been thoroughly tested and is functioning as expected.

**Signature**: _______________  
**Date**: _______________

---

**Happy Testing! 🍌**
