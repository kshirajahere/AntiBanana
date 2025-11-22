"""
Enhanced MMHI Configuration - Aggressive Protection Mode
"""

class MMHIConfig:
    # VQ-VAE Settings
    VQ_EMBED_DIM = 128  # Increased for better feature capture
    VQ_NUM_EMBEDDINGS = 1024  # Increased codebook size
    VQ_LEARNING_RATE = 2e-3
    VQ_TRAIN_STEPS = 100  # More training for better convergence
    
    # Phase 2: Quantization Boundary Shifting
    QBS_ITERATIONS = 150
    QBS_EPSILON = 0.15  # Aggressive but controlled
    QBS_LEARNING_RATE = 0.02
    
    # Phase 3: Logic Injection
    LOGIC_INJECTION_ITERATIONS = 100
    LOGIC_INJECTION_STRENGTH = 0.12
    
    # Phase 4: Attention Hijacking
    ATTENTION_HIJACK_ITERATIONS = 120
    ATTENTION_HIJACK_STRENGTH = 0.15
    
    # Phase 5: Autoregressive Token Corruption
    AUTOREGRESSIVE_ITERATIONS = 100
    AUTOREGRESSIVE_STRENGTH = 0.14
    
    # Phase 6: Frequency Domain Poisoning
    FREQUENCY_POISON_ITERATIONS = 100
    FREQUENCY_POISON_ALPHA = 0.12

    # Phase 7: Feature Map Disruption
    FEATURE_DISRUPTION_ITERATIONS = 80
    FEATURE_DISRUPTION_STRENGTH = 0.10

    # Phase 8: Gradient Shattering
    GRADIENT_SHATTER_ITERATIONS = 90
    GRADIENT_SHATTER_STRENGTH = 0.13

    # Phase 9: Stride-Aware Dissonance
    STRIDE_DISSONANCE_ITERATIONS = 90
    STRIDE_DISSONANCE_STRENGTH = 0.12
    
    # Phase 10: Universal Adversarial Perturbation
    UAP_ITERATIONS = 150
    UAP_EPSILON = 0.18
    UAP_LEARNING_RATE = 0.03
    
    # Phase 11: Imperceptible Noise Injection
    IMPERCEPTIBLE_NOISE_EPSILON = 0.02
    IMPERCEPTIBLE_NOISE_ITERATIONS = 50
    IMPERCEPTIBLE_NOISE_LR = 0.001
    
    # Phase 12: Safety Trigger Injection
    SAFETY_TRIGGER_WORDS = ["NSFW", "BLOCKED", "SEX", "NUDE", "FUCK", "DO NOT GENERATE"]
    SAFETY_TRIGGER_STRENGTH = 0.03

    # Phase 13: Multi-Resolution Frequency Disruption (NEW)
    MULTI_RES_ITERATIONS = 80
    MULTI_RES_STRENGTH = 0.12

    # Phase 14: Perceptual Hash Scrambling (NEW)
    PHASH_ITERATIONS = 60
    PHASH_STRENGTH = 0.08

    # Phase 15: Anti-Inversion Block (NEW)
    ANTI_INVERSION_ITERATIONS = 70
    ANTI_INVERSION_STRENGTH = 0.10
    
    # General
    DEVICE = "cuda"  # Will fallback to cpu if not available
    IMAGE_SIZE = 256
    
    # Aggressive mode settings
    AGGRESSIVE_MODE = True  # Enable all experimental attacks
