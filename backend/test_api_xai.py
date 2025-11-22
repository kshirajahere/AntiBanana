#!/usr/bin/env python3
"""
Quick test script to verify deepfake detection with XAI is working
Place a test image in the backend directory and run this script
"""

import requests
import os
import sys

# Configuration
API_URL = "http://localhost:5000/detect"
TEST_IMAGE = None

# Find a test image
for ext in ['.jpg', '.jpeg', '.png']:
    for name in ['test', 'sample', 'example', 'image']:
        path = os.path.join(os.path.dirname(__file__), f"{name}{ext}")
        if os.path.exists(path):
            TEST_IMAGE = path
            break
    if TEST_IMAGE:
        break

if not TEST_IMAGE:
    print("❌ No test image found!")
    print("   Place a test image in the backend directory (test.jpg, sample.png, etc.)")
    sys.exit(1)

print(f"📷 Testing with image: {TEST_IMAGE}")
print(f"🌐 API endpoint: {API_URL}\n")

# Test 1: Basic detection
print("=" * 60)
print("TEST 1: Basic Detection (No XAI)")
print("=" * 60)

try:
    with open(TEST_IMAGE, 'rb') as f:
        response = requests.post(
            API_URL,
            files={'file': f},
            data={
                'enable_xai': 'false',
                'c2pa': 'true'
            },
            timeout=30
        )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Detection successful!")
        print(f"Verdict: {result.get('verdict', 'Unknown')}")
        print(f"Confidence: {result.get('confidence', 0.0):.3f}")
        print(f"Type: {result.get('fake_type', 'Unknown')}")
        
        # C2PA info
        if 'c2pa_verification' in result:
            c2pa = result['c2pa_verification']
            print(f"\nC2PA: {c2pa.get('has_c2pa', False)}")
            if not c2pa.get('has_c2pa', False):
                print("  → No C2PA manifest (expected for regular images)")
        
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Detection with XAI
print("\n" + "=" * 60)
print("TEST 2: Detection with XAI (GradCAM++)")
print("=" * 60)

try:
    with open(TEST_IMAGE, 'rb') as f:
        response = requests.post(
            API_URL,
            files={'file': f},
            data={
                'enable_xai': 'true',
                'xai_methods': 'GradCAM++',
                'c2pa': 'false'  # Skip C2PA for faster XAI testing
            },
            timeout=60
        )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ XAI Detection successful!")
        
        # Check if XAI results exist
        if 'xai_explanations' in result:
            xai = result['xai_explanations']
            
            if 'error' in xai:
                print(f"❌ XAI Error: {xai['error']}")
                if 'traceback' in xai:
                    print(xai['traceback'])
            else:
                # Check prediction
                if 'prediction' in xai:
                    pred = xai['prediction']
                    print(f"\nPrediction: {pred.get('label_name', 'Unknown')}")
                    print(f"Confidence: {pred.get('confidence', 0.0):.3f}")
                
                # Check GradCAM++
                if 'GradCAM++' in xai:
                    gradcam = xai['GradCAM++']
                    if 'error' in gradcam:
                        print(f"❌ GradCAM++ Error: {gradcam['error']}")
                    else:
                        print("✅ GradCAM++ visualization generated!")
                        if 'overlay' in gradcam:
                            print("  → Heatmap overlay: ✓")
                        if 'original' in gradcam:
                            print("  → Original image: ✓")
                        if 'saliency' in gradcam:
                            print("  → Saliency map: ✓")
        else:
            print("⚠️ No XAI explanations in response")
            
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
