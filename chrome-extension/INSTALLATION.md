# 🚀 AntiBanana Extension - Quick Installation Guide

## Step-by-Step Installation

### 1️⃣ Start the Backend Server

Open a terminal and navigate to the backend directory:

```bash
cd backend
python main.py
```

You should see:
```
✅ Server running on http://localhost:5000
```

**Keep this terminal open!** The extension needs the backend running.

---

### 2️⃣ Install the Chrome Extension

1. **Open Chrome Extensions Page**
   - Navigate to `chrome://extensions/` in your browser
   - Or click: Menu → More Tools → Extensions

2. **Enable Developer Mode**
   - Toggle the **Developer mode** switch in the top-right corner

3. **Load the Extension**
   - Click **Load unpacked** button
   - Navigate to `AntiBanana/chrome-extension` folder
   - Click **Select Folder**

4. **Verify Installation**
   - You should see "AntiBanana - Deepfake Protection Suite" in your extensions
   - Pin it to toolbar by clicking the pin icon

---

### 3️⃣ Test the Extension

#### Test 1: Check Connection
1. Click the AntiBanana icon in Chrome toolbar
2. Check the status indicator at the top
3. Should show **Connected** with a green dot

#### Test 2: Detect an Image
1. In the extension popup, stay on the **Detect** tab
2. Ensure **Image** is selected
3. Click or drag an image file
4. Click **Analyze Media**
5. View results

#### Test 3: WhatsApp Web
1. Open https://web.whatsapp.com/
2. Navigate to a chat with images
3. Look for **🍌 Detect** buttons on images
4. Click to analyze

#### Test 4: Instagram
1. Open https://www.instagram.com/
2. Browse your feed
3. Look for **🍌 Detect** buttons on posts
4. Click to analyze

---

## ✅ Success Checklist

- [ ] Backend server is running
- [ ] Extension shows "Connected" status
- [ ] Can upload and detect images in popup
- [ ] Can detect videos in popup (try with MP4 file)
- [ ] Detect buttons appear on WhatsApp Web
- [ ] Detect buttons appear on Instagram
- [ ] Results popup appears after detection

---

## ❌ Troubleshooting

### Backend Won't Start
**Error**: ModuleNotFoundError or similar

**Solution**:
```bash
pip install -r requirements.txt
```

### Extension Shows "Offline"
**Problem**: Cannot connect to backend

**Solutions**:
1. Check backend is running on port 5000
2. In extension popup, verify Backend URL is `http://localhost:5000`
3. Click **Save** after changing URL
4. Refresh the page

### No Detect Buttons on WhatsApp/Instagram
**Problem**: Buttons don't appear

**Solutions**:
1. Refresh the page (F5 or Ctrl+R)
2. Wait a few seconds for page to load fully
3. Check extension is enabled in `chrome://extensions/`
4. Try clicking the extension icon and checking connection

### Detection Fails
**Problem**: Gets error during detection

**Solutions**:
1. Check backend terminal for error messages
2. Try a smaller file
3. For videos, reduce frame samples to 20
4. Restart backend server

---

## 🎉 You're All Set!

The extension is now fully functional. Explore all the features:

- **Detect Tab**: Upload any image or video
- **Protect Tab**: Protect images before sharing
- **C2PA Tab**: Verify content provenance
- **Explain Tab**: Get AI explanations

**On WhatsApp/Instagram**: Just click the 🍌 buttons!

---

## 📚 Next Steps

1. Read the full [README.md](./README.md) for detailed features
2. Check [TESTING_GUIDE.md](./TESTING_GUIDE.md) for comprehensive testing
3. Review [WHATSAPP_INTEGRATION.md](./WHATSAPP_INTEGRATION.md) for WhatsApp details

---

**Need Help?** Open an issue in the main repository.

**Enjoy protecting authenticity with AntiBanana! 🍌**
