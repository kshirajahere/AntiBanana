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

# Import Explainability Engine for XAI capabilities
from ExplainabilityEngine import ExplainabilityEngine, create_model_wrapper_for_pipeline

# Import C2PA Verifier for content provenance and authenticity
from C2PAVerifier import C2PAVerifier

# Import SynthID Detector for Google's invisible watermark detection
try:
    from SynthIDDetector import SynthIDDetector
except ImportError:
    print("⚠️  SynthIDDetector not available (optional feature)")
    SynthIDDetector = None

class DeepfakeDetector:
    def __init__(self, enable_xai=False):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading DeepfakeDetector on {self.device}...")
        
        # XAI Explainer (lazy loaded)
        self.enable_xai = enable_xai
        self.xai_explainer = None
        
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
        
        # 3. Initialize Explainability Engine for XAI
        try:
            self.explainability_engine = ExplainabilityEngine(device=self.device)
            
            # Create prediction wrappers for LIME/SHAP
            if self.ai_gen_pipe:
                self.ai_gen_predict_fn = create_model_wrapper_for_pipeline(self.ai_gen_pipe)
            else:
                self.ai_gen_predict_fn = None
                
            if self.faceswap_pipe:
                self.faceswap_predict_fn = create_model_wrapper_for_pipeline(self.faceswap_pipe)
            else:
                self.faceswap_predict_fn = None
            
            print("✅ Explainability Engine Initialized (LIME, SHAP, Grad-CAM)")
        except Exception as e:
            print(f"❌ Failed to initialize Explainability Engine: {e}")
            self.explainability_engine = None
            self.ai_gen_predict_fn = None
            self.faceswap_predict_fn = None
        
        # 4. Initialize C2PA Verifier for content provenance
        try:
            self.c2pa_verifier = C2PAVerifier()
            print("✅ C2PA Verifier Initialized (Content Provenance & Chain of Custody)")
        except Exception as e:
            print(f"❌ Failed to initialize C2PA Verifier: {e}")
            self.c2pa_verifier = None
        
        # 5. Initialize SynthID Detector for Google's invisible watermark detection
        try:
            if SynthIDDetector is not None:
                self.synthid_detector = SynthIDDetector()
            else:
                self.synthid_detector = None
        except Exception as e:
            print(f"❌ Failed to initialize SynthID Detector: {e}")
            self.synthid_detector = None

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

    def detect_all(self, image_path, include_c2pa=True):
        """Runs all detection methods and aggregates the result.
        
        Args:
            image_path: Path to the image file
            include_c2pa: Whether to include C2PA provenance analysis
        """
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            return {"error": f"Invalid image path: {e}"}
        
        # C2PA Provenance Check (if enabled)
        c2pa_result = None
        if include_c2pa and self.c2pa_verifier:
            try:
                c2pa_result = self.c2pa_verifier.verify_chain_of_custody(image_path)
            except Exception as e:
                print(f"⚠️ C2PA verification failed: {e}")
                c2pa_result = {"error": str(e)}
        
        # SynthID Detection (Google's invisible watermark)
        synthid_result = None
        if self.synthid_detector:
            try:
                synthid_result = self.synthid_detector.detect_synthid(image_path)
                print(f"🔍 SynthID Detection: {synthid_result.get('has_synthid', False)}")
            except Exception as e:
                print(f"⚠️ SynthID detection failed: {e}")
                synthid_result = {"error": str(e)}

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
        
        # Get SynthID score (if available)
        synthid_score = 0.0
        has_synthid = False
        if synthid_result and not synthid_result.get('error'):
            synthid_score = synthid_result.get('score', 0.0)
            has_synthid = synthid_result.get('has_synthid', False)
        
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
        # Adjusted weights to include SynthID detection
        W_SYNTHID = 0.25 # SynthID weight - strong indicator when present
        W_AI = 0.35      # Primary AI detection model weight (reduced from 0.45)
        W_FS = 0.15      # Face swap detection weight (reduced from 0.20)
        W_ELA = 0.10     # ELA weight (supporting evidence, reduced from 0.15)
        W_FREQ = 0.08    # Frequency analysis weight (supporting evidence, reduced from 0.10)
        W_TEXTURE = 0.05 # Texture inconsistency weight (reduced from 0.06)
        W_EDGE = 0.02    # Edge inconsistency weight (reduced from 0.04)
        
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
        
        # SynthID score calibration - if watermark detected, high confidence
        synthid_score_calibrated = synthid_score if has_synthid else synthid_score * 0.5
        
        # ELA and Frequency - calibrated thresholds
        # Lowered thresholds to catch subtle edits
        ela_score_calibrated = ela_score if ela_max_diff > 20 else ela_score * 0.7
        freq_score_calibrated = freq_score if freq_std > 18 else freq_score * 0.7
        
        # Texture and edge - calibrated for natural variation
        texture_score_calibrated = texture_score * 0.85 if texture_score < 0.5 else texture_score
        edge_score_calibrated = edge_score * 0.85 if edge_score < 0.5 else edge_score
        
        # === Weighted Ensemble ===
        ensemble_score = (
            W_SYNTHID * synthid_score_calibrated +
            W_AI * ai_score_calibrated +
            W_FS * fs_score_calibrated +
            W_ELA * ela_score_calibrated +
            W_FREQ * freq_score_calibrated +
            W_TEXTURE * texture_score_calibrated +
            W_EDGE * edge_score_calibrated
        )
        
        # === C2PA Trust Factor ===
        # Adjust scores based on C2PA provenance data
        c2pa_trust_boost = 0.0
        c2pa_risk_penalty = 0.0
        
        if c2pa_result:
            if c2pa_result.get("has_c2pa", False):
                if c2pa_result.get("verified", False):
                    # Verified C2PA chain of custody - boost trust
                    trust_level = c2pa_result.get("trust_level", "unknown")
                    if trust_level == "high":
                        c2pa_trust_boost = -0.15  # Reduce fake score
                    elif trust_level == "medium":
                        c2pa_trust_boost = -0.08
                else:
                    # Has C2PA but not verified - increase suspicion
                    c2pa_risk_penalty = 0.10
            else:
                # No C2PA data - slight penalty in modern context
                c2pa_risk_penalty = 0.05
        
        # === Multi-Signal Confirmation ===
        # Detect signals with balanced thresholds
        signal_count = 0
        strong_signals = []
        
        # SynthID detection - strong indicator
        if has_synthid and synthid_score_calibrated > 0.5:
            signal_count += 1
            strong_signals.append("SynthID")
        
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
        
        # Apply C2PA adjustments
        ensemble_score = ensemble_score + c2pa_trust_boost + c2pa_risk_penalty
        
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
            if has_synthid and synthid_score_calibrated > 0.5:
                # SynthID detected - Google AI generation
                generation_method = synthid_result.get('details', {}).get('generation_method', 'Google AI')
                fake_type = f"AI Generated ({generation_method})"
            elif fs_score_calibrated > ai_score_calibrated:
                fake_type = "Face Swap / Deepfake"
            elif ela_score_calibrated > 0.6 and ai_score_calibrated < 0.5:
                fake_type = "Digital Manipulation / Editing"
            else:
                fake_type = "AI Generated (Diffusion/GAN)"

        result = {
            "verdict": verdict,
            "confidence": final_score,
            "confidence_level": confidence_level,
            "fake_type": fake_type,
            # Add 'deepfake' for frontend backwards compatibility
            "deepfake": [{
                "label": "Fake" if verdict == "Fake" else "Real",
                "score": final_score if verdict == "Fake" else (1 - final_score)
            }, {
                "label": "Real" if verdict == "Fake" else "Fake", 
                "score": (1 - final_score) if verdict == "Fake" else final_score
            }],
            "breakdown": {
                "synthid_detection": synthid_result if synthid_result else {"score": 0.0, "has_synthid": False},
                "faceswap_score": fs_score,
                "ai_generation_score": ai_score,
                "frequency_analysis": freq_res,
                "ela_analysis": ela_res,
                "texture_analysis": texture_res,
                "edge_analysis": edge_res,
                "patch_variance": patch_variance
            },
            "calibrated_scores": {
                "synthid_calibrated": synthid_score_calibrated,
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
        
        # Add C2PA provenance data if available
        if c2pa_result:
            result["c2pa_verification"] = {
                "has_c2pa": c2pa_result.get("has_c2pa", False),
                "verified": c2pa_result.get("verified", False),
                "trust_level": c2pa_result.get("trust_level", "unknown"),
                "risk_score": c2pa_result.get("risk_score", 1.0),
                "warnings": c2pa_result.get("warnings", []),
                "claim_generator": c2pa_result.get("claim_generator", None),
                "edit_history_count": len(c2pa_result.get("edit_history", [])),
                "trust_adjustment": c2pa_trust_boost + c2pa_risk_penalty,
                # Pass through full data for frontend viewer
                "manifest": c2pa_result.get("manifest_data", {}),
                "signature": c2pa_result.get("signature_info", {}),
                "assertions": c2pa_result.get("assertions", [])
            }
        
        # Add SynthID detection data if available
        if synthid_result and not synthid_result.get('error'):
            result["synthid_detection"] = {
                "has_watermark": has_synthid,
                "confidence": synthid_result.get('confidence', 0.0),
                "watermark_strength": synthid_result.get('details', {}).get('watermark_strength', 0.0),
                "generation_method": synthid_result.get('details', {}).get('generation_method', 'unknown'),
                "frequency_score": synthid_result.get('details', {}).get('frequency_score', 0.0),
                "spatial_score": synthid_result.get('details', {}).get('spatial_score', 0.0),
                "color_score": synthid_result.get('details', {}).get('color_score', 0.0)
            }
        
        return result
    
    def generate_explainability(self, image_path, method='all', quick_mode=False):
        """
        Generate explainability visualizations for the detection result.
        
        Args:
            image_path: Path to the image file
            method: Explainability method ('lime', 'shap', 'gradcam', 'all')
            quick_mode: If True, uses faster but less accurate parameters
            
        Returns:
            Dictionary containing explainability visualizations and data
        """
        if not self.explainability_engine:
            return {
                "error": "Explainability Engine not initialized",
                "explanations": {}
            }
        
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            return {"error": f"Invalid image path: {e}"}
        
        explanations = {}
        
        # Determine which model to use for explanations (prefer AI gen model)
        primary_model = self.ai_gen_pipe
        primary_predict_fn = self.ai_gen_predict_fn
        model_name = "AI Generation Detector"
        
        if not primary_model and self.faceswap_pipe:
            primary_model = self.faceswap_pipe
            primary_predict_fn = self.faceswap_predict_fn
            model_name = "Face Swap Detector"
        
        if not primary_model or not primary_predict_fn:
            return {
                "error": "No detection models available for explanation",
                "explanations": {}
            }
        
        print(f"🔍 Generating explanations using {model_name}...")
        
        # Set parameters based on mode
        lime_samples = 300 if quick_mode else 1000
        shap_evals = 200 if quick_mode else 500
        
        # LIME Explanation
        if method in ['lime', 'all']:
            try:
                lime_result = self.explainability_engine.explain_with_lime(
                    image,
                    primary_predict_fn,
                    num_samples=lime_samples,
                    num_features=10,
                    positive_only=False
                )
                explanations['lime'] = lime_result
            except Exception as e:
                print(f"⚠️ LIME failed: {e}")
                explanations['lime'] = {"error": str(e)}
        
        # SHAP Explanation
        if method in ['shap', 'all']:
            try:
                shap_result = self.explainability_engine.explain_with_shap(
                    image,
                    primary_predict_fn,
                    num_evals=shap_evals
                )
                explanations['shap'] = shap_result
            except Exception as e:
                print(f"⚠️ SHAP failed: {e}")
                explanations['shap'] = {"error": str(e)}
        
        # Grad-CAM Explanations (requires access to model internals)
        if method in ['gradcam', 'all']:
            # Note: Grad-CAM requires PyTorch model with accessible layers
            # HuggingFace pipelines wrap models, making this complex
            # We'll attempt to extract the model from the pipeline
            try:
                # Get the underlying model from pipeline
                model = primary_model.model
                
                # Find target layers (typically last conv layer for ViT)
                # For Vision Transformers, we target the last attention layer
                target_layers = []
                
                # Try to find appropriate layers
                if hasattr(model, 'vit'):  # ViT-based model
                    if hasattr(model.vit, 'encoder'):
                        if hasattr(model.vit.encoder, 'layer'):
                            # Last transformer block
                            target_layers = [model.vit.encoder.layer[-1].layernorm_before]
                elif hasattr(model, 'base_model'):
                    # Alternative structure
                    base = model.base_model
                    if hasattr(base, 'encoder') and hasattr(base.encoder, 'layer'):
                        target_layers = [base.encoder.layer[-1].layernorm_before]
                
                if target_layers:
                    gradcam_result = self.explainability_engine.explain_with_gradcam(
                        image,
                        model,
                        target_layers,
                        target_class=1,  # Fake class
                        method='gradcam'
                    )
                    explanations['gradcam'] = gradcam_result
                    
                    # Also try GradCAM++
                    if not quick_mode:
                        gradcampp_result = self.explainability_engine.explain_with_gradcam(
                            image,
                            model,
                            target_layers,
                            target_class=1,
                            method='gradcam++'
                        )
                        explanations['gradcam++'] = gradcampp_result
                else:
                    explanations['gradcam'] = {
                        "error": "Could not identify appropriate target layers for Grad-CAM",
                        "note": "Grad-CAM requires direct access to model layers"
                    }
                    
            except Exception as e:
                print(f"⚠️ Grad-CAM failed: {e}")
                import traceback
                traceback.print_exc()
                explanations['gradcam'] = {"error": str(e)}
        
        # Create comparison visualization if multiple methods succeeded
        successful_explanations = {k: v for k, v in explanations.items() 
                                   if 'visualization' in v}
        
        if len(successful_explanations) > 1:
            try:
                comparison = self.explainability_engine.create_comparison_visualization(
                    successful_explanations
                )
                if comparison:
                    explanations['comparison'] = {
                        'visualization': comparison,
                        'description': 'Side-by-side comparison of all explanation methods'
                    }
            except Exception as e:
                print(f"⚠️ Comparison visualization failed: {e}")
        
        return {
            "model_used": model_name,
            "explanations": explanations,
            "quick_mode": quick_mode
        }
    
    def get_c2pa_report(self, image_path):
        """
        Generate comprehensive C2PA provenance report.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing complete C2PA provenance report
        """
        if not self.c2pa_verifier:
            return {
                "error": "C2PA Verifier not initialized",
                "has_c2pa": False
            }
        
        try:
            return self.c2pa_verifier.generate_provenance_report(image_path)
        except Exception as e:
            print(f"❌ Error generating C2PA report: {e}")
            return {
                "error": str(e),
                "has_c2pa": False
            }

    
    def get_xai_explanation(self, image_path, methods=None):
        """
        Generate XAI explanations for an image using GradCAM++ and other methods.
        
        Args:
            image_path (str): Path to the image file
            methods (list): List of XAI methods to use (default: ['GradCAM++'])
                           Options: 'GradCAM++', 'LIME', 'RISE', 'SHAP', 'SOBOL'
        
        Returns:
            dict: Dictionary containing XAI visualizations and predictions
        """
        if not self.enable_xai:
            return {
                "error": "XAI is not enabled. Initialize DeepfakeDetector with enable_xai=True"
            }
        
        try:
            # Lazy load XAI explainer
            if self.xai_explainer is None:
                # Add gradcam to path
                gradcam_path = os.path.join(os.path.dirname(__file__), 'gradcam')
                if gradcam_path not in sys.path:
                    sys.path.insert(0, gradcam_path)
                
                from gradcam.XAIExplainer import XAIExplainer
                
                # Path to the model
                model_path = os.path.join(gradcam_path, 'deepfake_best_model.pth')
                
                self.xai_explainer = XAIExplainer(
                    model_path=model_path,
                    device=self.device
                )
                print("✅ XAI Explainer Loaded")
            
            # Generate explanations
            if methods is None:
                methods = ['GradCAM++']
            
            results = self.xai_explainer.explain(image_path, methods=methods)
            return results
            
        except Exception as e:
            print(f"XAI Explanation Error: {e}")
            import traceback
            return {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def detect_all_with_xai(self, image_path, xai_methods=None):
        """
        Run full deepfake detection with XAI explanations.
        
        Args:
            image_path (str): Path to the image file
            xai_methods (list): List of XAI methods to use (default: ['GradCAM++'])
        
        Returns:
            dict: Combined results with detection and XAI explanations
        """
        # Get standard detection results
        detection_results = self.detect_all(image_path)
        
        # Add XAI explanations if enabled
        if self.enable_xai:
            xai_results = self.get_xai_explanation(image_path, methods=xai_methods)
            detection_results['xai_explanations'] = xai_results
        
        return detection_results


# Singleton instance for easy import
# detector = DeepfakeDetector()

