import torch
from pytorch_grad_cam.utils.image import show_cam_on_image
from torchvision.transforms import v2
import sys
sys.path.append('../../src')
from model.frame import FrameModel
from PIL import Image
from pytorch_grad_cam import GradCAMPlusPlus
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from matplotlib import pyplot as plt

def explain(inference_image,visualize_image,label,model,visualize=True):

    # Find the best target layer for GradCAM
    # For timm models, we want to use the last layer before the classifier
    target_layers = []
    
    # Try to find the features layer (common in timm models)
    if hasattr(model, 'features'):
        # Use the last convolutional layer in features
        target_layers = [model.features[-1]]
        print(f"✓ Using model.features[-1] as target layer")
    elif hasattr(model, 'model') and hasattr(model.model, 'features'):
        # For wrapped models (like FrameModel wrapping timm model)
        target_layers = [model.model.features[-1]]
        print(f"✓ Using model.model.features[-1] as target layer")
    else:
        # Fallback: find all convolutional layers and use the last one
        conv_layers = []
        for name, layer in model.named_modules():
            if isinstance(layer, torch.nn.Conv2d):
                conv_layers.append(layer)
        
        if conv_layers:
            # Use only the last conv layer for better performance
            target_layers = [conv_layers[-1]]
            print(f"✓ Using last conv layer as target: {conv_layers[-1]}")
    
    if not target_layers:
        raise ValueError("Could not find suitable target layers for GradCAM")

    #Set as target the explanation label
    targets = [ClassifierOutputTarget(label)]

    #Compute the explanation
    try:
        # Note: use_cuda parameter was removed in newer pytorch-grad-cam versions
        # The library automatically handles device placement based on model device
        cam = GradCAMPlusPlus(model=model, target_layers=target_layers)
        result=cam(input_tensor=inference_image.unsqueeze(0),targets=targets)
        
        #Get the saliency map
        saliance_map=result[0, :]
        
        print(f"✓ GradCAM++ computed successfully. Saliency map shape: {saliance_map.shape}")
    except Exception as e:
        print(f"❌ GradCAM++ computation failed: {e}")
        import traceback
        traceback.print_exc()
        raise

    #If selected visualize the result
    if(visualize):
        # Ensure visualize_image is in [0, 1] range
        if visualize_image.max() > 1.0:
            visualize_image = visualize_image / 255.0
        
        visualization = show_cam_on_image(visualize_image, saliance_map, use_rgb=True, image_weight=0.5)
        plt.imshow(visualization)
        plt.show()

    #Return the saliency map
    return saliance_map


if __name__ == "__main__":
    # Load the model
    rs_size = 224
    model = FrameModel.load_from_checkpoint("../../model/checkpoint/ff_attribution.ckpt", map_location='cuda').eval()

    # Create the transforms for inference and visualization purposes
    interpolation = 3
    inference_transforms = v2.Compose([
        v2.ToImage(),
        v2.Resize(rs_size, interpolation=interpolation, antialias=False),
        v2.ToDtype(torch.float32, scale=True),
        v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    visualize_transforms = v2.Compose([
        v2.ToImage(),
        v2.Resize(rs_size, interpolation=interpolation, antialias=False),
        v2.ToDtype(torch.float32, scale=True),
    ])

    #Open the image
    image = Image.open('test.jpg')
    #Apply the transformations
    inference_image = inference_transforms(image)
    visualize_image = visualize_transforms(image).permute(1, 2, 0).numpy()
    #Select the explanation label
    label = 0

    #Call the explanation method
    explain(inference_image, visualize_image, label, model)

