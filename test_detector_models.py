import sys
import os
import io
import logging
from PIL import Image
import numpy as np

# Add backend to path so imports work
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_detectors():
    print("\n--- Testing Image Detector Integration ---\n")
    
    # 1. Test ImageDetector
    try:
        from image_detector.detector import ImageDetector
        print("Initializing ImageDetector...")
        detector = ImageDetector()
        
        if detector.model_loaded:
            print("✓ ImageDetector loaded ML models successfully")
        else:
            print("✗ ImageDetector failed to load ML models (falling back to stats)")
            
        # create dummy image
        img = Image.new('RGB', (100, 100), color='white')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        print("Running detection on dummy image...")
        result = detector.detect(img_bytes, filename="test.png")
        
        analysis_mode = result.get('analysis_mode', 'Unknown')
        print(f"Analysis Mode reported: {analysis_mode}")
        
        if "ML Ensemble" in analysis_mode:
            print("✓ SUCCESS: ImageDetector is using ML models")
        else:
            print("✗ FAILURE: ImageDetector is using fallback mode")
            
    except Exception as e:
        print(f"✗ Error testing ImageDetector: {e}")

    print("\n--- Testing Ensemble Detector Integration ---\n")

    # 2. Test EnsembleDetector
    try:
        from image_detector.ensemble_detector import EnsembleDetector
        print("Initializing EnsembleDetector...")
        ensemble = EnsembleDetector()
        
        # Check active models
        active_models = []
        if ensemble.nyuad_detector and ensemble.nyuad_detector.model_loaded: active_models.append("NYUAD")
        if ensemble.dire_detector and ensemble.dire_detector.model_loaded: active_models.append("DIRE") # Note: dire_detector might rely on heuristic but model_loaded flag tells if it's "ready"
        if ensemble.clip_detector and ensemble.clip_detector.model_loaded: active_models.append("CLIP")
        
        print(f"Active Ensemble Models: {active_models}")
        
        print("Running ensemble detection...")
        result = ensemble.detect(img_bytes, filename="test.png")
        
        analysis_mode = result.get('analysis_mode', 'Unknown')
        print(f"Ensemble Analysis Mode: {analysis_mode}")

        if "Multi-Model" in analysis_mode or "Ensemble" in analysis_mode:
             print("✓ SUCCESS: EnsembleDetector is using multiple models")
        else:
             print("✗ FAILURE: EnsembleDetector is using fallback mode")

    except Exception as e:
        print(f"✗ Error testing EnsembleDetector: {e}")

if __name__ == "__main__":
    test_detectors()
