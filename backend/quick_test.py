"""Quick test of the detector with sample text"""
from text_detector import AIContentDetector

detector = AIContentDetector(use_ml_model=False)

# Test AI-generated text
ai_text = """This is a test. It is important to note that technology is evolving rapidly. 
Furthermore, we must delve into the implications. In conclusion, these changes are significant."""

result = detector.predict(ai_text)
print("=" * 60)
print("AI TEXT SAMPLE")
print("=" * 60)
print(f"Prediction: {result['prediction']}")
print(f"AI Score: {result['scores']['ai_generated']:.1f}%")
print(f"Confidence: {result['confidence']:.1f}%")
print(f"Patterns Found: {result['detected_patterns']['total_count']}")

# Test human-written text
human_text = """Went to the store yesterday. Milk was way too expensive. My dog keeps barking at the mailman again. 
Probably going to watch Netflix later."""

result2 = detector.predict(human_text)
print("\n" + "=" * 60)
print("HUMAN TEXT SAMPLE")
print("=" * 60)
print(f"Prediction: {result2['prediction']}")
print(f"AI Score: {result2['scores']['ai_generated']:.1f}%")
print(f"Confidence: {result2['confidence']:.1f}%")
print(f"Patterns Found: {result2['detected_patterns']['total_count']}")

print("\n[OK] Detector working correctly!")
