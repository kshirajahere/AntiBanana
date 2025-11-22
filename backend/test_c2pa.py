"""
Comprehensive Test Suite for C2PA Provenance Verification

This script demonstrates C2PA content authenticity features including:
- Manifest extraction and parsing
- Chain of custody verification
- Cryptographic signature validation
- Edit history timeline
- Provenance reporting
- Metadata integrity analysis

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

from C2PAVerifier import C2PAVerifier, quick_verify, generate_full_report


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(title)
    print("="*80)


def test_manifest_extraction(verifier, image_path):
    """Test C2PA manifest extraction."""
    print_section("TEST 1: C2PA Manifest Extraction")
    
    print(f"\n📄 Extracting C2PA manifest from: {os.path.basename(image_path)}")
    
    result = verifier.extract_c2pa_manifest(image_path)
    
    if result.get("has_c2pa", False):
        print("\n✅ C2PA Manifest Found!")
        print(f"   Active Manifest: {result.get('active_manifest', 'N/A')}")
        
        manifest_data = result.get('manifest_data', {})
        print(f"   Title: {manifest_data.get('title', 'N/A')}")
        print(f"   Format: {manifest_data.get('format', 'N/A')}")
        print(f"   Claim Generator: {manifest_data.get('claim_generator', 'N/A')}")
        
        # Count assertions
        assertions = manifest_data.get('assertions', [])
        print(f"   Assertions: {len(assertions)}")
        
        # Count ingredients
        ingredients = manifest_data.get('ingredients', [])
        print(f"   Ingredients: {len(ingredients)}")
        
    else:
        print("\n❌ No C2PA Manifest Found")
        if 'error' in result:
            print(f"   Error: {result['error']}")
        else:
            print(f"   Message: {result.get('message', 'Unknown')}")
    
    return result


def test_chain_of_custody(verifier, image_path):
    """Test chain of custody verification."""
    print_section("TEST 2: Chain of Custody Verification")
    
    print(f"\n🔐 Verifying chain of custody for: {os.path.basename(image_path)}")
    
    result = verifier.verify_chain_of_custody(image_path)
    
    print(f"\n📊 Verification Results:")
    print(f"   Has C2PA: {result.get('has_c2pa', False)}")
    print(f"   Verified: {result.get('verified', False)}")
    print(f"   Trust Level: {result.get('trust_level', 'unknown').upper()}")
    print(f"   Risk Score: {result.get('risk_score', 1.0):.2f}")
    
    if result.get('has_c2pa', False):
        print(f"\n   Claim Generator: {result.get('claim_generator', 'Unknown')}")
        print(f"   Signature Valid: {result.get('signature_valid', False)}")
        print(f"   Assertions: {len(result.get('assertions', []))}")
        print(f"   Ingredients: {len(result.get('ingredients', []))}")
        print(f"   Edit History: {len(result.get('edit_history', []))} entries")
    
    # Print warnings
    warnings = result.get('warnings', [])
    if warnings:
        print(f"\n⚠️  Warnings ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    else:
        print("\n✅ No warnings")
    
    return result


def test_edit_history(verifier, image_path):
    """Test edit history extraction."""
    print_section("TEST 3: Edit History Analysis")
    
    print(f"\n📝 Extracting edit history from: {os.path.basename(image_path)}")
    
    result = verifier.verify_chain_of_custody(image_path)
    edit_history = result.get('edit_history', [])
    
    if edit_history:
        print(f"\n✅ Found {len(edit_history)} edit(s)")
        print("\n   Edit Timeline:")
        
        for i, edit in enumerate(edit_history, 1):
            print(f"\n   [{i}] {edit.get('action', 'Unknown')}")
            print(f"       When: {edit.get('when', 'Unknown')}")
            print(f"       Software: {edit.get('software_agent', 'Unknown')}")
            
            params = edit.get('parameters', {})
            if params:
                print(f"       Parameters: {json.dumps(params, indent=10)[:100]}...")
    else:
        print("\n❌ No edit history found")
        if result.get('has_c2pa', False):
            print("   (C2PA manifest exists but contains no edit actions)")
        else:
            print("   (No C2PA manifest present)")
    
    return edit_history


def test_provenance_report(verifier, image_path):
    """Test comprehensive provenance report."""
    print_section("TEST 4: Comprehensive Provenance Report")
    
    print(f"\n📋 Generating provenance report for: {os.path.basename(image_path)}")
    
    report = verifier.generate_provenance_report(image_path)
    
    # File info
    file_info = report.get('file_info', {})
    print(f"\n📁 File Information:")
    print(f"   Filename: {file_info.get('filename', 'N/A')}")
    print(f"   Size: {file_info.get('size_bytes', 0):,} bytes")
    print(f"   Created: {file_info.get('created', 'N/A')}")
    print(f"   Modified: {file_info.get('modified', 'N/A')}")
    print(f"   SHA-256: {file_info.get('sha256_hash', 'N/A')[:32]}...")
    
    # Summary
    summary = report.get('summary', {})
    print(f"\n📊 Summary:")
    print(f"   Has C2PA: {summary.get('has_c2pa', False)}")
    print(f"   Verified: {summary.get('verified', False)}")
    print(f"   Trust Level: {summary.get('trust_level', 'unknown').upper()}")
    print(f"   Risk Score: {summary.get('risk_score', 1.0):.2f}")
    print(f"   Warnings: {summary.get('warnings_count', 0)}")
    
    # Recommendations
    recommendations = report.get('recommendations', [])
    if recommendations:
        print(f"\n💡 Recommendations ({len(recommendations)}):")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
    
    # Save full report
    output_dir = Path(__file__).parent / 'c2pa_reports'
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / f"{Path(image_path).stem}_c2pa_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Full report saved to: {report_file}")
    
    return report


def test_fallback_metadata(verifier, image_path):
    """Test fallback metadata analysis (EXIF)."""
    print_section("TEST 5: Fallback Metadata Analysis")
    
    print(f"\n🔍 Analyzing EXIF metadata for: {os.path.basename(image_path)}")
    
    exif_data = verifier._extract_exif_data(image_path)
    
    if exif_data and 'error' not in exif_data:
        print(f"\n✅ EXIF Data Found")
        
        # Key metadata
        print(f"\n   Camera Information:")
        print(f"   - Make: {exif_data.get('camera_make', 'N/A')}")
        print(f"   - Model: {exif_data.get('camera_model', 'N/A')}")
        
        print(f"\n   Software:")
        print(f"   - Software: {exif_data.get('software', 'N/A')}")
        
        print(f"\n   Timestamps:")
        print(f"   - DateTime: {exif_data.get('datetime', 'N/A')}")
        print(f"   - DateTimeOriginal: {exif_data.get('datetime_original', 'N/A')}")
        print(f"   - DateTimeDigitized: {exif_data.get('datetime_digitized', 'N/A')}")
        
        print(f"\n   Creator Information:")
        print(f"   - Artist: {exif_data.get('artist', 'N/A')}")
        print(f"   - Copyright: {exif_data.get('copyright', 'N/A')}")
        
        # Count all tags
        all_tags = exif_data.get('all_tags', {})
        print(f"\n   Total EXIF tags: {len(all_tags)}")
        
    else:
        print("\n❌ No EXIF Data Found")
        if 'error' in exif_data:
            print(f"   Error: {exif_data['error']}")
    
    # Metadata integrity
    integrity = verifier._analyze_metadata_integrity(exif_data, image_path)
    
    print(f"\n🔒 Metadata Integrity:")
    print(f"   Metadata Present: {integrity.get('metadata_present', False)}")
    print(f"   Metadata Stripped: {integrity.get('metadata_stripped', False)}")
    print(f"   Software Detected: {integrity.get('software_detected', False)}")
    print(f"   Camera Info Present: {integrity.get('camera_info_present', False)}")
    print(f"   Inconsistent Timestamps: {integrity.get('inconsistent_timestamps', False)}")
    
    return exif_data, integrity


def test_visual_timeline(verifier, image_path):
    """Test visual timeline generation."""
    print_section("TEST 6: Visual Timeline Generation")
    
    print(f"\n📈 Creating visual timeline for: {os.path.basename(image_path)}")
    
    # Get chain of custody
    result = verifier.verify_chain_of_custody(image_path)
    
    # Create timeline
    timeline = verifier.create_visual_timeline(result)
    
    if timeline:
        print("\n✅ Timeline visualization created")
        
        # Save timeline
        output_dir = Path(__file__).parent / 'c2pa_reports'
        output_dir.mkdir(exist_ok=True)
        
        # Convert base64 to HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>C2PA Timeline - {os.path.basename(image_path)}</title>
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
            <img src="{timeline}" alt="C2PA Timeline">
        </body>
        </html>
        """
        
        timeline_file = output_dir / f"{Path(image_path).stem}_timeline.html"
        with open(timeline_file, 'w') as f:
            f.write(html_content)
        
        print(f"   💾 Timeline saved to: {timeline_file}")
    else:
        print("\n❌ Timeline visualization not available")
        print("   (No edit history found or error during generation)")
    
    return timeline


