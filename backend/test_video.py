"""
Comprehensive Test Suite for Video Deepfake Detection

Tests intelligent frame sampling, parallel processing, and video analysis.

Author: Senior Developer @ Google
Date: November 22, 2025
"""

import os
import sys
import argparse
import json
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from VideoDeepfakeDetector import VideoDeepfakeDetector, VideoFrameSampler, analyze_video


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(title)
    print("="*80)


def test_video_info_extraction(detector, video_path):
    """Test video metadata extraction."""
    print_section("TEST 1: Video Information Extraction")
    
    print(f"\n📹 Extracting metadata from: {os.path.basename(video_path)}")
    
    video_info = detector.extract_video_info(video_path)
    
    print(f"\n✅ Video Metadata:")
    print(f"   Filename: {video_info['filename']}")
    print(f"   Duration: {video_info['duration_formatted']} ({video_info['duration']:.2f}s)")
    print(f"   Resolution: {video_info['resolution']}")
    print(f"   FPS: {video_info['fps']:.2f}")
    print(f"   Total Frames: {video_info['total_frames']}")
    print(f"   File Size: {video_info['file_size_mb']:.2f} MB")
    print(f"   SHA-256: {video_info['sha256'][:32]}...")
    
    return video_info


def test_frame_sampling_strategies(detector, video_path, num_samples=20):
    """Test different frame sampling strategies."""
    print_section("TEST 2: Frame Sampling Strategies")
    
    video_info = detector.extract_video_info(video_path)
    sampler = VideoFrameSampler(
        video_info['total_frames'],
        video_info['fps'],
        video_info['duration']
    )
    
    strategies = ['uniform', 'stratified', 'adaptive', 'scene_aware', 'hybrid']
    
    for strategy in strategies:
        print(f"\n🎯 Testing '{strategy}' sampling strategy:")
        frame_indices = sampler.smart_sampling(num_samples, strategy)
        
        print(f"   Sampled {len(frame_indices)} frames")
        print(f"   Frame indices: {frame_indices[:10]}{'...' if len(frame_indices) > 10 else ''}")
        print(f"   Coverage: {frame_indices[0]} to {frame_indices[-1]} "
              f"(span: {frame_indices[-1] - frame_indices[0]} frames)")
    
    return sampler


def test_frame_extraction(detector, video_path, num_samples=10):
    """Test frame extraction from video."""
    print_section("TEST 3: Frame Extraction")
    
    print(f"\n📸 Extracting {num_samples} frames from video...")
    
    frame_indices, frame_paths = detector.sample_frames(
        video_path,
        num_samples=num_samples,
        strategy='hybrid'
    )
    
    print(f"\n✅ Extracted {len(frame_paths)} frames:")
    for i, (idx, path) in enumerate(zip(frame_indices[:5], frame_paths[:5])):
        file_size = os.path.getsize(path) / 1024  # KB
        print(f"   {i+1}. Frame {idx}: {os.path.basename(path)} ({file_size:.1f} KB)")
    
    if len(frame_paths) > 5:
        print(f"   ... and {len(frame_paths) - 5} more frames")
    
    # Clean up
    if frame_paths:
        import shutil
        temp_dir = os.path.dirname(frame_paths[0])
        shutil.rmtree(temp_dir)
        print(f"\n   🧹 Cleaned up temporary directory")
    
    return frame_indices, frame_paths


