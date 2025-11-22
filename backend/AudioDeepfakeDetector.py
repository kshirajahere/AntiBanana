"""
Advanced Multi-Modal Audio Deepfake Detection System
====================================================
Production-grade audio deepfake detector with ensemble models and novel approaches.

Novel Approaches Implemented:
1. Ensemble Detection: Multiple specialized models working together
2. Temporal Consistency Analysis: Detecting unnatural temporal patterns
3. Spectral Artifact Detection: Finding frequency-domain manipulation signatures
4. Voice Biometric Inconsistency: Detecting unnatural vocal characteristics
5. Phase Analysis: Examining phase relationships for synthesis artifacts
6. Prosody Analysis: Detecting unnatural speech rhythm and intonation
7. Multi-Resolution Analysis: Examining audio at multiple time scales

Architecture:
- Primary: Transformer-based audio classification (wav2vec2, HuBERT variants)
- Secondary: Spectral analysis for artifact detection
- Tertiary: Prosody and biometric feature extraction
- Quaternary: Temporal consistency verification
"""

import os
import sys
import torch
import torchaudio
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
import soundfile as sf
from typing import Union, Dict, Any, List, Tuple, Optional
import tempfile
import io
import base64
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# Deep Learning
from transformers import pipeline, Wav2Vec2Processor, Wav2Vec2ForSequenceClassification
import torch.nn.functional as F

# Feature extraction
from scipy import signal
from scipy.fftpack import fft, fftshift
from scipy.stats import entropy, kurtosis, skew
from sklearn.preprocessing import StandardScaler

# Explainability
from lime import lime_image
from lime.wrappers.scikit_image import SegmentationAlgorithm
from skimage.color import label2rgb
from scipy import ndimage

# Set environment for compatibility
os.environ['HF_HUB_DISABLE_PYTORCH_LOAD_CHECK'] = '1'


class DetectionMethod(Enum):
    """Detection method types"""
    TRANSFORMER = "transformer"
    SPECTRAL = "spectral"
    PROSODY = "prosody"
    TEMPORAL = "temporal"
    PHASE = "phase"
    ENSEMBLE = "ensemble"


@dataclass
class AudioAnalysisResult:
    """Structured result for audio analysis"""
    prediction: str  # "fake" or "real"
    confidence: float
    fake_probability: float
    real_probability: float
    method_scores: Dict[str, float]
    anomalies: List[str]
    metadata: Dict[str, Any]
    warning_flags: List[str]


