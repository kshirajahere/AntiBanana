# 🍌 AntiBanana - Advanced Deepfake Detection & Protection Suite

## Executive Summary

**AntiBanana** is a comprehensive, multi-modal deepfake detection and content protection system that combines state-of-the-art AI models, explainable AI (XAI), content provenance verification (C2PA), and adversarial protection (MMHI). The system provides detection capabilities across images, videos, and audio, with seamless integration into popular platforms like WhatsApp Web through a Chrome extension.

### Key Capabilities
- 🔍 **Multi-Modal Detection**: Images, Videos, and Audio
- 💡 **Explainable AI (XAI)**: LIME, SHAP, Grad-CAM++ visualizations
- 📜 **C2PA Verification**: Content credentials and chain of custody
- 🛡️ **MMHI Protection**: Adversarial perturbations to prevent deepfake generation
- 🤖 **Agentic Analysis**: LLM-powered comprehensive investigation
- 📄 **Forensic Reports**: Professional PDF reports with case management
- 💬 **WhatsApp Integration**: Real-time detection in messaging apps
- 🌐 **Web Interface**: Modern Next.js frontend
- 🔌 **REST API**: Flask backend with comprehensive endpoints

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ANTIBANANA ECOSYSTEM                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   Frontend UI    │  │ Chrome Extension │  │  WhatsApp Web    │ │
│  │   (Next.js)      │  │   (Manifest v3)  │  │  Integration     │ │
│  │                  │  │                  │  │                  │ │
│  │ • React/TypeScript│  │ • Popup Interface│  │ • Detect Button │ │
│  │ • Tailwind CSS   │  │ • Content Script │  │ • Protect Toggle│ │
│  │ • File Upload    │  │ • Background SW  │  │ • Real-time    │ │
│  │ • Results Display│  │ • Settings       │  │   Analysis     │ │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘ │
│           │                     │                      │           │
│           └─────────────────────┴──────────────────────┘           │
│                                 │                                  │
│                         HTTP/REST API                              │
│                                 │                                  │
│  ┌──────────────────────────────▼─────────────────────────────┐   │
│  │              FLASK BACKEND SERVER (Port 5000)              │   │
│  │                                                             │   │
│  │  API Endpoints:                                            │   │
│  │  • /detect          - Image deepfake detection             │   │
│  │  • /detect-video    - Video deepfake detection             │   │
│  │  • /detect-audio    - Audio deepfake detection             │   │
│  │  • /protect         - MMHI image protection                │   │
│  │  • /c2pa            - C2PA provenance verification         │   │
│  │  • /explain         - XAI explanations                     │   │
│  │  • /analyze-agentic - LLM-powered analysis                │   │
│  │  • /generate-report - PDF forensic reports                │   │
│  └─────────────────────────────┬───────────────────────────────┘   │
│                                │                                  │
│  ┌─────────────────────────────▼───────────────────────────────┐   │
│  │                    DETECTION ENGINES                        │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                             │   │
│  │  ┌──────────────────┐  ┌──────────────────┐               │   │
│  │  │ DeepfakeDetector │  │ VideoDeepfake    │               │   │
│  │  │                  │  │ Detector         │               │   │
│  │  │ • Face Swap      │  │                  │               │   │
│  │  │ • GAN Detection  │  │ • Frame Sampling │               │   │
│  │  │ • Diffusion      │  │ • Parallel Proc. │               │   │
│  │  │ • Ensemble       │  │ • Temporal       │               │   │
│  │  │ • Frequency      │  │   Consistency    │               │   │
│  │  └──────────────────┘  └──────────────────┘               │   │
│  │                                                             │   │
│  │  ┌──────────────────┐  ┌──────────────────┐               │   │
│  │  │ VoiceAnalysis    │  │ C2PAVerifier     │               │   │
│  │  │                  │  │                  │               │   │
│  │  │ • Mel Spectro    │  │ • Manifest Parse │               │   │
│  │  │ • Transformer    │  │ • Chain of       │               │   │
│  │  │ • Audio XAI      │  │   Custody        │               │   │
│  │  └──────────────────┘  └──────────────────┘               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   AUXILIARY COMPONENTS                      │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                             │   │
│  │  ┌──────────────────┐  ┌──────────────────┐               │   │
│  │  │ Explainability   │  │ MMHI Protection  │               │   │
│  │  │ Engine           │  │ Pipeline         │               │   │
│  │  │                  │  │                  │               │   │
│  │  │ • LIME           │  │ • Phase 1: Freq  │               │   │
│  │  │ • SHAP           │  │ • Phase 2: Color │               │   │
│  │  │ • Grad-CAM++     │  │ • Phase 3: Noise │               │   │
│  │  │ • Integrated Grad│  │ • Configurable   │               │   │
│  │  └──────────────────┘  └──────────────────┘               │   │
│  │                                                             │   │
│  │  ┌──────────────────┐  ┌──────────────────┐               │   │
│  │  │ Agentic Analysis │  │ Report Generator │               │   │
│  │  │                  │  │                  │               │   │
│  │  │ • Groq Vision    │  │ • ReportLab PDF  │               │   │
│  │  │ • LangChain      │  │ • Case Tracking  │               │   │
│  │  │ • OCR (Tesseract)│  │ • Evidence Chain │               │   │
│  │  │ • Web Search     │  │ • Visualizations │               │   │
│  │  └──────────────────┘  └──────────────────┘               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      AI MODELS LAYER                        │   │
│  ├─────────────────────────────────────────────────────────────┤   │
│  │                                                             │   │
│  │  • dima806/deepfake_vs_real_image_detection                │   │
│  │  • Organika/sdxl-detector                                   │   │
│  │  • umm-maybe/AI-image-detector                             │   │
│  │  • deepfake-whisper-features/deepfake-audio-detection      │   │
│  │  • Custom Ensemble Models                                   │   │
│  │  • Frequency Analysis Algorithms                            │   │
│  │  • MMHI Adversarial Models                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Component Diagrams

