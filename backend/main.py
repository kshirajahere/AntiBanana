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

def get_detector():
    global detector
    if detector is None:
        detector = DeepfakeDetector()
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

    if file:
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        temp_path = temp_file.name
        temp_file.close()

        try:
            # Run detection
            det = get_detector()
            result = det.detect_all(temp_path, include_c2pa=include_c2pa)
            
            # Add explainability if requested
            if include_explanations:
                print(f"🔍 Generating explainability with method: {explanation_method}")
                explainability_result = det.generate_explainability(
                    temp_path, 
                    method=explanation_method,
                    quick_mode=quick_mode
                )
                result['explainability'] = explainability_result
            
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
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == '__main__':
    # Fix for multiprocessing on Windows
    from multiprocessing import freeze_support
    freeze_support()
    
    print("Starting Deepfake Detection Server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
