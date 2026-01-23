"""
Speed test for the detector - check if it's responsive now
"""
import time
from text_detector import AIContentDetector

# Initialize detector
detector = AIContentDetector(use_ml_model=False)

# Test texts
short_text = "hey whats up? yeah i totally get what you mean lol"

medium_text = """Furthermore, it is important to note that learning programming requires dedication and consistent practice. 
Additionally, one should leverage available resources such as online tutorials and documentation. 
In conclusion, the journey of learning to code is both challenging and rewarding. 
Moreover, it is crucial to maintain patience throughout the process. 
Research indicates that technology has revolutionized our world in many ways."""

long_text = medium_text * 5  # Create a longer text

print("="*60)
print("SPEED TEST - Detector Performance")
print("="*60)

# Test 1: Short text
print("\n1. SHORT TEXT (50 chars)")
start = time.time()
result = detector.predict(short_text, detailed=True)
elapsed = time.time() - start
print(f"   Time: {elapsed:.3f}s")
print(f"   Result: {result['prediction']} ({result['confidence']:.1f}%)")

# Test 2: Medium text
print("\n2. MEDIUM TEXT (500 chars)")
start = time.time()
result = detector.predict(medium_text, detailed=True)
elapsed = time.time() - start
print(f"   Time: {elapsed:.3f}s")
print(f"   Result: {result['prediction']} ({result['confidence']:.1f}%)")

# Test 3: Long text
print("\n3. LONG TEXT (2500+ chars - should skip detailed)")
start = time.time()
result = detector.predict(long_text, detailed=True)
elapsed = time.time() - start
print(f"   Time: {elapsed:.3f}s")
print(f"   Result: {result['prediction']} ({result['confidence']:.1f}%)")
has_sentence_analysis = "sentence_analysis" in result
print(f"   Has sentence analysis: {has_sentence_analysis}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("✓ If all tests completed in < 1s each, performance is good")
print("✓ Long text should skip detailed analysis (no sentence_analysis)")