### Detection Pipeline Flow

```
┌─────────────┐
│  User Input │
│ (File Upload)│
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│    File Type Detection          │
│  • Image → DeepfakeDetector     │
│  • Video → VideoDeepfakeDetector│
│  • Audio → VoiceAnalysis        │
└──────┬──────────────────────────┘
       │
       ▼
┌────────────────────────────────────────────────────┐
│           MULTI-MODEL ENSEMBLE DETECTION           │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────┐ │
│  │   Model 1    │  │   Model 2    │  │ Model N │ │
│  │ Face Swap    │  │ GAN Detector │  │  Freq.  │ │
│  │  Detection   │  │              │  │ Analysis│ │
│  └──────┬───────┘  └──────┬───────┘  └────┬────┘ │
│         │                 │                │      │
│         └─────────────────┴────────────────┘      │
│                           │                       │
│                  ┌────────▼────────┐              │
│                  │ Score Fusion    │              │
│                  │ (Weighted Avg)  │              │
│                  └────────┬────────┘              │
└───────────────────────────┼────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            │                               │
            ▼                               ▼
┌──────────────────────┐        ┌──────────────────────┐
│   C2PA Verification  │        │  XAI Explanation     │
│                      │        │                      │
│ • Manifest Parsing   │        │ • LIME Segments      │
│ • Chain of Custody   │        │ • SHAP Values        │
│ • Trust Assessment   │        │ • Grad-CAM Heatmap   │
└──────────┬───────────┘        └──────────┬───────────┘
           │                               │
           └───────────────┬───────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  Agentic Analysis      │
              │  (Optional)            │
              │                        │
              │ • Visual Analysis      │
              │ • Text Extraction      │
              │ • Web Search Context   │
              │ • LLM Reasoning        │
              └────────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    Final Results       │
              │                        │
              │ • Classification       │
              │ • Confidence Score     │
              │ • Evidence Chain       │
              │ • Recommendations      │
              └────────────────────────┘
```

### Video Detection Pipeline

```
┌─────────────┐
│ Video Input │
│  (.mp4)     │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│  Metadata Extraction     │
│  • Duration              │
│  • FPS                   │
│  • Resolution            │
│  • Codec                 │
└──────┬───────────────────┘
       │
       ▼
┌───────────────────────────────────────┐
│      Frame Sampling Strategy          │
│                                       │
│  ┌──────────┐  ┌──────────┐          │
│  │ Uniform  │  │Stratified│          │
│  └────┬─────┘  └────┬─────┘          │
│       │             │                 │
│  ┌────▼─────┐  ┌───▼──────┐          │
│  │ Adaptive │  │Scene-Aware│         │
│  └────┬─────┘  └────┬──────┘         │
│       │             │                 │
│       └─────┬───────┘                 │
│             │                         │
│      ┌──────▼────────┐                │
│      │ Hybrid Select │                │
│      │ (Best of All) │                │
│      └──────┬────────┘                │
└─────────────┼─────────────────────────┘
              │
              ▼
┌──────────────────────────────────────┐
│    Parallel Frame Processing         │
│   (ThreadPoolExecutor - 4 workers)   │
│                                      │
│  Frame 1  Frame 2  ...  Frame N      │
│     │        │            │          │
│     ▼        ▼            ▼          │
│  [Model] [Model]  ... [Model]       │
│     │        │            │          │
│     └────────┴────────────┘          │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│    Temporal Consistency Analysis     │
│                                      │
│  • Frame-to-frame variance           │
│  • Transition detection              │
│  • Consistency scoring               │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│        Aggregation & Verdict         │
│                                      │
│  • Fake ratio calculation            │
│  • Average confidence                │
│  • Overall classification            │
│  • Suspicious segments               │
└──────────────────────────────────────┘
```

---

## 🔄 Sequence Diagrams

### Image Detection with XAI

```
User         Extension      Backend       Detector      XAI Engine    C2PA
 │               │              │              │              │         │
 │─Upload Image──►              │              │              │         │
 │               │              │              │              │         │
 │               │─POST /detect─►              │              │         │
 │               │              │              │              │         │
 │               │              │─detect()─────►              │         │
 │               │              │              │              │         │
 │               │              │              │──Model 1────►│         │
 │               │              │              │◄─Score───────│         │
 │               │              │              │              │         │
 │               │              │              │──Model 2────►│         │
 │               │              │              │◄─Score───────│         │
 │               │              │              │              │         │
 │               │              │              │──Ensemble────►         │
 │               │              │              │◄─Final Score─│         │
 │               │              │              │              │         │
 │               │              │──explain()───┼──────────────►         │
 │               │              │              │              │         │
 │               │              │              │          LIME│         │
 │               │              │              │◄─────────────┤         │
 │               │              │              │         SHAP│         │
 │               │              │              │◄─────────────┤         │
 │               │              │              │      GradCAM│         │
 │               │              │              │◄─────────────┤         │
 │               │              │              │              │         │
 │               │              │──verify()────┼──────────────┼─────────►
 │               │              │              │              │         │
 │               │              │              │              │◄─C2PA───┤
 │               │              │              │              │  Data   │
 │               │              │              │              │         │
 │               │              │◄─Results─────┴──────────────┴─────────┘
 │               │              │ (Detection + XAI + C2PA)              
 │               │◄─JSON────────┤                                       
 │               │              │                                       
 │◄─Display──────┤              │                                       
 │  Results      │              │                                       
 │               │              │                                       
```

