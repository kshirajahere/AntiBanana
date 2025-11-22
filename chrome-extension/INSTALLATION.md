# AntiBanana Chrome Extension - Installation Guide

## 🍌 Welcome to AntiBanana!

A powerful Chrome extension for deepfake detection, image protection, C2PA verification, and AI explainability.

---

## 📋 Prerequisites

Before installing the extension, make sure you have:

1. **Google Chrome Browser** (version 88 or higher)
2. **Backend Server Running** on `http://localhost:5000`
   - Navigate to the backend folder: `cd AntiBanana/backend`
   - Start the server: `py main.py`
   - Verify it's running by visiting: http://localhost:5000/health

---

## 🚀 Installation Steps

### Step 1: Open Chrome Extensions Page

1. Open **Google Chrome**
2. Click the **three dots menu** (⋮) in the top-right corner
3. Navigate to: **Extensions** → **Manage Extensions**
   
   *Or simply type in the address bar:* `chrome://extensions/`

### Step 2: Enable Developer Mode

1. On the Extensions page, look for the **"Developer mode"** toggle in the **top-right corner**
2. **Turn it ON** (it should turn blue/enabled)

### Step 3: Load the Extension

1. Click the **"Load unpacked"** button (appears after enabling Developer mode)
2. Navigate to your AntiBanana project folder
3. Select the **`chrome-extension`** folder:
   ```
   C:\Users\kamal\Desktop\RIT\Projects\bit\real\AntiBanana\chrome-extension
   ```
4. Click **"Select Folder"**

### Step 4: Verify Installation

✅ You should see the **AntiBanana** extension card appear with:
- 🍌 Banana icon
- Name: "AntiBanana - Deepfake Protection Suite"
- Version: 1.0.0
- Status: **Enabled** (toggle should be ON)

### Step 5: Pin the Extension (Optional but Recommended)

1. Click the **puzzle piece icon** (🧩) in Chrome's toolbar
2. Find **AntiBanana** in the list
3. Click the **pin icon** (📌) next to it
4. The extension icon will now appear in your toolbar for easy access

---

## 🎯 Using the Extension

### Opening the Extension
- Click the 🍌 **AntiBanana icon** in your Chrome toolbar
- The popup window will open with 4 main tabs

### Features Overview

#### 1. 🔍 **Detect Tab**
- Upload an image to check if it's a deepfake
- Options:
  - ✅ Include C2PA Verification
  - ✅ Enable XAI Explanations
- Click **"Analyze Image"** to get results

#### 2. 🛡️ **Protect Tab**
- Upload an image to protect it against deepfake generation
- Choose protection strength:
  - Medium (default)
  - High
  - Extreme
- Click **"Protect Image"** and download the protected version

#### 3. 📜 **C2PA Tab**
- Verify C2PA provenance and chain of custody
- Upload an image to check for content credentials
- View detailed manifest information

#### 4. 💡 **Explain Tab**
- Generate explainability visualizations
- Methods available:
  - All Methods (LIME, SHAP, Grad-CAM)
  - Individual methods
- Quick mode option for faster processing

### Settings

At the bottom of the popup, you can configure:
- **Backend URL**: Default is `http://localhost:5000`
- Click **"Save"** after making changes

---

## 🔧 Troubleshooting

### Extension Not Loading?
- **Check Developer Mode**: Make sure it's enabled
- **Correct Folder**: Ensure you selected the `chrome-extension` folder, not the parent folder
- **Manifest Errors**: Check the Extensions page for any error messages

### Server Connection Issues?
- **Status Indicator**: Check the status in the top-right of the extension
  - 🟢 Green = Connected
  - 🔴 Red = Offline
- **Verify Backend**: Open http://localhost:5000/health in your browser
- **Port Conflicts**: Make sure nothing else is using port 5000
- **Update URL**: If using a different port/host, update it in Settings

### Images Not Processing?
- **File Format**: Only image files are supported (JPG, PNG, WebP, etc.)
- **File Size**: Very large images may take longer to process
- **Backend Logs**: Check the terminal where the backend is running for errors

### Extension Crashes?
1. Go to `chrome://extensions/`
2. Find AntiBanana
3. Click **"Reload"** (🔄) button
4. Try again

---

## 🔄 Updating the Extension

When you make changes to the extension code:

1. Go to `chrome://extensions/`
2. Find the **AntiBanana** extension
3. Click the **Reload** button (🔄)
4. The extension will reload with your changes

---

## 🗑️ Uninstalling

To remove the extension:

1. Go to `chrome://extensions/`
2. Find **AntiBanana**
3. Click **"Remove"**
4. Confirm the removal

---

## 📊 Backend Requirements

Make sure your backend server is running with all required dependencies:

```bash
cd backend
pip install -r requirements.txt
py main.py
```

The extension requires these endpoints to be available:
- `/health` - Server status check
- `/detect` - Deepfake detection
- `/protect` - Image protection (MMHI)
- `/c2pa` - C2PA verification
- `/explain` - Explainability generation

---

## 🎨 Features at a Glance

- ✅ **Modern UI** with gradient design and smooth animations
- ✅ **Tab-based Interface** for easy navigation
- ✅ **Drag & Drop** support for image uploads
- ✅ **Real-time Status** indicator for backend connection
- ✅ **Progress Indicators** during processing
- ✅ **Result Visualization** with images and metrics
- ✅ **Download Protected Images** directly from the extension
- ✅ **Persistent Settings** saved in Chrome storage

---

## 📝 Notes

- **Local Development**: This extension is configured for local development with the backend running on `localhost:5000`
- **Production Use**: To use with a remote backend, update the Backend URL in Settings
- **Privacy**: All processing happens on your configured backend server
- **Offline Mode**: The extension requires an active connection to the backend server

---

## 🆘 Need Help?

If you encounter issues:

1. Check the **browser console**: Right-click the extension popup → **Inspect** → **Console tab**
2. Check **backend logs** in the terminal where the server is running
3. Verify all backend dependencies are installed
4. Ensure the backend server is running and accessible

---

## 🎉 You're All Set!

Your AntiBanana Chrome extension is ready to use. Start detecting deepfakes, protecting images, and verifying content provenance right from your browser!

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Project**: AntiBanana - Deepfake Protection Suite