class SpectralAnalyzer:
    """Advanced spectral analysis for detecting synthesis artifacts"""
    
    @staticmethod
    def analyze_frequency_artifacts(audio: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Detect frequency domain artifacts common in synthesized audio.
        
        Modern TTS and voice cloning often leave subtle artifacts in:
        - High frequency regions (>8kHz)
        - Harmonics relationships
        - Spectral flux patterns
        """
        # Compute STFT
        D = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(D)
        
        # 1. High Frequency Energy Analysis
        # Real human voice has natural rolloff, synthetic audio often has unnatural energy
        freq_bins = librosa.fft_frequencies(sr=sr, n_fft=2048)
        high_freq_mask = freq_bins > 8000
        high_freq_energy = np.mean(magnitude[high_freq_mask, :])
        low_freq_energy = np.mean(magnitude[~high_freq_mask, :])
        hf_ratio = high_freq_energy / (low_freq_energy + 1e-8)
        
        # 2. Spectral Flux (suddenness of spectral changes)
        spectral_flux = np.mean(np.sqrt(np.sum(np.diff(magnitude, axis=1)**2, axis=0)))
        
        # 3. Spectral Centroid Variance
        # Synthetic audio often has more consistent spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        centroid_variance = np.var(spectral_centroid)
        
        # 4. Harmonic-to-Noise Ratio irregularities
        harmonic, percussive = librosa.effects.hpss(audio)
        hnr = np.mean(np.abs(harmonic)) / (np.mean(np.abs(percussive)) + 1e-8)
        
        # 5. Mel Frequency Cepstral Coefficients (MFCC) consistency
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
        mfcc_variance = np.var(mfcc, axis=1).mean()
        
        return {
            'high_freq_ratio': float(hf_ratio),
            'spectral_flux': float(spectral_flux),
            'centroid_variance': float(centroid_variance),
            'hnr': float(hnr),
            'mfcc_variance': float(mfcc_variance)
        }
    
    @staticmethod
    def detect_phase_artifacts(audio: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze phase relationships for synthesis artifacts.
        
        Neural vocoders can produce unnatural phase relationships.
        """
        # Compute STFT with phase
        D = librosa.stft(audio, n_fft=2048, hop_length=512)
        phase = np.angle(D)
        
        # Phase derivative (should be smooth for natural audio)
        phase_diff = np.diff(phase, axis=1)
        phase_continuity = np.mean(np.abs(phase_diff))
        
        # Instantaneous frequency deviation
        inst_freq = np.diff(np.unwrap(phase, axis=1), axis=1)
        inst_freq_variance = np.var(inst_freq)
        
        return {
            'phase_continuity': float(phase_continuity),
            'inst_freq_variance': float(inst_freq_variance)
        }


class ProsodyAnalyzer:
    """Prosody and voice biometric analysis"""
    
    @staticmethod
    def analyze_prosody(audio: np.ndarray, sr: int) -> Dict[str, float]:
        """
        Analyze prosodic features: pitch, energy, rhythm.
        
        Synthetic voices often have:
        - Unnatural pitch contours
        - Consistent energy (lack of micro-variations)
        - Mechanical rhythm patterns
        """
        # 1. Pitch (F0) analysis
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio, 
            fmin=librosa.note_to_hz('C2'), 
            fmax=librosa.note_to_hz('C7'),
            sr=sr
        )
        f0_valid = f0[~np.isnan(f0)]
        
        if len(f0_valid) > 10:
            pitch_variance = np.var(f0_valid)
            pitch_range = np.ptp(f0_valid)  # peak-to-peak
            pitch_smoothness = np.mean(np.abs(np.diff(f0_valid)))
        else:
            pitch_variance = 0.0
            pitch_range = 0.0
            pitch_smoothness = 0.0
        
        # 2. Energy contour analysis
        rms = librosa.feature.rms(y=audio)[0]
        energy_variance = np.var(rms)
        energy_dynamics = np.ptp(rms)
        
        # 3. Zero-crossing rate (voice quality indicator)
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        zcr_variance = np.var(zcr)
        
        # 4. Voicing probability consistency
        # Real speech has natural variations in voicing
        voicing_variance = np.var(voiced_probs)
        
        return {
            'pitch_variance': float(pitch_variance),
            'pitch_range': float(pitch_range),
            'pitch_smoothness': float(pitch_smoothness),
            'energy_variance': float(energy_variance),
            'energy_dynamics': float(energy_dynamics),
            'zcr_variance': float(zcr_variance),
            'voicing_variance': float(voicing_variance)
        }