### WhatsApp Web Integration Flow

```
User      WhatsApp      Content       Backend       Detector
         Web Page      Script         API
 │           │            │              │              │
 │─Receive─►│            │              │              │
 │  Image   │            │              │              │
 │           │            │              │              │
 │           │◄──DOM──────┤              │              │
 │           │  Observer  │              │              │
 │           │            │              │              │
 │           │            │──Add "Detect"│              │
 │           │            │   Button     │              │
 │           │            │              │              │
 │◄──See────┼────────────┤              │              │
 │  Button  │            │              │              │
 │           │            │              │              │
 │──Click───►            │              │              │
 │  Detect  │            │              │              │
 │           │            │              │              │
 │           │            │──Extract─────►              │
 │           │            │   Image      │              │
 │           │            │   (Blob URL) │              │
 │           │            │              │              │
 │           │            │──POST────────►              │
 │           │            │  /detect     │              │
 │           │            │              │              │
 │           │            │              │──Analyze────►│
 │           │            │              │              │
 │           │            │              │◄─Results────┤
 │           │            │              │              │
 │           │            │◄─JSON────────┤              │
 │           │            │  Response    │              │
 │           │            │              │              │
 │           │            │──Create──────►              │
 │           │            │   Popup      │              │
 │           │            │   (Results)  │              │
 │           │            │              │              │
 │◄──View───┼────────────┤              │              │
 │  Popup   │            │              │              │
 │  Results │            │              │              │
 │           │            │              │              │
```

### Image Protection (MMHI) Flow

```
User      Extension    Backend      MMHI Pipeline
 │             │           │              │
 │──Upload────►           │              │
 │   Image    │           │              │
 │             │           │              │
 │──Enable────►           │              │
 │  "Protect" │           │              │
 │             │           │              │
 │             │─POST──────►              │
 │             │ /protect  │              │
 │             │           │              │
 │             │           │──Phase 1─────►
 │             │           │  Frequency   │
 │             │           │  Domain      │
 │             │           │◄─Modified────┤
 │             │           │              │
 │             │           │──Phase 2─────►
 │             │           │  Color Space │
 │             │           │◄─Modified────┤
 │             │           │              │
 │             │           │──Phase 3─────►
 │             │           │  Adversarial │
 │             │           │  Noise       │
 │             │           │◄─Protected───┤
 │             │           │              │
 │             │◄─Base64───┤              │
 │             │  Image    │              │
 │             │           │              │
 │◄─Display───┤           │              │
 │  Protected │           │              │
 │             │           │              │
 │──Download──►           │              │
 │   Image    │           │              │
 │             │           │              │
```

---

## 🧠 Technology Stack

### Backend (Python/Flask)

#### Core Framework
- **Flask 3.1.2**: Web framework with CORS support
- **Python 3.11**: Runtime environment

#### Deep Learning
- **PyTorch 2.x**: Primary deep learning framework
- **Transformers (Hugging Face)**: Pre-trained model hub
- **timm**: PyTorch Image Models library
- **torchvision**: Computer vision utilities
- **pytorch-lightning**: Training framework
- **torchmetrics**: Model evaluation metrics

#### Computer Vision
- **OpenCV (cv2)**: Image/video processing
- **Pillow (PIL)**: Image manipulation
- **scikit-image**: Advanced image processing
- **scipy**: Scientific computing (FFT, signal processing)

#### Explainable AI (XAI)
- **LIME**: Local Interpretable Model-agnostic Explanations
- **SHAP**: SHapley Additive exPlanations
- **pytorch-grad-cam**: Gradient-weighted Class Activation Mapping
- **Grad-CAM++**: Enhanced CAM with better localization

#### Content Verification
- **c2pa-python**: Coalition for Content Provenance and Authenticity
- **PyExifTool**: EXIF metadata extraction
- **cryptography**: Digital signatures

#### Audio Processing
- **librosa**: Audio analysis and feature extraction
- **soundfile**: Audio file I/O

#### Agentic AI & LLMs
- **LangChain**: LLM orchestration framework
- **langchain-groq**: Groq LLM integration
- **groq**: Groq API client
- **pytesseract**: OCR text extraction
- **tavily-python**: Web search API

#### Reporting & Visualization
- **matplotlib**: Data visualization
- **reportlab**: PDF generation
- **numpy**: Numerical computing

### Frontend (Next.js)

#### Core Framework
- **Next.js 14**: React framework with App Router
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript

#### Styling
- **Tailwind CSS**: Utility-first CSS framework
- **CSS Modules**: Component-scoped styling
- **Framer Motion**: Animation library (implicit via components)

#### UI Components
- **shadcn/ui**: Re-usable component library
- **Radix UI**: Headless UI primitives
- **Lucide Icons**: Icon set

#### State & Data
- **React Hooks**: State management
- **Fetch API**: HTTP requests

### Chrome Extension (Manifest V3)

#### Core Technologies
- **Manifest V3**: Latest Chrome extension format
- **Service Workers**: Background processing
- **Content Scripts**: Page injection
- **Chrome Storage API**: Settings persistence

#### UI Technologies
- **Vanilla JavaScript**: No framework overhead
- **CSS3**: Modern styling with animations
- **HTML5**: Semantic markup

