"""
VisioNova ML Model Setup Script
Downloads and caches all required ML models from HuggingFace.
"""

import os
import logging
from transformers import AutoImageProcessor, AutoModelForImageClassification

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS = [
    "NYUAD-ComNets/NYUAD_AI-generated_images_detector",
    "haywoodsloan/ai-image-detector-dev-deploy",  # SwinV2
    "Organika/sdxl-detector",
    "dima806/deepfake_vs_real_image_detection",
    "Umotion/DeepTruth-Image-Detector", 
    
    # NEW: SOTA Models (Feb 2026) - User Selected
    # "Bombek1/ai-image-detector-siglip-dinov2",  # (Skipped due to config error)
    # "prithivMLmods/Deepfake-Detect-Siglip2",    # (User rejected)
    # "prithivMLmods/AI-vs-Deepfake-vs-Real-Siglip2", # (User rejected)
    # "Smogy/SMOGY-Ai-images-detector",           # (User rejected)
    
    "WpythonW/dinoV2-deepfake-detector",        # DINOv2 (Likely acceptable)
    "umm-maybe/AI-image-detector",              # 280k+ Downloads (ResNet/ViT hybrid)
]

# Additional models mentioned in code but maybe not standard HF:
# "Bombek1/SigLIP2-DINOv2" (Example, might need specific repo)
# "prithivMLmods/Deepfake-Detect-Siglip2"

def download_models():
    logger.info("Starting ML model download...")
    
    for model_id in MODELS:
        try:
            logger.info(f"Downloading {model_id}...")
            # Download processor and model
            AutoImageProcessor.from_pretrained(model_id)
            AutoModelForImageClassification.from_pretrained(model_id)
            logger.info(f"✓ Successfully downloaded {model_id}")
        except Exception as e:
            logger.error(f"✗ Failed to download {model_id}: {e}")

    logger.info("Model download complete.")

if __name__ == "__main__":
    download_models()
