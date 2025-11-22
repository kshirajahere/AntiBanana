from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
import sys
import json
from DeepfakeDetector import DeepfakeDetector
from VideoDeepfakeDetector import VideoDeepfakeDetector, analyze_video

# Import agentic analysis module
try:
    from SearchImage import AgenticReport
    AGENTIC_AVAILABLE = True
except ImportError as e:
    print(f"Warning: SearchImage module not available: {e}")
    AGENTIC_AVAILABLE = False

# Import audio detection module (new refactored version)
try:
    from AudioDeepfakeDetector import analyze_audio, AudioDeepfakeDetector
    AUDIO_DETECTION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AudioDeepfakeDetector module not available: {e}")
    AUDIO_DETECTION_AVAILABLE = False
    # Fallback to old module if available
    try:
        from VoiceAnalysis import analyze_audio
        AUDIO_DETECTION_AVAILABLE = True
        print("Using legacy VoiceAnalysis module")
    except ImportError:
        pass

# Import PDF report generation
try:
    from Report import generate_pdf_report, generate_case_number
    PDF_REPORT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Report module not available: {e}")
    PDF_REPORT_AVAILABLE = False

# Import video PDF report generation
try:
    from VideoReport import generate_video_pdf_report
    VIDEO_PDF_REPORT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: VideoReport module not available: {e}")
    VIDEO_PDF_REPORT_AVAILABLE = False

# Import audio protection module
try:
    from AudioProtection import protect_audio, AudioProtector
    AUDIO_PROTECTION_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AudioProtection module not available: {e}")
    AUDIO_PROTECTION_AVAILABLE = False

print(f"DeepfakeDetector loaded from: {sys.modules['DeepfakeDetector'].__file__}")

app = Flask(__name__)
CORS(app)

# Lazy loading of the detectors
detector = None
video_detector = None

def get_detector(enable_xai=False):
    global detector
    if detector is None:
        detector = DeepfakeDetector(enable_xai=enable_xai)
    elif enable_xai and not detector.enable_xai:
        # Reinitialize with XAI if needed
        detector = DeepfakeDetector(enable_xai=True)
    return detector

def get_video_detector():
    global video_detector
    if video_detector is None:
        video_detector = VideoDeepfakeDetector(get_detector())
    return video_detector

@app.route('/detect', methods=['POST'])
def detect_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get optional parameters
    include_explanations = request.form.get('explain', 'false').lower() == 'true'
    explanation_method = request.form.get('method', 'all')  # lime, shap, gradcam, or all
    quick_mode = request.form.get('quick', 'false').lower() == 'true'
    include_c2pa = request.form.get('c2pa', 'true').lower() == 'true'  # C2PA enabled by default

    # Check if XAI is requested
    enable_xai = request.form.get('enable_xai', 'false').lower() == 'true'
    xai_methods = request.form.get('xai_methods', 'GradCAM++').split(',')

    if file:
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        temp_path = temp_file.name
        temp_file.close()

        try:
            det = get_detector(enable_xai=enable_xai)
            result = det.detect_all(temp_path, include_c2pa=include_c2pa)
            
            # Add explainability if requested (using ExplainabilityEngine)
            if include_explanations:
                print(f"🔍 Generating explainability with method: {explanation_method}")
                explainability_result = det.generate_explainability(
                    temp_path, 
                    method=explanation_method,
                    quick_mode=quick_mode
                )
                result['explainability'] = explainability_result
            
            # Add XAI explanations if requested (using XAIExplainer)
            if enable_xai:
                print(f"🔍 Generating XAI explanations with methods: {xai_methods}")
                xai_result = det.get_xai_explanation(temp_path, methods=xai_methods)
                result['xai_explanations'] = xai_result

            
            print(jsonify(result))
            return jsonify(result)
        except Exception as e:
            print(jsonify({'error': str(e)}))
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'service': 'Deepfake Detection Backend-2'})

@app.route('/explain', methods=['POST'])
def explain_image():
    """
    Dedicated endpoint for generating explainability visualizations.
    Accepts: file, method (lime/shap/gradcam/all), quick (true/false)
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get parameters
    method = request.form.get('method', 'all')
    quick_mode = request.form.get('quick', 'false').lower() == 'true'
    
    if file:
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            # Generate explainability
            det = get_detector()
            result = det.generate_explainability(
                temp_path,
                method=method,
                quick_mode=quick_mode
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

@app.route('/c2pa', methods=['POST'])
def verify_c2pa():
    """
    Dedicated endpoint for C2PA provenance verification.
    Accepts: file
    Returns: Complete C2PA provenance report with chain of custody
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            # Generate C2PA report
            det = get_detector()
            result = det.get_c2pa_report(temp_path)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

