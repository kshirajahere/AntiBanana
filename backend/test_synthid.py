"""
Test script for SynthID integration
"""
import sys
import os

# Test the SynthID detector standalone
from SynthIDDetector import SynthIDDetector

def test_synthid_detector():
    print("=" * 60)
    print("Testing SynthID Detector Initialization")
    print("=" * 60)
    
    try:
        detector = SynthIDDetector()
        print("✅ SynthID Detector initialized successfully")
        print(f"   Min confidence threshold: {detector.min_confidence_threshold}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize SynthID Detector: {e}")
        return False

def test_integration():
    print("\n" + "=" * 60)
    print("Testing SynthID Integration with DeepfakeDetector")
    print("=" * 60)
    
    try:
        from DeepfakeDetector import DeepfakeDetector
        
        print("Initializing DeepfakeDetector with SynthID support...")
        detector = DeepfakeDetector(enable_xai=False)
        
        if detector.synthid_detector:
            print("✅ SynthID Detector successfully integrated")
            print("   Integration successful!")
            return True
        else:
            print("⚠️ SynthID Detector not initialized in DeepfakeDetector")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🧪 SynthID Integration Test Suite\n")
    
    # Test 1: SynthID Detector standalone
    test1_passed = test_synthid_detector()
    
    # Test 2: Integration with DeepfakeDetector
    test2_passed = test_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"SynthID Detector Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Integration Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! SynthID is ready to use.")
        print("\nHow it works:")
        print("- When an image is analyzed, SynthID detector checks for Google's invisible watermarks")
        print("- If a SynthID watermark is detected, the image is flagged as AI-generated")
        print("- SynthID detection is weighted at 25% in the ensemble scoring")
        print("- Results include detailed SynthID analysis in the breakdown")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return test1_passed and test2_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
