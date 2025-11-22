# 🚀 WhatsApp Web Integration - Quick Start

## What You Get

### 1️⃣ Detect Received Images
Every image in your WhatsApp chats gets a **"🍌 Detect"** button in the top-right corner.

```
┌─────────────────────────┐
│  [Image from friend]    │
│                         │
│              [🍌 Detect]│ ← Click this!
└─────────────────────────┘
```

**Click it to see:**
- ✅ Real or ⚠️ Fake classification
- Confidence percentage
- C2PA verification status

### 2️⃣ Protect Before Sending
When you attach an image, a toggle appears:

```
┌─────────────────────────────┐
│  [Your image preview]       │
│                             │
│  🛡️ [Toggle] Protect with  │ ← Enable this!
│     AntiBanana              │
│                             │
│  [Caption box]              │
│  [Send button]              │
└─────────────────────────────┘
```

**Enable it to:**
- Automatically protect your image
- Prevent deepfake generation
- Send protected version

## How to Use

### Step 1: Install Extension
```bash
# Make sure extension is loaded in Chrome
chrome://extensions/ → Load unpacked → Select chrome-extension folder
```

### Step 2: Start Backend
```bash
cd backend
py main.py
```

### Step 3: Open WhatsApp Web
Visit: https://web.whatsapp.com

### Step 4: Use Features!
- **Receive image** → See detect button → Click to analyze
- **Send image** → Enable protect toggle → Send protected

## Visual Guide

### Detect Button States

| State | Display | Meaning |
|-------|---------|---------|
| Ready | `🍌 Detect` | Click to analyze |
| Processing | `⏳ Analyzing...` | Backend processing |
| Real | `✅ Real` | Authentic image |
| Fake | `⚠️ FAKE` | Deepfake detected |
| Error | `❌ Error` | Analysis failed |

### Protect Toggle States

| State | Display | Meaning |
|-------|---------|---------|
| OFF | Gray toggle | Normal send |
| ON | Purple toggle | Will protect |
| Processing | Spinner + text | Protecting... |
| Done | `✅ Protected!` | Ready to send |

## Result Popup Example

```
┌──────────────────────────────┐
│ ⚠️ AntiBanana Detection    × │ ← Purple header
├──────────────────────────────┤
│ Classification:  ⚠️ Deepfake  │
│ Confidence:      87.3%       │
│ C2PA:            ✗ No C2PA   │
└──────────────────────────────┘
```

## Troubleshooting

### No detect button appearing?
1. Reload WhatsApp Web (Ctrl+R)
2. Check extension is enabled
3. Wait 2 seconds for page to load

### Protection not working?
1. Ensure backend is running
2. Toggle must be ON before sending
3. Check backend logs

### Backend offline?
1. Start backend: `cd backend && py main.py`
2. Verify: http://localhost:5000/health
3. Check extension settings for correct URL

## Tips

💡 **Tip 1**: Detect button auto-appears on all images  
💡 **Tip 2**: Protection happens automatically when toggle is ON  
💡 **Tip 3**: Results popup auto-closes after 10 seconds  
💡 **Tip 4**: Works in both light and dark mode  
💡 **Tip 5**: Process one image at a time for best results  

## Requirements

- ✅ Backend running on port 5000
- ✅ Extension installed and enabled
- ✅ WhatsApp Web open in Chrome
- ✅ Internet connection to backend

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Detect | 2-5s | Depends on backend |
| Protect | 3-7s | Medium strength |
| UI Response | Instant | Non-blocking |

---

📖 **Detailed guide**: [WHATSAPP_INTEGRATION.md](WHATSAPP_INTEGRATION.md)  
🔧 **Installation**: [INSTALLATION.md](INSTALLATION.md)  
📚 **Full README**: [README.md](README.md)

**Ready to go!** Just open WhatsApp Web and start using! 🎉
