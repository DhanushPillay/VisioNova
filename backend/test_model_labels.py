"""
Test script to check model label mapping
"""
from text_detector import AIContentDetector

# Test with both human and AI text
human_text = "hey whats up? yeah i totally get what you mean lol. like when i was trying to learn python last year i was so confused at first but then it just clicked you know?"

ai_text = "Furthermore, it is important to note that learning programming requires dedication and consistent practice. Additionally, one should leverage available resources such as online tutorials and documentation."

detector = AIContentDetector(use_ml_model=True)

print("="*60)
print("Testing Human Text:")
print("="*60)
result_human = detector.predict(human_text, detailed=False)
print(f"Text: {human_text[:80]}...")
print(f"Prediction: {result_human['prediction']}")
print(f"Scores: {result_human['scores']}")
print(f"Confidence: {result_human['confidence']}%")

print("\n" + "="*60)
print("Testing AI Text:")
print("="*60)
result_ai = detector.predict(ai_text, detailed=False)
print(f"Text: {ai_text[:80]}...")
print(f"Prediction: {result_ai['prediction']}")
print(f"Scores: {result_ai['scores']}")
print(f"Confidence: {result_ai['confidence']}%")

print("\n" + "="*60)
print("ANALYSIS:")
print("="*60)
if result_human['prediction'] == 'human' and result_ai['prediction'] == 'ai_generated':
    print("✓ Results are CORRECT")
elif result_human['prediction'] == 'ai_generated' and result_ai['prediction'] == 'human':
    print("✗ Results are REVERSED - need to swap label indices")
else:
    print("? Results are mixed - need further investigation")
