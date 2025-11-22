
import os
import sys
import traceback
import numpy as np
import time

# Add the LipSync directory to sys.path to allow imports from it
current_dir = os.path.dirname(os.path.abspath(__file__))
lipsync_dir = os.path.join(current_dir, 'LipSync')
if lipsync_dir not in sys.path:
    sys.path.append(lipsync_dir)

# Global variables to cache the model
lipsync_model = None
model_load_error = None

def load_model(checkpoint_path):
    global lipsync_model, model_load_error
    
    if lipsync_model is not None:
        return lipsync_model

    try:
        from model import LIPINC_model
        
        if not os.path.exists(checkpoint_path):
            model_load_error = f"Checkpoint file not found at {checkpoint_path}"
            print(f"Error: {model_load_error}")
            return None

        print(f"Loading LipSync model from {checkpoint_path}...")
        model = LIPINC_model()
        model.load_weights(checkpoint_path)
        lipsync_model = model
        print("LipSync model loaded successfully.")
        return lipsync_model
    except Exception as e:
        model_load_error = f"Failed to load LipSync model: {str(e)}"
        print(f"Error: {model_load_error}")
        traceback.print_exc()
        return None

def analyze_lip_sync(video_path):
    """
    Analyzes the lip sync of a video file.
    Returns a dictionary with the analysis results.
    """
    global model_load_error
    
    start_time = time.time()
    
    try:
        # Import utils here to avoid issues if dependencies are missing
        from utils import get_color_structure_frames
        
        # Define checkpoint path
        checkpoint_path = os.path.join(lipsync_dir, 'checkpoints', 'FakeAv.hdf5')
        
        # Load model
        model = load_model(checkpoint_path)
        if model is None:
            return {
                "error": model_load_error or "Model not loaded",
                "real_probability": 0.0,
                "fake_probability": 0.0,
                "description": "Lip sync analysis unavailable (Model missing)"
            }

        # Process video
        print(f"Processing video for lip sync: {video_path}")
        n_frames = 5 # number of local frames
        
        # Call the utility function to get frames
        # Returns: length_error, face, combined_frames, residue_frames, l_id, g_id
        length_error, face, combined_frames, residue_frames, l_id, g_id = get_color_structure_frames(n_frames, video_path)
        
        if length_error:
            return {
                "error": "Video too short",
                "real_probability": 0.0,
                "fake_probability": 0.0,
                "description": "Video is too short for lip sync analysis (needs > 30 frames)"
            }
            
        if len(combined_frames) == 0:
             return {
                "error": "No face detected",
                "real_probability": 0.0,
                "fake_probability": 0.0,
                "description": "Could not detect face or lips in the video"
            }

        # Prepare inputs for the model
        combined_frames = np.reshape(combined_frames, (1,) + combined_frames.shape)
        residue_frames = np.reshape(residue_frames, (1,) + residue_frames.shape)
        
        print(f"Shapes - Color Frames: {combined_frames.shape}, Structure Frames: {residue_frames.shape}")
        
        # Predict
        prediction = model.predict([combined_frames, residue_frames])
        
        # The model output seems to be [real_prob, fake_prob] based on demo.py
        # demo.py says: result = round(float(result[0][1]),3) which it calls "real probability"
        # But wait, demo.py line 135: out=(Dense(2, activation="softmax")(conv))
        # And line 402: video_des['Result'] = {"Real Probability": result, "Fake Probability":  round(1-result,4)}
        # Let's check demo.py again.
        # Line 82: result = round(float(result[0][1]),3)
        # Line 402: "Real Probability": result
        # So index 1 is Real Probability? Usually 0 is class 0, 1 is class 1.
        # If the classes are [Fake, Real], then 1 is Real.
        
        real_prob = float(prediction[0][1])
        fake_prob = float(prediction[0][0])
        
        # Normalize if needed, but softmax should sum to 1
        
        processing_time = time.time() - start_time
        
        return {
            "real_probability": real_prob,
            "fake_probability": fake_prob,
            "processing_time_seconds": round(processing_time, 2),
            "description": get_result_description(real_prob)
        }

    except ImportError as e:
        return {
            "error": f"Import Error: {str(e)}",
            "description": "Missing dependencies for lip sync analysis"
        }
    except Exception as e:
        print(f"Error during lip sync analysis: {str(e)}")
        traceback.print_exc()
        return {
            "error": str(e),
            "description": "An error occurred during lip sync analysis"
        }

def get_result_description(real_p):
    if real_p >= 0.99:
        return 'This sample is certainly real.'
    elif real_p >= 0.75:
        return 'This sample is likely real.'
    elif real_p >= 0.25:
        return 'This sample is maybe real.'
    elif real_p >= 0.01:
        return 'This sample is unlikely real.'
    else:
        return 'There is no chance that the sample is real.'
