# AntiBanana API Endpoints

Complete API documentation for all deepfake detection endpoints.

## Base URL
`http://localhost:5001`

---

## 1. Image Detection Endpoints

### 1.1 Basic Image Detection
**Endpoint:** `/detect`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Image file
- `explain` (optional): `true` to include XAI explanations (default: `false`)
- `method` (optional): XAI method - `lime`, `shap`, `gradcam`, or `all` (default: `all`)
- `quick` (optional): `true` for quick mode (default: `false`)
- `c2pa` (optional): `true` to include C2PA verification (default: `true`)

**Response:**
```json
{
  "results": [
    {
      "label": "Fake" | "Real",
      "score": 0.95,
      "model": "model_name"
    }
  ],
  "c2pa": { ... },
  "explainability": { ... }
}
```

---

### 1.2 XAI Explanations Only
**Endpoint:** `/explain`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Image file
- `method` (optional): `lime`, `shap`, `gradcam`, or `all` (default: `all`)
- `quick` (optional): `true` for quick mode (default: `false`)

**Response:**
```json
{
  "segmented": {
    "LIME": {
      "overlay": "base64_image",
      "saliency": "base64_image"
    },
    "GradCAM++": {
      "overlay": "base64_image",
      "saliency": "base64_image"
    },
    "SHAP": { ... }
  }
}
```

---

### 1.3 C2PA Verification Only
**Endpoint:** `/c2pa`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Image file

**Response:**
```json
{
  "has_c2pa": true,
  "manifest": { ... },
  "chain_of_custody": [ ... ],
  "trust_level": "high" | "medium" | "low" | "none"
}
```

---

### 1.4 Advanced Agentic Analysis
**Endpoint:** `/analyze-agentic`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Image file
- `include_metadata` (optional): Include C2PA metadata (default: `true`)

**Response:**
```json
{
  "detection": { ... },
  "xai": { ... },
  "agentic_analysis": {
    "Visual Content Analysis": "...",
    "Explanation Models Analysis": "...",
    "Anomaly Detection": "...",
    "Text Extraction": "...",
    "Image Metadata": "...",
    "Additional Context": "...",
    "Final Summary and Verdict": "..."
  }
}
```

**Features:**
- Groq Vision API analysis
- Multi-tool agentic approach
- LIME + Grad-CAM interpretation
- OCR text extraction
- Web search for context
- Comprehensive verdict

---

### 1.5 Generate PDF Report (Image)
**Endpoint:** `/generate-report`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Image file
- `investigator_name` (optional): Investigator name (default: "AI Detection System")
- `case_number` (optional): Case number (auto-generated if not provided)
- `include_xai` (optional): Include XAI visualizations (default: `true`)
- `include_c2pa` (optional): Include C2PA metadata (default: `true`)
- `include_agentic` (optional): Include agentic analysis (default: `false`)

**Response:**  
PDF file download with forensic report including:
- Case information with checksum
- Image preview
- EXIF metadata
- C2PA verification
- Detection results
- XAI visualizations
- Agentic analysis (if requested)

---

## 2. Audio Detection Endpoints

### 2.1 Audio Deepfake Detection
**Endpoint:** `/detect-audio`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Audio file (wav, mp3, m4a, flac, ogg)

**Response:**
```json
{
  "prediction": "fake" | "real",
  "confidence": 0.95,
  "is_fake": true,
  "images": {
    "waveform": "base64_image",
    "spectrogram": "base64_image",
    "mfcc": "base64_image",
    "lime": "base64_image",
    "gradcam": "base64_image"
  }
}
```

**Features:**
- Audio deepfake detection using transformer models
- Mel spectrogram analysis
- LIME and GradCAM explanations for audio
- Multiple visualization outputs

---

## 3. Video Detection Endpoints

### 3.1 Video Deepfake Detection
**Endpoint:** `/detect-video`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Video file
- `num_samples` (optional): Number of frames to sample, 5-100 (default: `30`)
- `strategy` (optional): Sampling strategy (default: `hybrid`)
  - `uniform`: Evenly spaced frames
  - `stratified`: Frames from different segments
  - `adaptive`: Gaussian distribution around center
  - `scene_aware`: Detect scene changes
  - `hybrid`: Combination of all strategies
- `max_workers` (optional): Parallel workers, 1-8 (default: `4`)
- `include_xai` (optional): Include XAI explanations (default: `false`)
- `include_c2pa` (optional): Include C2PA verification (default: `false`)

