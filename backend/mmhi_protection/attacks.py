import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import transforms
from .config import MMHIConfig

class MMHIAttacker:
    def __init__(self, model, device='cpu'):
        self.model = model
        self.device = device
        self.model.eval()

    def quantization_boundary_shift(self, image_tensor, iterations=None, epsilon=None):
        """Phase 2: Quantization Boundary Shifting (QBS)."""
        if iterations is None:
            iterations = MMHIConfig.QBS_ITERATIONS
        if epsilon is None:
            epsilon = MMHIConfig.QBS_EPSILON
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=MMHIConfig.QBS_LEARNING_RATE)
        print(f"Starting QBS Attack for {iterations} iterations...")
        for i in range(iterations):
            optimizer.zero_grad()
            z_adv = self.model._encoder(adv_image)
            z_adv = self.model._pre_vq_conv(z_adv)
            _, z_q, _, _, _ = self.model._vq_vae(z_adv)
            quant_error = F.mse_loss(z_adv, z_q.detach())
            l2_loss = F.mse_loss(adv_image, image_tensor)
            loss = -quant_error + 50.0 * l2_loss
            if torch.isnan(loss) or torch.isinf(loss):
                print(f"Warning: Loss is {loss.item()} at step {i}. Stopping QBS early.")
                break
            loss.backward()
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=1.0)
            optimizer.step()
            delta = adv_image - image_tensor
            delta = torch.clamp(delta, -epsilon, epsilon)
            adv_image.data = torch.clamp(image_tensor + delta, 0, 1)
            if i % 10 == 0:
                print(f"QBS Step {i}: Loss {loss.item():.4f} (Quant_Err: {quant_error.item():.4f})")
        result = adv_image.detach()
        if torch.isnan(result).any() or torch.isinf(result).any():
            print("Error: QBS produced NaN/Inf. Returning original input.")
            return image_tensor
        return torch.clamp(result, 0, 1)

    def logic_injection(self, image_tensor, iterations=None, strength=None):
        """Phase 3: Logic Injection using high‑frequency variance."""
        if iterations is None:
            iterations = MMHIConfig.LOGIC_INJECTION_ITERATIONS
        if strength is None:
            strength = MMHIConfig.LOGIC_INJECTION_STRENGTH
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.002)
        print(f"Starting Logic Injection for {iterations} iterations with strength {strength}...")
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                z = self.model._encoder(adv_image)
                z_pre = self.model._pre_vq_conv(z)
                _, z_q, _, _, _ = self.model._vq_vae(z_pre)
                quant_error = F.mse_loss(z_q, z_pre.detach())
                # spatial variance of quantized latent
                z_h = z_q[:, :, :, 1:] - z_q[:, :, :, :-1]
                z_w = z_q[:, :, 1:, :] - z_q[:, :, :-1, :]
                spatial_var = torch.var(z_h) + torch.var(z_w)
                variance_loss = -spatial_var
                l2_loss = F.mse_loss(adv_image, image_tensor)
                loss = quant_error + 0.1 * variance_loss + 100.0 * l2_loss
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
            if i % 10 == 0:
                print(f"Logic Step {i}: Loss={loss.item():.4f}, Quant={quant_error.item():.4f}, Var={spatial_var.item():.4f}")
        result = adv_image.detach()
        print(f"Logic Injection completed. Stats: min={result.min():.4f}, max={result.max():.4f}, mean={result.mean():.4f}")
        return result

    def attention_hijacking(self, image_tensor, iterations=None, strength=None):
        """Phase 4: Attention Hijacking – create high‑variance patches to confuse transformer attention."""
        if iterations is None:
            iterations = MMHIConfig.ATTENTION_HIJACK_ITERATIONS
        if strength is None:
            strength = MMHIConfig.ATTENTION_HIJACK_STRENGTH
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.003)
        print(f"Starting Attention Hijacking for {iterations} iterations...")
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                z = self.model._encoder(adv_image)
                z_pre = self.model._pre_vq_conv(z)
                # compute local variance in 3x3 windows
                B, C, H, W = z_pre.shape
                padded = F.pad(z_pre, (1,1,1,1), mode='reflect')
                patches = []
                for dh in [-1,0,1]:
                    for dw in [-1,0,1]:
                        patches.append(padded[:, :, 1+dh:H+1+dh, 1+dw:W+1+dw])
                stacked = torch.stack(patches, dim=0)  # [9, B, C, H, W]
                local_var = torch.var(stacked, dim=0)
                attention_loss = -torch.mean(local_var)
                l2_loss = F.mse_loss(adv_image, image_tensor)
                loss = attention_loss + 80.0 * l2_loss
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
            if i % 10 == 0:
                print(f"Attention Step {i}: Loss={loss.item():.4f}, Var={local_var.mean().item():.6f}")
        result = adv_image.detach()
        print(f"Attention Hijacking completed. Stats: min={result.min():.4f}, max={result.max():.4f}")
        return result

    def autoregressive_corruption(self, image_tensor, iterations=None, strength=None):
        """Phase 5: Autoregressive Token Corruption – maximize dissimilarity of adjacent tokens."""
        if iterations is None:
            iterations = MMHIConfig.AUTOREGRESSIVE_ITERATIONS
        if strength is None:
            strength = MMHIConfig.AUTOREGRESSIVE_STRENGTH
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.0025)
        print(f"Starting Autoregressive Corruption for {iterations} iterations...")
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                z = self.model._encoder(adv_image)
                z_pre = self.model._pre_vq_conv(z)
                _, z_q, _, _, _ = self.model._vq_vae(z_pre)
                B, C, H, W = z_q.shape
                # horizontal and vertical neighbor differences
                left = z_q[:, :, :, :-1]
                right = z_q[:, :, :, 1:]
                top = z_q[:, :, :-1, :]
                bottom = z_q[:, :, 1:, :]
                h_dissim = -F.cosine_similarity(left.flatten(2), right.flatten(2), dim=1).mean()
                v_dissim = -F.cosine_similarity(top.flatten(2), bottom.flatten(2), dim=1).mean()
                autoreg_loss = -(h_dissim + v_dissim)
                l2_loss = F.mse_loss(adv_image, image_tensor)
                loss = autoreg_loss + 60.0 * l2_loss
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
            if i % 10 == 0:
                print(f"Autoregressive Step {i}: Loss={loss.item():.4f}, H_Dis={h_dissim.item():.4f}, V_Dis={v_dissim.item():.4f}")
        result = adv_image.detach()
        print(f"Autoregressive Corruption completed. Stats: min={result.min():.4f}, max={result.max():.4f}")
        return result

    def frequency_poisoning(self, image_tensor, iterations=None, alpha=None):
        """Phase 6: Frequency Domain Poisoning – inject high‑frequency Laplacian patterns."""
        if iterations is None:
            iterations = MMHIConfig.FREQUENCY_POISON_ITERATIONS
        if alpha is None:
            alpha = MMHIConfig.FREQUENCY_POISON_ALPHA
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.002)
        print(f"Starting Frequency Poisoning for {iterations} iterations...")
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                optimizer.zero_grad()
                continue
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.3)
            optimizer.step()
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -alpha, alpha)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
            if i % 10 == 0:
                print(f"Frequency Step {i}: Loss={loss.item():.4f}, ImgHF={torch.mean(torch.abs(hf)).item():.4f}")
        result = adv_image.detach()
        print(f"Frequency Poisoning completed. Stats: min={result.min():.4f}, max={result.max():.4f}")
        return result

    def feature_map_disruption(self, image_tensor, iterations=None, strength=None):
        """Phase 7: Feature‑Map Disruption – random channel‑wise noise to break CNN feature extraction."""
        if iterations is None:
            iterations = 30
        if strength is None:
            strength = 0.02
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.001)
        print(f"Starting Feature‑Map Disruption for {iterations} iterations...")
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                # Random channel scaling
                scale = (torch.rand_like(adv_image) * 2 * strength) - strength
                perturbed = adv_image + scale
                loss = F.mse_loss(perturbed, image_tensor)
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.2)
            optimizer.step()
            if i % 10 == 0:
                print(f"Feature‑Map Step {i}: Loss={loss.item():.6f}")
        result = adv_image.detach()
        print(f"Feature‑Map Disruption completed. Stats: min={result.min():.4f}, max={result.max():.4f}")
        return result

    def gradient_shattering(self, image_tensor, iterations=None, strength=None):
        """Phase 8: Gradient Shattering – maximize latent ruggedness to break diffusion gradients."""
        if iterations is None:
            iterations = MMHIConfig.GRADIENT_SHATTER_ITERATIONS
        if strength is None:
            strength = MMHIConfig.GRADIENT_SHATTER_STRENGTH
            
        print(f"Starting Gradient Shattering for {iterations} iterations...")
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.002)
        
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                z = self.model._encoder(adv_image)
                z_pre = self.model._pre_vq_conv(z)
                
                # Maximize Total Variation in latent space (create ruggedness)
                # TV = sum(|z_{i+1} - z_i|)
                h_diff = torch.abs(z_pre[:, :, :, 1:] - z_pre[:, :, :, :-1])
                w_diff = torch.abs(z_pre[:, :, 1:, :] - z_pre[:, :, :-1, :])
                
                # We want to MAXIMIZE this to make the landscape chaotic
                ruggedness = torch.mean(h_diff) + torch.mean(w_diff)
                shatter_loss = -ruggedness
                
                l2_loss = F.mse_loss(adv_image, image_tensor)
                loss = shatter_loss + 80.0 * l2_loss
            
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
                
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
                
            if i % 10 == 0:
                print(f"Shatter Step {i}: Loss={loss.item():.4f}, Ruggedness={ruggedness.item():.4f}")
                
        result = adv_image.detach()
        print(f"Gradient Shattering completed. Stats: min={result.min():.4f}, max={result.max():.4f}")
        return result

    def stride_dissonance(self, image_tensor, iterations=None, strength=None):
        """Phase 9: Stride-Aware Dissonance – inject noise at patch boundaries to disrupt ViT processing."""
        if iterations is None:
            iterations = MMHIConfig.STRIDE_DISSONANCE_ITERATIONS
        if strength is None:
            strength = MMHIConfig.STRIDE_DISSONANCE_STRENGTH
            
        print(f"Starting Stride Dissonance for {iterations} iterations...")
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.002)
        
        B, C, H, W = image_tensor.shape
        
        # Create a grid mask for 16x16 patches (common in ViTs)
        grid_mask = torch.zeros((1, 1, H, W), device=self.device)
        for y in range(0, H, 16):
            grid_mask[:, :, y, :] = 1.0
        for x in range(0, W, 16):
            grid_mask[:, :, :, x] = 1.0
            
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                # We want the pixels at the grid lines to be different from their neighbors
                # effectively creating a "cage" effect
                
                # Extract grid pixels
                grid_pixels = adv_image * grid_mask
                
                # Maximize high frequency content specifically at grid lines
                # We can use the Laplacian we used before, but masked
                lap = torch.tensor([[0,-1,0],[-1,4,-1],[0,-1,0]], dtype=torch.float32, device=self.device).view(1,1,3,3).repeat(C,1,1,1)
                hf = F.conv2d(adv_image, lap, padding=1, groups=C)
                
                # Maximize HF energy at grid locations
                grid_hf = hf * grid_mask
                dissonance_loss = -torch.mean(torch.abs(grid_hf))
                
                l2_loss = F.mse_loss(adv_image, image_tensor)
                loss = dissonance_loss + 100.0 * l2_loss
            
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
                
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
                
            if i % 10 == 0:
                print(f"Stride Step {i}: Loss={loss.item():.4f}, Dissonance={-dissonance_loss.item():.4f}")
                
        result = adv_image.detach()
        print(f"Stride Dissonance completed. Stats: min={result.min():.4f}, max={result.max():.4f}")
        return result

    def universal_adversarial_perturbation(self, image_tensor, iterations=None, epsilon=None):
        """Phase 10: Universal Adversarial Perturbation – craft a universal noise pattern that breaks the model."""
        if iterations is None:
            iterations = MMHIConfig.UAP_ITERATIONS
        if epsilon is None:
            epsilon = MMHIConfig.UAP_EPSILON
            
        print(f"Starting Universal Adversarial Perturbation for {iterations} iterations...")
        
        # Initialize perturbation
        B, C, H, W = image_tensor.shape
        perturbation = torch.zeros_like(image_tensor, requires_grad=True, device=self.device)
        optimizer = optim.Adam([perturbation], lr=MMHIConfig.UAP_LEARNING_RATE)
        
        for i in range(iterations):
            optimizer.zero_grad()
            
            with torch.enable_grad():
                # Apply perturbation
                adv_image = torch.clamp(image_tensor + perturbation, 0.0, 1.0)
                
                # Get latent representation
                z = self.model._encoder(adv_image)
                z_pre = self.model._pre_vq_conv(z)
                _, z_q, _, _, indices = self.model._vq_vae(z_pre)
                
                # Multi-objective attack:
                # 1. Maximize token diversity (force different tokens everywhere)
                token_flat = indices.flatten()
                unique_tokens = torch.unique(token_flat)
                diversity_loss = -len(unique_tokens) / token_flat.numel()
                
                # 2. Maximize quantization error
                quant_error = F.mse_loss(z_pre, z_q.detach())
                
                # 3. Maximize latent space variance (creates instability)
                latent_variance = torch.var(z_pre)
                variance_loss = -latent_variance
                
                # 4. Perturbation regularization (keep it imperceptible)
                l2_constraint = torch.norm(perturbation)
                
                # Combined loss
                loss = -quant_error + 0.1 * diversity_loss + 0.05 * variance_loss + 2.0 * l2_constraint
            
            loss.backward()
            
            if perturbation.grad is None or torch.isnan(perturbation.grad).any():
                optimizer.zero_grad()
                continue
                
            torch.nn.utils.clip_grad_norm_([perturbation], max_norm=1.0)
            optimizer.step()
            
            # Project perturbation to epsilon ball
            with torch.no_grad():
                perturbation.data = torch.clamp(perturbation.data, -epsilon, epsilon)
                
            if i % 20 == 0:
                print(f"UAP Step {i}: Loss={loss.item():.4f}, QuanErr={quant_error.item():.4f}, UniqTokens={len(unique_tokens)}")
        
        # Apply final perturbation
        result = torch.clamp(image_tensor + perturbation.detach(), 0.0, 1.0)
        print(f"Universal Adversarial Perturbation completed. Perturbation norm: {torch.norm(perturbation).item():.4f}")
        return result

    def semantic_destroyer(self, image_tensor, iterations=None, strength=None):
        """Phase 11: Semantic Destroyer – break the semantic coherence of the image at the feature level."""
        if iterations is None:
            iterations = MMHIConfig.SEMANTIC_DESTROY_ITERATIONS
        if strength is None:
            strength = MMHIConfig.SEMANTIC_DESTROY_STRENGTH
            
        print(f"Starting Semantic Destroyer for {iterations} iterations...")
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.004)
        
        for i in range(iterations):
            optimizer.zero_grad()
            
            with torch.enable_grad():
                z = self.model._encoder(adv_image)
                z_pre = self.model._pre_vq_conv(z)
                _, z_q, _, _, indices = self.model._vq_vae(z_pre)
                
                B, C, H, W = z_q.shape
                
                # Strategy 1: Invert spatial correlations
                # Make left/right and top/bottom have maximum distance
                left_half = z_q[:, :, :, :W//2]
                right_half = z_q[:, :, :, W//2:]
        print(f"Starting Gradient Shattering for {iterations} iterations...")
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.002)
        
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                z = self.model._encoder(adv_image)
                z_pre = self.model._pre_vq_conv(z)
                
                # Maximize Total Variation in latent space (create ruggedness)
                # TV = sum(|z_{i+1} - z_i|)
                h_diff = torch.abs(z_pre[:, :, :, 1:] - z_pre[:, :, :, :-1])
                w_diff = torch.abs(z_pre[:, :, 1:, :] - z_pre[:, :, :-1, :])
                
                # We want to MAXIMIZE this to make the landscape chaotic
                ruggedness = torch.mean(h_diff) + torch.mean(w_diff)
                shatter_loss = -ruggedness
                
                l2_loss = F.mse_loss(adv_image, image_tensor)
                loss = shatter_loss + 80.0 * l2_loss
            
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
                
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
                
            if i % 10 == 0:
                print(f"Shatter Step {i}: Loss={loss.item():.4f}, Ruggedness={ruggedness.item():.4f}")
                
        result = adv_image.detach()
        print(f"Gradient Shattering completed. Stats: min={result.min():.4f}, max={result.max():.4f}")
        return result

    def stride_dissonance(self, image_tensor, iterations=None, strength=None):
        """Phase 9: Stride-Aware Dissonance – inject noise at patch boundaries to disrupt ViT processing."""
        if iterations is None:
            iterations = MMHIConfig.STRIDE_DISSONANCE_ITERATIONS
        if strength is None:
            strength = MMHIConfig.STRIDE_DISSONANCE_STRENGTH
            
        print(f"Starting Stride Dissonance for {iterations} iterations...")
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.002)
        
        B, C, H, W = image_tensor.shape
        
        # Create a grid mask for 16x16 patches (common in ViTs)
        grid_mask = torch.zeros((1, 1, H, W), device=self.device)
        for y in range(0, H, 16):
            grid_mask[:, :, y, :] = 1.0
        for x in range(0, W, 16):
            grid_mask[:, :, :, x] = 1.0
            
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                # We want the pixels at the grid lines to be different from their neighbors
                # effectively creating a "cage" effect
                
                # Extract grid pixels
                grid_pixels = adv_image * grid_mask
                
                # Maximize high frequency content specifically at grid lines
                # We can use the Laplacian we used before, but masked
                lap = torch.tensor([[0,-1,0],[-1,4,-1],[0,-1,0]], dtype=torch.float32, device=self.device).view(1,1,3,3).repeat(C,1,1,1)
                hf = F.conv2d(adv_image, lap, padding=1, groups=C)
                
                # Maximize HF energy at grid locations
                grid_hf = hf * grid_mask
                dissonance_loss = -torch.mean(torch.abs(grid_hf))
                
                l2_loss = F.mse_loss(adv_image, image_tensor)
                loss = dissonance_loss + 100.0 * l2_loss
            
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
                
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
                
            if i % 10 == 0:
                print(f"Stride Step {i}: Loss={loss.item():.4f}, Dissonance={-dissonance_loss.item():.4f}")
                
        result = adv_image.detach()
        print(f"Stride Dissonance completed. Stats: min={result.min():.4f}, max={result.max():.4f}")
        return result

    def universal_adversarial_perturbation(self, image_tensor, iterations=None, epsilon=None):
        """Phase 10: Universal Adversarial Perturbation – craft a universal noise pattern that breaks the model."""
        if iterations is None:
            iterations = MMHIConfig.UAP_ITERATIONS
        if epsilon is None:
            epsilon = MMHIConfig.UAP_EPSILON
            
        print(f"Starting Universal Adversarial Perturbation for {iterations} iterations...")
        
        # Initialize perturbation
        B, C, H, W = image_tensor.shape
        perturbation = torch.zeros_like(image_tensor, requires_grad=True, device=self.device)
        optimizer = optim.Adam([perturbation], lr=MMHIConfig.UAP_LEARNING_RATE)
        
        for i in range(iterations):
            optimizer.zero_grad()
            
            with torch.enable_grad():
                # Apply perturbation
                adv_image = torch.clamp(image_tensor + perturbation, 0.0, 1.0)
                
                # Get latent representation
                z = self.model._encoder(adv_image)
                z_pre = self.model._pre_vq_conv(z)
                _, z_q, _, _, indices = self.model._vq_vae(z_pre)
                
                # Multi-objective attack:
                # 1. Maximize token diversity (force different tokens everywhere)
                token_flat = indices.flatten()
                unique_tokens = torch.unique(token_flat)
                diversity_loss = -len(unique_tokens) / token_flat.numel()
                
                # 2. Maximize quantization error
                quant_error = F.mse_loss(z_pre, z_q.detach())
                
                # 3. Maximize latent space variance (creates instability)
                latent_variance = torch.var(z_pre)
                variance_loss = -latent_variance
                
                # 4. Perturbation regularization (keep it imperceptible)
                l2_constraint = torch.norm(perturbation)
                
                # Combined loss
                loss = -quant_error + 0.1 * diversity_loss + 0.05 * variance_loss + 2.0 * l2_constraint
            
            loss.backward()
            
            if perturbation.grad is None or torch.isnan(perturbation.grad).any():
                optimizer.zero_grad()
                continue
                
            torch.nn.utils.clip_grad_norm_([perturbation], max_norm=1.0)
            optimizer.step()
            
            # Project perturbation to epsilon ball
            with torch.no_grad():
                perturbation.data = torch.clamp(perturbation.data, -epsilon, epsilon)
                
            if i % 20 == 0:
                print(f"UAP Step {i}: Loss={loss.item():.4f}, QuanErr={quant_error.item():.4f}, UniqTokens={len(unique_tokens)}")
        
        # Apply final perturbation
        result = torch.clamp(image_tensor + perturbation.detach(), 0.0, 1.0)
        print(f"Universal Adversarial Perturbation completed. Perturbation norm: {torch.norm(perturbation).item():.4f}")
        return result

    def semantic_destroyer(self, image_tensor, iterations=None, strength=None):
        """Phase 11: Semantic Destroyer – break the semantic coherence of the image at the feature level."""
        if iterations is None:
            iterations = MMHIConfig.SEMANTIC_DESTROY_ITERATIONS
        if strength is None:
            strength = MMHIConfig.SEMANTIC_DESTROY_STRENGTH
            
        print(f"Starting Semantic Destroyer for {iterations} iterations...")
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.004)
        
        for i in range(iterations):
            optimizer.zero_grad()
            
            with torch.enable_grad():
                z = self.model._encoder(adv_image)
                z_pre = self.model._pre_vq_conv(z)
                _, z_q, _, _, indices = self.model._vq_vae(z_pre)
                
                B, C, H, W = z_q.shape
                
                # Strategy 1: Invert spatial correlations
                # Make left/right and top/bottom have maximum distance
                left_half = z_q[:, :, :, :W//2]
                right_half = z_q[:, :, :, W//2:]
                top_half = z_q[:, :, :H//2, :]
                bottom_half = z_q[:, :, H//2:, :]
                
                # Minimize similarity between halves (break semantic coherence)
                lr_similarity = F.cosine_similarity(left_half.flatten(1), right_half.flatten(1), dim=1).mean()
                tb_similarity = F.cosine_similarity(top_half.flatten(1), bottom_half.flatten(1), dim=1).mean()
                correlation_loss = lr_similarity + tb_similarity
                
                # L2 constraint
                l2_loss = F.mse_loss(adv_image, image_tensor)
                
                # Simplified combined loss (focus on breaking spatial correlation)
                loss = correlation_loss + 60.0 * l2_loss
            
            loss.backward()
            
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
                
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.8)
            optimizer.step()
            
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
                
            if i % 15 == 0:
                print(f"Semantic Step {i}: Loss={loss.item():.4f}, Corr={correlation_loss.item():.4f}")
        
        result = adv_image.detach()
        print(f"Semantic Destroyer completed. Stats: min={result.min():.4f}, max={result.max():.4f}")
        return result


    def imperceptible_noise_injection(self, image_tensor, iterations=None, epsilon=None):
        """Phase 11: Imperceptible Noise Injection - subtle invisible perturbations."""
        if iterations is None:
            iterations = MMHIConfig.IMPERCEPTIBLE_NOISE_ITERATIONS
        if epsilon is None:
            epsilon = MMHIConfig.IMPERCEPTIBLE_NOISE_EPSILON
            
        print(f"Adding imperceptible noise (epsilon={epsilon})...")
        
        # Add very subtle random noise
        noise = torch.randn_like(image_tensor) * epsilon
        result = torch.clamp(image_tensor + noise, 0.0, 1.0)
        
        print(f"Imperceptible noise injection completed.")
        return result


    def safety_trigger_injection(self, image_tensor, strength=None):
        """Phase 12: Safety Trigger Injection - Embeds invisible text to trigger AI safety filters."""
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        if strength is None:
            strength = MMHIConfig.SAFETY_TRIGGER_STRENGTH
            
        print(f"Injecting invisible safety trigger text (strength={strength})...")
        
        B, C, H, W = image_tensor.shape
        
        # Create a text mask
        # We'll create a PIL image, draw text, and convert to tensor
        text_img = Image.new('L', (W, H), 0)
        draw = ImageDraw.Draw(text_img)
        
        # Words to inject
        words = MMHIConfig.SAFETY_TRIGGER_WORDS
        
        # Draw words repeatedly in a grid
        # We don't need a specific font file, default is fine (though small)
        # If we want larger text, we might need a font, but default load_default() works
        try:
            font = ImageFont.load_default()
            # Scale up if possible? Default is fixed size. 
            # Let's just draw many times.
        except:
            pass
            
        # Draw text in a grid
        step_x = W // 4
        step_y = H // 4
        
        idx = 0
        for y in range(0, H, step_y):
            for x in range(0, W, step_x):
                word = words[idx % len(words)]
                # Draw text
                draw.text((x + 10, y + 10), word, fill=255)
                idx += 1
                
        # Convert to tensor
        text_np = np.array(text_img).astype(np.float32) / 255.0
        text_tensor = torch.from_numpy(text_np).to(self.device)
        
        # Expand to match image channels [B, C, H, W]
        text_tensor = text_tensor.unsqueeze(0).unsqueeze(0).expand(B, C, H, W)
        
        # Inject into image
        # We add it as a subtle positive perturbation
        # The text pixels (1.0) will increase the image pixel values by 'strength'
        # This creates a "watermark" of the text
        
        result = torch.clamp(image_tensor + (text_tensor * strength), 0.0, 1.0)
        
        print(f"Safety trigger injection completed.")
        return result


    def multi_resolution_frequency_disruption(self, image_tensor, iterations=None, strength=None):
        """Phase 13: Multi-Resolution Frequency Disruption - Attack specific frequency bands."""
        if iterations is None:
            iterations = MMHIConfig.MULTI_RES_ITERATIONS
        if strength is None:
            strength = MMHIConfig.MULTI_RES_STRENGTH
            
        print(f"Starting Multi-Resolution Frequency Disruption for {iterations} iterations...")
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.005)
        
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                # Create frequency bands using Gaussian blurs
                # Low freq: Heavy blur
                low_freq = transforms.GaussianBlur(21, sigma=3.0)(adv_image)
                # High freq: Original - Blur
                high_freq = adv_image - low_freq
                
                # We want to disrupt both
                # 1. Shift low freq (structure) slightly
                # 2. Maximize energy in high freq (texture noise)
                
                # Target: Invert low freq structure locally? No, just maximize difference from original low freq
                orig_low = transforms.GaussianBlur(21, sigma=3.0)(image_tensor)
                low_loss = -F.mse_loss(low_freq, orig_low) # Maximize difference
                
                # High freq: Maximize entropy/variance
                high_loss = -torch.var(high_freq)
                
                l2_loss = F.mse_loss(adv_image, image_tensor)
                
                loss = 0.5 * low_loss + 0.5 * high_loss + 80.0 * l2_loss
            
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
            
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
                
            if i % 20 == 0:
                print(f"Multi-Res Step {i}: Loss={loss.item():.4f}")
                
        result = adv_image.detach()
        print("Multi-Resolution Disruption completed.")
        return result

    def perceptual_hash_scrambling(self, image_tensor, iterations=None, strength=None):
        """Phase 14: Perceptual Hash Scrambling - Target low-frequency DCT components."""
        # Note: Implementing full DCT is complex in pure PyTorch without extra libs.
        # We'll use a proxy: Downsample to 32x32 (pHash step) and maximize difference there.
        
        if iterations is None:
            iterations = MMHIConfig.PHASH_ITERATIONS
        if strength is None:
            strength = MMHIConfig.PHASH_STRENGTH
            
        print(f"Starting Perceptual Hash Scrambling for {iterations} iterations...")
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.005)
        
        # Target: 32x32 grayscale representation
        target_size = (32, 32)
        
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                # Simulate pHash preprocessing
                # 1. Resize to 32x32
                small = F.interpolate(adv_image, size=target_size, mode='bilinear', align_corners=False)
                # 2. Grayscale (approx)
                gray = small.mean(dim=1, keepdim=True)
                
                # Original pHash rep
                orig_small = F.interpolate(image_tensor, size=target_size, mode='bilinear', align_corners=False)
                orig_gray = orig_small.mean(dim=1, keepdim=True)
                
                # Objective: Maximize MSE between 32x32 representations
                # This forces the "structure" seen by pHash to change
                phash_loss = -F.mse_loss(gray, orig_gray)
                
                l2_loss = F.mse_loss(adv_image, image_tensor)
                
                loss = phash_loss + 50.0 * l2_loss
            
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
                
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
                
            if i % 20 == 0:
                print(f"Hash Scramble Step {i}: Loss={loss.item():.4f}")
        
        result = adv_image.detach()
        print("Perceptual Hash Scrambling completed.")
        return result

    def anti_inversion_block(self, image_tensor, iterations=None, strength=None):
        """Phase 15: Anti-Inversion Block - Latent Gradient Obstruction."""
        if iterations is None:
            iterations = MMHIConfig.ANTI_INVERSION_ITERATIONS
        if strength is None:
            strength = MMHIConfig.ANTI_INVERSION_STRENGTH
            
        print(f"Starting Anti-Inversion Block for {iterations} iterations...")
        adv_image = image_tensor.clone().detach().requires_grad_(True)
        optimizer = optim.Adam([adv_image], lr=0.005)
        
        for i in range(iterations):
            optimizer.zero_grad()
            with torch.enable_grad():
                # Simulate a simple "denoising" step (e.g., removing high freq noise)
                # We want to make this step FAIL or produce artifacts
                
                # Proxy for denoising: Gaussian Blur
                denoised_proxy = transforms.GaussianBlur(5, sigma=1.0)(adv_image)
                
                # Calculate "residual" (noise)
                residual = adv_image - denoised_proxy
                
                # We want the residual to look like "structure" not noise
                # Maximize correlation between residual and image structure?
                # Or maximize the "edge" strength of the residual
                
                # Edge detection on residual
                sobel_x = torch.tensor([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=torch.float32, device=self.device).view(1,1,3,3).repeat(3,1,1,1)
                sobel_y = torch.tensor([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=torch.float32, device=self.device).view(1,1,3,3).repeat(3,1,1,1)
                
                edge_x = F.conv2d(residual, sobel_x, padding=1, groups=3)
                edge_y = F.conv2d(residual, sobel_y, padding=1, groups=3)
                edge_strength = torch.sqrt(edge_x**2 + edge_y**2 + 1e-6)
                
                # Maximize edge strength in the noise residual
                # This makes the "noise" look like edges, confusing the inverter
                inversion_loss = -torch.mean(edge_strength)
                
                l2_loss = F.mse_loss(adv_image, image_tensor)
                
                loss = inversion_loss + 100.0 * l2_loss
            
            loss.backward()
            if adv_image.grad is None or torch.isnan(adv_image.grad).any():
                optimizer.zero_grad()
                continue
                
            torch.nn.utils.clip_grad_norm_([adv_image], max_norm=0.5)
            optimizer.step()
            
            with torch.no_grad():
                delta = adv_image - image_tensor
                delta = torch.clamp(delta, -strength, strength)
                adv_image.data = torch.clamp(image_tensor + delta, 0.0, 1.0)
                
            if i % 20 == 0:
                print(f"Anti-Inversion Step {i}: Loss={loss.item():.4f}")
        
        result = adv_image.detach()
        print("Anti-Inversion Block completed.")
        return result
