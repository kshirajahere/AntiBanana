"""
Test GradCAM integration with the full detection pipeline
"""

import sys
import os

backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from DeepfakeDetector import DeepfakeDetector
import json

def test_full_integration():
    print("=" * 60)
    print("Testing GradCAM++ with Full Detection Pipeline")
    print("=" * 60)
    
    # Find test image
    test_image = None
    gradcam_path = os.path.join(backend_path, 'gradcam')
    
    for root, dirs, files in os.walk(gradcam_path):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')) and 'test' in file.lower():
                test_image = os.path.join(root, file)
                break
        if test_image:
            break
    
    if not test_image:
        print("❌ No test image found")
        return False
    
    print(f"\n✓ Using test image: {test_image}")
    
    # Initialize detector with XAI enabled
    print("\n1. Initializing DeepfakeDetector with XAI enabled...")
    detector = DeepfakeDetector(enable_xai=True)
    
    # Run detection with XAI
    print("\n2. Running detection with XAI explanations...")
    try:
        result = detector.get_xai_explanation(test_image, methods=['GradCAM++'])
        
        print("\n3. Analyzing results...")
        print(f"✓ Result keys: {list(result.keys())}")
        
        # The result IS the XAI explanations - no nested structure
        if 'GradCAM++' in result:
            gradcam = result['GradCAM++']
            
            if 'error' in gradcam:
                print(f"\n❌ GradCAM++ error: {gradcam['error']}")
                return False
            
            print(f"\n✅ GradCAM++ heatmap generated!")
            print(f"  Visualizations: {list(gradcam.keys())}")
            
            # Verify all required visualizations
            required = ['original', 'overlay', 'saliency']
            for key in required:
                if key in gradcam and isinstance(gradcam[key], str) and 'data:image' in gradcam[key]:
                    print(f"  ✓ {key}: Present")
                else:
                    print(f"  ❌ {key}: Missing or invalid")
                    return False
            
            # Check prediction info
            if 'prediction' in result:
                pred = result['prediction']
                print(f"\n  Prediction: {pred.get('label_name', 'Unknown')}")
                print(f"  Confidence: {pred.get('confidence', 0):.4f}")
            
            return True
        else:
            print(f"\n❌ GradCAM++ not found in results")
            print(f"  Available keys: {list(result.keys())}")
            return False
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🧪 Full Integration Test: GradCAM++ with DeepfakeDetector\n")
    
    success = test_full_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ FULL INTEGRATION TEST PASSED!")
        print("\nGradCAM++ heatmaps are working end-to-end!")
        print("\nTo use in the frontend:")
        print("1. POST to /detect with enable_xai=true parameter")
        print("2. Or use get_xai_explanation() method")
        print("3. The response will include base64-encoded heatmap images")
    else:
        print("❌ FULL INTEGRATION TEST FAILED!")
        print("\nCheck the errors above for details.")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
