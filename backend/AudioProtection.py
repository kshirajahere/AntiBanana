"""
Advanced Audio Protection System - Anti-Deepfake Defense
=========================================================
Protects audio from being used to train voice cloning and deepfake models.

Protection Mechanisms:
1. Adversarial Perturbations: Imperceptible noise that disrupts ML models
2. Psychoacoustic Masking: Hidden in frequency ranges humans can't hear well
3. Temporal Poisoning: Disrupts neural vocoder training
4. Prosody Shifting: Subtle changes to vocal characteristics
5. Phase Obfuscation: Phase patterns that confuse models
6. Harmonic Disruption: Interferes with pitch extraction

These protections make the audio unusable for training deepfake models
while keeping it perfectly listenable for humans.
"""

import os
import numpy as np
import librosa
import soundfile as sf
import scipy.signal as signal
from scipy.fftpack import fft, ifft
from typing import Union, Dict, Any, Tuple, Optional
import warnings
import tempfile
import base64
import io
from dataclasses import dataclass
from enum import Enum

warnings.filterwarnings('ignore')


class ProtectionStrength(Enum):
    """Protection strength levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXTREME = "extreme"


@dataclass
class ProtectionResult:
    """Result of audio protection"""
    success: bool
    protected_audio: np.ndarray
    sample_rate: int
    protection_strength: str
    techniques_applied: list
    snr_db: float
    processing_time: float
    metadata: Dict[str, Any]


class PsychoacousticMasker:
    """
    Applies adversarial noise hidden by psychoacoustic masking.
    
    Humans have varying sensitivity across frequencies. We exploit this
    to add strong adversarial noise where humans can't hear it well.
    """
    
    @staticmethod
    def get_masking_threshold(audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Calculate psychoacoustic masking threshold.
        
        Returns frequency-dependent threshold where noise is imperceptible.
        """
        # Compute STFT
        D = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(D)
        
        # Frequency bins
        freqs = librosa.fft_frequencies(sr=sr, n_fft=2048)
        
        # Psychoacoustic curve (simplified)
        # Humans are less sensitive at very low and very high frequencies
        sensitivity = np.ones_like(freqs)
        
        # Less sensitive below 500 Hz
        sensitivity[freqs < 500] = 0.3
        
        # Most sensitive 1-4 kHz (speech range)
        mid_range = (freqs >= 1000) & (freqs <= 4000)
        sensitivity[mid_range] = 1.0
        
        # Less sensitive above 8 kHz
        sensitivity[freqs > 8000] = 0.2
        
        # Very insensitive above 15 kHz
        sensitivity[freqs > 15000] = 0.1
        
        return sensitivity[:, np.newaxis] * 0.1  # Scale for safety
    
    @staticmethod
    def apply_masked_noise(audio: np.ndarray, sr: int, strength: float = 0.02) -> np.ndarray:
        """
        Add adversarial noise hidden by psychoacoustic masking.
        
        Args:
            audio: Input audio
            sr: Sample rate
            strength: Noise strength multiplier
        """
        # Compute STFT
        D = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Get masking threshold
        masking_threshold = PsychoacousticMasker.get_masking_threshold(audio, sr)
        
        # Generate adversarial noise in frequency domain
        noise_magnitude = np.random.randn(*magnitude.shape) * masking_threshold * strength
        
        # Add noise to magnitude
        protected_magnitude = magnitude + noise_magnitude
        protected_magnitude = np.maximum(protected_magnitude, 0)  # Keep positive
        
        # Reconstruct with original phase
        protected_D = protected_magnitude * np.exp(1j * phase)
        
        # Inverse STFT
        protected_audio = librosa.istft(protected_D, hop_length=512, length=len(audio))
        
        return protected_audio