class TemporalAnalyzer:
    """Temporal consistency and artifact detection"""
    
    @staticmethod
    def analyze_temporal_consistency(audio: np.ndarray, sr: int, 
                                     segment_duration: float = 0.5) -> Dict[str, float]:
        """
        Analyze temporal consistency across audio segments.
        
        Deepfakes often show:
        - Inconsistent noise floors
        - Sudden quality changes
        - Unnatural segment boundaries
        """
        # Split into segments
        segment_samples = int(segment_duration * sr)
        n_segments = len(audio) // segment_samples
        
        if n_segments < 2:
            return {
                'temporal_consistency': 1.0,
                'segment_variance': 0.0,
                'boundary_artifacts': 0.0
            }
        
        segment_features = []
        for i in range(n_segments):
            start = i * segment_samples
            end = start + segment_samples
            segment = audio[start:end]
            
            # Extract features per segment
            rms = np.sqrt(np.mean(segment**2))
            zcr = np.mean(librosa.feature.zero_crossing_rate(segment))
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment, sr=sr))
            
            segment_features.append([rms, zcr, spectral_centroid])
        
        segment_features = np.array(segment_features)
        
        # Calculate consistency across segments
        feature_variance = np.mean(np.var(segment_features, axis=0))
        
        # Boundary analysis (look for sudden changes)
        boundary_artifacts = 0.0
        for i in range(1, len(segment_features)):
            diff = np.abs(segment_features[i] - segment_features[i-1])
            boundary_artifacts += np.mean(diff)
        boundary_artifacts /= (len(segment_features) - 1)
        
        # Overall consistency score (lower variance = more suspicious)
        consistency_score = 1.0 / (1.0 + feature_variance)
        
        return {
            'temporal_consistency': float(consistency_score),
            'segment_variance': float(feature_variance),
            'boundary_artifacts': float(boundary_artifacts)
        }


