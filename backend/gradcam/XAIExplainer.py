"""
XAI Explainer for Deepfake Detection Model
Provides explainable AI visualizations using GradCAM++, LIME, and other methods
Works with the deepfake_best_model.pth checkpoint
"""

import os
import sys
import torch
from torchvision.transforms import v2
from PIL import Image
import numpy as np
import cv2
import io
import base64
import traceback

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class XAIExplainer:
    """
    Provides explainable AI visualizations for deepfake detection.
    Supports multiple XAI methods: GradCAM++, LIME, RISE, SHAP, SOBOL
    """
    
    def __init__(self, model_path=None, device=None):
        """
        Initialize the XAI Explainer
        
        Args:
            model_path (str): Path to the model checkpoint (.pth or .ckpt file)
            device (str): Device to run on ('cuda' or 'cpu')
        """
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.model_path = model_path
        
        if model_path is None:
            # Use default model path
            self.model_path = os.path.join(current_dir, 'deepfake_best_model.pth')
        
        # Image preprocessing transforms
        # Match the training configuration: 64x64 image size
        self.rs_size = 64
        self.interpolation = 3
        
        self.inference_transforms = v2.Compose([
            v2.ToImage(),
            v2.Resize(self.rs_size, interpolation=self.interpolation, antialias=False),
            v2.ToDtype(torch.float32, scale=True),
            v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        self.visualize_transforms = v2.Compose([
            v2.ToImage(),
            v2.Resize(self.rs_size, interpolation=self.interpolation, antialias=False),
            v2.ToDtype(torch.float32, scale=True),
        ])
        
        print(f"XAIExplainer initialized with device: {self.device}")
    
    def load_model(self):
        """
        Load the deepfake detection model from checkpoint
        Supports both .pth (PyTorch state dict) and .ckpt (Lightning checkpoint) formats
        """
        if self.model is not None:
            return self.model
        
        try:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model checkpoint not found at: {self.model_path}")
            
            print(f"Loading model from: {self.model_path}")
            
            # Try loading as Lightning checkpoint first
            if self.model_path.endswith('.ckpt'):
                from model.frame import FrameModel
                self.model = FrameModel.load_from_checkpoint(
                    self.model_path, 
                    map_location=self.device
                )
            else:
                # Load as pure PyTorch model
                # The Kaggle model uses rexnet_150 architecture
                import timm
                
                # Try to infer architecture from the checkpoint
                checkpoint = torch.load(self.model_path, map_location=self.device)
                
                # Inspect checkpoint keys to determine architecture
                # RexNet has keys like: stem.conv.weight, features.X.conv_exp, etc.
                # ResNet has keys like: conv1.weight, layer1.0.conv1, etc.
                if isinstance(checkpoint, dict):
                    sample_keys = list(checkpoint.keys())[:5]
                else:
                    sample_keys = []
                
                # Determine architecture from keys
                if any('stem.conv' in k or 'features.' in k for k in sample_keys):
                    # RexNet architecture
                    model_name = 'rexnet_150'
                    print(f"✓ Detected RexNet architecture from checkpoint keys")
                elif any('model.conv1' in k or 'model.layer1' in k for k in sample_keys):
                    # ResNet wrapped in FrameModel
                    model_name = 'resnet50'
                    print(f"✓ Detected ResNet architecture from checkpoint keys")
                else:
                    # Default to rexnet_150 (Kaggle training default)
                    model_name = 'rexnet_150'
                    print(f"⚠️ Could not determine architecture, defaulting to {model_name}")
                
                # If it's a full Lightning checkpoint
                if 'state_dict' in checkpoint:
                    # Extract model architecture info from hyperparameters if available
                    if 'hyper_parameters' in checkpoint:
                        hparams = checkpoint['hyper_parameters']
                        model_name = hparams.get('model_name', model_name)
                        num_classes = hparams.get('num_classes', 2)
                        
                        # Create the FrameModel wrapper
                        from model.frame import FrameModel
                        self.model = FrameModel(
                            model_name=model_name,
                            num_classes=num_classes,
                            task='binary' if num_classes <= 2 else 'multiclass'
                        )
                        self.model.load_state_dict(checkpoint['state_dict'])
                    else:
                        # Fallback: create model with detected architecture
                        from model.frame import FrameModel
                        self.model = FrameModel(
                            model_name=model_name,
                            num_classes=2,
                            task='binary'
                        )
                        self.model.load_state_dict(checkpoint['state_dict'])
                else:
                    # Pure state dict - load directly into timm model (no FrameModel wrapper)
                    print(f"✓ Loading pure state dict into {model_name}")
                    self.model = timm.create_model(
                        model_name,
                        pretrained=False,
                        num_classes=2
                    )
                    self.model.load_state_dict(checkpoint)
            
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ Model loaded successfully on {self.device}")
            return self.model
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            traceback.print_exc()
            return None
    
    def encode_image_to_base64(self, image_array):
        """Convert a NumPy array to a base64-encoded image string"""
        # Convert numpy array to PIL Image
        if image_array.dtype != np.uint8:
            image_array = (image_array * 255).astype(np.uint8)
        
        pil_img = Image.fromarray(image_array)
        
        # Save the image to a BytesIO object
        buffered = io.BytesIO()
        pil_img.save(buffered, format="PNG")
        
        # Encode to base64
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return f"data:image/png;base64,{img_str}"
    
    def generate_saliency_visualization(self, original_image, saliency_map):
        """
        Generate a visualization of the saliency map overlaid on the original image.
        
        Args:
            original_image: The original image as a numpy array (H, W, C)
            saliency_map: The saliency map as a numpy array (H, W)
            
        Returns:
            dict: Dictionary containing 'original', 'saliency', and 'overlay' images as base64 strings
        """
        result = {}
        
        # Ensure saliency map is 2D
        if len(saliency_map.shape) > 2:
            if len(saliency_map.shape) == 3 and saliency_map.shape[2] == 1:
                saliency_map = saliency_map[:, :, 0]
            else:
                saliency_map = np.mean(saliency_map, axis=2) if saliency_map.shape[2] > 1 else saliency_map[:, :, 0]
        
        # Resize saliency map to match original image dimensions
        h, w = original_image.shape[:2]
        saliency_map = cv2.resize(saliency_map, (w, h))
        
        # Normalize saliency map to [0, 1]
        if saliency_map.max() > saliency_map.min():
            saliency_map = (saliency_map - saliency_map.min()) / (saliency_map.max() - saliency_map.min())
        
        # Apply colormap
        heatmap = cv2.applyColorMap(np.uint8(255 * saliency_map), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        # Convert original image to uint8 if it's float
        if original_image.dtype == np.float32 or original_image.dtype == np.float64:
            original_image = (original_image * 255).astype(np.uint8)
        
        # Create overlay
        alpha = 0.4
        try:
            overlay = cv2.addWeighted(original_image, 1 - alpha, heatmap, alpha, 0)
        except Exception:
            overlay = original_image.copy()
            overlay = (overlay * 0.7).astype(np.uint8)
            mask = np.stack([saliency_map] * 3, axis=2)
            mask = (mask * 255 * 0.3).astype(np.uint8)
            overlay = overlay + mask
            overlay = np.clip(overlay, 0, 255).astype(np.uint8)
        
        # Store results as base64
        result['original'] = self.encode_image_to_base64(original_image)
        result['saliency'] = self.encode_image_to_base64((saliency_map * 255).astype(np.uint8))
        result['overlay'] = self.encode_image_to_base64(overlay)
        
        return result
    
    def explain(self, image_path, methods=None):
        """
        Generate XAI explanations for a given image
        
        Args:
            image_path (str): Path to the image file or PIL Image object
            methods (list): List of XAI methods to use (default: ['GradCAM++'])
                           Options: 'GradCAM++', 'LIME', 'RISE', 'SHAP', 'SOBOL'
        
        Returns:
            dict: Dictionary containing visualization results for each method
        """
        # Load model if not already loaded
        if self.model is None:
            self.model = self.load_model()
            if self.model is None:
                return {'error': 'Failed to load model'}
        
        # Default to GradCAM++ only if no methods specified
        if methods is None:
            methods = ['GradCAM++']
        
        try:
            # Load image
            if isinstance(image_path, str):
                original_image = Image.open(image_path).convert("RGB")
            elif isinstance(image_path, Image.Image):
                original_image = image_path.convert("RGB")
            else:
                return {'error': 'Invalid image input. Must be path or PIL Image'}
            
            # Process image for inference
            inference_image = self.inference_transforms(original_image)
            
            # Process image for visualization
            visualize_image = self.visualize_transforms(original_image)
            visualize_image_numpy = visualize_image.permute(1, 2, 0).numpy()
            
            # Move to device
            inference_image_device = inference_image.to(self.device)
            
            # Get prediction
            with torch.no_grad():
                output = self.model(inference_image_device.unsqueeze(0))
            
            output = output.cpu().reshape(-1, ).numpy()
            
            # Get predicted label
            explanation_label_index = np.argmax(output)
            
            # Store results
            results = {
                'prediction': {
                    'scores': output.tolist(),
                    'label': int(explanation_label_index),
                    'label_name': 'Fake' if explanation_label_index == 1 else 'Real',
                    'confidence': float(output[explanation_label_index])
                }
            }
            
            # Generate visualizations for each method
            for method in methods:
                try:
                    saliency = None
                    
                    if method == "GradCAM++":
                        from explanation.methods.gradcam_xai import explain as GradCAM
                        saliency = GradCAM(inference_image, visualize_image_numpy, explanation_label_index, self.model, visualize=False)
                    
                    elif method == "LIME":
                        from explanation.methods.lime_xai import explain as LIME
                        saliency = LIME(visualize_image_numpy, self.inference_transforms, explanation_label_index, self.model)
                    
                    elif method == "RISE":
                        from explanation.methods.rise_xai import explain as RISE
                        saliency = RISE(inference_image, visualize_image_numpy, explanation_label_index, self.model)
                    
                    elif method == "SHAP":
                        from explanation.methods.shap_xai import explain as SHAP
                        saliency = SHAP(inference_image, visualize_image_numpy, explanation_label_index, self.model)
                    
                    elif method == "SOBOL":
                        from explanation.methods.sobol_xai import explain as SOBOL
                        saliency = SOBOL(inference_image, visualize_image_numpy, explanation_label_index, self.model)
                    
                    else:
                        results[method] = {'error': f'Unknown method: {method}'}
                        continue
                    
                    # Convert tensor to numpy if needed
                    if isinstance(saliency, torch.Tensor):
                        saliency = saliency.cpu().numpy()
                    
                    # Generate visualization
                    original_np = np.array(original_image.resize((self.rs_size, self.rs_size)))
                    visualization = self.generate_saliency_visualization(original_np, saliency)
                    
                    # Store results
                    results[method] = visualization
                    
                except Exception as e:
                    results[method] = {
                        'error': str(e),
                        'traceback': traceback.format_exc()
                    }
                    print(f"Error generating {method}: {e}")
            
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'traceback': traceback.format_exc()
            }


# Convenience function for easy usage
def explain_image(image_path, model_path=None, methods=None):
    """
    Convenience function to generate XAI explanations
    
    Args:
        image_path: Path to image or PIL Image
        model_path: Path to model checkpoint (default: deepfake_best_model.pth)
        methods: List of XAI methods (default: ['GradCAM++'])
    
    Returns:
        dict: Explanation results
    """
    explainer = XAIExplainer(model_path=model_path)
    return explainer.explain(image_path, methods=methods)


if __name__ == "__main__":
    # Test the explainer
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        explainer = XAIExplainer()
        results = explainer.explain(image_path, methods=['GradCAM++'])
        
        print("\nPrediction:", results.get('prediction'))
        print("\nMethods processed:", [k for k in results.keys() if k != 'prediction' and 'error' not in results[k]])
        
        if 'error' in results:
            print(f"\nError: {results['error']}")
    else:
        print("Usage: python XAIExplainer.py <image_path>")
