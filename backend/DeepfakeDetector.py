import os
import sys
import numpy as np

# Disable the torch.load security check for transformers
# This allows PyTorch 2.5.1 to work with newer transformers versions
# The models will still use safetensors format when available
os.environ['HF_HUB_DISABLE_PYTORCH_LOAD_CHECK'] = '1'

import torch
from transformers import pipeline
from PIL import Image
import cv2
from scipy.fftpack import fft2, fftshift

class DeepfakeDetector:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading DeepfakeDetector on {self.device}...")
        
        # 1. Face Swap Detection Model (Existing ViT)
        # Good for DeepFaceLab, FaceSwap, etc.
        try:
            self.faceswap_pipe = pipeline(
                "image-classification", 
                model="Wvolf/ViT_Deepfake_Detection", 
                device=self.device
            )
            print("✅ Face Swap Detection Model Loaded")
        except Exception as e:
            print(f"❌ Failed to load Face Swap Model: {e}")
            self.faceswap_pipe = None

        # 2. AI Generation Detection Model
        # Good for Diffusion models (Midjourney, DALL-E, Stable Diffusion, "Nano Banana")
        try:
            self.ai_gen_pipe = pipeline(
                "image-classification", 
                model="umm-maybe/AI-Image-Detector", 
                device=self.device
            )
            print("✅ AI Generation Detection Model Loaded")
        except Exception as e:
            print(f"❌ Failed to load AI Generation Model: {e}")
            self.ai_gen_pipe = None

    def detect_faceswap(self, image):
        """Detects traditional face swapping deepfakes."""
        if not self.faceswap_pipe:
            return {"score": 0.0, "label": "Error"}
        
        try:
            results = self.faceswap_pipe(image)
            # Expected output: [{'label': 'fake', 'score': 0.9}, {'label': 'real', 'score': 0.1}]
            # We want the score for 'fake'
            fake_score = 0.0
            for res in results:
                if res['label'].lower() in ['fake', 'deepfake']:
                    fake_score = res['score']
            return {"score": fake_score, "details": results}
        except Exception as e:
            print(f"Face Swap Detection Error: {e}")
            return {"score": 0.0, "error": str(e)}

    def detect_generation(self, image):
        """Detects AI-generated images (Diffusion/GANs)."""
        if not self.ai_gen_pipe:
            return {"score": 0.0, "label": "Error"}
        
        try:
            results = self.ai_gen_pipe(image)
            # Check labels for this specific model. Usually 'artificial' vs 'human'
            ai_score = 0.0
            for res in results:
                if res['label'].lower() in ['artificial', 'ai', 'fake']:
                    ai_score = res['score']
            return {"score": ai_score, "details": results}
        except Exception as e:
            print(f"AI Generation Detection Error: {e}")
            return {"score": 0.0, "error": str(e)}

    def perform_ela(self, image_path, quality=90):
        """
        Performs Error Level Analysis (ELA).
        Saves the image at a specific quality and compares it to the original.
        High difference indicates potential manipulation (pasted regions).
        """
        try:
            original = Image.open(image_path).convert('RGB')
            
            # Save as temporary JPEG
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                tmp_name = tmp.name
            
            original.save(tmp_name, 'JPEG', quality=quality)
            resaved = Image.open(tmp_name)
            
            # Calculate difference
            ela_image = Image.fromarray(np.abs(np.array(original).astype(float) - np.array(resaved).astype(float)).astype(np.uint8))
            
            # Calculate statistics
            ela_data = np.array(ela_image)
            max_diff = np.max(ela_data)
            mean_diff = np.mean(ela_data)
            
            # Clean up
            try:
                os.remove(tmp_name)
            except:
                pass

            # Heuristic: If there are regions with significantly higher error than background, it's suspicious.
            # A high max_diff with a low mean_diff suggests local editing.
            
            score = 0.0
            # Refined scoring logic
            # Relaxed threshold from 10 back to 20 to reduce false positives on real images
            if max_diff > 20:
                # Normalize score based on intensity of difference
                # 20 -> 0.0
                # 70 -> 1.0 (Steeper curve to catch smaller edits)
                normalized_diff = min((max_diff - 20) / 50.0, 1.0) 
                
                score = normalized_diff
                
                # Penalize if mean difference is high (indicates global compression/noise rather than local edit)
                if mean_diff > 15:
                    score *= 0.2 # Likely just a low quality image
                elif mean_diff > 5:
                    score *= 0.8 # Some global noise
                else:
                    # Clean background with high local diff -> Strong indicator of splicing
                    score += 0.2 
                    score = min(score, 1.0)
            
            return {
                "score": float(score),
                "details": {
                    "max_difference": float(max_diff),
                    "mean_difference": float(mean_diff)
                }
            }
        except Exception as e:
            print(f"ELA Error: {e}")
            return {"score": 0.0, "error": str(e)}

    def analyze_frequency(self, image_path):
        """
        Performs simple Frequency Domain Analysis to detect artifacts.
        Real images tend to have different spectral distributions than GAN/Diffusion images.
        This is a heuristic/statistical measure.
        """
        try:
            img = cv2.imread(image_path, 0) # Read as grayscale
            if img is None:
                return {"score": 0.0, "error": "Could not read image"}

            f = fft2(img)
            fshift = fftshift(f)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)
            
            # Calculate some simple statistics on the spectrum
            # High frequency anomalies often indicate GANs
            mean_freq = np.mean(magnitude_spectrum)
            std_freq = np.std(magnitude_spectrum)
            
            # Heuristic scoring for frequency analysis
            # GANs often have higher frequency artifacts (checkerboard patterns)
            # This is a very rough heuristic and should be calibrated
            score = 0.0
            # Relaxed threshold from 15 to 20
            if std_freq > 20:
                 # 20 -> 0.0, 40 -> 1.0
                 score = min((std_freq - 20) / 20.0, 1.0)
            
            return {
                "score": float(score), 
                "details": {
                    "mean_frequency": float(mean_freq),
                    "std_frequency": float(std_freq)
                }
            }
        except Exception as e:
            print(f"Frequency Analysis Error: {e}")
            return {"score": 0.0, "error": str(e)}

    def detect_texture_inconsistency(self, image_path):
        """
        Analyzes texture patterns across the image to detect splicing/copy-paste.
        Inconsistent texture patterns indicate local edits.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"score": 0.0, "error": "Could not read image"}
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Divide image into 5x5 grid
            h, w = gray.shape
            grid_h, grid_w = h // 5, w // 5
            
            texture_scores = []
            for i in range(5):
                for j in range(5):
                    y1, y2 = i * grid_h, (i + 1) * grid_h
                    x1, x2 = j * grid_w, (j + 1) * grid_w
                    patch = gray[y1:y2, x1:x2]
                    
                    # Calculate local texture using Laplacian variance
                    laplacian = cv2.Laplacian(patch, cv2.CV_64F)
                    variance = laplacian.var()
                    texture_scores.append(variance)
            
            # Calculate coefficient of variation (std/mean)
            # High variation indicates inconsistent textures (splicing)
            mean_texture = np.mean(texture_scores)
            std_texture = np.std(texture_scores)
            
            if mean_texture > 0:
                cv_texture = std_texture / mean_texture
            else:
                cv_texture = 0
            
            # Normalize to 0-1 score
            # High CV (>0.8) indicates inconsistency
            # BUT: Natural images with varied content (landscapes, multiple objects) also have high CV
            # We need to be more conservative
            score = 0.0
            if cv_texture > 1.5:  # Much higher threshold
                score = min((cv_texture - 1.5) / 1.5, 1.0)
            elif cv_texture > 1.2:
                score = (cv_texture - 1.2) / 0.6  # Gentle ramp up
            
            return {
                "score": float(score),
                "details": {
                    "coefficient_of_variation": float(cv_texture),
                    "mean_texture": float(mean_texture),
                    "std_texture": float(std_texture)
                }
            }
        except Exception as e:
            print(f"Texture Analysis Error: {e}")
            return {"score": 0.0, "error": str(e)}
    
    def detect_edge_inconsistency(self, image_path):
        """
        Detects inconsistent edges/boundaries that indicate splicing or object insertion.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"score": 0.0, "error": "Could not read image"}
            
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Divide into grid and check for anomalous edge patterns
            h, w = edges.shape
            grid_h, grid_w = h // 5, w // 5
            
            edge_densities = []
            for i in range(5):
                for j in range(5):
                    y1, y2 = i * grid_h, (i + 1) * grid_h
                    x1, x2 = j * grid_w, (j + 1) * grid_w
                    patch = edges[y1:y2, x1:x2]
                    
                    # Calculate edge density
                    density = np.sum(patch > 0) / (patch.shape[0] * patch.shape[1])
                    edge_densities.append(density)
            
            # High std in edge density suggests spliced regions
            std_density = np.std(edge_densities)
            mean_density = np.mean(edge_densities)
            
            # Score based on variation
            # Natural images can have varied edge density (sky vs ground, smooth vs detailed areas)
            # Only flag if EXTREMELY high variation
            score = 0.0
            if std_density > 0.12:  # Much higher threshold
                score = min((std_density - 0.12) * 5, 1.0)
            
            return {
                "score": float(score),
                "details": {
                    "edge_density_std": float(std_density),
                    "edge_density_mean": float(mean_density)
                }
            }
        except Exception as e:
            print(f"Edge Analysis Error: {e}")
            return {"score": 0.0, "error": str(e)}

    def scan_patches(self, image, grid_size=5):
        """
        Splits the image into a FINER grid and runs detection on each patch.
        Useful for detecting small local edits (clothing, accessories, etc).
        Returns the MAX score found across global image and all patches.
        """
        if not self.ai_gen_pipe:
            return {"score": 0.0, "patches": []}

        # 1. Run Global Detection first
        global_res = self.detect_generation(image)
        max_score = global_res.get('score', 0)
        
        patch_details = []
        patch_details.append({
            "type": "global",
            "score": max_score
        })
        
        patch_scores = [max_score]

        w, h = image.size
        # Use finer grid (5x5 instead of 3x3) for better localization
        if w >= 224 and h >= 224:
            step_x = w // grid_size
            step_y = h // grid_size
            
            for i in range(grid_size):
                for j in range(grid_size):
                    left = i * step_x
                    upper = j * step_y
                    right = left + step_x
                    lower = upper + step_y
                    
                    # Crop
                    patch = image.crop((left, upper, right, lower))
                    
                    # Detect on patch
                    res = self.detect_generation(patch)
                    score = res.get('score', 0)
                    
                    # Don't dampen as much - we want to catch small edits
                    adjusted_score = score
                    if score < 0.9: 
                         adjusted_score = score * 0.85 # Less dampening
                    
                    patch_scores.append(adjusted_score)
                    
                    patch_details.append({
                        "type": "patch",
                        "grid_pos": (i, j),
                        "score": score,
                        "adjusted_score": adjusted_score
                    })
                    
                    if adjusted_score > max_score:
                        max_score = adjusted_score
        
        # Calculate variance in patch scores
        # High variance suggests some patches are more "fake" than others (localized editing)
        patch_variance = np.var(patch_scores) if len(patch_scores) > 1 else 0
        
        # If variance is high and max score is reasonable, boost it
        if patch_variance > 0.02 and max_score > 0.3:
            max_score = min(max_score + 0.1, 1.0)

        return {
            "score": max_score,
            "details": patch_details,
            "patch_variance": float(patch_variance)
        }

    def detect_all(self, image_path):
        """Runs all detection methods and aggregates the result."""
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            return {"error": f"Invalid image path: {e}"}

        faceswap_res = self.detect_faceswap(image)
        
        # Use scan_patches with finer grid instead of simple detect_generation
        aigen_res = self.scan_patches(image, grid_size=5)
        
        freq_res = self.analyze_frequency(image_path)
        ela_res = self.perform_ela(image_path)
        
        # New detection methods for small edits
        texture_res = self.detect_texture_inconsistency(image_path)
        edge_res = self.detect_edge_inconsistency(image_path)

        # Get raw scores
        fs_score = faceswap_res.get('score', 0)
        ai_score = aigen_res.get('score', 0)
        ela_score = ela_res.get('score', 0)
        freq_score = freq_res.get('score', 0)
        texture_score = texture_res.get('score', 0)
        edge_score = edge_res.get('score', 0)
        
        # Get ELA details for more nuanced analysis
        ela_max_diff = ela_res.get('details', {}).get('max_difference', 0)
        ela_mean_diff = ela_res.get('details', {}).get('mean_difference', 0)
        
        # Get frequency details
        freq_std = freq_res.get('details', {}).get('std_frequency', 0)
        
        # Get patch variance (indicates localized editing)
        patch_variance = aigen_res.get('patch_variance', 0)
        
        # === ADVANCED WEIGHTED ENSEMBLE WITH CONFIDENCE CALIBRATION ===
        
        # Weight configuration (based on model reliability)
        # Balanced weights to catch fakes while avoiding false positives
        # "Sweet Spot" Tuning: Slightly reduced AI weight to allow heuristics to contribute more
        W_AI = 0.45      # Primary AI detection model weight
        W_FS = 0.20      # Face swap detection weight
        W_ELA = 0.15     # ELA weight (supporting evidence)
        W_FREQ = 0.10    # Frequency analysis weight (supporting evidence)
        W_TEXTURE = 0.06 # Texture inconsistency weight
        W_EDGE = 0.04    # Edge inconsistency weight
        
        # === Confidence Calibration ===
        # Many models are overconfident. We apply sigmoid calibration to adjust scores.
        
        def calibrate_score(score, temperature=2.0, shift=0.5):
            """
            Apply temperature scaling and shift to calibrate model confidence.
            Higher temperature = more conservative (pushes scores toward 0.5)
            """
            # Logit transform
            epsilon = 1e-7
            score = np.clip(score, epsilon, 1 - epsilon)
            logit = np.log(score / (1 - score))
            
            # Apply temperature and shift
            calibrated_logit = logit / temperature - shift
            
            # Back to probability
            calibrated_score = 1 / (1 + np.exp(-calibrated_logit))
            return float(calibrated_score)
        
        # Calibrate individual scores
        # "Sweet Spot" Tuning: Reduced temperature to 1.3 (from 1.8) to allow high confidence scores to shine
        # Reduced shift to 0.05 (from 0.15) to stop artificially lowering scores
        ai_score_calibrated = calibrate_score(ai_score, temperature=1.3, shift=0.05)
        fs_score_calibrated = calibrate_score(fs_score, temperature=1.3, shift=0.05)
        
        # ELA and Frequency - calibrated thresholds
        # Lowered thresholds to catch subtle edits
        ela_score_calibrated = ela_score if ela_max_diff > 20 else ela_score * 0.7
        freq_score_calibrated = freq_score if freq_std > 18 else freq_score * 0.7
        
        # Texture and edge - calibrated for natural variation
        texture_score_calibrated = texture_score * 0.85 if texture_score < 0.5 else texture_score
        edge_score_calibrated = edge_score * 0.85 if edge_score < 0.5 else edge_score
        
        # === Weighted Ensemble ===
        ensemble_score = (
            W_AI * ai_score_calibrated +
            W_FS * fs_score_calibrated +
            W_ELA * ela_score_calibrated +
            W_FREQ * freq_score_calibrated +
            W_TEXTURE * texture_score_calibrated +
            W_EDGE * edge_score_calibrated
        )
        
        # === Multi-Signal Confirmation ===
        # Detect signals with balanced thresholds
        signal_count = 0
        strong_signals = []
        
        # Lowered signal thresholds to be more sensitive
        if ai_score_calibrated > 0.35:
            signal_count += 1
            strong_signals.append("AI")
        if fs_score_calibrated > 0.35:
            signal_count += 1
            strong_signals.append("FaceSwap")
        if ela_score_calibrated > 0.40 and ela_max_diff > 22:
            signal_count += 1
            strong_signals.append("ELA")
        if freq_score_calibrated > 0.40 and freq_std > 20:
            signal_count += 1
            strong_signals.append("Frequency")
        if texture_score_calibrated > 0.45:
            signal_count += 1
            strong_signals.append("Texture")
        if edge_score_calibrated > 0.45:
            signal_count += 1
            strong_signals.append("Edge")
        if patch_variance > 0.025:
            signal_count += 1
            strong_signals.append("PatchVariance")
        
        # Consensus boost: If 2+ signals agree, increase confidence
        if signal_count >= 2:
            consensus_boost = 0.15 * (signal_count - 1) # Increased boost slightly
            ensemble_score = min(ensemble_score + consensus_boost, 1.0)
        
        # === Anomaly Detection: Check for Outliers ===
        # Relaxed penalties
        if ela_score > 0.7 and ai_score_calibrated < 0.3 and fs_score_calibrated < 0.3:
            ensemble_score *= 0.85 # Was 0.75
        
        if freq_score > 0.8 and ai_score_calibrated < 0.3 and fs_score_calibrated < 0.3:
            ensemble_score *= 0.85 # Was 0.75
        
        # If texture/edge are high but AI models disagree, reduce impact
        if (texture_score > 0.6 or edge_score > 0.6) and ai_score_calibrated < 0.35 and fs_score_calibrated < 0.35:
            ensemble_score *= 0.9 # Was 0.8
        
        # NEW: If AI model is confident it's fake, trust it even if heuristics are low
        if ai_score_calibrated > 0.55 or fs_score_calibrated > 0.55:
            # Boost score - AI models detected something
            ensemble_score = max(ensemble_score, ai_score_calibrated * 0.95, fs_score_calibrated * 0.95)
        
        final_score = float(np.clip(ensemble_score, 0, 1))
        
        # === Dynamic Threshold Based on Confidence ===
        # Balanced threshold that adapts to signal strength
        base_threshold = 0.50 # Lowered from 0.52
        
        # Lower threshold if multiple strong signals detected
        if signal_count >= 3:
            threshold = 0.45  # Lower bar when multiple signals agree
        elif signal_count >= 2:
            threshold = 0.48  # Moderate bar for 2 signals
        else:
            threshold = base_threshold  # Higher bar for single signal
        
        verdict = "Real"
        confidence_level = "Low"
        
        if final_score > threshold:
            verdict = "Fake"
            if final_score > 0.80:
                confidence_level = "High"
            elif final_score > 0.65: # Lowered from 0.70
                confidence_level = "Medium"
            else:
                confidence_level = "Low"
        else:
            verdict = "Real"
            real_confidence = 1 - final_score
            if real_confidence > 0.60:
                confidence_level = "High"
            elif real_confidence > 0.45:
                confidence_level = "Medium"
            else:
                confidence_level = "Low"
        
        # Determine the type of fake
        fake_type = "Unknown"
        if verdict == "Fake":
            if fs_score_calibrated > ai_score_calibrated:
                fake_type = "Face Swap / Deepfake"
            elif ela_score_calibrated > 0.6 and ai_score_calibrated < 0.5:
                fake_type = "Digital Manipulation / Editing"
            else:
                fake_type = "AI Generated (Diffusion/GAN)"

        return {
            "verdict": verdict,
            "confidence": final_score,
            "confidence_level": confidence_level,
            "fake_type": fake_type,
            "breakdown": {
                "faceswap_score": fs_score,
                "ai_generation_score": ai_score,
                "frequency_analysis": freq_res,
                "ela_analysis": ela_res,
                "texture_analysis": texture_res,
                "edge_analysis": edge_res,
                "patch_variance": patch_variance
            },
            "calibrated_scores": {
                "ai_calibrated": ai_score_calibrated,
                "faceswap_calibrated": fs_score_calibrated,
                "ela_calibrated": ela_score_calibrated,
                "freq_calibrated": freq_score_calibrated,
                "texture_calibrated": texture_score_calibrated,
                "edge_calibrated": edge_score_calibrated
            },
            "detection_signals": strong_signals,
            "signal_count": signal_count
        }

# Singleton instance for easy import
# detector = DeepfakeDetector()