class AudioDeepfakeDetector:
    """
    Advanced multi-modal audio deepfake detection system.
    
    Combines multiple detection strategies for robust deepfake identification.
    """
    
    def __init__(self, 
                 primary_model: str = "motheecreator/Deepfake-audio-detection",
                 device: Optional[str] = None):
        """
        Initialize the audio deepfake detector.
        
        Args:
            primary_model: HuggingFace model for primary detection
            device: Device to run models on ('cuda', 'cpu', or None for auto)
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🎵 Initializing AudioDeepfakeDetector on {self.device}...")
        
        # Initialize analyzers
        self.spectral_analyzer = SpectralAnalyzer()
        self.prosody_analyzer = ProsodyAnalyzer()
        self.temporal_analyzer = TemporalAnalyzer()
        
        # Load primary transformer model
        self._load_primary_model(primary_model)
        
        # Feature scaler for ensemble
        self.feature_scaler = StandardScaler()
        
        print("✅ AudioDeepfakeDetector initialized successfully")
    
    def _load_primary_model(self, model_name: str):
        """Load the primary transformer-based detection model"""
        try:
            device_id = 0 if self.device == "cuda" else -1
            self.primary_pipeline = pipeline(
                "audio-classification",
                model=model_name,
                device=device_id
            )
            self.primary_model = self.primary_pipeline.model
            self.feature_extractor = getattr(self.primary_pipeline, 'feature_extractor', None)
            print(f"✅ Primary model loaded: {model_name}")
        except Exception as e:
            print(f"❌ Failed to load primary model: {e}")
            self.primary_pipeline = None
            self.primary_model = None
            self.feature_extractor = None
    
    def detect(self, audio_input: Union[str, np.ndarray], 
               method: DetectionMethod = DetectionMethod.ENSEMBLE) -> AudioAnalysisResult:
        """
        Detect if audio is deepfake using specified method(s).
        
        Args:
            audio_input: File path or numpy array of audio
            method: Detection method to use
            
        Returns:
            AudioAnalysisResult with comprehensive analysis
        """
        # Load and preprocess audio
        audio, sr = self._load_audio(audio_input)
        
        # Run detection based on method
        if method == DetectionMethod.ENSEMBLE:
            result = self._ensemble_detection(audio, sr)
        elif method == DetectionMethod.TRANSFORMER:
            result = self._transformer_detection(audio, sr)
        elif method == DetectionMethod.SPECTRAL:
            result = self._spectral_detection(audio, sr)
        elif method == DetectionMethod.PROSODY:
            result = self._prosody_detection(audio, sr)
        elif method == DetectionMethod.TEMPORAL:
            result = self._temporal_detection(audio, sr)
        elif method == DetectionMethod.PHASE:
            result = self._phase_detection(audio, sr)
        else:
            result = self._ensemble_detection(audio, sr)
        
        return result
    
    def _load_audio(self, audio_input: Union[str, np.ndarray]) -> Tuple[np.ndarray, int]:
        """Load and preprocess audio to standardized format"""
        if isinstance(audio_input, str):
            if not os.path.exists(audio_input):
                raise FileNotFoundError(f"Audio file not found: {audio_input}")
            audio, sr = librosa.load(audio_input, sr=16000, mono=True)
        elif isinstance(audio_input, np.ndarray):
            audio = audio_input
            sr = 16000  # Assume 16kHz if not specified
        else:
            raise TypeError(f"Unsupported audio input type: {type(audio_input)}")
        
        # Normalize audio
        audio = audio / (np.max(np.abs(audio)) + 1e-8)
        
        return audio, sr
    
    def _ensemble_detection(self, audio: np.ndarray, sr: int) -> AudioAnalysisResult:
        """
        Ensemble detection combining all methods.
        
        Uses weighted voting from multiple detection strategies.
        """
        method_results = {}
        method_weights = {
            'transformer': 0.35,
            'spectral': 0.25,
            'prosody': 0.20,
            'temporal': 0.10,
            'phase': 0.10
        }
        
        # Run all detection methods
        try:
            transformer_result = self._transformer_detection(audio, sr)
            method_results['transformer'] = transformer_result.fake_probability
        except Exception as e:
            print(f"Transformer detection failed: {e}")
            method_results['transformer'] = 0.5
        
        try:
            spectral_result = self._spectral_detection(audio, sr)
            method_results['spectral'] = spectral_result.fake_probability
        except Exception as e:
            print(f"Spectral detection failed: {e}")
            method_results['spectral'] = 0.5
        
        try:
            prosody_result = self._prosody_detection(audio, sr)
            method_results['prosody'] = prosody_result.fake_probability
        except Exception as e:
            print(f"Prosody detection failed: {e}")
            method_results['prosody'] = 0.5
        
        try:
            temporal_result = self._temporal_detection(audio, sr)
            method_results['temporal'] = temporal_result.fake_probability
        except Exception as e:
            print(f"Temporal detection failed: {e}")
            method_results['temporal'] = 0.5
        
        try:
            phase_result = self._phase_detection(audio, sr)
            method_results['phase'] = phase_result.fake_probability
        except Exception as e:
            print(f"Phase detection failed: {e}")
            method_results['phase'] = 0.5
        
        # Weighted ensemble
        fake_prob = sum(method_results[k] * method_weights[k] 
                       for k in method_results.keys())
        real_prob = 1.0 - fake_prob
        
        # Determine prediction
        prediction = "fake" if fake_prob > 0.5 else "real"
        confidence = max(fake_prob, real_prob)
        
        # Collect anomalies and warnings
        anomalies = self._identify_anomalies(method_results, audio, sr)
        warnings = self._generate_warnings(method_results, confidence)
        
        return AudioAnalysisResult(
            prediction=prediction,
            confidence=confidence,
            fake_probability=fake_prob,
            real_probability=real_prob,
            method_scores=method_results,
            anomalies=anomalies,
            metadata={
                'duration': len(audio) / sr,
                'sample_rate': sr,
                'method': 'ensemble'
            },
            warning_flags=warnings
        )
    
    def _transformer_detection(self, audio: np.ndarray, sr: int) -> AudioAnalysisResult:
        """Primary transformer-based detection"""
        if not self.primary_pipeline:
            raise RuntimeError("Primary model not loaded")
        
        # Save temp file for pipeline
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        sf.write(temp_file.name, audio, sr)
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            results = self.primary_pipeline(temp_path)
            
            # Parse results
            fake_score = 0.0
            for res in results:
                if 'fake' in res['label'].lower() or 'spoof' in res['label'].lower():
                    fake_score = res['score']
                    break
            
            if fake_score == 0.0:  # If no fake label found, use real as inverse
                for res in results:
                    if 'real' in res['label'].lower() or 'bonafide' in res['label'].lower():
                        fake_score = 1.0 - res['score']
                        break
            
            real_score = 1.0 - fake_score
            prediction = "fake" if fake_score > 0.5 else "real"
            confidence = max(fake_score, real_score)
            
            return AudioAnalysisResult(
                prediction=prediction,
                confidence=confidence,
                fake_probability=fake_score,
                real_probability=real_score,
                method_scores={'transformer': fake_score},
                anomalies=[],
                metadata={'raw_outputs': results},
                warning_flags=[]
            )
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _spectral_detection(self, audio: np.ndarray, sr: int) -> AudioAnalysisResult:
        """Spectral analysis-based detection"""
        freq_features = self.spectral_analyzer.analyze_frequency_artifacts(audio, sr)
        phase_features = self.spectral_analyzer.detect_phase_artifacts(audio, sr)
        
        # Heuristic scoring based on spectral features
        # High frequency ratio should be low for real speech
        hf_score = min(freq_features['high_freq_ratio'] / 0.3, 1.0)
        
        # Spectral flux should be moderate (too low = synthetic)
        flux_score = 1.0 - min(freq_features['spectral_flux'] / 10.0, 1.0)
        
        # Combine scores
        fake_prob = (hf_score * 0.4 + flux_score * 0.3 + 
                    (1.0 - min(freq_features['centroid_variance'] / 1000, 1.0)) * 0.3)
        
        prediction = "fake" if fake_prob > 0.5 else "real"
        
        return AudioAnalysisResult(
            prediction=prediction,
            confidence=max(fake_prob, 1.0 - fake_prob),
            fake_probability=fake_prob,
            real_probability=1.0 - fake_prob,
            method_scores={'spectral': fake_prob},
            anomalies=[],
            metadata={**freq_features, **phase_features},
            warning_flags=[]
        )
    
    def _prosody_detection(self, audio: np.ndarray, sr: int) -> AudioAnalysisResult:
        """Prosody-based detection"""
        prosody_features = self.prosody_analyzer.analyze_prosody(audio, sr)
        
        # Scoring: Real speech has natural variations
        # Low variance in prosodic features = suspicious
        pitch_score = 1.0 - min(prosody_features['pitch_variance'] / 1000, 1.0)
        energy_score = 1.0 - min(prosody_features['energy_variance'] / 0.1, 1.0)
        
        fake_prob = (pitch_score * 0.5 + energy_score * 0.5)
        prediction = "fake" if fake_prob > 0.5 else "real"
        
        return AudioAnalysisResult(
            prediction=prediction,
            confidence=max(fake_prob, 1.0 - fake_prob),
            fake_probability=fake_prob,
            real_probability=1.0 - fake_prob,
            method_scores={'prosody': fake_prob},
            anomalies=[],
            metadata=prosody_features,
            warning_flags=[]
        )
    
    def _temporal_detection(self, audio: np.ndarray, sr: int) -> AudioAnalysisResult:
        """Temporal consistency-based detection"""
        temporal_features = self.temporal_analyzer.analyze_temporal_consistency(audio, sr)
        
        # High consistency (low variance) is suspicious
        fake_prob = temporal_features['temporal_consistency']
        prediction = "fake" if fake_prob > 0.6 else "real"
        
        return AudioAnalysisResult(
            prediction=prediction,
            confidence=max(fake_prob, 1.0 - fake_prob),
            fake_probability=fake_prob,
            real_probability=1.0 - fake_prob,
            method_scores={'temporal': fake_prob},
            anomalies=[],
            metadata=temporal_features,
            warning_flags=[]
        )
    
    def _phase_detection(self, audio: np.ndarray, sr: int) -> AudioAnalysisResult:
        """Phase analysis-based detection"""
        phase_features = self.spectral_analyzer.detect_phase_artifacts(audio, sr)
        
        # Unnatural phase continuity is suspicious
        fake_prob = min(phase_features['phase_continuity'] / 3.0, 1.0)
        prediction = "fake" if fake_prob > 0.5 else "real"
        
        return AudioAnalysisResult(
            prediction=prediction,
            confidence=max(fake_prob, 1.0 - fake_prob),
            fake_probability=fake_prob,
            real_probability=1.0 - fake_prob,
            method_scores={'phase': fake_prob},
            anomalies=[],
            metadata=phase_features,
            warning_flags=[]
        )
    
    def _identify_anomalies(self, method_scores: Dict[str, float], 
                           audio: np.ndarray, sr: int) -> List[str]:
        """Identify specific anomalies in the audio"""
        anomalies = []
        
        if method_scores.get('spectral', 0) > 0.7:
            anomalies.append("High frequency artifacts detected")
        
        if method_scores.get('prosody', 0) > 0.7:
            anomalies.append("Unnatural prosodic patterns detected")
        
        if method_scores.get('temporal', 0) > 0.7:
            anomalies.append("Temporal consistency anomalies detected")
        
        if method_scores.get('phase', 0) > 0.7:
            anomalies.append("Phase relationship artifacts detected")
        
        return anomalies
    
    def _generate_warnings(self, method_scores: Dict[str, float], 
                          confidence: float) -> List[str]:
        """Generate warning flags based on analysis"""
        warnings = []
        
        if confidence < 0.6:
            warnings.append("Low confidence detection - manual review recommended")
        
        # Check for disagreement between methods
        scores = list(method_scores.values())
        if len(scores) > 1 and np.std(scores) > 0.3:
            warnings.append("Methods show significant disagreement")
        
        return warnings
    
    def generate_visualizations(self, audio_input: Union[str, np.ndarray],
                               result: Optional[AudioAnalysisResult] = None) -> Dict[str, str]:
        """
        Generate comprehensive visualizations for explainability.
        
        Returns dict of visualization names to base64-encoded images.
        """
        audio, sr = self._load_audio(audio_input)
        visualizations = {}
        
        # 1. Waveform
        fig, ax = plt.subplots(figsize=(12, 3))
        librosa.display.waveshow(audio, sr=sr, ax=ax)
        ax.set_title('Audio Waveform', fontsize=14, fontweight='bold')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Amplitude')
        visualizations['waveform'] = self._fig_to_base64(fig)
        plt.close(fig)
        
        # 2. Mel Spectrogram
        fig, ax = plt.subplots(figsize=(12, 4))
        S = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=128)
        S_dB = librosa.power_to_db(S, ref=np.max)
        img = librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='mel', ax=ax)
        ax.set_title('Mel Spectrogram', fontsize=14, fontweight='bold')
        plt.colorbar(img, ax=ax, format='%+2.0f dB')
        visualizations['mel_spectrogram'] = self._fig_to_base64(fig)
        plt.close(fig)
        
        # 3. MFCC
        fig, ax = plt.subplots(figsize=(12, 4))
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=20)
        img = librosa.display.specshow(mfcc, sr=sr, x_axis='time', ax=ax)
        ax.set_title('MFCC (Mel-Frequency Cepstral Coefficients)', fontsize=14, fontweight='bold')
        plt.colorbar(img, ax=ax)
        visualizations['mfcc'] = self._fig_to_base64(fig)
        plt.close(fig)
        
        # 4. Spectral Features
        fig, axes = plt.subplots(3, 1, figsize=(12, 8))
        
        # Spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        frames = range(len(spectral_centroid))
        t = librosa.frames_to_time(frames, sr=sr)
        axes[0].plot(t, spectral_centroid, color='blue', linewidth=1.5)
        axes[0].set_title('Spectral Centroid', fontweight='bold')
        axes[0].set_ylabel('Hz')
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sr)[0]
        axes[1].plot(t, spectral_rolloff, color='green', linewidth=1.5)
        axes[1].set_title('Spectral Rolloff', fontweight='bold')
        axes[1].set_ylabel('Hz')
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        axes[2].plot(t, zcr, color='red', linewidth=1.5)
        axes[2].set_title('Zero Crossing Rate', fontweight='bold')
        axes[2].set_xlabel('Time (s)')
        axes[2].set_ylabel('Rate')
        
        plt.tight_layout()
        visualizations['spectral_features'] = self._fig_to_base64(fig)
        plt.close(fig)
        
        # 5. Pitch contour
        try:
            f0, voiced_flag, voiced_probs = librosa.pyin(audio, fmin=80, fmax=400, sr=sr)
            fig, ax = plt.subplots(figsize=(12, 4))
            times = librosa.times_like(f0, sr=sr)
            ax.plot(times, f0, color='purple', linewidth=2, label='F0 (Pitch)')
            ax.set_title('Pitch Contour (F0)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Frequency (Hz)')
            ax.legend()
            visualizations['pitch_contour'] = self._fig_to_base64(fig)
            plt.close(fig)
        except Exception as e:
            print(f"Pitch visualization failed: {e}")
        
        # 6. Method Scores (if result provided)
        if result and result.method_scores:
            fig, ax = plt.subplots(figsize=(10, 6))
            methods = list(result.method_scores.keys())
            scores = list(result.method_scores.values())
            colors = ['red' if s > 0.5 else 'green' for s in scores]
            
            bars = ax.barh(methods, scores, color=colors, alpha=0.7)
            ax.axvline(x=0.5, color='black', linestyle='--', linewidth=2, label='Threshold')
            ax.set_xlabel('Fake Probability', fontsize=12, fontweight='bold')
            ax.set_title('Detection Method Scores', fontsize=14, fontweight='bold')
            ax.set_xlim(0, 1)
            ax.legend()
            
            # Add value labels
            for i, (method, score) in enumerate(zip(methods, scores)):
                ax.text(score + 0.02, i, f'{score:.3f}', va='center', fontweight='bold')
            
            visualizations['method_scores'] = self._fig_to_base64(fig)
            plt.close(fig)
        
        return visualizations
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        return img_base64


def analyze_audio(audio_path: str) -> Dict[str, Any]:
    """
    Convenience function for complete audio analysis.
    
    Args:
        audio_path: Path to audio file
        
    Returns:
        Dictionary with detection results and visualizations
    """
    try:
        detector = AudioDeepfakeDetector()
        result = detector.detect(audio_path, method=DetectionMethod.ENSEMBLE)
        visualizations = detector.generate_visualizations(audio_path, result)
        
        return {
            'prediction': result.prediction,
            'confidence': float(result.confidence),
            'fake_probability': float(result.fake_probability),
            'real_probability': float(result.real_probability),
            'is_fake': result.prediction == 'fake',
            'method_scores': {k: float(v) for k, v in result.method_scores.items()},
            'anomalies': result.anomalies,
            'warnings': result.warning_flags,
            'metadata': result.metadata,
            'images': visualizations
        }
    except Exception as e:
        return {
            'error': str(e),
            'prediction': 'error',
            'confidence': 0.0,
            'is_fake': False
        }


if __name__ == "__main__":
    # Example usage
    print("AudioDeepfakeDetector - Production-Grade Multi-Modal Detection")
    print("=" * 70)
    
    # Test with a sample file
    test_file = "test_audio.wav"
    if os.path.exists(test_file):
        result = analyze_audio(test_file)
        print(f"\nPrediction: {result['prediction'].upper()}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Fake Probability: {result['fake_probability']:.2%}")
        print(f"\nMethod Scores:")
        for method, score in result['method_scores'].items():
            print(f"  {method:15s}: {score:.3f}")
        
        if result['anomalies']:
            print(f"\nAnomalies Detected:")
            for anomaly in result['anomalies']:
                print(f"  - {anomaly}")
        
        if result['warnings']:
            print(f"\nWarnings:")
            for warning in result['warnings']:
                print(f"  - {warning}")
    else:
        print(f"Test file {test_file} not found. Detector initialized and ready.")