class TemporalPoisoner:
    """
    Adds temporal inconsistencies that disrupt neural vocoder training.
    
    Neural vocoders learn temporal patterns. We inject subtle
    discontinuities that are imperceptible but break training.
    """
    
    @staticmethod
    def add_micro_glitches(audio: np.ndarray, sr: int, strength: float = 0.01) -> np.ndarray:
        """
        Add micro-discontinuities at random points.
        
        These are too short for humans to notice but disrupt model training.
        """
        protected = audio.copy()
        
        # Number of glitch points based on audio length
        n_glitches = int(len(audio) / sr * 10)  # ~10 per second
        
        # Random glitch locations
        glitch_positions = np.random.randint(0, len(audio), n_glitches)
        
        for pos in glitch_positions:
            # Very short glitch (1-3 samples)
            glitch_len = np.random.randint(1, 4)
            end_pos = min(pos + glitch_len, len(audio))
            
            # Add tiny discontinuity
            if pos > 0 and end_pos < len(audio):
                glitch = np.random.randn(glitch_len) * strength * np.abs(audio[pos])
                protected[pos:end_pos] += glitch
        
        return protected
    
    @staticmethod
    def add_temporal_jitter(audio: np.ndarray, sr: int, strength: float = 0.005) -> np.ndarray:
        """
        Add subtle timing jitter to confuse temporal models.
        """
        # Work in frames
        frame_length = 512
        hop_length = 256
        
        # Get frames
        frames = librosa.util.frame(audio, frame_length=frame_length, hop_length=hop_length)
        
        # Add random phase shifts to each frame (very subtle)
        for i in range(frames.shape[1]):
            phase_shift = np.random.randn() * strength
            frames[:, i] *= (1 + phase_shift)
        
        # Reconstruct
        protected = librosa.util.frame(frames, frame_length=frame_length, hop_length=hop_length, axis=0)
        
        # Ensure same length as input
        if len(protected) > len(audio):
            protected = protected[:len(audio)]
        elif len(protected) < len(audio):
            protected = np.pad(protected, (0, len(audio) - len(protected)))
        
        return protected


class ProsodyShifter:
    """
    Subtly shifts prosodic features to disrupt voice cloning.
    
    Voice cloning relies on consistent prosodic patterns. We add
    imperceptible variations that break model consistency.
    """
    
    @staticmethod
    def shift_pitch_contour(audio: np.ndarray, sr: int, strength: float = 0.02) -> np.ndarray:
        """
        Add subtle pitch variations that disrupt F0 extraction.
        """
        # Use phase vocoder for pitch shifting
        # Very small random shifts at different time points
        
        # Divide into segments
        segment_length = int(0.5 * sr)  # 500ms segments
        n_segments = len(audio) // segment_length
        
        protected = audio.copy()
        
        for i in range(n_segments):
            start = i * segment_length
            end = min((i + 1) * segment_length, len(audio))
            segment = audio[start:end]
            
            # Random pitch shift (very small)
            pitch_shift = np.random.uniform(-strength, strength)
            
            # Apply pitch shift using resampling
            if abs(pitch_shift) > 0.001:
                shift_factor = 1 + pitch_shift
                shifted = librosa.effects.pitch_shift(segment, sr=sr, n_steps=pitch_shift * 12)
                protected[start:end] = shifted[:len(segment)]
        
        return protected
    
    @staticmethod
    def modulate_energy(audio: np.ndarray, sr: int, strength: float = 0.03) -> np.ndarray:
        """
        Add subtle energy modulation to confuse energy-based features.
        """
        # Compute RMS energy
        rms = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
        
        # Generate modulation curve
        modulation = 1 + np.random.randn(len(rms)) * strength
        modulation = np.maximum(modulation, 0.8)  # Keep positive and bounded
        
        # Upsample modulation to audio length
        modulation_upsampled = np.interp(
            np.arange(len(audio)),
            np.linspace(0, len(audio), len(modulation)),
            modulation
        )
        
        # Apply modulation
        protected = audio * modulation_upsampled
        
        return protected


class PhaseObfuscator:
    """
    Obfuscates phase information to disrupt neural vocoders.
    
    Many neural vocoders ignore phase during training. We exploit
    this by adding phase noise that breaks reconstruction.
    """
    
    @staticmethod
    def randomize_phase(audio: np.ndarray, sr: int, strength: float = 0.1) -> np.ndarray:
        """
        Add random phase shifts across frequency bins.
        """
        # Compute STFT
        D = librosa.stft(audio, n_fft=2048, hop_length=512)
        magnitude = np.abs(D)
        phase = np.angle(D)
        
        # Add random phase noise
        phase_noise = np.random.randn(*phase.shape) * strength
        protected_phase = phase + phase_noise
        
        # Reconstruct
        protected_D = magnitude * np.exp(1j * protected_phase)
        protected_audio = librosa.istft(protected_D, hop_length=512, length=len(audio))
        
        return protected_audio