def run_all_tests(image_path):
    """Run all C2PA tests."""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE C2PA VERIFICATION TEST SUITE")
    print("="*80)
    print(f"\n📁 Image: {image_path}")
    
    # Verify image exists
    if not os.path.exists(image_path):
        print(f"\n❌ Error: Image not found at {image_path}")
        return
    
    # Initialize verifier
    print("\n🔄 Initializing C2PA Verifier...")
    verifier = C2PAVerifier()
    
    # Run tests
    test_manifest_extraction(verifier, image_path)
    test_chain_of_custody(verifier, image_path)
    test_edit_history(verifier, image_path)
    test_provenance_report(verifier, image_path)
    test_fallback_metadata(verifier, image_path)
    test_visual_timeline(verifier, image_path)
    
    print("\n" + "="*80)
    print("✅ ALL C2PA TESTS COMPLETED")
    print("="*80)
    print("\n📁 Reports saved to: ./c2pa_reports/")


def main():
    parser = argparse.ArgumentParser(
        description='Test C2PA Provenance Verification',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full test suite
  python test_c2pa.py image.jpg
  
  # Quick verification
  python test_c2pa.py image.jpg --quick
  
  # Generate report only
  python test_c2pa.py image.jpg --report

Features Tested:
  1. C2PA Manifest Extraction
  2. Chain of Custody Verification
  3. Edit History Analysis
  4. Comprehensive Provenance Report
  5. Fallback Metadata Analysis (EXIF)
  6. Visual Timeline Generation
        """
    )
    
    parser.add_argument('image', help='Path to the image file to analyze')
    parser.add_argument('--quick', action='store_true', 
                       help='Quick verification only')
    parser.add_argument('--report', action='store_true',
                       help='Generate report only')
    
    args = parser.parse_args()
    
    if args.quick:
        print("\n🚀 Quick C2PA Verification")
        print("="*80)
        result = quick_verify(args.image)
        print(json.dumps(result, indent=2))
    elif args.report:
        print("\n📋 Generating C2PA Report")
        print("="*80)
        report = generate_full_report(args.image)
        print(json.dumps(report, indent=2))
    else:
        run_all_tests(args.image)


if __name__ == '__main__':
    main()
