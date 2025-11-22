"""
Comprehensive Test Suite for XAI Features in Deepfake Detector

This script demonstrates all explainability features including:
- LIME (Local Interpretable Model-agnostic Explanations)
- SHAP (SHapley Additive exPlanations)
- Grad-CAM (Gradient-weighted Class Activation Mapping)
- Grad-CAM++
- Comprehensive explainability reports

Author: Senior Developer @ Google
Date: November 22, 2025
"""

import os
import sys
import argparse
from pathlib import Path
import json
from PIL import Image

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from DeepfakeDetector import DeepfakeDetector


def test_basic_detection(detector, image_path):
    """Test basic deepfake detection without explanations."""
    print("\n" + "="*80)
    print("TEST 1: Basic Deepfake Detection")
    print("="*80)
    
    result = detector.detect_all(image_path)
    
    print(f"\n📊 Detection Result:")
    print(f"   Verdict: {result['verdict']}")
    print(f"   Confidence: {result['confidence']:.4f}")
    print(f"   Confidence Level: {result['confidence_level']}")
    print(f"   Fake Type: {result['fake_type']}")
    print(f"   Detection Signals: {', '.join(result['detection_signals'])}")
    print(f"   Signal Count: {result['signal_count']}")
    
    return result


def test_lime_explanation(detector, image_path):
    """Test LIME explainability."""
    print("\n" + "="*80)
    print("TEST 2: LIME Explanation")
    print("="*80)
    
    print("\nGenerating LIME explanation (this may take 30-60 seconds)...")
    result = detector.generate_explainability(image_path, method='lime', quick_mode=False)
    
    if 'lime' in result.get('explanations', {}):
        lime_result = result['explanations']['lime']
        if 'error' not in lime_result:
            print(f"\n✅ LIME Explanation Generated")
            print(f"   Method: {lime_result['method']}")
            print(f"   Description: {lime_result['description']}")
            print(f"   Top Label: {lime_result['top_label']}")
            print(f"   Number of Superpixels: {lime_result['num_superpixels']}")
            print(f"   Visualization: {'Available' if 'visualization' in lime_result else 'N/A'}")
            
            # Save visualization if available
            if 'visualization' in lime_result:
                save_visualization(lime_result['visualization'], 'lime_explanation.html')
        else:
            print(f"❌ LIME Error: {lime_result['error']}")
    else:
        print("❌ LIME explanation not generated")
    
    return result


def test_shap_explanation(detector, image_path):
    """Test SHAP explainability."""
    print("\n" + "="*80)
    print("TEST 3: SHAP Explanation")
    print("="*80)
    
    print("\nGenerating SHAP explanation (this may take 1-2 minutes)...")
    result = detector.generate_explainability(image_path, method='shap', quick_mode=False)
    
    if 'shap' in result.get('explanations', {}):
        shap_result = result['explanations']['shap']
        if 'error' not in shap_result:
            print(f"\n✅ SHAP Explanation Generated")
            print(f"   Method: {shap_result['method']}")
            print(f"   Description: {shap_result['description']}")
            print(f"   Mean Abs SHAP: {shap_result.get('mean_abs_shap', 'N/A')}")
            print(f"   Max Abs SHAP: {shap_result.get('max_abs_shap', 'N/A')}")
            print(f"   Visualization: {'Available' if 'visualization' in shap_result else 'N/A'}")
            
            # Save visualization if available
            if 'visualization' in shap_result:
                save_visualization(shap_result['visualization'], 'shap_explanation.html')
        else:
            print(f"❌ SHAP Error: {shap_result['error']}")
    else:
        print("❌ SHAP explanation not generated")
    
    return result


def test_gradcam_explanation(detector, image_path):
    """Test Grad-CAM explainability."""
    print("\n" + "="*80)
    print("TEST 4: Grad-CAM Explanation")
    print("="*80)
    
    print("\nGenerating Grad-CAM explanation...")
    result = detector.generate_explainability(image_path, method='gradcam', quick_mode=False)
    
    if 'gradcam' in result.get('explanations', {}):
        gradcam_result = result['explanations']['gradcam']
        if 'error' not in gradcam_result:
            print(f"\n✅ Grad-CAM Explanation Generated")
            print(f"   Method: {gradcam_result['method']}")
            print(f"   Description: {gradcam_result['description']}")
            print(f"   Max Activation: {gradcam_result.get('cam_max_activation', 'N/A')}")
            print(f"   Mean Activation: {gradcam_result.get('cam_mean_activation', 'N/A')}")
            print(f"   High Activation Area: {gradcam_result.get('high_activation_area', 'N/A'):.2%}")
            print(f"   Visualization: {'Available' if 'visualization' in gradcam_result else 'N/A'}")
            
            # Save visualization if available
            if 'visualization' in gradcam_result:
                save_visualization(gradcam_result['visualization'], 'gradcam_explanation.html')
        else:
            print(f"❌ Grad-CAM Error: {gradcam_result['error']}")
    else:
        print("❌ Grad-CAM explanation not generated")
    
    return result