@app.route('/protect', methods=['POST'])
@app.route('/protect_image', methods=['POST'])
def protect_image():
    """
    MMHI Protection endpoint - Protects images against deepfake generation.
    Accepts: file, strength (medium/high/extreme)
    Returns: Protected image as base64
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get protection strength parameter
    strength = request.form.get('strength', 'medium')
    if strength not in ['medium', 'high', 'extreme']:
        strength = 'medium'
    
    if file:
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            # Import and initialize MMHI pipeline
            from mmhi_protection.mmhi_pipeline import MMHIPipeline
            
            print(f"🛡️ Protecting image with strength: {strength}")
            pipeline = MMHIPipeline()
            
            # Protect the image
            result = pipeline.protect(temp_path, strength=strength)
            
            # Convert protected image to base64
            import io
            import base64
            from PIL import Image
            
            buf = io.BytesIO()
            result["protected_image"].save(buf, format="PNG")
            img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            
            return jsonify({
                'protected_image': img_b64,
                'processing_time': result['processing_time'],
                'phases_applied': result['phases_applied'],
                'strength': strength
            })
            
        except Exception as e:
            print(f"❌ Protection failed: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

@app.route('/protect-audio', methods=['POST'])
@app.route('/protect_audio', methods=['POST'])
def protect_audio_endpoint():
    """
    Audio protection endpoint - Protects audio against voice cloning and deepfake generation.
    
    Accepts:
        - file: Audio file (wav, mp3, m4a, flac, ogg)
        - strength: Protection strength (low/medium/high/extreme, default: medium)
    
    Returns:
        Protected audio as base64 with metadata
    """
    if not AUDIO_PROTECTION_AVAILABLE:
        return jsonify({'error': 'Audio protection module not available. Please install dependencies.'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Validate audio file extension
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Invalid audio format. Allowed: {allowed_extensions}'}), 400
    
    # Get protection strength parameter
    strength = request.form.get('strength', 'medium')
    if strength not in ['low', 'medium', 'high', 'extreme']:
        strength = 'medium'
    
    if file:
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
        file.save(temp_file.name)
        temp_path = temp_file.name
        temp_file.close()
        
        try:
            print(f"🛡️  Protecting audio with strength: {strength}")
            
            # Protect the audio
            result = protect_audio(temp_path, strength=strength)
            
            if not result['success']:
                return jsonify({'error': result.get('error', 'Protection failed')}), 500
            
            return jsonify({
                'success': True,
                'protected_audio': result['protected_audio_base64'],
                'sample_rate': result['sample_rate'],
                'protection_strength': result['protection_strength'],
                'techniques_applied': result['techniques_applied'],
                'snr_db': result['snr_db'],
                'processing_time': result['processing_time'],
                'metadata': result['metadata']
            })
            
        except Exception as e:
            print(f"❌ Audio protection failed: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

@app.route('/detect-audio', methods=['POST'])
def detect_audio():
    """
    Audio deepfake detection endpoint.
    
    Accepts:
        - file: Audio file (wav, mp3, etc.)
    
    Returns:
        Audio analysis with:
        - Prediction (real/fake)
        - Confidence score
        - XAI visualizations (waveform, spectrogram, MFCC, LIME, GradCAM)
    """
    if not AUDIO_DETECTION_AVAILABLE:
        return jsonify({'error': 'Audio detection module not available. Please install dependencies.'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Validate audio file extension
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.flac', '.ogg'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        return jsonify({'error': f'Invalid audio format. Allowed: {allowed_extensions}'}), 400
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
    file.save(temp_file.name)
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        # Analyze audio
        print(f"Analyzing audio file: {file.filename}")
        result = analyze_audio(temp_path)
        
        if 'error' in result:
            return jsonify(result), 500
        
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/analyze-agentic', methods=['POST'])
def analyze_agentic():
    """
    Advanced agentic analysis endpoint using multi-modal AI agents.
    
    Requires XAI visualizations (LIME and Grad-CAM) to be generated first.
    Accepts:
        - file: Image file
        - include_metadata: Include C2PA metadata (default: true)
    
    Returns:
        Comprehensive multi-modal analysis report with:
        - Visual Content Analysis (Groq Vision API)
        - Explanation Models Analysis (LIME + Grad-CAM interpretation)
        - Anomaly Detection (Computer Vision)
        - Text Extraction (OCR)
        - Web Search Context
        - Final Verdict with Reasoning
    """
    if not AGENTIC_AVAILABLE:
        return jsonify({'error': 'Agentic analysis module not available. Please install dependencies.'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    include_metadata = request.form.get('include_metadata', 'true').lower() == 'true'
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
    file.save(temp_file.name)
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        # First run detection with XAI
        det = get_detector()
        detection_result = det.detect_all(temp_path, include_c2pa=include_metadata)
        
        # Generate XAI explanations
        xai_result = det.generate_explainability(temp_path, method='all', quick_mode=False)
        
        # Extract LIME and GradCAM visualizations
        lime_base64 = None
        gradcam_base64 = None
        
        if 'segmented' in xai_result:
            if 'LIME' in xai_result['segmented']:
                lime_data = xai_result['segmented']['LIME']
                lime_base64 = lime_data.get('overlay') or lime_data.get('saliency')
            
            if 'GradCAM++' in xai_result['segmented']:
                gradcam_data = xai_result['segmented']['GradCAM++']
                gradcam_base64 = gradcam_data.get('overlay') or gradcam_data.get('saliency')
        
        if not lime_base64 or not gradcam_base64:
            return jsonify({'error': 'Failed to generate XAI visualizations'}), 500
        
        # Prepare metadata string
        metadata_str = json.dumps(detection_result.get('c2pa', {})) if include_metadata else "{}"
        output_str = json.dumps(detection_result.get('results', []))
        
        # Run agentic analysis
        print("Running agentic multi-modal analysis...")
        agentic_result = AgenticReport(
            image_path=temp_path,
            lime_base64=lime_base64,
            gradcam_base64=gradcam_base64,
            metadata=metadata_str,
            output=output_str
        )
        
        # Combine results
        final_result = {
            'detection': detection_result,
            'xai': xai_result,
            'agentic_analysis': agentic_result
        }
        
        return jsonify(final_result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """
    Generate forensic PDF report for image analysis.
    
    Accepts:
        - file: Image file
        - investigator_name: Name of investigator (optional)
        - case_number: Case number (optional, auto-generated if not provided)
        - include_xai: Include XAI visualizations (default: true)
        - include_c2pa: Include C2PA metadata (default: true)
        - include_agentic: Include agentic analysis (default: false)
    
    Returns:
        PDF report file
    """
    if not PDF_REPORT_AVAILABLE:
        return jsonify({'error': 'PDF report module not available. Please install dependencies.'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get parameters
    investigator_name = request.form.get('investigator_name', 'AI Detection System')
    case_number = request.form.get('case_number', generate_case_number())
    include_xai = request.form.get('include_xai', 'true').lower() == 'true'
    include_c2pa = request.form.get('include_c2pa', 'true').lower() == 'true'
    include_agentic = request.form.get('include_agentic', 'false').lower() == 'true'
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
    file.save(temp_file.name)
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        # Run detection
        det = get_detector()
        detection_result = det.detect_all(temp_path, include_c2pa=include_c2pa)
        
        # Prepare analysis results
        analysis_results = {
            'deepfake': detection_result['results'][0]['label'] if detection_result['results'] else 'Unknown',
            'confidence': detection_result['results'][0]['score'] if detection_result['results'] else 0,
            'results': detection_result['results']
        }
        
        # Add C2PA data if available
        if include_c2pa and 'c2pa' in detection_result:
            analysis_results['c2pa'] = detection_result['c2pa']
        
        # Generate XAI if requested
        if include_xai:
            xai_result = det.generate_explainability(temp_path, method='all', quick_mode=False)
            analysis_results['xai'] = xai_result
        
        # Run agentic analysis if requested
        if include_agentic and AGENTIC_AVAILABLE and include_xai:
            # Extract LIME and GradCAM
            lime_base64 = None
            gradcam_base64 = None
            
            if 'segmented' in xai_result:
                if 'LIME' in xai_result['segmented']:
                    lime_data = xai_result['segmented']['LIME']
                    lime_base64 = lime_data.get('overlay') or lime_data.get('saliency')
                
                if 'GradCAM++' in xai_result['segmented']:
                    gradcam_data = xai_result['segmented']['GradCAM++']
                    gradcam_base64 = gradcam_data.get('overlay') or gradcam_data.get('saliency')
            
            if lime_base64 and gradcam_base64:
                metadata_str = json.dumps(detection_result.get('c2pa', {}))
                output_str = json.dumps(detection_result.get('results', []))
                
                agentic_result = AgenticReport(
                    image_path=temp_path,
                    lime_base64=lime_base64,
                    gradcam_base64=gradcam_base64,
                    metadata=metadata_str,
                    output=output_str
                )
                analysis_results['report'] = agentic_result
        
        # Generate PDF report
        report_filename = f"forensic_report_{case_number}.pdf"
        report_path = os.path.join(tempfile.gettempdir(), report_filename)
        
        generate_pdf_report(
            output_path=report_path,
            case_number=case_number,
            investigator_name=investigator_name,
            analysis_results=analysis_results,
            image_path=temp_path
        )
        
        # Send the PDF file
        return send_file(
            report_path,
            as_attachment=True,
            download_name=report_filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up input file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/detect-video', methods=['POST'])
def detect_video():
    """
    Video deepfake detection endpoint with intelligent frame sampling.
    
    Accepts:
        - file: Video file
        - num_samples: Number of frames to sample (default: 30)
        - strategy: Sampling strategy (default: 'hybrid')
          Options: 'uniform', 'stratified', 'adaptive', 'scene_aware', 'hybrid'
        - max_workers: Parallel processing workers (default: 4)
        - include_xai: Include XAI explanations (default: false)
        - include_c2pa: Include C2PA verification (default: false)
    
    Returns:
        Comprehensive video analysis report
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get parameters
    num_samples = int(request.form.get('num_samples', 30))
    strategy = request.form.get('strategy', 'hybrid')
    max_workers = int(request.form.get('max_workers', 4))
    include_xai = request.form.get('include_xai', 'false').lower() == 'true'
    include_c2pa = request.form.get('include_c2pa', 'false').lower() == 'true'
    
    # Validate parameters
    if num_samples < 5 or num_samples > 100:
        return jsonify({'error': 'num_samples must be between 5 and 100'}), 400
    
    valid_strategies = ['uniform', 'stratified', 'adaptive', 'scene_aware', 'hybrid']
    if strategy not in valid_strategies:
        return jsonify({'error': f'Invalid strategy. Must be one of: {valid_strategies}'}), 400
    
    if max_workers < 1 or max_workers > 8:
        return jsonify({'error': 'max_workers must be between 1 and 8'}), 400
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
    file.save(temp_file.name)
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        # Analyze video
        vid_detector = get_video_detector()
        result = vid_detector.analyze_video_parallel(
            temp_path,
            num_samples=num_samples,
            strategy=strategy,
            max_workers=max_workers,
            include_xai=include_xai,
            include_c2pa=include_c2pa
        )
        
        print(jsonify(result))
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/generate-video-report', methods=['POST'])
def generate_video_report():
    """
    Generate forensic PDF report for video analysis.
    
    Accepts:
        - file: Video file
        - investigator_name: Name of investigator (optional)
        - case_number: Case number (optional, auto-generated if not provided)
        - num_samples: Number of frames to sample (default: 30)
        - strategy: Sampling strategy (default: 'hybrid')
        - include_xai: Include XAI visualizations for high-score frames (default: false)
    
    Returns:
        PDF report file with video analysis
    """
    if not VIDEO_PDF_REPORT_AVAILABLE:
        return jsonify({'error': 'Video PDF report module not available. Please install dependencies.'}), 503
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get parameters
    investigator_name = request.form.get('investigator_name', 'AI Detection System')
    case_number = request.form.get('case_number', generate_case_number() if PDF_REPORT_AVAILABLE else 'AUTO-GENERATED')
    num_samples = int(request.form.get('num_samples', 30))
    strategy = request.form.get('strategy', 'hybrid')
    include_xai = request.form.get('include_xai', 'false').lower() == 'true'
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
    file.save(temp_file.name)
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        # Analyze video
        vid_detector = get_video_detector()
        video_analysis = vid_detector.analyze_video_parallel(
            temp_path,
            num_samples=num_samples,
            strategy=strategy,
            max_workers=4,
            include_xai=False,  # We'll handle XAI separately in the report
            include_c2pa=False
        )
        
        # Extract sample frame paths if available
        sample_frames = []
        if 'frame_paths' in video_analysis:
            sample_frames = video_analysis['frame_paths'][:6]  # Limit to 6 frames
        
        # Generate PDF report
        report_filename = f"video_forensic_report_{case_number}.pdf"
        report_path = os.path.join(tempfile.gettempdir(), report_filename)
        
        generate_video_pdf_report(
            output_path=report_path,
            case_number=case_number,
            investigator_name=investigator_name,
            video_analysis=video_analysis,
            video_path=temp_path,
            sample_frames=sample_frames,
            model_path=None  # XAI model path - set to None for now
        )
        
        # Send the PDF file
        return send_file(
            report_path,
            as_attachment=True,
            download_name=report_filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up input file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    # Fix for multiprocessing on Windows
    from multiprocessing import freeze_support
    freeze_support()
    
    print("Starting Deepfake Detection Server on port 5000...")
    # Disable reloader to prevent restarts during file processing
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
