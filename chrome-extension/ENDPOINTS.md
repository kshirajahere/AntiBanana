# AntiBanana Chrome Extension - Backend Endpoints Reference

## Backend Configuration
- **Base URL**: `http://localhost:5000`
- **Host**: `0.0.0.0` (accessible from any interface)
- **Port**: `5000`

## Available Endpoints

### 1. Health Check
```
GET /health
```
**Purpose**: Check if backend server is running  
**Response**: `{"status": "ok"}`

---

### 2. Image Detection
```
POST /detect
```
**Purpose**: Detect deepfakes in images  
**Form Data**:
- `file` (required): Image file (jpg, png, etc.)
- `c2pa` (optional): "true" or "false" - Include C2PA verification
- `enable_xai` (optional): "true" or "false" - Enable XAI explanations
- `xai_methods` (optional): Comma-separated methods (e.g., "GradCAM++,IntegratedGradients")

**Response**:
```json
{
  "deepfake_detection": {
    "is_fake": true/false,
    "confidence": 0.0-1.0,
    "manipulation_type": "string",
    "processing_time": 0.0
  },
  "c2pa_verification": { ... },
  "xai_explanations": { ... }
}
```

---

### 3. Video Detection
```
POST /detect-video
```
**Purpose**: Detect deepfakes in videos (frame-by-frame analysis)  
**Form Data**:
- `file` (required): Video file (mp4, avi, mov, webm, etc.)
- `num_samples` (optional): Number of frames to analyze (default: 5)

**Response**:
```json
{
  "video_deepfake_detection": {
    "is_fake": true/false,
    "confidence": 0.0-1.0,
    "processing_time": 0.0
  },
  "frame_results": [
    {
      "frame_number": 0,
      "timestamp": 0.0,
      "is_fake": true/false,
      "confidence": 0.0-1.0
    }
  ],
  "analysis_summary": {
    "total_frames": 5,
    "fake_frames": 2,
    "real_frames": 3
  }
}
```

---

### 4. Audio Detection
```
POST /detect-audio
```
**Purpose**: Detect AI-generated audio  
**Form Data**:
- `file` (required): Audio file (wav, mp3, etc.)

**Response**:
```json
{
  "audio_deepfake_detection": {
    "is_fake": true/false,
    "confidence": 0.0-1.0,
    "processing_time": 0.0
  }
}
```

---

### 5. Image Protection (MMHI Watermarking)
```
POST /protect
```
**Purpose**: Add imperceptible watermark to protect images  
**Form Data**:
- `file` (required): Image file
- `strength` (optional): "medium", "high", or "extreme" (default: "medium")

**Response**:
```json
{
  "success": true,
  "protected_image": "base64_encoded_image",
  "message": "Image protected successfully",
  "protection_strength": "medium",
  "processing_time": 0.0
}
```

---

### 6. C2PA Provenance Verification
```
POST /c2pa
```
**Purpose**: Verify C2PA content credentials  
**Form Data**:
- `file` (required): Image file

**Response**:
```json
{
  "has_c2pa": true/false,
  "valid": true/false,
  "claims": [...],
  "manifests": [...],
  "processing_time": 0.0
}
```

---

### 7. XAI Explanations
```
POST /explain
```
**Purpose**: Generate explainability visualizations  
**Form Data**:
- `file` (required): Image file
- `methods` (optional): Comma-separated methods ("LIME", "SHAP", "GradCAM++", "IntegratedGradients")
- `quick_mode` (optional): "true" or "false"

**Response**:
```json
{
  "detection": {
    "is_fake": true/false,
    "confidence": 0.0-1.0
  },
  "visualizations": {
    "gradcam_plus": "base64_image",
    "integrated_gradients": "base64_image",
    "lime": "base64_image",
    "shap": "base64_image"
  },
  "processing_time": 0.0
}
```

---

## Extension Usage

### Popup Extension
All endpoints are accessible through the popup interface with 4 tabs:
1. **Detect**: Image/video detection with optional C2PA and XAI
2. **Protect**: Image watermarking with MMHI
3. **C2PA**: Content provenance verification
4. **Explain**: XAI visualizations

### WhatsApp Web Integration
The content script automatically injects:
1. **Detect buttons**: On received images/videos (top-right corner)
2. **Protect toggle**: On attachment preview (top-left corner)

### Endpoint Configuration in Code

**content.js**:
```javascript
let BACKEND_URL = 'http://localhost:5000';

// Image detection
fetch(`${BACKEND_URL}/detect`, { ... })

// Video detection  
fetch(`${BACKEND_URL}/detect-video`, { ... })

// Image protection
fetch(`${BACKEND_URL}/protect`, { ... })
```

**popup.js**:
```javascript
let BACKEND_URL = 'http://localhost:5000';

// All endpoints follow same pattern
fetch(`${BACKEND_URL}/${endpoint}`, { ... })
```

---

## CORS Configuration
The backend has CORS enabled for all origins:
```python
CORS(app, resources={r"/*": {"origins": "*"}})
```

This allows the Chrome extension to make cross-origin requests.

---

## Error Handling
All endpoints return appropriate HTTP status codes:
- `200 OK`: Success
- `400 Bad Request`: Invalid input
- `500 Internal Server Error`: Processing error

Error response format:
```json
{
  "error": "Error message description"
}
```

---

## Testing
Start backend:
```bash
cd backend
python main.py
```

Test health endpoint:
```bash
curl http://localhost:5000/health
```

Load extension in Chrome:
1. Open `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `chrome-extension` folder

---

## Notes
- Video detection processes `num_samples` frames (default: 5)
- XAI methods increase processing time significantly
- Protected images are returned as base64-encoded PNG
- C2PA verification only works with images that have embedded credentials
