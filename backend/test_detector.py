import sys
import os
import numpy as np
from PIL import Image

# Add current directory to path
sys.path.append(os.getcwd())

from DeepfakeDetector import DeepfakeDetector

def test_detector():
    print("Initializing Detector...")
    try:
        detector = DeepfakeDetector()
        print("Detector initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize detector: {e}")
        return

    # Create a dummy image (random noise)
    print("Creating dummy image...")
    img = Image.fromarray(np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8))
    img_path = "test_dummy.jpg"
    img.save(img_path)

    try:
        print("Running detection on dummy image...")
        result = detector.detect_all(img_path)
        print("Detection result:")
        print(result)
        
        if "verdict" in result and "confidence" in result:
            print("✅ Test Passed: Detection returned valid structure.")
        else:
            print("❌ Test Failed: Invalid result structure.")
            
    except Exception as e:
        print(f"❌ Test Failed with error: {e}")
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)

if __name__ == "__main__":
    test_detector()