def test_comprehensive_explanation(detector, image_path):
    """Test comprehensive explainability with all methods."""
    print("\n" + "="*80)
    print("TEST 5: Comprehensive Explainability Report")
    print("="*80)
    
    print("\nGenerating comprehensive explainability report with all methods...")
    print("⏳ This will take several minutes. Please be patient...")
    
    result = detector.generate_explainability(image_path, method='all', quick_mode=False)
    
    print(f"\n📊 Comprehensive Report:")
    print(f"   Model Used: {result.get('model_used', 'N/A')}")
    print(f"   Quick Mode: {result.get('quick_mode', False)}")
    
    explanations = result.get('explanations', {})
    print(f"\n   Generated Explanations:")
    
    for method, explanation in explanations.items():
        status = "✅" if 'error' not in explanation else "❌"
        print(f"   {status} {method.upper()}")
        
        if 'visualization' in explanation and method != 'comparison':
            save_visualization(explanation['visualization'], f'{method}_comprehensive.html')
    
    # Save comparison if available
    if 'comparison' in explanations and 'visualization' in explanations['comparison']:
        save_visualization(explanations['comparison']['visualization'], 'comparison_all_methods.html')
        print(f"\n   ✅ Comparison visualization saved")
    
    return result


def test_quick_mode(detector, image_path):
    """Test quick mode for faster explanations."""
    print("\n" + "="*80)
    print("TEST 6: Quick Mode Explanations")
    print("="*80)
    
    print("\nGenerating quick mode explanations (faster, less accurate)...")
    result = detector.generate_explainability(image_path, method='all', quick_mode=True)
    
    print(f"\n📊 Quick Mode Report:")
    print(f"   Model Used: {result.get('model_used', 'N/A')}")
    print(f"   Quick Mode: {result.get('quick_mode', False)}")
    
    explanations = result.get('explanations', {})
    success_count = sum(1 for e in explanations.values() if 'error' not in e)
    
    print(f"   Successfully Generated: {success_count}/{len(explanations)} methods")
    
    return result


def save_visualization(base64_data, filename):
    """Save base64 visualization to HTML file."""
    output_dir = Path(__file__).parent / 'xai_outputs'
    output_dir.mkdir(exist_ok=True)
    
    output_path = output_dir / filename
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>XAI Visualization - {filename}</title>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                background-color: #1e1e1e;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }}
            img {{
                max-width: 100%;
                height: auto;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <img src="{base64_data}" alt="XAI Visualization">
    </body>
    </html>
    """
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"   💾 Saved: {output_path}")


def run_all_tests(image_path, tests_to_run='all'):
    """Run all XAI tests."""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE XAI TEST SUITE FOR DEEPFAKE DETECTOR")
    print("="*80)
    print(f"\n📁 Image: {image_path}")
    
    # Verify image exists
    if not os.path.exists(image_path):
        print(f"\n❌ Error: Image not found at {image_path}")
        return
    
    # Load image info
    try:
        img = Image.open(image_path)
        print(f"   Size: {img.size[0]}x{img.size[1]}")
        print(f"   Mode: {img.mode}")
    except Exception as e:
        print(f"\n❌ Error loading image: {e}")
        return
    
    # Initialize detector
    print("\n🔄 Initializing Deepfake Detector with XAI capabilities...")
    detector = DeepfakeDetector()
    
    # Run selected tests
    if tests_to_run == 'all' or '1' in tests_to_run:
        test_basic_detection(detector, image_path)
    
    if tests_to_run == 'all' or '2' in tests_to_run:
        test_lime_explanation(detector, image_path)
    
    if tests_to_run == 'all' or '3' in tests_to_run:
        test_shap_explanation(detector, image_path)
    
    if tests_to_run == 'all' or '4' in tests_to_run:
        test_gradcam_explanation(detector, image_path)
    
    if tests_to_run == 'all' or '5' in tests_to_run:
        test_comprehensive_explanation(detector, image_path)
    
    if tests_to_run == 'all' or '6' in tests_to_run:
        test_quick_mode(detector, image_path)
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED")
    print("="*80)
    print("\n📁 Visualizations saved to: ./xai_outputs/")
    print("\n💡 TIP: Open the HTML files in a browser to view the visualizations")


def main():
    parser = argparse.ArgumentParser(
        description='Test XAI features for Deepfake Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python test_xai.py image.jpg
  
  # Run specific tests
  python test_xai.py image.jpg --tests 1,2,3
  
  # Run only LIME
  python test_xai.py image.jpg --tests 2
  
  # Run comprehensive report
  python test_xai.py image.jpg --tests 5

Available Tests:
  1. Basic Detection
  2. LIME Explanation
  3. SHAP Explanation
  4. Grad-CAM Explanation
  5. Comprehensive Report (All Methods)
  6. Quick Mode (Fast Explanations)
        """
    )
    
    parser.add_argument('image', help='Path to the image file to analyze')
    parser.add_argument('--tests', default='all', 
                       help='Comma-separated test numbers to run (e.g., "1,2,3" or "all")')
    
    args = parser.parse_args()
    
    run_all_tests(args.image, args.tests)


if __name__ == '__main__':
    main()