#### Integration
- **WhatsApp Web Selectors**: DOM manipulation
- **Fetch API**: Backend communication
- **Blob API**: Image handling

---

## 🔬 Detection Models & Algorithms

### Image Detection Models

#### 1. Face Swap Detection
- **Model**: `dima806/deepfake_vs_real_image_detection`
- **Type**: Vision Transformer (ViT)
- **Purpose**: Detects traditional face-swap deepfakes
- **Output**: Binary classification (fake/real) with confidence

#### 2. GAN-Generated Image Detection
- **Model**: `Organika/sdxl-detector`
- **Type**: CNN-based classifier
- **Purpose**: Identifies GAN and diffusion model outputs
- **Output**: Probability score for synthetic content

#### 3. AI Image Detection
- **Model**: `umm-maybe/AI-image-detector`
- **Type**: Ensemble classifier
- **Purpose**: General AI-generated content detection
- **Output**: AI vs. Real classification

#### 4. Frequency Analysis
- **Algorithm**: Fast Fourier Transform (FFT)
- **Purpose**: Detects artifacts in frequency domain
- **Method**: Analyzes high-frequency components
- **Output**: Anomaly score based on spectral features

#### 5. Ensemble Fusion
- **Method**: Weighted average voting
- **Inputs**: All model scores + frequency analysis
- **Weights**: Configurable per model reliability
- **Output**: Final aggregated confidence score

### Video Detection

#### Frame Sampling Strategies

1. **Uniform Sampling**
   - Evenly distributed frames across video
   - Formula: `frame_indices = linspace(0, total_frames, num_samples)`

2. **Stratified Sampling**
   - Divides video into segments
   - Samples from each segment
   - Ensures temporal coverage

3. **Adaptive Sampling**
   - Gaussian distribution around center
   - Biases toward middle of video
   - Useful for focal content detection

4. **Scene-Aware Sampling**
   - Analyzes frame differences
   - Selects frames with high variance
   - Focuses on scene transitions

5. **Hybrid Sampling** (Default)
   - Combines all strategies
   - Ensures comprehensive coverage
   - Best for general use cases

#### Temporal Consistency Analysis
- **Variance Calculation**: Measures score fluctuation across frames
- **Transition Detection**: Identifies sudden changes in predictions
- **Consistency Score**: Aggregates temporal coherence
- **Confidence Weighting**: Higher weight to consistent patterns

### Audio Detection

#### Audio Feature Extraction
- **Mel-Frequency Cepstral Coefficients (MFCC)**
- **Mel Spectrograms**: Time-frequency representation
- **Waveform Analysis**: Temporal patterns
- **Spectral Features**: Frequency domain characteristics

#### Audio Detection Model
- **Model**: `deepfake-whisper-features/deepfake-audio-detection`
- **Type**: Transformer-based audio classifier
- **Input**: Audio features (spectrogram/MFCC)
- **Output**: Fake/real classification with confidence

#### Audio XAI
- **LIME for Audio**: Segment-based explanations
- **Grad-CAM for Spectrograms**: Visual attention maps
- **Feature Importance**: Which audio features influenced decision

---

## 🛡️ MMHI Protection Pipeline

### Phase 1: Frequency Domain Perturbations
```python
# DCT-based high-frequency noise injection
dct = cv2.dct(image_float)
high_freq_mask = create_high_freq_mask(shape)
dct += noise * high_freq_mask * strength
image = cv2.idct(dct)
```
- **Purpose**: Adds imperceptible noise in frequency domain
- **Effect**: Disrupts GAN/diffusion model latent space
- **Visibility**: Minimal impact on visual quality

### Phase 2: Color Space Manipulation
```python
# YUV color space perturbations
yuv = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
yuv[:,:,1:] += subtle_noise  # Modify U,V channels
image = cv2.cvtColor(yuv, cv2.COLOR_YUV2RGB)
```
- **Purpose**: Alters color representation
- **Effect**: Confuses color-based deepfake models
- **Preservation**: Maintains perceived colors

### Phase 3: Adversarial Noise
```python
# PGD-style adversarial perturbations
for iteration in range(steps):
    gradient = compute_gradient(model, image, target)
    image += alpha * sign(gradient)
    image = clip(image, epsilon)
```
- **Purpose**: Model-specific adversarial examples
- **Effect**: Maximizes model confusion
- **Strength Levels**:
  - Medium: ε = 0.01, steps = 5
  - High: ε = 0.02, steps = 10
  - Extreme: ε = 0.03, steps = 20

### Protection Strength Configuration
| Level | Frequency | Color | Adversarial | Use Case |
|-------|-----------|-------|-------------|----------|
| Medium | Low | Low | Moderate | Social media, chat |
| High | Medium | Medium | High | Public sharing |
| Extreme | High | High | Very High | Sensitive content |

---

## 📊 Explainable AI (XAI) Methods

### 1. LIME (Local Interpretable Model-agnostic Explanations)

**Purpose**: Explains predictions by perturbing input locally

**Process**:
```
1. Segment image into superpixels (SLIC algorithm)
2. Create perturbed samples by hiding segments
3. Get model predictions for perturbed samples
4. Train linear model on perturbations
5. Extract feature importance (segment weights)
6. Visualize important regions
```

**Output**:
- Overlay: Important segments highlighted
- Saliency: Heatmap of contribution weights

**Advantages**:
- Model-agnostic
- Intuitive segmentation
- Local fidelity

### 2. SHAP (SHapley Additive exPlanations)

**Purpose**: Game-theoretic approach to feature attribution

