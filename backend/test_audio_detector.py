"""
Test Script for Advanced AudioDeepfakeDetector
==============================================
Comprehensive testing of the new audio detection system.
"""

import os
import sys
import time
import numpy as np
import soundfile as sf
from AudioDeepfakeDetector import (
    AudioDeepfakeDetector, 
    DetectionMethod,
    analyze_audio
)

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def generate_test_audio(duration=3.0, sr=16000, frequency=440):
    """Generate a simple test sine wave"""
    t = np.linspace(0, duration, int(sr * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    return audio, sr


def test_initialization():
    """Test 1: Detector initialization"""
    print_header("TEST 1: Detector Initialization")
    
    try:
        start_time = time.time()
        detector = AudioDeepfakeDetector()
        init_time = time.time() - start_time
        
        print_success(f"Detector initialized successfully in {init_time:.2f}s")
        print_info(f"Device: {detector.device}")
        print_info(f"Primary model loaded: {detector.primary_model is not None}")
        print_info(f"Spectral analyzer ready: {detector.spectral_analyzer is not None}")
        print_info(f"Prosody analyzer ready: {detector.prosody_analyzer is not None}")
        print_info(f"Temporal analyzer ready: {detector.temporal_analyzer is not None}")
        
        return detector, True
    except Exception as e:
        print_error(f"Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None, False


def test_synthetic_audio(detector):
    """Test 2: Detection on synthetic audio"""
    print_header("TEST 2: Detection on Synthetic Audio")
    
    try:
        # Generate test audio
        print_info("Generating synthetic test audio...")
        audio, sr = generate_test_audio(duration=3.0, sr=16000)
        
        # Save to temp file
        temp_file = "test_synthetic.wav"
        sf.write(temp_file, audio, sr)
        print_success(f"Test audio created: {temp_file}")
        
        # Test ensemble detection
        print_info("Running ensemble detection...")
        start_time = time.time()
        result = detector.detect(temp_file, method=DetectionMethod.ENSEMBLE)
        detection_time = time.time() - start_time
        
        print_success(f"Detection completed in {detection_time:.2f}s")
        print(f"\n{Colors.BOLD}Results:{Colors.ENDC}")
        print(f"  Prediction: {Colors.OKGREEN if result.prediction == 'real' else Colors.FAIL}{result.prediction.upper()}{Colors.ENDC}")
        print(f"  Confidence: {result.confidence:.2%}")
        print(f"  Fake Probability: {result.fake_probability:.2%}")
        
        print(f"\n{Colors.BOLD}Method Scores:{Colors.ENDC}")
        for method, score in result.method_scores.items():
            bar = "█" * int(score * 20)
            print(f"  {method:15s}: {score:.3f} [{bar}]")
        
        if result.anomalies:
            print(f"\n{Colors.BOLD}Anomalies:{Colors.ENDC}")
            for anomaly in result.anomalies:
                print(f"  - {anomaly}")
        
        if result.warning_flags:
            print(f"\n{Colors.BOLD}Warnings:{Colors.ENDC}")
            for warning in result.warning_flags:
                print_warning(warning)
        
        # Clean up
        os.unlink(temp_file)
        return True
        
    except Exception as e:
        print_error(f"Synthetic audio test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_methods(detector):
    """Test 3: Individual detection methods"""
    print_header("TEST 3: Individual Detection Methods")
    
    try:
        # Generate test audio
        audio, sr = generate_test_audio(duration=2.0, sr=16000)
        temp_file = "test_methods.wav"
        sf.write(temp_file, audio, sr)
        
        methods = [
            (DetectionMethod.TRANSFORMER, "Transformer"),
            (DetectionMethod.SPECTRAL, "Spectral Analysis"),
            (DetectionMethod.PROSODY, "Prosody Analysis"),
            (DetectionMethod.TEMPORAL, "Temporal Analysis"),
            (DetectionMethod.PHASE, "Phase Analysis"),
        ]
        
        print(f"\n{Colors.BOLD}Testing individual methods:{Colors.ENDC}\n")
        
        results = []
        for method, name in methods:
            try:
                start = time.time()
                result = detector.detect(temp_file, method=method)
                elapsed = time.time() - start
                
                status = "✅" if result.confidence > 0.5 else "⚠️"
                print(f"{status} {name:20s}: {result.fake_probability:.3f} ({elapsed:.2f}s)")
                results.append((name, result.fake_probability))
            except Exception as e:
                print_error(f"  {name}: {e}")
        
        # Visualize comparison
        print(f"\n{Colors.BOLD}Method Comparison:{Colors.ENDC}\n")
        max_score = max(score for _, score in results) if results else 1.0
        for name, score in results:
            bar_length = int((score / max_score) * 40)
            bar = "█" * bar_length
            print(f"  {name:20s} {bar} {score:.3f}")
        
        # Clean up
        os.unlink(temp_file)
        return True
        
    except Exception as e:
        print_error(f"Individual methods test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualization_generation(detector):
    """Test 4: Visualization generation"""
    print_header("TEST 4: Visualization Generation")
    
    try:
        # Generate test audio
        audio, sr = generate_test_audio(duration=2.0, sr=16000)
        temp_file = "test_viz.wav"
        sf.write(temp_file, audio, sr)
        
        print_info("Generating visualizations...")
        start_time = time.time()
        result = detector.detect(temp_file, method=DetectionMethod.ENSEMBLE)
        visualizations = detector.generate_visualizations(temp_file, result)
        viz_time = time.time() - start_time
        
        print_success(f"Visualizations generated in {viz_time:.2f}s")
        print(f"\n{Colors.BOLD}Available Visualizations:{Colors.ENDC}")
        for viz_name, viz_data in visualizations.items():
            size_kb = len(viz_data) / 1024
            print(f"  ✓ {viz_name:25s} ({size_kb:.1f} KB)")
        
        # Clean up
        os.unlink(temp_file)
        return True
        
    except Exception as e:
        print_error(f"Visualization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_analyze_audio_function():
    """Test 5: Convenience function"""
    print_header("TEST 5: analyze_audio() Convenience Function")
    
    try:
        # Generate test audio
        audio, sr = generate_test_audio(duration=2.0, sr=16000)
        temp_file = "test_convenience.wav"
        sf.write(temp_file, audio, sr)
        
        print_info("Testing analyze_audio() function...")
        start_time = time.time()
        result = analyze_audio(temp_file)
        total_time = time.time() - start_time
        
        print_success(f"Analysis completed in {total_time:.2f}s")
        
        if 'error' in result:
            print_error(f"Error in result: {result['error']}")
            return False
        
        print(f"\n{Colors.BOLD}Complete Analysis Results:{Colors.ENDC}")
        print(f"  Prediction: {result['prediction'].upper()}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Is Fake: {result['is_fake']}")
        
        print(f"\n{Colors.BOLD}Method Scores:{Colors.ENDC}")
        for method, score in result['method_scores'].items():
            print(f"  {method:15s}: {score:.3f}")
        
        print(f"\n{Colors.BOLD}Metadata:{Colors.ENDC}")
        for key, value in result['metadata'].items():
            if key not in ['raw_outputs']:
                print(f"  {key}: {value}")
        
        print(f"\n{Colors.BOLD}Visualizations:{Colors.ENDC}")
        for viz_name in result['images'].keys():
            print(f"  ✓ {viz_name}")
        
        # Clean up
        os.unlink(temp_file)
        return True
        
    except Exception as e:
        print_error(f"Convenience function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audio_length_variations(detector):
    """Test 6: Different audio lengths"""
    print_header("TEST 6: Audio Length Variations")
    
    durations = [0.5, 1.0, 2.0, 5.0, 10.0]
    
    print(f"\n{Colors.BOLD}Testing different audio lengths:{Colors.ENDC}\n")
    
    for duration in durations:
        try:
            audio, sr = generate_test_audio(duration=duration, sr=16000)
            temp_file = f"test_{duration}s.wav"
            sf.write(temp_file, audio, sr)
            
            start = time.time()
            result = detector.detect(temp_file, method=DetectionMethod.ENSEMBLE)
            elapsed = time.time() - start
            
            print(f"  {duration:4.1f}s audio: {result.prediction:5s} (confidence: {result.confidence:.2%}, time: {elapsed:.2f}s)")
            
            os.unlink(temp_file)
        except Exception as e:
            print_error(f"  {duration}s test failed: {e}")
    
    return True


def run_performance_benchmark(detector):
    """Test 7: Performance benchmark"""
    print_header("TEST 7: Performance Benchmark")
    
    try:
        # Generate test audio
        audio, sr = generate_test_audio(duration=3.0, sr=16000)
        temp_file = "test_benchmark.wav"
        sf.write(temp_file, audio, sr)
        
        n_iterations = 5
        print_info(f"Running {n_iterations} iterations for each method...\n")
        
        methods = [
            (DetectionMethod.ENSEMBLE, "Ensemble"),
            (DetectionMethod.TRANSFORMER, "Transformer"),
            (DetectionMethod.SPECTRAL, "Spectral"),
            (DetectionMethod.PROSODY, "Prosody"),
            (DetectionMethod.TEMPORAL, "Temporal"),
            (DetectionMethod.PHASE, "Phase"),
        ]
        
        print(f"{Colors.BOLD}{'Method':<20} {'Mean Time':<12} {'Std Dev':<12} {'Min':<10} {'Max':<10}{Colors.ENDC}")
        print("-" * 70)
        
        for method, name in methods:
            times = []
            for i in range(n_iterations):
                start = time.time()
                try:
                    result = detector.detect(temp_file, method=method)
                    elapsed = time.time() - start
                    times.append(elapsed)
                except Exception as e:
                    print_error(f"  {name} iteration {i+1} failed: {e}")
                    continue
            
            if times:
                mean_time = np.mean(times)
                std_time = np.std(times)
                min_time = np.min(times)
                max_time = np.max(times)
                
                print(f"{name:<20} {mean_time:<12.3f} {std_time:<12.3f} {min_time:<10.3f} {max_time:<10.3f}")
        
        # Clean up
        os.unlink(temp_file)
        return True
        
    except Exception as e:
        print_error(f"Performance benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║    Advanced Audio Deepfake Detector - Comprehensive Test Suite   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    # Track test results
    results = []
    
    # Test 1: Initialization
    detector, success = test_initialization()
    results.append(("Initialization", success))
    
    if not success:
        print_error("Cannot proceed without successful initialization")
        return
    
    # Test 2: Synthetic audio
    success = test_synthetic_audio(detector)
    results.append(("Synthetic Audio Detection", success))
    
    # Test 3: Individual methods
    success = test_individual_methods(detector)
    results.append(("Individual Methods", success))
    
    # Test 4: Visualizations
    success = test_visualization_generation(detector)
    results.append(("Visualization Generation", success))
    
    # Test 5: Convenience function
    success = test_analyze_audio_function()
    results.append(("Convenience Function", success))
    
    # Test 6: Length variations
    success = test_audio_length_variations(detector)
    results.append(("Length Variations", success))
    
    # Test 7: Performance benchmark
    success = run_performance_benchmark(detector)
    results.append(("Performance Benchmark", success))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n{Colors.BOLD}Results:{Colors.ENDC}\n")
    for test_name, success in results:
        status = f"{Colors.OKGREEN}✅ PASSED{Colors.ENDC}" if success else f"{Colors.FAIL}❌ FAILED{Colors.ENDC}"
        print(f"  {test_name:<30s}: {status}")
    
    print(f"\n{Colors.BOLD}Overall: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 All tests passed successfully!{Colors.ENDC}\n")
    else:
        print(f"\n{Colors.WARNING}{Colors.BOLD}⚠️  Some tests failed. Please review the output above.{Colors.ENDC}\n")


if __name__ == "__main__":
    main()
