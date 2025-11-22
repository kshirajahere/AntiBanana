# Quick Setup Guide - Audio Detection Refactor

## New Dependencies Added

The refactored audio detection system requires one additional dependency:

```bash
pip install torchaudio
```

Or install all dependencies from requirements.txt:

```bash
cd backend
pip install -r requirements.txt
```

## Installation Steps

### 1. Install Dependencies
```bash
# Navigate to backend
cd backend

# Install all requirements
pip install -r requirements.txt

# Or install only new audio dependencies
pip install torchaudio scipy scikit-image
```

### 2. Verify Installation
```bash
python -c "from AudioDeepfakeDetector import AudioDeepfakeDetector; print('✅ Audio detector ready')"
```

### 3. Run Tests (Optional)
```bash
python test_audio_detector.py
```

### 4. Start Server
```bash
python main.py
```

## Dependency Summary

### Core Audio Processing
- `torchaudio` - PyTorch audio processing (**NEW**)
- `librosa` - Audio feature extraction
- `soundfile` - Audio I/O

### Already Installed (from previous)
- `scipy` - Signal processing
- `scikit-image` - Image processing for visualizations
- `matplotlib` - Plotting
- `transformers` - Transformer models
- `torch` - Deep learning framework

## Troubleshooting

### Issue: torchaudio installation fails

**Solution 1**: Install with pip
```bash
pip install torchaudio
```

**Solution 2**: Install matching torch version
```bash
# Check your torch version
python -c "import torch; print(torch.__version__)"

# Install matching torchaudio (e.g., for torch 2.0.0)
pip install torchaudio==2.0.0
```

**Solution 3**: CPU-only version
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Issue: librosa installation fails

**Solution**: Install with conda (if using conda)
```bash
conda install -c conda-forge librosa
```

Or use pip with wheel:
```bash
pip install librosa --no-cache-dir
```

### Issue: Import error for AudioDeepfakeDetector

**Check 1**: Verify file location
```bash
ls backend/AudioDeepfakeDetector.py
```

**Check 2**: Verify Python can find it
```bash
cd backend
python -c "import AudioDeepfakeDetector"
```

**Check 3**: Check dependencies
```bash
python -c "import torchaudio, librosa, soundfile, scipy; print('All dependencies OK')"
```

## Minimal Installation (Development)

If you only want to test the audio detector without full deployment:

```bash
# Core audio dependencies
pip install torch torchaudio librosa soundfile scipy

# Visualization
pip install matplotlib

# ML models
pip install transformers

# Utilities
pip install numpy scikit-image scikit-learn
```

## Docker Installation (Future)

For containerized deployment (coming soon):

```dockerfile
FROM python:3.10

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

CMD ["python", "main.py"]
```

## Verification Checklist

After installation, verify everything works:

- [ ] `import torchaudio` - No errors
- [ ] `import librosa` - No errors
- [ ] `from AudioDeepfakeDetector import AudioDeepfakeDetector` - No errors
- [ ] `python test_audio_detector.py` - All tests pass
- [ ] `python main.py` - Server starts
- [ ] POST to `/detect-audio` - Returns results

## Quick Test

```bash
cd backend

# Generate test audio
python -c "
import numpy as np
import soundfile as sf
audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 16000))
sf.write('test.wav', audio, 16000)
print('Created test.wav')
"

# Test detection
python -c "
from AudioDeepfakeDetector import analyze_audio
result = analyze_audio('test.wav')
print(f\"Prediction: {result['prediction']}\")
print(f\"Confidence: {result['confidence']:.2%}\")
"

# Clean up
rm test.wav
```

## Platform-Specific Notes

### Windows
- Use PowerShell or Command Prompt
- Paths use backslashes: `backend\AudioDeepfakeDetector.py`
- Use `python` (not `python3`)

### Linux/Mac
- Use Terminal
- Paths use forward slashes: `backend/AudioDeepfakeDetector.py`
- May need `python3` and `pip3`

### Conda Environment
```bash
# Create new environment
conda create -n antibanana python=3.10
conda activate antibanana

# Install PyTorch with conda (recommended)
conda install pytorch torchvision torchaudio -c pytorch

# Install other dependencies
pip install -r requirements.txt
```

## Estimated Installation Time

- **Fast internet**: 2-5 minutes
- **Slow internet**: 10-15 minutes
- **Dependencies size**: ~2-3 GB (PyTorch, torchaudio, transformers)

## Support

If you encounter issues:

1. Check this guide first
2. Verify Python version (3.8-3.11 recommended)
3. Check pip version: `pip --version`
4. Try upgrading pip: `pip install --upgrade pip`
5. Check requirements.txt is up to date

---

**Quick Start**: `pip install torchaudio && python test_audio_detector.py`