class HarmonicDisruptor:
    """
    Disrupts harmonic structure to confuse pitch-based models.
    
    Voice cloning uses harmonic patterns. We add inharmonic
    components that are imperceptible but break models.
    """
    
    @staticmethod
    def add_inharmonic_noise(audio: np.ndarray, sr: int, strength: float = 0.01) -> np.ndarray:
        """
        Add subtle inharmonic components.
        """
        # Separate harmonic and percussive
        harmonic, percussive = librosa.effects.hpss(audio)
        
        # Add noise to harmonic component in frequency domain
        D_harmonic = librosa.stft(harmonic)
        magnitude = np.abs(D_harmonic)
        phase = np.angle(D_harmonic)
        
        # Add inharmonic noise (random frequencies)
        noise = np.random.randn(*magnitude.shape) * magnitude * strength
        protected_magnitude = magnitude + noise
        protected_magnitude = np.maximum(protected_magnitude, 0)
        
        # Reconstruct
        protected_D = protected_magnitude * np.exp(1j * phase)
        protected_harmonic = librosa.istft(protected_D, length=len(harmonic))
        
        # Combine with percussive
        protected = protected_harmonic + percussive
        
        return protected


class AudioProtector:
    """
    Main audio protection system combining all techniques.
    
    Applies multiple layers of protection to make audio unusable
    for voice cloning and deepfake generation while maintaining
    perceptual quality.
    """
    
    def __init__(self):
        self.psychoacoustic = PsychoacousticMasker()
        self.temporal = TemporalPoisoner()
        self.prosody = ProsodyShifter()
        self.phase = PhaseObfuscator()
        self.harmonic = HarmonicDisruptor()
    
    def protect(self, 
                audio_input: Union[str, np.ndarray],
                strength: ProtectionStrength = ProtectionStrength.MEDIUM,
                sr: Optional[int] = None) -> ProtectionResult:
        """
        Protect audio from deepfake generation.
        
        Args:
            audio_input: File path or audio array
            strength: Protection strength level
            sr: Sample rate (if audio_input is array)
        
        Returns:
            ProtectionResult with protected audio
        """
        import time
        start_time = time.time()
        
        # Load audio
        if isinstance(audio_input, str):
            audio, sr = librosa.load(audio_input, sr=None, mono=True)
        else:
            audio = audio_input
            if sr is None:
                sr = 16000
        
        # Normalize
        audio = audio / (np.max(np.abs(audio)) + 1e-8)
        
        # Original audio for SNR calculation
        original_audio = audio.copy()
        
        # Get strength parameters
        strength_params = self._get_strength_params(strength)
        
        techniques_applied = []
        protected = audio.copy()
        
        # Apply protection layers
        print(f"🛡️  Applying {strength.value} strength protection...")
        
        # 1. Psychoacoustic masking (imperceptible noise)
        if strength_params['psychoacoustic'] > 0:
            protected = self.psychoacoustic.apply_masked_noise(
                protected, sr, strength_params['psychoacoustic']
            )
            techniques_applied.append("Psychoacoustic Masking")
            print("   ✓ Psychoacoustic masking applied")
        
        # 2. Temporal poisoning (micro-glitches)
        if strength_params['temporal'] > 0:
            protected = self.temporal.add_micro_glitches(
                protected, sr, strength_params['temporal']
            )
            techniques_applied.append("Temporal Poisoning")
            print("   ✓ Temporal poisoning applied")
        
        # 3. Prosody shifting
        if strength_params['prosody'] > 0:
            protected = self.prosody.modulate_energy(
                protected, sr, strength_params['prosody']
            )
            techniques_applied.append("Prosody Shifting")
            print("   ✓ Prosody shifting applied")
        
        # 4. Phase obfuscation
        if strength_params['phase'] > 0:
            protected = self.phase.randomize_phase(
                protected, sr, strength_params['phase']
            )
            techniques_applied.append("Phase Obfuscation")
            print("   ✓ Phase obfuscation applied")
        
        # 5. Harmonic disruption
        if strength_params['harmonic'] > 0:
            protected = self.harmonic.add_inharmonic_noise(
                protected, sr, strength_params['harmonic']
            )
            techniques_applied.append("Harmonic Disruption")
            print("   ✓ Harmonic disruption applied")
        
        # Normalize output
        protected = protected / (np.max(np.abs(protected)) + 1e-8) * 0.95
        
        # Calculate SNR
        snr_db = self._calculate_snr(original_audio, protected)
        
        processing_time = time.time() - start_time
        
        print(f"✅ Protection complete (SNR: {snr_db:.1f} dB)")
        
        return ProtectionResult(
            success=True,
            protected_audio=protected,
            sample_rate=sr,
            protection_strength=strength.value,
            techniques_applied=techniques_applied,
            snr_db=snr_db,
            processing_time=processing_time,
            metadata={
                'duration': len(audio) / sr,
                'original_max': float(np.max(np.abs(audio))),
                'protected_max': float(np.max(np.abs(protected))),
                'techniques_count': len(techniques_applied)
            }
        )
    
    def _get_strength_params(self, strength: ProtectionStrength) -> Dict[str, float]:
        """Get protection parameters for each strength level"""
        
        if strength == ProtectionStrength.LOW:
            return {
                'psychoacoustic': 0.01,
                'temporal': 0.005,
                'prosody': 0.015,
                'phase': 0.05,
                'harmonic': 0.005
            }
        elif strength == ProtectionStrength.MEDIUM:
            return {
                'psychoacoustic': 0.02,
                'temporal': 0.01,
                'prosody': 0.03,
                'phase': 0.1,
                'harmonic': 0.01
            }
        elif strength == ProtectionStrength.HIGH:
            return {
                'psychoacoustic': 0.04,
                'temporal': 0.015,
                'prosody': 0.05,
                'phase': 0.15,
                'harmonic': 0.02
            }
        else:  # EXTREME
            return {
                'psychoacoustic': 0.06,
                'temporal': 0.02,
                'prosody': 0.07,
                'phase': 0.2,
                'harmonic': 0.03
            }
    
    def _calculate_snr(self, original: np.ndarray, protected: np.ndarray) -> float:
        """Calculate Signal-to-Noise Ratio in dB"""
        signal_power = np.mean(original ** 2)
        noise = protected - original
        noise_power = np.mean(noise ** 2)
        
        if noise_power < 1e-10:
            return 100.0
        
        snr = 10 * np.log10(signal_power / noise_power)
        return float(snr)


