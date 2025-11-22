"""
Explainability Engine for Deepfake Detection
Implements LIME, SHAP, and Grad-CAM for model interpretability

Author: Senior Developer @ Google
Date: November 22, 2025
"""

import os
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import cv2
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Union
import io
import base64

# XAI Libraries
from lime import lime_image
from lime.wrappers.scikit_image import SegmentationAlgorithm
import shap
from pytorch_grad_cam import GradCAM, GradCAMPlusPlus, ScoreCAM, AblationCAM
from pytorch_grad_cam.utils.image import show_cam_on_image
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

# Image processing
from skimage.segmentation import mark_boundaries
from skimage.transform import resize


class ExplainabilityEngine:
    """
    Comprehensive explainability engine providing multiple XAI techniques
    for deepfake detection model interpretation.
    """
    
    def __init__(self, model_wrapper=None, device='cuda'):
        """
        Initialize the explainability engine.
        
        Args:
            model_wrapper: A wrapper around the detection model
            device: Device to run computations on ('cuda' or 'cpu')
        """
        self.device = device if torch.cuda.is_available() else 'cpu'
        self.model_wrapper = model_wrapper
        
        # LIME explainer configuration
        self.lime_explainer = None
        
        # SHAP explainer configuration  
        self.shap_explainer = None
        
        print(f"✅ ExplainabilityEngine initialized on {self.device}")
    
    def _prepare_image(self, image: Union[str, Image.Image, np.ndarray], 
                      target_size: Tuple[int, int] = (224, 224)) -> Tuple[np.ndarray, Image.Image]:
        """
        Prepare image for explainability analysis.
        
        Args:
            image: Input image (path, PIL Image, or numpy array)
            target_size: Target size for resizing
            
        Returns:
            Tuple of (numpy array normalized to [0,1], PIL Image)
        """
        if isinstance(image, str):
            img = Image.open(image).convert('RGB')
        elif isinstance(image, Image.Image):
            img = image.convert('RGB')
        elif isinstance(image, np.ndarray):
            img = Image.fromarray(image.astype('uint8'))
        else:
            raise ValueError("Image must be path, PIL Image, or numpy array")
        
        # Resize
        img_resized = img.resize(target_size, Image.LANCZOS)
        
        # Convert to numpy array normalized to [0, 1]
        img_array = np.array(img_resized) / 255.0
        
        return img_array, img_resized
    
    def _encode_image_to_base64(self, fig_or_array: Union[plt.Figure, np.ndarray]) -> str:
        """
        Convert matplotlib figure or numpy array to base64 string.
        
        Args:
            fig_or_array: Matplotlib figure or numpy array
            
        Returns:
            Base64 encoded string of the image
        """
        buffer = io.BytesIO()
        
        if isinstance(fig_or_array, plt.Figure):
            fig_or_array.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
            plt.close(fig_or_array)
        elif isinstance(fig_or_array, np.ndarray):
            # Convert numpy array to PIL Image and save
            img = Image.fromarray((fig_or_array * 255).astype(np.uint8))
            img.save(buffer, format='PNG')
        else:
            raise ValueError("Input must be matplotlib Figure or numpy array")
        
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        
        return f"data:image/png;base64,{img_base64}"
    
    def explain_with_lime(self, 
                         image: Union[str, Image.Image],
                         model_predict_fn,
                         num_samples: int = 1000,
                         num_features: int = 10,
                         positive_only: bool = False) -> Dict:
        """
        Generate LIME explanation for the prediction.
        
        LIME (Local Interpretable Model-agnostic Explanations) perturbs the input
        by hiding/showing superpixels and observes how predictions change.
        
        Args:
            image: Input image
            model_predict_fn: Function that takes batch of images and returns predictions
            num_samples: Number of perturbed samples to generate
            num_features: Number of superpixels to highlight
            positive_only: Whether to show only positive contributions
            
        Returns:
            Dictionary containing LIME explanation and visualization
        """
        print("🔍 Generating LIME explanation...")
        
        try:
            # Prepare image
            img_array, _ = self._prepare_image(image)
            
            # Initialize LIME explainer
            if self.lime_explainer is None:
                self.lime_explainer = lime_image.LimeImageExplainer(random_state=42)
            
            # Generate explanation
            explanation = self.lime_explainer.explain_instance(
                img_array,
                model_predict_fn,
                top_labels=2,
                hide_color=0,
                num_samples=num_samples,
                segmentation_fn=SegmentationAlgorithm('quickshift', kernel_size=4, 
                                                      max_dist=200, ratio=0.2)
            )
            
            # Get mask for the predicted class (label 1 = fake)
            temp, mask = explanation.get_image_and_mask(
                explanation.top_labels[0],
                positive_only=positive_only,
                num_features=num_features,
                hide_rest=False
            )
            
            # Create visualization
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Original image
            axes[0].imshow(img_array)
            axes[0].set_title('Original Image', fontsize=12, fontweight='bold')
            axes[0].axis('off')
            
            # LIME explanation with boundaries
            axes[1].imshow(mark_boundaries(temp, mask))
            axes[1].set_title('LIME Superpixel Boundaries', fontsize=12, fontweight='bold')
            axes[1].axis('off')
            
            # Heatmap of positive/negative contributions
            axes[2].imshow(mask, cmap='RdYlGn', alpha=0.8)
            axes[2].imshow(img_array, alpha=0.3)
            axes[2].set_title('Feature Importance Heatmap', fontsize=12, fontweight='bold')
            axes[2].axis('off')
            
            plt.tight_layout()
            
            # Convert to base64
            visualization = self._encode_image_to_base64(fig)
            
            # Get feature importance scores
            feature_importance = explanation.local_exp[explanation.top_labels[0]]
            
            return {
                'method': 'LIME',
                'visualization': visualization,
                'feature_importance': dict(feature_importance[:num_features]),
                'top_label': int(explanation.top_labels[0]),
                'num_superpixels': len(feature_importance),
                'description': 'LIME highlights image regions (superpixels) that most influenced the prediction'
            }
            
        except Exception as e:
            print(f"❌ LIME explanation failed: {e}")
            return {
                'method': 'LIME',
                'error': str(e),
                'description': 'LIME explanation generation failed'
            }
    
    def explain_with_shap(self,
                         image: Union[str, Image.Image],
                         model_predict_fn,
                         background_samples: Optional[np.ndarray] = None,
                         num_evals: int = 500) -> Dict:
        """
        Generate SHAP explanation for the prediction.
        
        SHAP (SHapley Additive exPlanations) uses game theory to assign each pixel
        a contribution score to the prediction.
        
        Args:
            image: Input image
            model_predict_fn: Function that takes batch of images and returns predictions
            background_samples: Background dataset for SHAP (if None, uses masker)
            num_evals: Number of evaluations for SHAP
            
        Returns:
            Dictionary containing SHAP explanation and visualization
        """
        print("🔍 Generating SHAP explanation...")
        
        try:
            # Prepare image
            img_array, _ = self._prepare_image(image)
            
            # Reshape for model input [1, H, W, C]
            img_batch = np.expand_dims(img_array, axis=0)
            
            # Create a masker for image data
            masker = shap.maskers.Image("inpaint_telea", img_array.shape)
            
            # Initialize SHAP explainer (Partition explainer for images)
            if self.shap_explainer is None or True:  # Always recreate for stability
                self.shap_explainer = shap.Explainer(
                    model_predict_fn,
                    masker,
                    output_names=["real", "fake"]
                )
            
            # Generate SHAP values
            shap_values = self.shap_explainer(
                img_batch,
                max_evals=num_evals,
                batch_size=50,
                outputs=shap.Explanation.argsort.flip[:1]  # Top prediction
            )
            
            # Create visualization
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Original image
            axes[0].imshow(img_array)
            axes[0].set_title('Original Image', fontsize=12, fontweight='bold')
            axes[0].axis('off')
            
            # SHAP values heatmap
            shap_img = shap_values.values[0]
            if len(shap_img.shape) == 3:  # [H, W, C]
                shap_img = np.mean(np.abs(shap_img), axis=2)  # Average across channels
            
            im1 = axes[1].imshow(shap_img, cmap='RdBu_r', alpha=0.8)
            axes[1].imshow(img_array, alpha=0.3)
            axes[1].set_title('SHAP Values (Red=Positive, Blue=Negative)', fontsize=12, fontweight='bold')
            axes[1].axis('off')
            plt.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
            
            # Overlay of positive contributions
            positive_shap = np.maximum(shap_img, 0)
            im2 = axes[2].imshow(positive_shap, cmap='Reds', alpha=0.7)
            axes[2].imshow(img_array, alpha=0.4)
            axes[2].set_title('Positive Contributions (Towards Fake)', fontsize=12, fontweight='bold')
            axes[2].axis('off')
            plt.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)
            
            plt.tight_layout()
            
            # Convert to base64
            visualization = self._encode_image_to_base64(fig)
            
            # Calculate statistics
            mean_shap = float(np.mean(np.abs(shap_img)))
            max_shap = float(np.max(np.abs(shap_img)))
            
            return {
                'method': 'SHAP',
                'visualization': visualization,
                'mean_abs_shap': mean_shap,
                'max_abs_shap': max_shap,
                'description': 'SHAP assigns each pixel a contribution score based on game theory principles'
            }
            
        except Exception as e:
            print(f"❌ SHAP explanation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'method': 'SHAP',
                'error': str(e),
                'description': 'SHAP explanation generation failed'
            }
    
    def explain_with_gradcam(self,
                            image: Union[str, Image.Image],
                            model: torch.nn.Module,
                            target_layers: List[torch.nn.Module],
                            target_class: Optional[int] = None,
                            method: str = 'gradcam') -> Dict:
        """
        Generate Grad-CAM explanation for the prediction.
        
        Grad-CAM (Gradient-weighted Class Activation Mapping) visualizes which
        regions of the image are important for the neural network's decision.
        
        Args:
            image: Input image
            model: PyTorch model
            target_layers: List of target layers for Grad-CAM
            target_class: Target class to explain (None = predicted class)
            method: CAM method ('gradcam', 'gradcam++', 'scorecam', 'ablationcam')
            
        Returns:
            Dictionary containing Grad-CAM explanation and visualization
        """
        print(f"🔍 Generating {method.upper()} explanation...")
        
        try:
            # Prepare image
            img_array, img_pil = self._prepare_image(image)
            
            # Convert to tensor [1, C, H, W]
            img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).unsqueeze(0).float()
            img_tensor = img_tensor.to(self.device)
            
            # Select CAM method
            cam_methods = {
                'gradcam': GradCAM,
                'gradcam++': GradCAMPlusPlus,
                'scorecam': ScoreCAM,
                'ablationcam': AblationCAM
            }
            
            CAMMethod = cam_methods.get(method.lower(), GradCAM)
            
            # Initialize CAM
            cam = CAMMethod(model=model, target_layers=target_layers)
            
            # Set target
            targets = None
            if target_class is not None:
                targets = [ClassifierOutputTarget(target_class)]
            
            # Generate CAM
            grayscale_cam = cam(input_tensor=img_tensor, targets=targets)
            grayscale_cam = grayscale_cam[0, :]  # Remove batch dimension
            
            # Create visualization
            cam_image = show_cam_on_image(img_array, grayscale_cam, use_rgb=True)
            
            # Create figure with multiple views
            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            
            # Original image
            axes[0].imshow(img_array)
            axes[0].set_title('Original Image', fontsize=12, fontweight='bold')
            axes[0].axis('off')
            
            # Grad-CAM heatmap
            axes[1].imshow(grayscale_cam, cmap='jet')
            axes[1].set_title(f'{method.upper()} Heatmap', fontsize=12, fontweight='bold')
            axes[1].axis('off')
            
            # Overlay
            axes[2].imshow(cam_image)
            axes[2].set_title('Grad-CAM Overlay', fontsize=12, fontweight='bold')
            axes[2].axis('off')
            
            plt.tight_layout()
            
            # Convert to base64
            visualization = self._encode_image_to_base64(fig)
            
            # Calculate statistics
            cam_max = float(np.max(grayscale_cam))
            cam_mean = float(np.mean(grayscale_cam))
            cam_area = float(np.sum(grayscale_cam > 0.5) / grayscale_cam.size)  # % of high activation
            
            return {
                'method': f'{method.upper()}',
                'visualization': visualization,
                'cam_max_activation': cam_max,
                'cam_mean_activation': cam_mean,
                'high_activation_area': cam_area,
                'description': f'{method.upper()} highlights regions the neural network focused on for classification'
            }
            
        except Exception as e:
            print(f"❌ {method.upper()} explanation failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'method': f'{method.upper()}',
                'error': str(e),
                'description': f'{method.upper()} explanation generation failed'
            }
    
    def generate_comprehensive_report(self,
                                     image: Union[str, Image.Image],
                                     model: torch.nn.Module,
                                     target_layers: List[torch.nn.Module],
                                     model_predict_fn,
                                     include_lime: bool = True,
                                     include_shap: bool = True,
                                     include_gradcam: bool = True) -> Dict:
        """
        Generate a comprehensive explainability report using all available methods.
        
        Args:
            image: Input image
            model: PyTorch model
            target_layers: Target layers for Grad-CAM
            model_predict_fn: Prediction function for LIME/SHAP
            include_lime: Whether to include LIME
            include_shap: Whether to include SHAP
            include_gradcam: Whether to include Grad-CAM
            
        Returns:
            Dictionary containing all explanations
        """
        print("📊 Generating comprehensive explainability report...")
        
        report = {
            'timestamp': None,
            'explanations': {}
        }
        
        # LIME explanation
        if include_lime:
            report['explanations']['lime'] = self.explain_with_lime(
                image, model_predict_fn, num_samples=500, num_features=10
            )
        
        # SHAP explanation
        if include_shap:
            report['explanations']['shap'] = self.explain_with_shap(
                image, model_predict_fn, num_evals=300
            )
        
        # Grad-CAM explanations (multiple methods)
        if include_gradcam:
            gradcam_methods = ['gradcam', 'gradcam++']
            for method in gradcam_methods:
                report['explanations'][method] = self.explain_with_gradcam(
                    image, model, target_layers, method=method
                )
        
        print("✅ Comprehensive explainability report generated")
        
        return report
    
    def create_comparison_visualization(self, 
                                       explanations: Dict[str, Dict]) -> str:
        """
        Create a side-by-side comparison of all explanation methods.
        
        Args:
            explanations: Dictionary of explanations from different methods
            
        Returns:
            Base64 encoded comparison image
        """
        try:
            num_methods = len([e for e in explanations.values() if 'visualization' in e])
            
            if num_methods == 0:
                return None
            
            fig, axes = plt.subplots(1, num_methods, figsize=(5*num_methods, 5))
            
            if num_methods == 1:
                axes = [axes]
            
            idx = 0
            for method_name, explanation in explanations.items():
                if 'visualization' in explanation:
                    # Decode base64 and display
                    img_data = explanation['visualization'].split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    img = Image.open(io.BytesIO(img_bytes))
                    
                    axes[idx].imshow(img)
                    axes[idx].set_title(f'{method_name.upper()} Explanation', 
                                       fontsize=12, fontweight='bold')
                    axes[idx].axis('off')
                    idx += 1
            
            plt.tight_layout()
            
            return self._encode_image_to_base64(fig)
            
        except Exception as e:
            print(f"❌ Comparison visualization failed: {e}")
            return None


# Utility function for creating model wrappers
def create_model_wrapper_for_pipeline(pipeline):
    """
    Create a wrapper function for HuggingFace pipelines compatible with LIME/SHAP.
    
    Args:
        pipeline: HuggingFace pipeline object
        
    Returns:
        Prediction function
    """
    def predict_fn(images):
        """
        Predict function for LIME/SHAP.
        
        Args:
            images: Numpy array of images [N, H, W, C] in range [0, 1]
            
        Returns:
            Numpy array of predictions [N, num_classes]
        """
        batch_results = []
        
        for img in images:
            # Convert to PIL Image
            img_pil = Image.fromarray((img * 255).astype(np.uint8))
            
            # Get predictions
            results = pipeline(img_pil)
            
            # Convert to probability array [real_prob, fake_prob]
            probs = [0.0, 0.0]
            for res in results:
                if res['label'].lower() in ['real', 'human']:
                    probs[0] = res['score']
                elif res['label'].lower() in ['fake', 'artificial', 'deepfake']:
                    probs[1] = res['score']
            
            batch_results.append(probs)
        
        return np.array(batch_results)
    
    return predict_fn