def test_single_video_analysis(detector, video_path, num_samples=15):
    """Test complete video analysis with default settings."""
    print_section("TEST 4: Single Video Analysis")
    
    print(f"\n🎬 Analyzing video: {os.path.basename(video_path)}")
    print(f"   Samples: {num_samples}")
    print(f"   Strategy: hybrid")
    print(f"   Workers: 4")
    
    result = detector.analyze_video_parallel(
        video_path,
        num_samples=num_samples,
        strategy='hybrid',
        max_workers=4,
        include_xai=False,
        include_c2pa=False
    )
    
    print(f"\n📊 Analysis Results:")
    print(f"   Overall Verdict: {result['overall_verdict']}")
    print(f"   Overall Confidence: {result['overall_confidence']:.2%}")
    print(f"   Processing Time: {result['processing_time_formatted']}")
    
    stats = result['statistics']
    print(f"\n   Statistics:")
    print(f"   - Total Frames Analyzed: {stats['total_frames']}")
    print(f"   - Fake Frames: {stats['fake_frames']}")
    print(f"   - Real Frames: {stats['real_frames']}")
    print(f"   - Fake Ratio: {stats['fake_ratio']:.2%}")
    print(f"   - Avg Confidence: {stats['avg_confidence']:.2%}")
    print(f"   - Std Confidence: {stats['std_confidence']:.4f}")
    
    temporal = result.get('temporal_analysis', {})
    print(f"\n   Temporal Analysis:")
    print(f"   - Consistency Score: {temporal.get('consistency_score', 0):.2%}")
    print(f"   - Variance: {temporal.get('variance', 0):.4f}")
    print(f"   - Transitions: {temporal.get('transitions', 0)}")
    print(f"   - Trend: {temporal.get('trend', 'N/A')}")
    
    # Save report
    output_dir = Path(__file__).parent / 'video_reports'
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / f"{Path(video_path).stem}_report.json"
    with open(report_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n   💾 Full report saved to: {report_file}")
    
    return result


def test_video_with_xai(detector, video_path, num_samples=10):
    """Test video analysis with XAI explanations."""
    print_section("TEST 5: Video Analysis with XAI")
    
    print(f"\n🔍 Analyzing video with XAI explanations (GradCAM)...")
    print(f"   Note: XAI increases processing time significantly")
    
    result = detector.analyze_video_parallel(
        video_path,
        num_samples=num_samples,
        strategy='uniform',
        max_workers=2,  # Reduce workers for XAI
        include_xai=True,
        include_c2pa=False
    )
    
    print(f"\n📊 Analysis Complete:")
    print(f"   Verdict: {result['overall_verdict']}")
    print(f"   Processing Time: {result['processing_time_formatted']}")
    
    # Count frames with XAI
    frames_with_xai = sum(1 for f in result['frame_results'] if 'xai' in f)
    print(f"   Frames with XAI: {frames_with_xai}/{len(result['frame_results'])}")
    
    return result


def test_video_with_c2pa(detector, video_path, num_samples=10):
    """Test video analysis with C2PA verification."""
    print_section("TEST 6: Video Analysis with C2PA")
    
    print(f"\n🔐 Analyzing video with C2PA verification...")
    
    result = detector.analyze_video_parallel(
        video_path,
        num_samples=num_samples,
        strategy='stratified',
        max_workers=4,
        include_xai=False,
        include_c2pa=True
    )
    
    print(f"\n📊 Analysis Complete:")
    print(f"   Verdict: {result['overall_verdict']}")
    
    c2pa_summary = result.get('c2pa_summary', {})
    print(f"\n   C2PA Summary:")
    print(f"   - Has C2PA: {c2pa_summary.get('has_c2pa', False)}")
    print(f"   - Frames with C2PA: {c2pa_summary.get('frames_with_c2pa', 0)}")
    print(f"   - Verified Frames: {c2pa_summary.get('verified_frames', 0)}")
    
    return result


def test_comparison_strategies(detector, video_path, num_samples=20):
    """Compare different sampling strategies."""
    print_section("TEST 7: Strategy Comparison")
    
    strategies = ['uniform', 'stratified', 'adaptive', 'hybrid']
    results = {}
    
    print(f"\n📊 Comparing sampling strategies on {num_samples} frames...")
    
    for strategy in strategies:
        print(f"\n   Testing '{strategy}'...")
        
        result = detector.analyze_video_parallel(
            video_path,
            num_samples=num_samples,
            strategy=strategy,
            max_workers=4,
            include_xai=False,
            include_c2pa=False
        )
        
        results[strategy] = {
            'verdict': result['overall_verdict'],
            'confidence': result['overall_confidence'],
            'fake_ratio': result['statistics']['fake_ratio'],
            'processing_time': result['processing_time_seconds'],
            'consistency': result['temporal_analysis']['consistency_score']
        }
    
    print(f"\n📈 Comparison Results:")
    print(f"\n{'Strategy':<15} {'Verdict':<12} {'Confidence':<12} {'Fake Ratio':<12} {'Time (s)':<10} {'Consistency':<12}")
    print("-" * 80)
    
    for strategy, data in results.items():
        print(f"{strategy:<15} {data['verdict']:<12} {data['confidence']:<12.2%} "
              f"{data['fake_ratio']:<12.2%} {data['processing_time']:<10.1f} {data['consistency']:<12.2%}")
    
    return results


def run_all_tests(video_path, quick=False):
    """Run all video detection tests."""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE VIDEO DEEPFAKE DETECTION TEST SUITE")
    print("="*80)
    print(f"\n📁 Video: {video_path}")
    
    # Verify video exists
    if not os.path.exists(video_path):
        print(f"\n❌ Error: Video not found at {video_path}")
        return
    
    # Initialize detector
    print("\n🔄 Initializing Video Deepfake Detector...")
    detector = VideoDeepfakeDetector()
    
    # Run tests
    test_video_info_extraction(detector, video_path)
    test_frame_sampling_strategies(detector, video_path, num_samples=15)
    test_frame_extraction(detector, video_path, num_samples=10)
    
    if quick:
        print("\n⚡ Quick mode: Running single analysis only")
        test_single_video_analysis(detector, video_path, num_samples=15)
    else:
        test_single_video_analysis(detector, video_path, num_samples=20)
        test_video_with_xai(detector, video_path, num_samples=8)
        test_video_with_c2pa(detector, video_path, num_samples=10)
        test_comparison_strategies(detector, video_path, num_samples=15)
    
    print("\n" + "="*80)
    print("✅ ALL VIDEO TESTS COMPLETED")
    print("="*80)
    print("\n📁 Reports saved to: ./video_reports/")


def main():
    parser = argparse.ArgumentParser(
        description='Test Video Deepfake Detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full test suite
  python test_video.py video.mp4
  
  # Quick test
  python test_video.py video.mp4 --quick
  
  # Single analysis with custom settings
  python test_video.py video.mp4 --samples 30 --strategy hybrid

Features Tested:
  1. Video Information Extraction
  2. Frame Sampling Strategies
  3. Frame Extraction
  4. Single Video Analysis
  5. Video Analysis with XAI
  6. Video Analysis with C2PA
  7. Strategy Comparison
        """
    )
    
    parser.add_argument('video', help='Path to the video file to analyze')
    parser.add_argument('--quick', action='store_true', 
                       help='Quick test mode (single analysis only)')
    parser.add_argument('--samples', type=int, default=20,
                       help='Number of frames to sample (default: 20)')
    parser.add_argument('--strategy', default='hybrid',
                       help='Sampling strategy (default: hybrid)')
    
    args = parser.parse_args()
    
    if args.quick:
        run_all_tests(args.video, quick=True)
    elif args.samples or args.strategy != 'hybrid':
        # Custom single analysis
        print("\n🎬 Custom Video Analysis")
        print("="*80)
        detector = VideoDeepfakeDetector()
        result = detector.analyze_video_parallel(
            args.video,
            num_samples=args.samples,
            strategy=args.strategy,
            max_workers=4
        )
        print(f"\nVerdict: {result['overall_verdict']}")
        print(f"Confidence: {result['overall_confidence']:.2%}")
    else:
        run_all_tests(args.video, quick=False)


if __name__ == '__main__':
    main()