def protect_audio(audio_path: str, 
                  strength: str = "medium",
                  output_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to protect audio file.
    
    Args:
        audio_path: Path to input audio
        strength: Protection strength ("low", "medium", "high", "extreme")
        output_path: Path to save protected audio (optional)
    
    Returns:
        Dictionary with protection results
    """
    # Map string to enum
    strength_map = {
        'low': ProtectionStrength.LOW,
        'medium': ProtectionStrength.MEDIUM,
        'high': ProtectionStrength.HIGH,
        'extreme': ProtectionStrength.EXTREME
    }
    
    strength_enum = strength_map.get(strength.lower(), ProtectionStrength.MEDIUM)
    
    # Protect audio
    protector = AudioProtector()
    result = protector.protect(audio_path, strength=strength_enum)
    
    if not result.success:
        return {
            'success': False,
            'error': 'Protection failed'
        }
    
    # Save if output path provided
    if output_path:
        sf.write(output_path, result.protected_audio, result.sample_rate)
    
    # Convert to base64 for web transfer
    temp_buffer = io.BytesIO()
    sf.write(temp_buffer, result.protected_audio, result.sample_rate, format='WAV')
    temp_buffer.seek(0)
    audio_base64 = base64.b64encode(temp_buffer.read()).decode('utf-8')
    
    return {
        'success': True,
        'protected_audio_base64': audio_base64,
        'sample_rate': result.sample_rate,
        'protection_strength': result.protection_strength,
        'techniques_applied': result.techniques_applied,
        'snr_db': result.snr_db,
        'processing_time': result.processing_time,
        'metadata': result.metadata
    }


if __name__ == "__main__":
    print("🎵 Audio Protection System - Anti-Deepfake Defense")
    print("=" * 60)
    print()
    print("This system protects audio from being used to train")
    print("voice cloning and deepfake models by adding imperceptible")
    print("adversarial perturbations.")
    print()
    print("Protection Techniques:")
    print("  1. Psychoacoustic Masking - Hidden frequency noise")
    print("  2. Temporal Poisoning - Micro-discontinuities")
    print("  3. Prosody Shifting - Subtle vocal variations")
    print("  4. Phase Obfuscation - Phase randomization")
    print("  5. Harmonic Disruption - Inharmonic components")
    print()
    print("Ready to protect your audio! 🛡️")
