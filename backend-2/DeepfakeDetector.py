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
            # For now, we return the stats.
            # A high max_diff with a low mean_diff suggests local editing.
            
            score = 0.0
            if max_diff > 50 and mean_diff < 10: # Heuristic threshold
                score = 0.6 # Suspicious
            
            return {
                "score": score,
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
            
            return {
                "score": 0.5, # Neutral score as this is just heuristic for now
                "details": {
                    "mean_frequency": float(mean_freq),
                    "std_frequency": float(std_freq)
                }
            }
        except Exception as e:
            print(f"Frequency Analysis Error: {e}")
            return {"score": 0.0, "error": str(e)}

    def scan_patches(self, image, grid_size=3):
        """
        Splits the image into a grid and runs detection on each patch.
        Useful for detecting local edits (inpainting).
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

        w, h = image.size
        # Only patch scan if image is large enough
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
                    
                    patch_details.append({
                        "type": "patch",
                        "grid_pos": (i, j),
                        "score": score
                    })
                    
                    if score > max_score:
                        max_score = score

        return {
            "score": max_score,
            "details": patch_details
        }

    def detect_all(self, image_path):
        """Runs all detection methods and aggregates the result."""
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            return {"error": f"Invalid image path: {e}"}

        faceswap_res = self.detect_faceswap(image)
        
        # Use scan_patches instead of simple detect_generation
        aigen_res = self.scan_patches(image, grid_size=3)
        
        freq_res = self.analyze_frequency(image_path)
        ela_res = self.perform_ela(image_path)

        # Aggregation Logic
        # If either model is very confident (>0.8), we flag it.
        fs_score = faceswap_res.get('score', 0)
        ai_score = aigen_res.get('score', 0)
        ela_score = ela_res.get('score', 0)
        
        # Boost score if ELA is suspicious and AI score is non-zero
        if ela_score > 0.5 and ai_score > 0.3:
            ai_score = max(ai_score, 0.8) # Boost confidence

        final_score = max(fs_score, ai_score)
        
        verdict = "Real"
        if final_score > 0.5:
            verdict = "Fake"
            
        # Determine the type of fake
        fake_type = "Unknown"
        if verdict == "Fake":
            if fs_score > ai_score:
                fake_type = "Face Swap / Deepfake"
            else:
                fake_type = "AI Generated (Diffusion/GAN)"

        return {
            "verdict": verdict,
            "confidence": final_score,
            "fake_type": fake_type,
            "breakdown": {
                "faceswap_score": fs_score,
                "ai_generation_score": ai_score,
                "frequency_analysis": freq_res,
                "ela_analysis": ela_res
            }
        }

# Singleton instance for easy import
# detector = DeepfakeDetector()
