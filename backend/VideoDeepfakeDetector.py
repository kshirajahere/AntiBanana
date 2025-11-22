"""
Video Deepfake Detection Engine
Implements intelligent frame sampling and parallel analysis for video content

Features:
- Smart frame sampling with multiple distribution strategies
- Parallel frame processing for performance
- Integration with XAI explanations
- C2PA provenance verification for video frames
- Temporal consistency analysis
- Comprehensive video-level reporting
- Progress tracking and resumable processing

Author: Senior Developer @ Google
Date: November 22, 2025
"""

import os
import sys
import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from collections import defaultdict

# Import detection modules
from DeepfakeDetector import DeepfakeDetector


class VideoFrameSampler:
    """
    Intelligent frame sampling strategies for efficient video analysis.
    """
    
    def __init__(self, total_frames: int, fps: float, duration: float):
        """
        Initialize sampler with video properties.
        
        Args:
            total_frames: Total number of frames in video
            fps: Frames per second
            duration: Video duration in seconds
        """
        self.total_frames = total_frames
        self.fps = fps
        self.duration = duration
    
    def uniform_sampling(self, num_samples: int = 30) -> List[int]:
        """
        Uniform sampling across the entire video.
        
        Args:
            num_samples: Number of frames to sample
            
        Returns:
            List of frame indices
        """
        if num_samples >= self.total_frames:
            return list(range(self.total_frames))
        
        step = self.total_frames / num_samples
        return [int(i * step) for i in range(num_samples)]
    
    def stratified_sampling(self, num_samples: int = 30) -> List[int]:
        """
        Stratified sampling - divides video into segments and samples from each.
        Good for ensuring coverage across the entire video.
        
        Args:
            num_samples: Number of frames to sample
            
        Returns:
            List of frame indices
        """
        segments = min(num_samples, 10)  # Max 10 segments
        frames_per_segment = num_samples // segments
        segment_size = self.total_frames // segments
        
        samples = []
        for i in range(segments):
            segment_start = i * segment_size
            segment_end = (i + 1) * segment_size
            
            # Sample randomly within each segment
            for _ in range(frames_per_segment):
                frame_idx = np.random.randint(segment_start, min(segment_end, self.total_frames))
                samples.append(frame_idx)
        
        # Add remaining samples randomly
        remaining = num_samples - len(samples)
        if remaining > 0:
            extra_samples = np.random.choice(self.total_frames, remaining, replace=False)
            samples.extend(extra_samples.tolist())
        
        return sorted(list(set(samples)))
    
    def adaptive_sampling(self, num_samples: int = 30, bias_to_middle: bool = True) -> List[int]:
        """
        Adaptive sampling with optional bias towards middle of video.
        Uses a weighted distribution.
        
        Args:
            num_samples: Number of frames to sample
            bias_to_middle: Whether to bias sampling towards the middle
            
        Returns:
            List of frame indices
        """
        if num_samples >= self.total_frames:
            return list(range(self.total_frames))
        
        # Create probability distribution
        if bias_to_middle:
            # Gaussian distribution centered at middle
            mean = self.total_frames / 2
            std = self.total_frames / 6  # Cover most of video within 3 std devs
            
            x = np.arange(self.total_frames)
            probabilities = np.exp(-0.5 * ((x - mean) / std) ** 2)
            probabilities = probabilities / probabilities.sum()
        else:
            # Uniform probabilities
            probabilities = np.ones(self.total_frames) / self.total_frames
        
        # Sample based on probabilities
        samples = np.random.choice(
            self.total_frames,
            size=num_samples,
            replace=False,
            p=probabilities
        )
        
        return sorted(samples.tolist())
    
    def scene_aware_sampling(self, num_samples: int = 30, scene_change_threshold: int = 5) -> List[int]:
        """
        Sample with preference for scene changes (key moments).
        Note: This is a heuristic - actual scene detection would require loading frames.
        
        Args:
            num_samples: Number of frames to sample
            scene_change_threshold: Seconds to consider as potential scene boundary
            
        Returns:
            List of frame indices
        """
        # Estimate potential scene boundaries at regular intervals
        scene_interval_frames = int(scene_change_threshold * self.fps)
        
        # Key frames at potential scene boundaries
        key_frames = list(range(0, self.total_frames, scene_interval_frames))
        
        # Add start and end
        key_frames.append(0)
        key_frames.append(self.total_frames - 1)
        key_frames = sorted(list(set(key_frames)))
        
        # If we have enough key frames, sample from them
        if len(key_frames) >= num_samples:
            return sorted(np.random.choice(key_frames, num_samples, replace=False).tolist())
        
        # Otherwise, include all key frames and add random samples
        remaining = num_samples - len(key_frames)
        available_frames = [f for f in range(self.total_frames) if f not in key_frames]
        
        if remaining > 0 and available_frames:
            extra_samples = np.random.choice(available_frames, min(remaining, len(available_frames)), replace=False)
            key_frames.extend(extra_samples.tolist())
        
        return sorted(key_frames)
    
    def smart_sampling(self, num_samples: int = 30, strategy: str = "hybrid") -> List[int]:
        """
        Smart sampling combining multiple strategies.
        
        Args:
            num_samples: Number of frames to sample
            strategy: Sampling strategy ('uniform', 'stratified', 'adaptive', 'scene_aware', 'hybrid')
            
        Returns:
            List of frame indices
        """
        if strategy == "uniform":
            return self.uniform_sampling(num_samples)
        elif strategy == "stratified":
            return self.stratified_sampling(num_samples)
        elif strategy == "adaptive":
            return self.adaptive_sampling(num_samples, bias_to_middle=True)
        elif strategy == "scene_aware":
            return self.scene_aware_sampling(num_samples)
        elif strategy == "hybrid":
            # Combine multiple strategies for best coverage
            uniform_samples = self.uniform_sampling(num_samples // 3)
            stratified_samples = self.stratified_sampling(num_samples // 3)
            adaptive_samples = self.adaptive_sampling(num_samples // 3)
            
            all_samples = list(set(uniform_samples + stratified_samples + adaptive_samples))
            
            # If we need more samples, add random ones
            if len(all_samples) < num_samples:
                remaining = num_samples - len(all_samples)
                available = [f for f in range(self.total_frames) if f not in all_samples]
                if available:
                    extra = np.random.choice(available, min(remaining, len(available)), replace=False)
                    all_samples.extend(extra.tolist())
            
            return sorted(list(set(all_samples)))[:num_samples]
        else:
            # Default to uniform
            return self.uniform_sampling(num_samples)


class VideoDeepfakeDetector:
    """
    Comprehensive video deepfake detection with frame sampling and parallel processing.
    """
    
    def __init__(self, detector: Optional[DeepfakeDetector] = None):
        """
        Initialize video detector.
        
        Args:
            detector: DeepfakeDetector instance (creates new if None)
        """
        self.detector = detector or DeepfakeDetector()
        print("✅ VideoDeepfakeDetector initialized")
    
    def extract_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Extract metadata from video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video metadata
        """
        video = cv2.VideoCapture(video_path)
        
        if not video.isOpened():
            raise ValueError(f"Unable to open video file: {video_path}")
        
        fps = video.get(cv2.CAP_PROP_FPS)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        
        video.release()
        
        # Get file size
        file_size = os.path.getsize(video_path)
        
        # Calculate hash
        file_hash = self._calculate_file_hash(video_path)
        
        return {
            "filename": os.path.basename(video_path),
            "path": video_path,
            "fps": fps,
            "total_frames": total_frames,
            "width": width,
            "height": height,
            "duration": duration,
            "duration_formatted": f"{int(duration // 60)}:{int(duration % 60):02d}",
            "file_size_bytes": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "resolution": f"{width}x{height}",
            "sha256": file_hash
        }
    
    def _calculate_file_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """Calculate SHA-256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def sample_frames(self, video_path: str, num_samples: int = 30, 
                     strategy: str = "hybrid") -> Tuple[List[int], List[str]]:
        """
        Sample frames from video using intelligent sampling.
        
        Args:
            video_path: Path to video file
            num_samples: Number of frames to sample
            strategy: Sampling strategy
            
        Returns:
            Tuple of (frame_indices, frame_paths)
        """
        print(f"🎬 Sampling {num_samples} frames from video using '{strategy}' strategy...")
        
        # Get video info
        video_info = self.extract_video_info(video_path)
        
        # Initialize sampler
        sampler = VideoFrameSampler(
            video_info['total_frames'],
            video_info['fps'],
            video_info['duration']
        )
        
        # Get frame indices
        frame_indices = sampler.smart_sampling(num_samples, strategy)
        
        # Extract frames
        frame_paths = self._extract_frames_at_indices(video_path, frame_indices)
        
        print(f"✅ Sampled {len(frame_paths)} frames")
        
        return frame_indices, frame_paths
    
    def _extract_frames_at_indices(self, video_path: str, indices: List[int]) -> List[str]:
        """
        Extract specific frames from video.
        
        Args:
            video_path: Path to video file
            indices: List of frame indices to extract
            
        Returns:
            List of paths to extracted frames
        """
        # Create temp directory for frames
        temp_dir = tempfile.mkdtemp(prefix="video_frames_")
        
        video = cv2.VideoCapture(video_path)
        frame_paths = []
        
        current_frame = 0
        indices_set = set(indices)
        
        while video.isOpened():
            ret, frame = video.read()
            
            if not ret:
                break
            
            if current_frame in indices_set:
                frame_path = os.path.join(temp_dir, f"frame_{current_frame:06d}.jpg")
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
            
            current_frame += 1
            
            # Early exit if we've extracted all needed frames
            if len(frame_paths) == len(indices):
                break
        
        video.release()
        
        return frame_paths
    
    def analyze_frame(self, frame_path: str, frame_idx: int, 
                     include_xai: bool = False, include_c2pa: bool = True) -> Dict[str, Any]:
        """
        Analyze a single frame.
        
        Args:
            frame_path: Path to frame image
            frame_idx: Frame index in video
            include_xai: Whether to include XAI explanations
            include_c2pa: Whether to include C2PA verification
            
        Returns:
            Detection result for the frame
        """
        try:
            # Run detection
            result = self.detector.detect_all(frame_path, include_c2pa=include_c2pa)
            
            # Add frame metadata
            result['frame_index'] = frame_idx
            result['frame_path'] = frame_path
            
            # Add XAI if requested (quick mode for videos)
            if include_xai:
                try:
                    xai_result = self.detector.generate_explainability(
                        frame_path,
                        method='gradcam',  # GradCAM is fastest for videos
                        quick_mode=True
                    )
                    result['xai'] = xai_result
                except Exception as e:
                    result['xai_error'] = str(e)
            
            return result
            
        except Exception as e:
            return {
                'frame_index': frame_idx,
                'frame_path': frame_path,
                'error': str(e)
            }
    
    def analyze_video_parallel(self, video_path: str, num_samples: int = 30,
                               strategy: str = "hybrid", max_workers: int = 4,
                               include_xai: bool = False, include_c2pa: bool = False) -> Dict[str, Any]:
        """
        Analyze video with parallel frame processing.
        
        Args:
            video_path: Path to video file
            num_samples: Number of frames to sample
            strategy: Sampling strategy
            max_workers: Number of parallel workers
            include_xai: Whether to include XAI explanations
            include_c2pa: Whether to include C2PA verification
            
        Returns:
            Comprehensive video analysis report
        """
        print("\n" + "="*80)
        print("🎥 VIDEO DEEPFAKE DETECTION - COMPREHENSIVE ANALYSIS")
        print("="*80)
        
        start_time = datetime.now()
        
        # Extract video info
        print("\n📊 Extracting video metadata...")
        video_info = self.extract_video_info(video_path)
        
        print(f"\n   Filename: {video_info['filename']}")
        print(f"   Duration: {video_info['duration_formatted']}")
        print(f"   Resolution: {video_info['resolution']}")
        print(f"   FPS: {video_info['fps']:.2f}")
        print(f"   Total Frames: {video_info['total_frames']}")
        print(f"   Size: {video_info['file_size_mb']:.2f} MB")
        
        # Sample frames
        frame_indices, frame_paths = self.sample_frames(video_path, num_samples, strategy)
        
        print(f"\n🔍 Analyzing {len(frame_paths)} frames in parallel (workers: {max_workers})...")
        
        # Analyze frames in parallel
        frame_results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.analyze_frame, 
                    frame_path, 
                    frame_idx,
                    include_xai,
                    include_c2pa
                ): (frame_idx, frame_path) 
                for frame_idx, frame_path in zip(frame_indices, frame_paths)
            }
            
            completed = 0
            for future in as_completed(futures):
                result = future.result()
                frame_results.append(result)
                completed += 1
                
                # Progress indicator
                progress = (completed / len(frame_paths)) * 100
                print(f"   Progress: {progress:.1f}% ({completed}/{len(frame_paths)}) - "
                      f"Frame {result.get('frame_index', '?')}: {result.get('verdict', 'Error')}")
        
        # Sort results by frame index
        frame_results.sort(key=lambda x: x.get('frame_index', 0))
        
        # Aggregate results
        print("\n📈 Aggregating results...")
        aggregated_report = self._aggregate_frame_results(frame_results, video_info, strategy)
        
        # Add frame paths to report for PDF generation
        aggregated_report['frame_paths'] = frame_paths
        
        # Add frame scores (confidence values) for visualization
        frame_scores = [r.get('confidence', 0) for r in frame_results if 'error' not in r]
        aggregated_report['frame_scores'] = frame_scores
        
        # Calculate temporal consistency
        print("⏱️  Analyzing temporal consistency...")
        temporal_analysis = self._analyze_temporal_consistency(frame_results)
        aggregated_report['temporal_analysis'] = temporal_analysis
        
        # Clean up temp frames
        if frame_paths:
            temp_dir = os.path.dirname(frame_paths[0])
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
        
        # Add timing
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        aggregated_report['processing_time_seconds'] = processing_time
        aggregated_report['processing_time_formatted'] = f"{int(processing_time // 60)}:{int(processing_time % 60):02d}"
        
        print("\n" + "="*80)
        print("✅ VIDEO ANALYSIS COMPLETE")
        print("="*80)
        print(f"   Processing Time: {aggregated_report['processing_time_formatted']}")
        print(f"   Verdict: {aggregated_report['overall_verdict']}")
        print(f"   Confidence: {aggregated_report['overall_confidence']:.2%}")
        print(f"   Fake Frames: {aggregated_report['statistics']['fake_frames']}/{aggregated_report['statistics']['total_frames']}")
        
        return aggregated_report
    
    def _aggregate_frame_results(self, frame_results: List[Dict], 
                                 video_info: Dict, strategy: str) -> Dict[str, Any]:
        """
        Aggregate frame-level results into video-level report.
        
        Args:
            frame_results: List of frame detection results
            video_info: Video metadata
            strategy: Sampling strategy used
            
        Returns:
            Aggregated video analysis report
        """
        # Count verdicts
        fake_count = sum(1 for r in frame_results if r.get('verdict') == 'Fake')
        real_count = sum(1 for r in frame_results if r.get('verdict') == 'Real')
        error_count = sum(1 for r in frame_results if 'error' in r)
        
        total_valid = len(frame_results) - error_count
        
        # Calculate statistics
        if total_valid > 0:
            confidences = [r.get('confidence', 0) for r in frame_results if 'error' not in r]
            avg_confidence = np.mean(confidences) if confidences else 0
            max_confidence = np.max(confidences) if confidences else 0
            min_confidence = np.min(confidences) if confidences else 0
            std_confidence = np.std(confidences) if confidences else 0
            
            # Overall verdict based on majority and high confidence frames
            fake_ratio = fake_count / total_valid
            high_confidence_fakes = sum(1 for r in frame_results 
                                       if r.get('verdict') == 'Fake' and r.get('confidence', 0) > 0.7)
            
            # Decision logic
            if fake_ratio > 0.5:  # Majority fake
                overall_verdict = "Fake"
                overall_confidence = avg_confidence
            elif high_confidence_fakes >= 3:  # At least 3 high-confidence fakes
                overall_verdict = "Fake"
                overall_confidence = avg_confidence * 0.9  # Slightly reduce confidence
            elif fake_ratio > 0.3:  # Significant fake content
                overall_verdict = "Suspicious"
                overall_confidence = avg_confidence * 0.8
            else:
                overall_verdict = "Real"
                overall_confidence = 1 - avg_confidence
        else:
            overall_verdict = "Error"
            overall_confidence = 0
            avg_confidence = 0
            max_confidence = 0
            min_confidence = 0
            std_confidence = 0
        
        # Aggregate C2PA data if available
        c2pa_summary = self._aggregate_c2pa_data(frame_results)
        
        # Build comprehensive report
        report = {
            "video_info": video_info,
            "sampling": {
                "strategy": strategy,
                "num_samples": len(frame_results),
                "frame_indices": [r.get('frame_index') for r in frame_results if 'frame_index' in r]
            },
            "overall_verdict": overall_verdict,
            "overall_confidence": float(overall_confidence),
            "statistics": {
                "total_frames": len(frame_results),
                "fake_frames": fake_count,
                "real_frames": real_count,
                "error_frames": error_count,
                "fake_ratio": float(fake_ratio) if total_valid > 0 else 0,
                "avg_confidence": float(avg_confidence),
                "max_confidence": float(max_confidence),
                "min_confidence": float(min_confidence),
                "std_confidence": float(std_confidence)
            },
            "frame_results": frame_results,
            "c2pa_summary": c2pa_summary,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        return report
    
    def _aggregate_c2pa_data(self, frame_results: List[Dict]) -> Dict[str, Any]:
        """Aggregate C2PA data from all frames."""
        c2pa_frames = [r for r in frame_results if 'c2pa_provenance' in r]
        
        if not c2pa_frames:
            return {
                "has_c2pa": False,
                "frames_with_c2pa": 0,
                "message": "No C2PA data found in any frames"
            }
        
        verified_count = sum(1 for r in c2pa_frames 
                            if r['c2pa_provenance'].get('verified', False))
        
        trust_levels = defaultdict(int)
        for r in c2pa_frames:
            trust_level = r['c2pa_provenance'].get('trust_level', 'unknown')
            trust_levels[trust_level] += 1
        
        return {
            "has_c2pa": True,
            "frames_with_c2pa": len(c2pa_frames),
            "verified_frames": verified_count,
            "trust_levels": dict(trust_levels),
            "verification_ratio": verified_count / len(c2pa_frames) if c2pa_frames else 0
        }
    
    def _analyze_temporal_consistency(self, frame_results: List[Dict]) -> Dict[str, Any]:
        """
        Analyze temporal consistency across frames.
        
        Args:
            frame_results: List of frame detection results
            
        Returns:
            Temporal consistency analysis
        """
        # Extract confidence scores over time
        confidences = []
        frame_indices = []
        
        for r in frame_results:
            if 'error' not in r:
                confidences.append(r.get('confidence', 0))
                frame_indices.append(r.get('frame_index', 0))
        
        if len(confidences) < 2:
            return {
                "consistency_score": 0,
                "variance": 0,
                "transitions": 0,
                "message": "Insufficient data for temporal analysis"
            }
        
        # Calculate variance (low variance = consistent)
        variance = float(np.var(confidences))
        
        # Count verdict transitions (Real -> Fake or vice versa)
        transitions = 0
        for i in range(1, len(frame_results)):
            if 'error' not in frame_results[i] and 'error' not in frame_results[i-1]:
                if frame_results[i].get('verdict') != frame_results[i-1].get('verdict'):
                    transitions += 1
        
        # Consistency score (higher = more consistent)
        consistency_score = 1 - min(variance, 1.0)  # Normalize to 0-1
        
        # Trend analysis
        if len(confidences) > 5:
            # Simple linear trend
            x = np.arange(len(confidences))
            z = np.polyfit(x, confidences, 1)
            trend = "increasing" if z[0] > 0.01 else "decreasing" if z[0] < -0.01 else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "consistency_score": float(consistency_score),
            "variance": float(variance),
            "transitions": transitions,
            "trend": trend,
            "message": f"{'High' if consistency_score > 0.7 else 'Low'} temporal consistency"
        }


def analyze_video(video_path: str, num_samples: int = 30, strategy: str = "hybrid",
                 max_workers: int = 4, include_xai: bool = False, 
                 include_c2pa: bool = False) -> Dict[str, Any]:
    """
    Convenience function for video analysis.
    
    Args:
        video_path: Path to video file
        num_samples: Number of frames to sample
        strategy: Sampling strategy
        max_workers: Number of parallel workers
        include_xai: Include XAI explanations
        include_c2pa: Include C2PA verification
        
    Returns:
        Video analysis report
    """
    detector = VideoDeepfakeDetector()
    return detector.analyze_video_parallel(
        video_path,
        num_samples=num_samples,
        strategy=strategy,
        max_workers=max_workers,
        include_xai=include_xai,
        include_c2pa=include_c2pa
    )
