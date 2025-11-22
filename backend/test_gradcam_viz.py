"""
Test GradCAM Visualization
This script tests if GradCAM++ heatmaps are properly generated
"""

import sys
import os

# Add paths
backend_path = os.path.dirname(os.path.abspath(__file__))
gradcam_path = os.path.join(backend_path, 'gradcam')
sys.path.insert(0, gradcam_path)

from gradcam.XAIExplainer import XAIExplainer
import json

def test_gradcam():
    print("=" * 60)
    print("Testing GradCAM++ Visualization")
    print("=" * 60)
    
    # Initialize explainer
    print("\n1. Initializing XAI Explainer...")
    model_path = os.path.join(gradcam_path, 'deepfake_best_model.pth')
    
    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        return False
    
    explainer = XAIExplainer(model_path=model_path)
    
    # Load model
    print("\n2. Loading model...")
    model = explainer.load_model()
    
    if model is None:
        print("❌ Failed to load model")
        return False
    
    print(f"✓ Model loaded successfully")
    print(f"✓ Model type: {type(model).__name__}")
    print(f"✓ Has 'features' attribute: {hasattr(model, 'features')}")
    
    if hasattr(model, 'features'):
        print(f"✓ Number of feature layers: {len(model.features)}")
        print(f"✓ Last feature layer: {model.features[-1]}")
    
    # Find a test image
    print("\n3. Looking for test image...")
    
    # Try to find any image in the backend folder
    test_image = None
    for root, dirs, files in os.walk(backend_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                test_image = os.path.join(root, file)
                break
        if test_image:
            break
    
    if not test_image:
        print("⚠️ No test image found. Creating a dummy test...")
        # Create a dummy image
        from PIL import Image
        import numpy as np
        dummy_img = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
        test_image = os.path.join(backend_path, 'test_dummy.jpg')
        dummy_img.save(test_image)
        print(f"✓ Created dummy test image at: {test_image}")
    else:
        print(f"✓ Found test image: {test_image}")
    
    # Test GradCAM explanation
    print("\n4. Generating GradCAM++ explanation...")
    try:
        results = explainer.explain(test_image, methods=['GradCAM++'])
        
        print("\n5. Analyzing results...")
        print(f"✓ Results keys: {list(results.keys())}")
        
        # Check prediction
        if 'prediction' in results:
            pred = results['prediction']
            print(f"\n   Prediction:")
            print(f"   - Label: {pred.get('label_name', 'Unknown')}")
            print(f"   - Confidence: {pred.get('confidence', 0):.4f}")
        
        # Check GradCAM++
        if 'GradCAM++' in results:
            gradcam_result = results['GradCAM++']
            
            if 'error' in gradcam_result:
                print(f"\n❌ GradCAM++ Error: {gradcam_result['error']}")
                if 'traceback' in gradcam_result:
                    print(f"\nTraceback:")
                    print(gradcam_result['traceback'])
                return False
            else:
                print(f"\n✅ GradCAM++ generated successfully!")
                print(f"   Available visualizations: {list(gradcam_result.keys())}")
                
                # Check for required keys
                required_keys = ['original', 'overlay', 'saliency']
                for key in required_keys:
                    if key in gradcam_result:
                        # Check if it's a base64 image
                        if isinstance(gradcam_result[key], str) and 'data:image' in gradcam_result[key]:
                            print(f"   ✓ {key}: Generated (base64 image)")
                        else:
                            print(f"   ⚠️ {key}: Present but not in expected format")
                    else:
                        print(f"   ❌ {key}: Missing")
                
                return True
        else:
            print("\n❌ GradCAM++ results not found in output")
            return False
            
    except Exception as e:
        print(f"\n❌ Exception during explanation: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🧪 GradCAM Visualization Test\n")
    
    success = test_gradcam()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ GradCAM++ TEST PASSED!")
        print("\nThe heatmap visualization should now appear in the frontend.")
        print("Make sure to use the 'enable_xai=true' parameter in the API call.")
    else:
        print("❌ GradCAM++ TEST FAILED!")
        print("\nPlease check the errors above and ensure:")
        print("1. The model file exists at backend/gradcam/deepfake_best_model.pth")
        print("2. The model has a 'features' attribute (timm model)")
        print("3. pytorch-grad-cam is installed: pip install pytorch-grad-cam")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
