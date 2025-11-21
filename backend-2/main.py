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

    if file:
        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        file.save(temp_file.name)
        temp_path = temp_file.name
        temp_file.close()

        try:
            # Run detection
            det = get_detector()
            result = det.detect_all(temp_path)
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

if __name__ == '__main__':
    # Fix for multiprocessing on Windows
    from multiprocessing import freeze_support
    freeze_support()
    
    print("Starting Deepfake Detection Server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)