**Response:**
```json
{
  "metadata": {
    "duration": 10.5,
    "fps": 30,
    "total_frames": 315,
    "resolution": "1280x720"
  },
  "overall_verdict": "Fake" | "Real",
  "overall_confidence": 0.85,
  "statistics": {
    "total_frames": 30,
    "fake_frames": 25,
    "real_frames": 5,
    "fake_ratio": 0.833,
    "avg_confidence": 0.85
  },
  "frame_scores": [0.12, 0.85, ...],
  "frame_paths": ["path1", "path2", ...],
  "temporal_analysis": {
    "consistency_score": 0.75,
    "variance": 0.05,
    "transitions": 2
  },
  "processing_time_seconds": 45.2
}
```

---

### 3.2 Generate PDF Report (Video)
**Endpoint:** `/generate-video-report`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Video file
- `investigator_name` (optional): Investigator name (default: "AI Detection System")
- `case_number` (optional): Case number (auto-generated if not provided)
- `num_samples` (optional): Number of frames to sample (default: `30`)
- `strategy` (optional): Sampling strategy (default: `hybrid`)
- `include_xai` (optional): Include XAI for high-score frames (default: `false`)

**Response:**  
PDF file download with forensic report including:
- Case information
- Video metadata
- Executive summary (LLM-generated)
- Frame-by-frame analysis chart
- Deepfake assessment verdict
- Technical details
- Sample frames with scores
- Temporal consistency analysis
- Recommendations

---

## 4. Utility Endpoints

### 4.1 Health Check
**Endpoint:** `/health`  
**Method:** `GET`

**Response:**
```json
{
  "status": "ok",
  "service": "Deepfake Detection Backend-2"
}
```

---

## Testing Examples

### cURL Examples

**1. Basic Image Detection:**
```bash
curl -X POST http://localhost:5001/detect \
  -F "file=@image.jpg" \
  -F "explain=true" \
  -F "c2pa=true"
```

**2. Agentic Analysis:**
```bash
curl -X POST http://localhost:5001/analyze-agentic \
  -F "file=@image.jpg" \
  -F "include_metadata=true"
```

**3. Generate PDF Report:**
```bash
curl -X POST http://localhost:5001/generate-report \
  -F "file=@image.jpg" \
  -F "investigator_name=John Doe" \
  -F "include_xai=true" \
  -F "include_agentic=true" \
  --output report.pdf
```

**4. Audio Detection:**
```bash
curl -X POST http://localhost:5001/detect-audio \
  -F "file=@audio.wav"
```

**5. Video Detection:**
```bash
curl -X POST http://localhost:5001/detect-video \
  -F "file=@video.mp4" \
  -F "num_samples=30" \
  -F "strategy=hybrid" \
  -F "max_workers=4"
```

**6. Video PDF Report:**
```bash
curl -X POST http://localhost:5001/generate-video-report \
  -F "file=@video.mp4" \
  -F "investigator_name=Jane Smith" \
  -F "num_samples=20" \
  --output video_report.pdf
```

---

## Dependencies Status

### Required Python Packages:
- ✅ `torch`, `torchvision`, `transformers` - Deep learning
- ✅ `opencv-python` - Video/image processing
- ✅ `flask`, `flask-cors` - Web server
- ✅ `lime`, `shap`, `pytorch-grad-cam` - XAI
- ✅ `c2pa-python` - Content credentials
- ✅ `langchain`, `langchain-groq`, `groq` - Agentic AI
- ✅ `pytesseract` - OCR (requires Tesseract binary)
- ✅ `tavily-python` - Web search
- ✅ `reportlab` - PDF generation
- ✅ `librosa`, `soundfile` - Audio processing

### External Dependencies:
- Tesseract OCR: Required for text extraction (install separately)
- GROQ API Key: Required for agentic analysis and video reports
- Tavily API Key: Required for web search in agentic analysis

---

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200` - Success
- `400` - Bad request (missing file, invalid parameters)
- `500` - Server error
- `503` - Service unavailable (module not loaded)

Error response format:
```json
{
  "error": "Error message description"
}
```

---

## Notes

1. **Module Availability**: Endpoints gracefully handle missing dependencies and return 503 with helpful error messages.

2. **Temporary Files**: All uploaded files are saved to temporary locations and cleaned up after processing.

3. **PDF Reports**: Generated PDFs are saved to the system temp directory with unique case numbers.

4. **Parallel Processing**: Video detection uses ThreadPoolExecutor for efficient frame processing.

5. **API Keys**: Ensure GROQ_API_KEY and TAVILY_API_KEY are set in environment variables or update the code with your keys.

6. **Performance**: Video processing time depends on video length, sampling strategy, and number of workers.