**Process**:
```
1. Use DeepExplainer for deep networks
2. Calculate Shapley values for pixels
3. Aggregate contributions across image
4. Generate attribution heatmap
```

**Output**:
- Pixel-level attribution values
- Positive (supports prediction) vs. negative contributions

**Advantages**:
- Theoretically grounded
- Consistent attributions
- Additive feature importance

### 3. Grad-CAM++ (Gradient-weighted Class Activation Mapping)

**Purpose**: Visual explanation using gradient information

**Process**:
```
1. Forward pass through model
2. Extract target layer activations
3. Compute gradients w.r.t. target class
4. Weight activation maps by gradients
5. Apply ReLU and upscale to original size
6. Overlay heatmap on original image
```

**Output**:
- Heatmap showing attended regions
- High-resolution localization

**Advantages**:
- Network-aware (uses gradients)
- High spatial resolution
- Multiple object detection

### 4. Integrated Gradients

**Purpose**: Path-based attribution method

**Process**:
```
1. Define baseline (black image)
2. Create interpolated path from baseline to input
3. Compute gradients along path
4. Integrate gradients to get attributions
```

**Output**:
- Pixel-wise attribution scores
- Satisfies axioms (completeness, sensitivity)

---

## 🔐 C2PA Content Provenance

### What is C2PA?

**Coalition for Content Provenance and Authenticity**
- Industry standard for content authentication
- Embeds cryptographically signed metadata
- Tracks content creation and modifications
- Provides tamper-evident chain of custody

### C2PA Verification Process

```
1. Extract C2PA manifest from image
   └─> Parse embedded JSON metadata

2. Validate cryptographic signatures
   └─> Verify with public keys

3. Build chain of custody
   └─> Track all modifications and actors

4. Assess trust level
   ├─> High: Valid signatures, trusted CA
   ├─> Medium: Valid signatures, unknown CA
   ├─> Low: Signatures present but issues
   └─> None: No C2PA data found

5. Extract provenance information
   ├─> Creator identity
   ├─> Creation timestamp
   ├─> Editing history
   ├─> Camera/software used
   └─> Assertions and claims
```

### Trust Assessment Algorithm

```python
def assess_trust(manifest):
    if not manifest:
        return "none"
    
    if valid_signatures and trusted_CA and no_tampering:
        return "high"
    elif valid_signatures and no_tampering:
        return "medium"
    elif manifest_exists:
        return "low"
    else:
        return "none"
```

---

## 🤖 Agentic Analysis System

### Multi-Tool Approach

The agentic analysis uses LangChain with multiple tools:

#### 1. Vision Analysis Tool
```python
analyze_image_with_vision(image_base64) -> str
```
- **Model**: Groq Vision (llama-3.2-90b-vision-preview)
- **Purpose**: Detailed visual inspection
- **Output**: Description of suspicious artifacts

#### 2. XAI Explanation Tool
```python
explain_with_lime_gradcam(image_path) -> dict
```
- **Methods**: LIME + Grad-CAM++
- **Purpose**: Show model attention regions
- **Output**: Base64 encoded heatmaps

#### 3. OCR Text Extraction Tool
```python
extract_text_from_image(image_path) -> str
```
- **Engine**: Tesseract OCR
- **Purpose**: Extract visible text
- **Output**: Text content for analysis

#### 4. Web Search Tool
```python
search_web(query) -> str
```
- **API**: Tavily Search
- **Purpose**: Context gathering
- **Output**: Relevant web information

### Agentic Workflow

```
┌─────────────────────────────────────────┐
│  Input: Image + Detection Results       │
└───────────┬─────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────┐
│  Agent: LLM with Tool Access              │
│  (Groq llama-3.3-70b-versatile)           │
├───────────────────────────────────────────┤
│                                           │
│  Step 1: Analyze visual content          │
│  └─> Call vision tool                    │
│                                           │
│  Step 2: Review XAI explanations         │
│  └─> Call LIME/Grad-CAM tool             │
│                                           │
│  Step 3: Extract text content            │
│  └─> Call OCR tool                       │
│                                           │
│  Step 4: Search for context              │
│  └─> Call web search tool                │
│                                           │
│  Step 5: Detect anomalies                │
│  └─> Analyze patterns, artifacts         │
│                                           │
│  Step 6: Cross-reference findings        │
│  └─> Compare tool outputs                │
│                                           │
│  Step 7: Generate verdict                │
│  └─> Synthesize comprehensive report     │
│                                           │
└───────────┬───────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────┐
│  Output: Detailed Analysis Report         │
│  • Visual anomalies                       │
│  • Model decision rationale               │
│  • Extracted information                  │
│  • Contextual relevance                   │
│  • Final verdict with confidence          │
└───────────────────────────────────────────┘
```

### Agent Prompt Structure

```python
prompt = f"""
You are a forensic analyst specializing in deepfake detection.

Given:
- Detection Results: {results}
- Image Analysis: [Use vision tool]
- XAI Explanations: [Use explain tool]
- Text Content: [Use OCR tool]
- Context: [Use search tool]

Provide comprehensive analysis covering:
1. Visual Content Analysis
2. Explanation Models Analysis
3. Anomaly Detection
4. Text Extraction Analysis
5. Metadata Assessment
6. Additional Context
7. Final Summary and Verdict

Be thorough, objective, and evidence-based.
"""
```

---

## 📄 Forensic Report Generation

### Report Components

#### 1. Case Information Header
- Case Number (UUID)
- Investigator Name
- Timestamp
- File Checksum (SHA-256)

