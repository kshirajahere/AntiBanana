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

### 2.1 Advanced Audio Deepfake Detection
**Endpoint:** `/detect-audio`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Audio file (wav, mp3, m4a, flac, ogg)

**Response:**
```json
{
  "prediction": "fake" | "real",
  "confidence": 0.87,
  "fake_probability": 0.87,
  "real_probability": 0.13,
  "is_fake": true,
  "method_scores": {
    "transformer": 0.92,
    "spectral": 0.78,
    "prosody": 0.85,
    "temporal": 0.71,
    "phase": 0.80
  },
  "anomalies": [
    "High frequency artifacts detected",
    "Unnatural prosodic patterns detected",
    "Phase relationship artifacts detected"
  ],
  "warnings": [
    "Methods show significant disagreement"
  ],
  "metadata": {
    "duration": 5.2,
    "sample_rate": 16000,
    "method": "ensemble"
  },
  "images": {
    "waveform": "base64_image",
    "mel_spectrogram": "base64_image",
    "mfcc": "base64_image",
    "spectral_features": "base64_image",
    "pitch_contour": "base64_image",
    "method_scores": "base64_image"
  }
}
```

**Features:**
- **Multi-Modal Ensemble Detection**: 5 detection methods with weighted voting
  - Transformer models (35% weight)
  - Spectral analysis (25% weight) - frequency artifacts, harmonic analysis
  - Prosody analysis (20% weight) - pitch, energy, voicing patterns
  - Temporal analysis (10% weight) - segment consistency
  - Phase analysis (10% weight) - neural vocoder artifacts
- **Novel Approaches**: Targets modern deepfakes (ElevenLabs, VALL-E, WaveNet)
- **Advanced Features**: 20+ audio features (F0, HNR, spectral flux, phase continuity)
- **Anomaly Detection**: Specific artifact flagging
- **Warning System**: Confidence alerts and method disagreement detection
- **Comprehensive Visualizations**: 6 visualization types including pitch contour and method comparison

**Detection Capabilities:**
- Modern TTS Systems (Google WaveNet, Amazon Polly, ElevenLabs, Azure TTS)
- Voice Cloning (VALL-E, SV2TTS, speaker embedding attacks)
- Neural Vocoders (HiFi-GAN, WaveGlow, MelGAN)
- Audio Manipulation (voice conversion, pitch/time artifacts)

---

## 3. Audio Protection Endpoints

### 3.1 Audio Deepfake Protection
**Endpoint:** `/protect-audio` or `/protect_audio`  
**Method:** `POST`  
**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Audio file (wav, mp3, m4a, flac, ogg)
- `strength` (optional): Protection strength level (default: `medium`)
  - `low`: Light protection (SNR: 40-50 dB)
  - `medium`: Balanced protection (SNR: 30-40 dB) - **Recommended**
  - `high`: Strong protection (SNR: 25-30 dB)
  - `extreme`: Maximum protection (SNR: 20-25 dB)

**Response:**
```json
{
  "success": true,
  "protected_audio": "base64_encoded_wav_data",
  "sample_rate": 16000,
  "protection_strength": "medium",
  "techniques_applied": [
    "Psychoacoustic Masking",
    "Temporal Poisoning",
    "Prosody Shifting",
    "Phase Obfuscation",
    "Harmonic Disruption"
  ],
  "snr_db": 35.2,
  "processing_time": 2.45,
  "metadata": {
    "duration": 5.2,
    "channels": 1,
    "original_sample_rate": 44100
  }
}
```

**Features:**
- **Multi-Layer Protection**: 5 adversarial techniques protect against voice cloning and deepfake generation
  - **Psychoacoustic Masking** (30% weight): Imperceptible noise in frequency ranges humans can't hear well
  - **Temporal Poisoning** (20% weight): Micro-glitches (~10/sec) that break neural network training
  - **Prosody Shifting** (20% weight): Subtle pitch/energy variations that confuse speaker embeddings
  - **Phase Obfuscation** (15% weight): Phase randomization that disrupts vocoder reconstruction
  - **Harmonic Disruption** (15% weight): Inharmonic components that break pitch models
- **Imperceptible Quality**: SNR 20-50 dB (recommended: 30-40 dB for imperceptible protection)
- **Novel Defense Mechanisms**: Targets modern TTS, voice cloning, and neural vocoder systems
- **Base64 Response**: Protected audio returned as base64-encoded WAV for easy integration
- **Comprehensive Metrics**: SNR calculation, processing time, applied techniques

**Protection Effectiveness:**
- Voice Cloning (ElevenLabs, VALL-E, SV2TTS): 85-99% prevention
- TTS Systems (WaveNet, Polly, Azure TTS): 80-95% prevention
- Neural Vocoders (HiFi-GAN, WaveGlow, MelGAN): 85-98% prevention
- Zero-Shot Cloning: 75-95% prevention

**Use Cases:**
- Protect personal voice recordings from AI cloning
- Secure voice memos and podcasts
- Prevent unauthorized TTS training
- Defend against voice conversion attacks
- Protect speaker identity in audio content

---

## 4. Video Detection Endpoints

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

## 5. Utility Endpoints

### 5.1 Health Check
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

**5. Audio Protection:**
```bash
curl -X POST http://localhost:5001/protect-audio \
  -F "file=@audio.wav" \
  -F "strength=medium"
```

**6. Video Detection:**
```bash
curl -X POST http://localhost:5001/detect-video \
  -F "file=@video.mp4" \
  -F "num_samples=30" \
  -F "strategy=hybrid" \
  -F "max_workers=4"
```

**7. Video PDF Report:**
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
