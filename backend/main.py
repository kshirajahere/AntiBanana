from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
import sys
from DeepfakeDetector import DeepfakeDetector

print(f"DeepfakeDetector loaded from: {sys.modules['DeepfakeDetector'].__file__}")

app = Flask(__name__)
CORS(app)

# Lazy loading of the detector
detector = None

def get_detector(enable_xai=False):
    global detector
    if detector is None:
        detector = DeepfakeDetector(enable_xai=enable_xai)
    elif enable_xai and not detector.enable_xai:
        # Reinitialize with XAI if needed
        detector = DeepfakeDetector(enable_xai=True)
    return detector

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

if __name__ == '__main__':
    # Fix for multiprocessing on Windows
    from multiprocessing import freeze_support
    freeze_support()
    
    print("Starting Deepfake Detection Server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
