"""
Media Protection Module - Updated with MMHI Framework

This module provides API-compatible functions for protecting images
using the Multi-Modal Hallucination Injection (MMHI) framework.

Legacy API maintained for backward compatibility, but now powered by MMHI.
"""

import base64
import io
import sys
import os
from pathlib import Path
from io import BytesIO
from PIL import Image
from typing import Optional

# Add backend to path to allow importing mmhi_protection as a package
current_dir = Path(__file__).parent
backend_dir = current_dir.parent
sys.path.insert(0, str(backend_dir))

# Import MMHI framework
try:
    from mmhi_protection.mmhi_pipeline import MMHIPipeline
    from mmhi_protection.api import get_mmhi_api
    MMHI_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MMHI framework not available: {e}")
    print("Falling back to basic protection mode")
    MMHI_AVAILABLE = False

# Global MMHI API instance (lazy initialization)
_mmhi_api = None


def get_protection_api(strength: str = "medium"):
    """
    Get or initialize the MMHI protection API.

    Args:
        strength: Protection strength ('low', 'medium', 'high', 'extreme')

    Returns:
        MMHI API instance
    """
    global _mmhi_api

    if not MMHI_AVAILABLE:
        raise RuntimeError("MMHI framework not available")

    if _mmhi_api is None:
        _mmhi_api = get_mmhi_api(default_strength=strength)

    return _mmhi_api


def model_run(b64_source: str, strength: str = "medium", phases: Optional[list] = None) -> str:
    """
    Protect an image using MMHI framework (new implementation).

    This replaces the old PGD-based VAE attack with the comprehensive
    Multi-Modal Hallucination Injection framework.

    Args:
        b64_source: Base64-encoded input image
        strength: Protection strength ('low', 'medium', 'high', 'extreme')
        phases: List of phases to enable (default: [1, 2, 3, 4])

    Returns:
        Base64-encoded protected image
    """
    if not MMHI_AVAILABLE:
        raise RuntimeError("MMHI framework not available")

    # Get MMHI API
    api = get_protection_api(strength)

    # Protect image using MMHI
    result = api.protect_base64(
        b64_string=b64_source,
        strength=strength,
        phases=phases
    )

    # Return protected image as base64
    return result['protected_image_b64']


def predict(prompt: str, strength: str = "medium") -> str:
    """
    Legacy API endpoint for protecting images.

    Args:
        prompt: Base64-encoded image (legacy parameter name kept for compatibility)
        strength: Protection strength

    Returns:
        Base64-encoded protected image
    """
    return model_run(prompt, strength=strength)


def protect_image_advanced(
    b64_source: str,
    strength: str = "medium",
    phases: Optional[list] = None,
    return_info: bool = False
):
    """
    Advanced protection with detailed information.

    Args:
        b64_source: Base64-encoded input image
        strength: Protection strength
        phases: List of phases to enable
        return_info: Whether to return protection info

    Returns:
        Protected image (base64) or tuple of (image, info) if return_info=True
    """
    if not MMHI_AVAILABLE:
        raise RuntimeError("MMHI framework not available")

    api = get_protection_api(strength)

    result = api.protect_base64(
        b64_string=b64_source,
        strength=strength,
        phases=phases
    )

    if return_info:
        return result['protected_image_b64'], result
    else:
        return result['protected_image_b64']


# Backward compatibility - keep old function names
def old_pgd_protection(b64_source: str) -> str:
    """
    Old PGD-based VAE protection (deprecated).

    This function is kept for reference but is deprecated.
    Use model_run() or protect_image_advanced() instead.
    """
    print("Warning: old_pgd_protection is deprecated. Using MMHI framework instead.")
    return model_run(b64_source, strength="low", phases=[4])  # Phase 4 includes VAE attack


if __name__ == "__main__":
    # Test the new implementation
    print("Testing MMHI Media Protection Module")

    if not MMHI_AVAILABLE:
        print("Error: MMHI framework not available")
        sys.exit(1)

    # Test with a sample image
    # Use Path to handle file existence check correctly
    test_image_path = Path(r"C:\Users\sayal\Downloads\pratz1.jpg")

    if test_image_path.exists():
        print(f"Testing with: {test_image_path}")

        # Load and encode image
        with open(test_image_path, 'rb') as f:
            image_data = f.read()
            b64_image = base64.b64encode(image_data).decode('utf-8')

        # Protect image
        print("Applying MMHI protection...")
        protected_b64, info = protect_image_advanced(
            b64_image,
            strength="medium",
            phases=[1, 2, 3, 4, 5, 6, 7, 8, 9],  # Test all phases
            return_info=True
        )

        # Save result
        output_path = backend_dir / "media_protected_test.png"
        protected_data = base64.b64decode(protected_b64)
        with open(output_path, 'wb') as f:
            f.write(protected_data)

        print(f"✅ Protection successful!")
        print(f"📁 Saved to: {output_path}")
        print(f"⏱️  Processing time: {info['processing_time_seconds']}s")
        print(f"🎯 Phases applied: {info['phases_applied']}")
    else:
        print(f"Test image not found: {test_image_path}")
        print("Place a test_image.jpg in the backend directory to test")