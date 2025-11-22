import torch
import numpy as np
from PIL import Image
import io
import base64
import time
from torchvision import transforms
from .models import MiniVQVAE
from .attacks import MMHIAttacker
from .config import MMHIConfig

class MMHIPipeline:
    def __init__(self):
        self.device = torch.device(MMHIConfig.DEVICE if torch.cuda.is_available() else "cpu")
        print(f"MMHI Pipeline initialized on {self.device}")
        # Proxy VQ‑VAE model (trained per‑image)
        self.proxy_model = MiniVQVAE().to(self.device)
        self.attacker = MMHIAttacker(self.proxy_model, self.device)
        self.preprocess = transforms.Compose([
            transforms.Resize((MMHIConfig.IMAGE_SIZE, MMHIConfig.IMAGE_SIZE)),
            transforms.ToTensor(),
        ])

    def _load_image(self, image_path_or_obj):
        if isinstance(image_path_or_obj, str):
            img = Image.open(image_path_or_obj).convert('RGB')
        else:
            img = image_path_or_obj.convert('RGB')
        return img

    def protect(self, image_path_or_obj, strength="medium", phases=None):
        """Run the full multi‑phase protection pipeline.
        Returns a dict with the protected PIL image, processing time and a list of applied phases.
        """
        start = time.time()
        image = self._load_image(image_path_or_obj)
        original_size = image.size
        img_tensor = self.preprocess(image).unsqueeze(0).to(self.device)

        # Phase 1 – train a per‑image proxy VQ‑VAE
        print("Phase 1: Training Proxy Tokenizer…")
        self.proxy_model.fit(img_tensor, steps=MMHIConfig.VQ_TRAIN_STEPS, device=self.device)

        # Helper to adjust strength‑dependent hyper‑parameters
        def strength_params(high, extreme, default):
            if strength == "high":
                return high
            if strength == "extreme":
                return extreme
            return default

        # Phase 2 – Quantization Boundary Shifting
        print("Phase 2: Quantization Boundary Shifting…")
        qbs_iter = strength_params(100, 200, MMHIConfig.QBS_ITERATIONS)
        qbs_eps  = strength_params(0.08, 0.12, MMHIConfig.QBS_EPSILON)
        protected = self.attacker.quantization_boundary_shift(img_tensor, iterations=qbs_iter, epsilon=qbs_eps)

        # Phase 3 – Logic Injection
        print("Phase 3: Logic Injection…")
        logic_iter = strength_params(50, 70, MMHIConfig.LOGIC_INJECTION_ITERATIONS)
        logic_str  = strength_params(0.05, 0.07, MMHIConfig.LOGIC_INJECTION_STRENGTH)
        prev = protected.clone()
        protected = self.attacker.logic_injection(protected, iterations=logic_iter, strength=logic_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Logic Injection – reverting.")
            protected = prev

        # Phase 4 – Attention Hijacking
        print("Phase 4: Attention Hijacking…")
        att_iter = strength_params(60, 80, MMHIConfig.ATTENTION_HIJACK_ITERATIONS)
        att_str  = strength_params(0.06, 0.08, MMHIConfig.ATTENTION_HIJACK_STRENGTH)
        prev = protected.clone()
        protected = self.attacker.attention_hijacking(protected, iterations=att_iter, strength=att_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Attention Hijacking – reverting.")
            protected = prev

        # Phase 5 – Autoregressive Token Corruption
        print("Phase 5: Autoregressive Token Corruption…")
        auto_iter = strength_params(50, 70, MMHIConfig.AUTOREGRESSIVE_ITERATIONS)
        auto_str  = strength_params(0.07, 0.09, MMHIConfig.AUTOREGRESSIVE_STRENGTH)
        prev = protected.clone()
        protected = self.attacker.autoregressive_corruption(protected, iterations=auto_iter, strength=auto_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Autoregressive Corruption – reverting.")
            protected = prev

        # Phase 6 – Frequency Domain Poisoning
        print("Phase 6: Frequency Domain Poisoning…")
        freq_iter = strength_params(35, 50, MMHIConfig.FREQUENCY_POISON_ITERATIONS)
        freq_alpha = strength_params(0.03, 0.04, MMHIConfig.FREQUENCY_POISON_ALPHA)
        prev = protected.clone()
        protected = self.attacker.frequency_poisoning(protected, iterations=freq_iter, alpha=freq_alpha)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Frequency Poisoning – reverting.")
            protected = prev

        # Phase 7 – Feature‑Map Disruption
        print("Phase 7: Feature‑Map Disruption…")
        fm_iter = strength_params(45, 60, 30)
        fm_str  = strength_params(0.03, 0.04, 0.02)
        prev = protected.clone()
        protected = self.attacker.feature_map_disruption(protected, iterations=fm_iter, strength=fm_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Feature‑Map Disruption – reverting.")
            protected = prev

        # Phase 8: Gradient Shattering
        print("Phase 8: Gradient Shattering…")
        shatter_iter = strength_params(40, 50, MMHIConfig.GRADIENT_SHATTER_ITERATIONS)
        shatter_str = strength_params(0.05, 0.06, MMHIConfig.GRADIENT_SHATTER_STRENGTH)
        prev = protected.clone()
        protected = self.attacker.gradient_shattering(protected, iterations=shatter_iter, strength=shatter_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Gradient Shattering – reverting.")
            protected = prev

        # Phase 9: Stride-Aware Dissonance
        print("Phase 9: Stride-Aware Dissonance…")
        stride_iter = strength_params(40, 50, MMHIConfig.STRIDE_DISSONANCE_ITERATIONS)
        stride_str = strength_params(0.04, 0.05, MMHIConfig.STRIDE_DISSONANCE_STRENGTH)
        prev = protected.clone()
        protected = self.attacker.stride_dissonance(protected, iterations=stride_iter, strength=stride_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Stride Dissonance – reverting.")
            protected = prev

        # Phase 10: Universal Adversarial Perturbation (NEW - AGGRESSIVE)
        print("Phase 10: Universal Adversarial Perturbation…")
        uap_iter = strength_params(200, 300, MMHIConfig.UAP_ITERATIONS)
        uap_eps = strength_params(0.22, 0.30, MMHIConfig.UAP_EPSILON)
        prev = protected.clone()
        protected = self.attacker.universal_adversarial_perturbation(protected, iterations=uap_iter, epsilon=uap_eps)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after UAP – reverting.")
            protected = prev

        # Phase 11: Imperceptible Noise Injection (NEW - Subtle final layer)
        print("Phase 11: Imperceptible Noise Injection…")
        noise_eps = strength_params(0.025, 0.035, MMHIConfig.IMPERCEPTIBLE_NOISE_EPSILON)
        prev = protected.clone()
        protected = self.attacker.imperceptible_noise_injection(protected, epsilon=noise_eps)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Imperceptible Noise – reverting.")
            protected = prev

        # Phase 12: Safety Trigger Injection (NEW - AI Visible Text)
        print("Phase 12: Safety Trigger Injection…")
        safety_str = strength_params(0.03, 0.05, MMHIConfig.SAFETY_TRIGGER_STRENGTH)
        prev = protected.clone()
        protected = self.attacker.safety_trigger_injection(protected, strength=safety_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Safety Trigger – reverting.")
            protected = prev

        # Phase 13: Multi-Resolution Frequency Disruption (NEW)
        print("Phase 13: Multi-Resolution Frequency Disruption…")
        mr_iter = strength_params(60, 80, MMHIConfig.MULTI_RES_ITERATIONS)
        mr_str = strength_params(0.10, 0.15, MMHIConfig.MULTI_RES_STRENGTH)
        prev = protected.clone()
        protected = self.attacker.multi_resolution_frequency_disruption(protected, iterations=mr_iter, strength=mr_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Multi-Res Disruption – reverting.")
            protected = prev

        # Phase 14: Perceptual Hash Scrambling (NEW)
        print("Phase 14: Perceptual Hash Scrambling…")
        ph_iter = strength_params(50, 70, MMHIConfig.PHASH_ITERATIONS)
        ph_str = strength_params(0.06, 0.10, MMHIConfig.PHASH_STRENGTH)
        prev = protected.clone()
        protected = self.attacker.perceptual_hash_scrambling(protected, iterations=ph_iter, strength=ph_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Hash Scrambling – reverting.")
            protected = prev

        # Phase 15: Anti-Inversion Block (NEW)
        print("Phase 15: Anti-Inversion Block…")
        ai_iter = strength_params(60, 80, MMHIConfig.ANTI_INVERSION_ITERATIONS)
        ai_str = strength_params(0.08, 0.12, MMHIConfig.ANTI_INVERSION_STRENGTH)
        prev = protected.clone()
        protected = self.attacker.anti_inversion_block(protected, iterations=ai_iter, strength=ai_str)
        if torch.isnan(protected).any() or torch.isinf(protected).any():
            print("Warning: NaN/Inf after Anti-Inversion – reverting.")
            protected = prev

        # Final post‑processing
        protected = protected.squeeze(0).cpu().detach()
        protected = torch.clamp(protected, 0, 1)
        protected_image = transforms.ToPILImage()(protected)
        protected_image = protected_image.resize(original_size, Image.LANCZOS)

        elapsed = time.time() - start
        return {
            "protected_image": protected_image,
            "processing_time": elapsed,
            "phases_applied": [
                "Proxy Training",
                "QBS",
                "Logic Injection",
                "Attention Hijacking",
                "Autoregressive Corruption",
                "Frequency Poisoning",
                "Feature‑Map Disruption",
                "Gradient Shattering",
                "Stride Dissonance",
                "Universal Adversarial Perturbation",
                "Imperceptible Noise Injection",
                "Safety Trigger Injection",
                "Multi-Resolution Frequency Disruption",
                "Perceptual Hash Scrambling",
                "Anti-Inversion Block"
            ]
        }

    def protect_base64(self, b64_string, strength="medium", phases=None):
        image_data = base64.b64decode(b64_string)
        image = Image.open(io.BytesIO(image_data))
        result = self.protect(image, strength, phases=phases)
        buf = io.BytesIO()
        result["protected_image"].save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {
            "protected_image_b64": img_b64,
            "processing_time_seconds": result["processing_time"],
            "phases_applied": result["phases_applied"]
        }