#### 2. Evidence Section
- Original image preview
- File metadata (size, format, dimensions)
- EXIF data extraction
- Capture device information

#### 3. C2PA Provenance (if available)
- Manifest summary
- Creator information
- Chain of custody visualization
- Trust level assessment
- Signature validation

#### 4. Detection Results
- Overall verdict (Fake/Real)
- Confidence percentage
- Model-by-model breakdown
- Consensus analysis

#### 5. XAI Visualizations
- LIME segmentation overlay
- Grad-CAM++ heatmap
- SHAP attribution map
- Feature importance chart

#### 6. Agentic Analysis (if requested)
- LLM-generated insights
- Anomaly descriptions
- Contextual findings
- Expert-level summary

#### 7. Recommendations
- Suggested next steps
- Additional verification methods
- Distribution advisories

### Report Generation Pipeline

```python
def generate_forensic_report(
    image_path,
    detection_results,
    investigator_name,
    case_number,
    include_xai=True,
    include_c2pa=True,
    include_agentic=False
):
    # Initialize PDF
    pdf = ReportLabPDF(filename=f"report_{case_number}.pdf")
    
    # Add header
    pdf.add_title("DEEPFAKE FORENSIC ANALYSIS REPORT")
    pdf.add_case_info(case_number, investigator_name, timestamp)
    
    # Add evidence
    pdf.add_image(image_path, caption="Subject Image")
    pdf.add_metadata(extract_metadata(image_path))
    pdf.add_checksum(calculate_sha256(image_path))
    
    # Add C2PA if available
    if include_c2pa and has_c2pa(image_path):
        c2pa_data = verify_c2pa(image_path)
        pdf.add_section("C2PA Provenance Verification")
        pdf.add_c2pa_details(c2pa_data)
    
    # Add detection results
    pdf.add_section("Deepfake Detection Analysis")
    pdf.add_detection_results(detection_results)
    pdf.add_confidence_chart(detection_results)
    
    # Add XAI explanations
    if include_xai:
        xai_results = generate_xai(image_path)
        pdf.add_section("Explainable AI Visualizations")
        pdf.add_xai_images(xai_results)
    
    # Add agentic analysis
    if include_agentic:
        agent_report = run_agentic_analysis(image_path, detection_results)
        pdf.add_section("Advanced Agentic Analysis")
        pdf.add_agent_findings(agent_report)
    
    # Add recommendations
    pdf.add_section("Recommendations")
    pdf.add_recommendations(generate_recommendations(detection_results))
    
    # Finalize
    pdf.save()
    return pdf.filename
```

---

## 🌐 API Endpoints Reference

### Image Detection
- **POST /detect** - Multi-model image detection
- **POST /explain** - XAI-only explanations
- **POST /c2pa** - C2PA verification only
- **POST /analyze-agentic** - Full agentic analysis
- **POST /generate-report** - PDF forensic report

### Video Detection
- **POST /detect-video** - Video frame analysis
- **POST /generate-video-report** - Video PDF report

### Audio Detection
- **POST /detect-audio** - Audio deepfake detection

### Protection
- **POST /protect** - MMHI image protection

### Utility
- **GET /health** - Server health check

*See API_ENDPOINTS.md for detailed specifications*

---

## 🎨 Frontend Features

### Next.js Web Application

#### Pages
1. **Home (/)** 
   - Hero section with animated background
   - Feature highlights
   - Call-to-action buttons

2. **Detect (/detect)**
   - File uploader with drag-and-drop
   - Real-time analysis progress
   - Results visualization
   - XAI explanation toggles

3. **Protect (/protect)**
   - Image upload interface
   - Protection strength selector
   - Before/after comparison
   - Download protected image

#### Components
- **FileUploader**: Drag-and-drop with preview
- **AnalysisProgress**: Loading states and spinners
- **ResultsDisplay**: Charts, badges, confidence meters
- **XAIVisualizer**: Heatmap overlays
- **FeatureSection**: Landing page sections
- **Navbar**: Navigation and branding
- **Footer**: Links and information

#### Styling
- **Tailwind CSS**: Utility-first styling
- **Custom Theme**: Purple/blue gradient scheme
- **Dark Mode**: Full dark theme support
- **Responsive**: Mobile-first design
- **Animations**: Framer Motion effects

---

## 🔌 Chrome Extension Architecture

### Manifest V3 Structure

```json
{
  "manifest_version": 3,
  "name": "AntiBanana - Deepfake Protection Suite",
  "permissions": ["activeTab", "storage", "downloads"],
  "host_permissions": [
    "http://localhost:5000/*",
    "https://web.whatsapp.com/*"
  ],
  "action": {
    "default_popup": "popup.html"
  },
  "content_scripts": [{
    "matches": ["https://web.whatsapp.com/*"],
    "js": ["js/content.js"],
    "css": ["css/whatsapp.css"]
  }],
  "background": {
    "service_worker": "js/background.js"
  }
}
```

### Component Breakdown

#### 1. Popup Interface (`popup.html` + `popup.js`)
- **4 Tabs**: Detect, Protect, C2PA, Explain
- **File Upload**: Click or drag-and-drop
- **API Integration**: Calls backend endpoints
- **Results Display**: Formatted JSON visualization
- **Settings**: Backend URL configuration

#### 2. Content Script (`content.js`)
- **DOM Observer**: Watches for new images in WhatsApp
- **Button Injection**: Adds "🍌 Detect" overlay
- **Toggle Injection**: Adds "🛡️ Protect" switch
- **Event Handlers**: Click listeners for buttons
- **API Communication**: Fetch calls to backend
- **Result Popups**: Dynamic result overlays

