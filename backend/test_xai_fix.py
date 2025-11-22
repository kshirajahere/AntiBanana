"""
Test script to verify XAI and model loading fixes
"""

import os
import sys

# Add gradcam to path
gradcam_path = os.path.join(os.path.dirname(__file__), 'gradcam')
if gradcam_path not in sys.path:
    sys.path.insert(0, gradcam_path)

from gradcam.XAIExplainer import XAIExplainer
from PIL import Image

def test_model_loading():
    """Test that the model loads correctly"""
    print("=" * 60)
    print("TEST 1: Model Loading")
    print("=" * 60)
    
    try:
        model_path = os.path.join(gradcam_path, 'deepfake_best_model.pth')
        print(f"Model path: {model_path}")
        print(f"Model exists: {os.path.exists(model_path)}")
        
        explainer = XAIExplainer(model_path=model_path, device='cpu')
        model = explainer.load_model()
        
        if model is not None:
            print("✅ Model loaded successfully!")
            print(f"Model type: {type(model)}")
            print(f"Model device: {next(model.parameters()).device}")
            return True
        else:
            print("❌ Model loading failed!")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_image_processing():
    """Test image preprocessing"""
    print("\n" + "=" * 60)
    print("TEST 2: Image Preprocessing")
    print("=" * 60)
    
    try:
        # Create a test image
        from PIL import Image
        import numpy as np
        
        test_img = Image.fromarray(np.uint8(np.random.rand(256, 256, 3) * 255))
        
        explainer = XAIExplainer(device='cpu')
        
        # Process image
        processed = explainer.inference_transforms(test_img)
        
        print(f"✅ Image preprocessing successful!")
        print(f"Input image size: {test_img.size}")
        print(f"Processed tensor shape: {processed.shape}")
        print(f"Expected shape: torch.Size([3, 64, 64])")
        
        if processed.shape == (3, 64, 64):
            print("✅ Correct tensor dimensions!")
            return True
        else:
            print(f"❌ Wrong dimensions! Expected (3, 64, 64), got {processed.shape}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_pipeline():
    """Test the complete XAI explanation pipeline"""
    print("\n" + "=" * 60)
    print("TEST 3: Full XAI Pipeline (if test image available)")
    print("=" * 60)
    
    # Look for a test image
    test_image_path = None
    for ext in ['.jpg', '.jpeg', '.png']:
        for name in ['test', 'sample', 'example']:
            path = os.path.join(os.path.dirname(__file__), f"{name}{ext}")
            if os.path.exists(path):
                test_image_path = path
                break
        if test_image_path:
            break
    
    if not test_image_path:
        print("⚠️ No test image found. Skipping full pipeline test.")
        print("   To test, place a test image in the backend directory.")
        return None
    
    try:
        print(f"Using test image: {test_image_path}")
        
        explainer = XAIExplainer(device='cpu')
        results = explainer.explain(test_image_path, methods=['GradCAM++'])
        
        if 'error' in results:
            print(f"❌ Explanation failed: {results['error']}")
            if 'traceback' in results:
                print(results['traceback'])
            return False
        
        print("✅ Full pipeline successful!")
        if 'prediction' in results:
            pred = results['prediction']
            print(f"Prediction: {pred.get('label_name', 'Unknown')}")
            print(f"Confidence: {pred.get('confidence', 0.0):.3f}")
        
        if 'GradCAM++' in results:
            if 'error' in results['GradCAM++']:
                print(f"⚠️ GradCAM++ had error: {results['GradCAM++']['error']}")
            else:
                print("✅ GradCAM++ visualization generated!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🔧 Testing XAI and Model Loading Fixes\n")
    
    results = []
    
    # Run tests
    results.append(("Model Loading", test_model_loading()))
    results.append(("Image Preprocessing", test_image_processing()))
    results.append(("Full Pipeline", test_full_pipeline()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        
        print(f"{test_name:25} {status}")
    
    # Overall result
    failed = sum(1 for _, r in results if r is False)
    passed = sum(1 for _, r in results if r is True)
    
    print("\n" + "=" * 60)
    if failed == 0:
        print(f"🎉 ALL TESTS PASSED ({passed}/{len([r for r in results if r is not None])})")
    else:
        print(f"❌ {failed} TEST(S) FAILED")
    print("=" * 60 + "\n")
