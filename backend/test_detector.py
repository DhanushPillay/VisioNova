import sys
import os
import json

# Add backend to path to import detector
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from text_checker import AIContentDetector
    
    print("Initializing AI Content Detector...")
    detector = AIContentDetector()
    
    test_texts = [
        "The quick brown fox jumps over the lazy dog. This is a classic sentence used for testing purposes and it is likely written by a human.",
        "As an AI language model, I can generate text that sounds natural but may follow certain patterns. Here is an example of such text structure."
    ]
    
    for i, text in enumerate(test_texts):
        print(f"\nTest {i+1}:")
        print(f"Text: {text[:50]}...")
        result = detector.predict(text)
        print(f"Result: {json.dumps(result, indent=2)}")

except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
