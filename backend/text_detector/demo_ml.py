#!/usr/bin/env python3
"""
Quick test for ML-based AI text detection
Tests with sample texts without needing a trained model
"""

from utils_ml import preprocess, extra_features


def demo_preprocessing():
    """Demo the preprocessing function"""
    print("\n" + "="*70)
    print("TEXT PREPROCESSING DEMO")
    print("="*70 + "\n")
    
    test_cases = [
        "Hello! How are you?",
        "The implementation (of AI) requires careful consideration, isn't it?",
        "123 numbers and symbols!!! are removed.",
        "   Extra    whitespace    is    normalized   ",
    ]
    
    for text in test_cases:
        processed = preprocess(text)
        print(f"Original:   {text}")
        print(f"Processed:  {processed}")
        print()


def demo_features():
    """Demo the feature extraction"""
    print("="*70)
    print("FEATURE EXTRACTION DEMO")
    print("="*70 + "\n")
    
    test_texts = [
        "Short text",
        "This is a longer text with more words to analyze",
        "The quick brown fox jumps over the lazy dog and the quick brown fox jumps",
        "Varied unique words contribute to higher vocabulary diversity metrics",
    ]
    
    for text in test_texts:
        processed = preprocess(text)
        features = extra_features(processed)
        words = processed.split()
        unique = len(set(words))
        
        print(f"Text: {text}")
        print(f"  Words: {len(words)}")
        print(f"  Unique: {unique}")
        print(f"  Unique Ratio: {features[1]:.4f}")
        print(f"  Features: {features}")
        print()


def demo_ml_predictor():
    """Demo the ML predictor (if model exists)"""
    print("="*70)
    print("ML PREDICTOR DEMO")
    print("="*70 + "\n")
    
    try:
        from predict_ml import MLTextPredictor
        
        print("[INFO] Loading ML model...")
        predictor = MLTextPredictor()
        
        test_texts = [
            ("hey whats up buddy", "Human casual text"),
            ("In conclusion, the multifaceted implications warrant examination", "AI formal text"),
            ("implementation necessitates careful computational consideration", "AI academic text"),
        ]
        
        for text, description in test_texts:
            print(f"\n{description}")
            print(f"Text: {text}")
            result = predictor.predict(text)
            print(f"  Prediction: {result['prediction']}")
            print(f"  Confidence: {result['confidence']:.2f}%")
            print(f"  Human: {result['human_prob']:.4f}, AI: {result['ai_prob']:.4f}")
        
    except FileNotFoundError:
        print("[INFO] ML model not found. Train first with:")
        print("       python train_ml.py dataset.csv")
        print("\n[TIP] You can still test preprocessing and features above.")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("ML TEXT DETECTION - DEMO")
    print("="*70)
    
    # Always run these
    demo_preprocessing()
    demo_features()
    
    # Try ML demo
    demo_ml_predictor()
    
    print("\n" + "="*70)
    print("Demo complete!")
    print("="*70 + "\n")
