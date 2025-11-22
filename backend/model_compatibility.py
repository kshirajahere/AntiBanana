"""
Model Compatibility Helper
Helps convert and load different model checkpoint formats for XAI
"""

import torch
import os
import sys

def inspect_model_checkpoint(checkpoint_path):
    """
    Inspect a PyTorch checkpoint file and print its structure
    """
    print(f"\n{'='*80}")
    print(f"Inspecting: {checkpoint_path}")
    print(f"{'='*80}\n")
    
    if not os.path.exists(checkpoint_path):
        print(f"❌ File not found: {checkpoint_path}")
        return None
    
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        print("📦 Checkpoint Type:", type(checkpoint))
        
        if isinstance(checkpoint, dict):
            print("\n🔑 Keys in checkpoint:")
            for key in checkpoint.keys():
                print(f"  - {key}")
                
            # Check for Lightning checkpoint
            if 'state_dict' in checkpoint:
                print("\n✅ This is a Lightning checkpoint")
                
                if 'hyper_parameters' in checkpoint:
                    print("\n⚙️  Hyperparameters:")
                    hparams = checkpoint['hyper_parameters']
                    for key, value in hparams.items():
                        print(f"  - {key}: {value}")
                
                if 'state_dict' in checkpoint:
                    state_dict = checkpoint['state_dict']
                    print(f"\n📊 State dict has {len(state_dict)} parameters")
                    print("\nFirst 10 parameter names:")
                    for i, key in enumerate(list(state_dict.keys())[:10]):
                        print(f"  {i+1}. {key}")
            else:
                print("\n✅ This is a pure PyTorch state dict")
                print(f"\n📊 State dict has {len(checkpoint)} parameters")
                print("\nFirst 10 parameter names:")
                for i, key in enumerate(list(checkpoint.keys())[:10]):
                    print(f"  {i+1}. {key}")
        else:
            print("\n⚠️  Unknown checkpoint format")
        
        return checkpoint
        
    except Exception as e:
        print(f"\n❌ Error loading checkpoint: {e}")
        import traceback
        traceback.print_exc()
        return None

def convert_to_lightning_format(state_dict_path, output_path, model_name='resnet50', num_classes=2):
    """
    Convert a pure PyTorch state dict to Lightning checkpoint format
    """
    print(f"\n{'='*80}")
    print(f"Converting to Lightning format")
    print(f"{'='*80}\n")
    
    try:
        # Load state dict
        state_dict = torch.load(state_dict_path, map_location='cpu')
        
        # If already a Lightning checkpoint, just copy it
        if isinstance(state_dict, dict) and 'state_dict' in state_dict:
            print("✅ Already in Lightning format, copying...")
            torch.save(state_dict, output_path)
            return True
        
        # Create Lightning checkpoint structure
        lightning_checkpoint = {
            'state_dict': state_dict,
            'hyper_parameters': {
                'model_name': model_name,
                'num_classes': num_classes,
                'task': 'binary' if num_classes <= 2 else 'multiclass',
                'pretrained': False,
            },
            'epoch': 0,
            'global_step': 0,
        }
        
        # Save
        torch.save(lightning_checkpoint, output_path)
        print(f"✅ Converted and saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_loading(checkpoint_path):
    """
    Test if the model can be loaded with XAIExplainer
    """
    print(f"\n{'='*80}")
    print(f"Testing model loading with XAIExplainer")
    print(f"{'='*80}\n")
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from gradcam.XAIExplainer import XAIExplainer
        
        explainer = XAIExplainer(model_path=checkpoint_path, device='cpu')
        model = explainer.load_model()
        
        if model is not None:
            print("✅ Model loaded successfully!")
            print(f"Model type: {type(model)}")
            print(f"Device: {next(model.parameters()).device}")
            return True
        else:
            print("❌ Model loading returned None")
            return False
            
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Model Compatibility Helper')
    parser.add_argument('checkpoint', help='Path to model checkpoint')
    parser.add_argument('--inspect', action='store_true', help='Inspect checkpoint structure')
    parser.add_argument('--convert', help='Convert to Lightning format and save to this path')
    parser.add_argument('--test', action='store_true', help='Test loading with XAIExplainer')
    parser.add_argument('--model-name', default='resnet50', help='Model architecture name')
    parser.add_argument('--num-classes', type=int, default=2, help='Number of classes')
    
    args = parser.parse_args()
    
    # Inspect
    if args.inspect or not (args.convert or args.test):
        checkpoint = inspect_model_checkpoint(args.checkpoint)
    
    # Convert
    if args.convert:
        convert_to_lightning_format(
            args.checkpoint, 
            args.convert,
            model_name=args.model_name,
            num_classes=args.num_classes
        )
    
    # Test
    if args.test:
        test_model_loading(args.checkpoint)
    
    print("\n" + "="*80)
    print("Done!")
    print("="*80 + "\n")

if __name__ == "__main__":
    # If no arguments, show help
    if len(sys.argv) == 1:
        print("\n" + "="*80)
        print("Model Compatibility Helper")
        print("="*80 + "\n")
        print("Usage examples:")
        print("\n1. Inspect a checkpoint:")
        print("   python model_compatibility.py path/to/model.pth --inspect")
        print("\n2. Convert to Lightning format:")
        print("   python model_compatibility.py model.pth --convert model_lightning.ckpt")
        print("\n3. Test loading:")
        print("   python model_compatibility.py model.pth --test")
        print("\n4. All at once:")
        print("   python model_compatibility.py model.pth --inspect --test")
        print("\n" + "="*80 + "\n")
        
        # Check if default model exists and inspect it
        default_model = "gradcam/deepfake_best_model.pth"
        if os.path.exists(default_model):
            print(f"Found default model: {default_model}")
            print("Inspecting...\n")
            inspect_model_checkpoint(default_model)
            
            print("\nTesting loading...")
            test_model_loading(default_model)
        else:
            print(f"⚠️  Default model not found at: {default_model}")
            print("Please provide a checkpoint path as argument")
    else:
        main()