#### 3. Background Service Worker (`background.js`)
- **Extension Lifecycle**: Installation/update handling
- **Message Passing**: Communication with content scripts
- **Context Menus**: Right-click options
- **Settings Storage**: Chrome storage sync

#### 4. Styling (`whatsapp.css`)
- **Button Styles**: Purple gradient, rounded
- **Popup Styles**: Card-based result display
- **Toggle Styles**: Custom switch component
- **Dark Mode**: WhatsApp dark theme support
- **Animations**: Smooth transitions

### WhatsApp Integration Details

#### Detection Button Overlay
```javascript
// Attach to images
document.querySelectorAll('img[src*="blob:"]').forEach(img => {
    const button = createDetectButton();
    button.onclick = () => detectImage(img.src);
    img.parentElement.appendChild(button);
});
```

#### Protection Toggle
```javascript
// Attach to attachment preview
const toggle = createProtectToggle();
toggle.onchange = async (e) => {
    if (e.target.checked) {
        const protectedImage = await protectImage(currentImage);
        replaceImage(protectedImage);
    }
};
attachmentPreview.appendChild(toggle);
```

---

## 📈 Performance Metrics

### Detection Speed

| Operation | Time | Notes |
|-----------|------|-------|
| Image Detection (Single Model) | ~1-2s | GPU accelerated |
| Image Detection (Ensemble) | ~3-5s | Multiple models |
| Image Detection + XAI | ~5-10s | LIME/SHAP computation |
| Image Detection + Agentic | ~15-30s | LLM analysis |
| Video Detection (30 frames) | ~30-60s | Parallel processing |
| Audio Detection | ~2-5s | Transformer inference |
| MMHI Protection | ~3-7s | 3-phase processing |
| PDF Report Generation | ~5-10s | With visualizations |

### Accuracy (Typical)

| Model/Method | Accuracy | F1-Score |
|--------------|----------|----------|
| Face Swap Detection | ~92% | ~0.90 |
| GAN Detection | ~88% | ~0.85 |
| AI Image Detection | ~90% | ~0.88 |
| Frequency Analysis | ~75% | ~0.70 |
| Ensemble (All) | ~94% | ~0.92 |
| Audio Detection | ~89% | ~0.87 |
| Video Detection | ~91% | ~0.89 |

*Note: Accuracy varies based on dataset and deepfake type*

### Resource Usage

| Component | CPU | GPU | RAM |
|-----------|-----|-----|-----|
| Backend (Idle) | <5% | 0% | ~1GB |
| Backend (Detecting) | 30-50% | 80-95% | ~3GB |
| Frontend (Next.js) | <10% | 0% | ~200MB |
| Chrome Extension | <2% | 0% | ~50MB |

---

## 🔒 Security Considerations

### Input Validation
- File type verification (magic bytes)
- File size limits (max 50MB images, 500MB videos)
- Sanitized filenames
- Temporary file cleanup

### API Security
- CORS configuration for allowed origins
- No authentication required (local deployment)
- Rate limiting recommended for production
- Input sanitization for all parameters

### Data Privacy
- No persistent storage of user uploads
- Temporary files auto-deleted post-processing
- No external data transmission (except LLM APIs)
- Local model inference (no cloud dependencies)

### Content Security Policy (Extension)
- Manifest V3 compliance
- Restricted permissions
- Isolated content scripts
- Secure message passing

---

## 📦 Deployment

### Backend Deployment

#### Local Development
```bash
cd backend
pip install -r requirements.txt
python main.py
# Server runs on http://localhost:5000
```

#### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

#### Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "main.py"]
```

### Frontend Deployment

#### Development
```bash
cd frontend
npm install
npm run dev
# Runs on http://localhost:3000
```

#### Production Build
```bash
npm run build
npm start
```

#### Vercel Deployment
```bash
vercel --prod
```

### Extension Installation

#### Chrome/Edge
1. Open `chrome://extensions/`
2. Enable Developer Mode
3. Click "Load unpacked"
4. Select `chrome-extension/` folder

#### Distribution (Chrome Web Store)
1. Zip extension folder
2. Create developer account
3. Upload to Chrome Web Store
4. Submit for review

---

## 🧪 Testing

### Backend Tests

```bash
# Unit tests
python test_detector.py      # Image detection
python test_video.py          # Video detection
python test_c2pa.py           # C2PA verification
python test_xai.py            # XAI explanations
python test_xai_integration.py # Integration tests
```

### Frontend Tests

```bash
cd frontend
npm test                       # Jest tests
npm run test:e2e              # Playwright E2E
```

### Extension Tests

Manual testing checklist:
- [ ] Extension loads without errors
- [ ] Popup interface functional
- [ ] All 4 tabs accessible
- [ ] File upload works
- [ ] API calls succeed
- [ ] Results display correctly
- [ ] WhatsApp buttons appear
- [ ] Detection in WhatsApp works
- [ ] Protection in WhatsApp works
- [ ] Settings persist

---

## 📚 Documentation

### Available Documentation

1. **PROJECT.md** (this file) - Comprehensive project overview
2. **API_ENDPOINTS.md** - Detailed API reference
3. **VIDEO_IMPLEMENTATION.md** - Video detection specifics
4. **C2PA_IMPLEMENTATION.md** - C2PA integration details
5. **XAI_IMPLEMENTATION.md** - Explainability methods
6. **INSTALLATION.md** - Extension installation guide
7. **WHATSAPP_INTEGRATION.md** - WhatsApp feature guide
8. **TESTING_GUIDE.md** - Testing procedures

