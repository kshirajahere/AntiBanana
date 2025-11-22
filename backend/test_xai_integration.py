"""
Test script for XAI integration with DeepfakeDetector
Tests the complete pipeline from model loading to visualization generation
"""

import os
import sys

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from DeepfakeDetector import DeepfakeDetector
from PIL import Image
import json

def test_basic_detection():
    """Test basic deepfake detection without XAI"""
    print("\n" + "="*80)
    print("TEST 1: Basic Deepfake Detection (without XAI)")
    print("="*80)
    
    detector = DeepfakeDetector(enable_xai=False)
    
    # You would need to provide a test image path
    test_image = "test_image.jpg"
    
    if not os.path.exists(test_image):
        print(f"⚠️  Test image not found: {test_image}")
        print("Please provide a test image to run this test")
        return False
    
    try:
        results = detector.detect_all(test_image)
        print("\n✅ Detection completed successfully!")
        print(f"Verdict: {results.get('verdict')}")
        print(f"Confidence: {results.get('confidence', 0):.4f}")
        print(f"Fake Type: {results.get('fake_type')}")
        return True
    except Exception as e:
        print(f"\n❌ Detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_xai_detection():
    """Test deepfake detection with XAI explanations"""
    print("\n" + "="*80)
    print("TEST 2: Deepfake Detection with XAI Explanations")
    print("="*80)
    
    detector = DeepfakeDetector(enable_xai=True)
    
    test_image = "test_image.jpg"
    
    if not os.path.exists(test_image):
        print(f"⚠️  Test image not found: {test_image}")
        print("Please provide a test image to run this test")
        return False
    
    try:
        results = detector.detect_all_with_xai(test_image, xai_methods=['GradCAM++'])
        
        print("\n✅ Detection with XAI completed successfully!")
        print(f"Verdict: {results.get('verdict')}")
        print(f"Confidence: {results.get('confidence', 0):.4f}")
        
        if 'xai_explanations' in results:
            xai = results['xai_explanations']
            print("\n📊 XAI Results:")
            
            if 'prediction' in xai:
                pred = xai['prediction']
                print(f"  - XAI Model Prediction: {pred.get('label_name')}")
                print(f"  - XAI Confidence: {pred.get('confidence', 0):.4f}")
            
            if 'GradCAM++' in xai and 'overlay' in xai['GradCAM++']:
                print(f"  - GradCAM++ visualization generated: ✓")
            
            if 'error' in xai:
                print(f"  - XAI Error: {xai['error']}")
        
        return True
    except Exception as e:
        print(f"\n❌ Detection with XAI failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_xai_model_only():
    """Test XAI model loading and prediction independently"""
    print("\n" + "="*80)
    print("TEST 3: XAI Model Loading and Prediction")
    print("="*80)
    
    try:
        from gradcam.XAIExplainer import XAIExplainer
        
        test_image = "test_image.jpg"
        
        if not os.path.exists(test_image):
            print(f"⚠️  Test image not found: {test_image}")
            print("Please provide a test image to run this test")
            return False
        
        explainer = XAIExplainer()
        print("\n✅ XAI Explainer initialized successfully!")
        
        # Check if model file exists
        model_path = os.path.join(backend_path, 'gradcam', 'deepfake_best_model.pth')
        if os.path.exists(model_path):
            print(f"✅ Model file found: {model_path}")
        else:
            print(f"⚠️  Model file not found: {model_path}")
            print("Please ensure deepfake_best_model.pth is in the gradcam folder")
            return False
        
        results = explainer.explain(test_image, methods=['GradCAM++'])
        
        if 'error' in results:
            print(f"\n❌ XAI explanation failed: {results['error']}")
            if 'traceback' in results:
                print(results['traceback'])
            return False
        
        print("\n✅ XAI explanation generated successfully!")
        
        if 'prediction' in results:
            pred = results['prediction']
            print(f"Prediction: {pred.get('label_name')}")
            print(f"Confidence: {pred.get('confidence', 0):.4f}")
        
        if 'GradCAM++' in results and 'overlay' in results['GradCAM++']:
            print("GradCAM++ heatmap: ✓")
        
        return True
        
    except Exception as e:
        print(f"\n❌ XAI model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test if all required dependencies are installed"""
    print("\n" + "="*80)
    print("TEST 4: Dependency Check")
    print("="*80)
    
    dependencies = {
        'torch': 'PyTorch',
        'torchvision': 'TorchVision',
        'timm': 'timm (PyTorch Image Models)',
        'pytorch_lightning': 'PyTorch Lightning',
        'pytorch_grad_cam': 'pytorch-grad-cam',
        'lime': 'LIME',
        'transformers': 'Transformers',
        'PIL': 'Pillow',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'scipy': 'SciPy',
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
    }
    
    all_installed = True
    
    for module_name, display_name in dependencies.items():
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - NOT INSTALLED")
            all_installed = False
    
    if all_installed:
        print("\n✅ All dependencies are installed!")
    else:
        print("\n⚠️  Some dependencies are missing. Install them using:")
        print("pip install -r requirements.txt")
    
    return all_installed

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("XAI INTEGRATION TEST SUITE")
    print("="*80)
    
    tests = [
        ("Dependency Check", test_dependencies),
        ("Basic Detection", test_basic_detection),
        ("XAI Model Only", test_xai_model_only),
        ("Full XAI Detection", test_xai_detection),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! XAI integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