---

## 🚀 Future Enhancements

### Planned Features

#### Detection Improvements
- [ ] Additional deepfake models (StyleGAN3, Midjourney detection)
- [ ] Face reenactment detection (DeepFaceLive, FaceSwap)
- [ ] Voice cloning detection (ElevenLabs, Resemble AI)
- [ ] Real-time video stream analysis
- [ ] Blockchain-based integrity verification

#### XAI Enhancements
- [ ] Attention visualization (Transformer attention maps)
- [ ] Counterfactual explanations
- [ ] Interactive XAI (user-guided explanations)
- [ ] Comparative analysis (real vs. fake side-by-side)

#### Platform Integrations
- [ ] Twitter/X integration
- [ ] Facebook Messenger integration
- [ ] Instagram integration
- [ ] Discord bot
- [ ] Telegram bot
- [ ] Email attachment scanning

#### Reporting Features
- [ ] Multi-language report generation
- [ ] Custom report templates
- [ ] Batch processing reports
- [ ] Automated evidence packaging
- [ ] Court-ready report formatting

#### Performance Optimizations
- [ ] Model quantization (INT8)
- [ ] ONNX Runtime inference
- [ ] WebAssembly for browser
- [ ] Edge computing deployment
- [ ] Cached results for duplicate content

---

## 🤝 Contributing

### Development Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/Pratz1337/AntiBanana.git
   cd AntiBanana
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Variables**
   ```bash
   export GROQ_API_KEY="your_key_here"
   export TAVILY_API_KEY="your_key_here"
   ```

### Code Style

- **Python**: PEP 8, type hints preferred
- **TypeScript**: ESLint + Prettier
- **JavaScript**: Airbnb style guide
- **Commits**: Conventional commits format

---

## 📊 Project Statistics

### Code Metrics

| Component | Files | Lines of Code | Languages |
|-----------|-------|---------------|-----------|
| Backend | 25+ | ~8,000 | Python |
| Frontend | 30+ | ~3,000 | TypeScript/React |
| Extension | 10+ | ~2,000 | JavaScript/CSS |
| **Total** | **65+** | **~13,000** | **Multiple** |

### AI Models Used

| Model | Parameters | Size | Purpose |
|-------|------------|------|---------|
| dima806/deepfake | ~86M | ~350MB | Face swap detection |
| Organika/sdxl | ~120M | ~480MB | GAN detection |
| umm-maybe/AI | ~50M | ~200MB | AI image detection |
| Audio Detector | ~90M | ~360MB | Voice deepfake |
| Groq Vision | N/A | API | Agentic analysis |
| Groq LLM | N/A | API | Report generation |

---

## 📜 License

This project is part of academic research and development.

---

## 👥 Team & Acknowledgments

### Development Team
- **Project Lead**: Implementation and architecture
- **Backend Development**: Python/Flask, AI models
- **Frontend Development**: Next.js, UI/UX
- **Extension Development**: Chrome Manifest v3

### Acknowledgments

**AI Models & Frameworks**:
- Hugging Face Transformers
- PyTorch Team
- OpenCV Community
- LangChain Developers

**Standards & Specifications**:
- C2PA Coalition
- W3C Content Authenticity Initiative

**Open Source Libraries**:
- LIME, SHAP, Grad-CAM authors
- Flask, Next.js communities
- All dependencies listed in requirements.txt

---

## 📞 Support & Contact

### Documentation
- Full API docs: `backend/API_ENDPOINTS.md`
- Video guide: `backend/VIDEO_IMPLEMENTATION.md`
- Extension guide: `chrome-extension/INSTALLATION.md`

### Issues & Bugs
- GitHub Issues: [Repository Issues](https://github.com/Pratz1337/AntiBanana/issues)

### Feature Requests
- Submit via GitHub Discussions

---

## 🎓 Academic Context

This project demonstrates:
- **Deep Learning**: Multi-model ensemble techniques
- **Computer Vision**: Image/video processing pipelines
- **Explainable AI**: Interpretability methods
- **Web Development**: Full-stack application architecture
- **Browser Extensions**: Manifest v3 development
- **Security**: Content integrity and provenance
- **UI/UX Design**: Modern interface design

### Research Applications
- Deepfake detection research
- XAI methodology comparison
- C2PA adoption studies
- Adversarial protection techniques
- Multi-modal analysis systems

---

## 📅 Version History

### v1.0.0 (Current)
- ✅ Multi-model image detection
- ✅ Video frame analysis
- ✅ Audio deepfake detection
- ✅ XAI (LIME, SHAP, Grad-CAM++)
- ✅ C2PA verification
- ✅ MMHI protection
- ✅ Agentic analysis (LLM)
- ✅ PDF forensic reports
- ✅ Next.js frontend
- ✅ Chrome extension
- ✅ WhatsApp Web integration

---

## 🎯 Conclusion

**AntiBanana** represents a comprehensive solution to the deepfake detection challenge, combining:
- **Advanced AI**: Multiple detection models with ensemble fusion
- **Transparency**: Explainable AI for trust and understanding
- **Provenance**: C2PA verification for content authenticity
- **Protection**: MMHI adversarial perturbations
- **Intelligence**: LLM-powered agentic analysis
- **Accessibility**: Web, extension, and chat integrations

The system is designed for scalability, modularity, and real-world deployment across multiple platforms and use cases.

---

**Built with 🍌 by the AntiBanana Team**

*Last Updated: November 2025*
*Version: 1.0.0*
*Status: Production Ready*
