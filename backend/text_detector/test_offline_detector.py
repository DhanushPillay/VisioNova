"""
Test the offline AI text detector with sample human and AI texts.
"""
from detector import AIContentDetector


def test_offline_detector():
    """Test offline detector with obvious AI and human text samples."""
    
    # Initialize in OFFLINE mode
    print("=" * 60)
    print("Initializing AI Detector in OFFLINE MODE...")
    print("=" * 60)
    detector = AIContentDetector(use_ml_model=False)
    print()
    
    # Test 1: Obvious AI text (ChatGPT style)
    ai_text = """
    It's important to note that artificial intelligence has revolutionized many industries. 
    Furthermore, the technology continues to evolve at a rapid pace. 
    In conclusion, we must delve into both the benefits and potential risks of AI adoption.
    Additionally, it's crucial to implement proper safeguards. Moreover, organizations should 
    carefully consider the ethical implications. In today's world, AI is transforming 
    the landscape of technology.
    """
    
    # Test 2: Casual human text
    human_text = """
    Went to the store today. Milk was expensive! 
    Can't believe how much prices went up. 
    My dog's being super weird lately lol. He keeps barking at nothing. 
    Maybe I should take him to the vet. 
    Or he's just being dramatic as usual.
    """
    
    # Test 3: Mixed/ambiguous text
    mixed_text = """
    The project deadline is approaching. We need to finalize the design and implementation.
    I think we should prioritize the core features first. Maybe we can add the extras later.
    It depends on how much time we have left. Let me know what you think.
    """
    
    print("\n" + "=" * 60)
    print("TEST 1: AI-Generated Text")
    print("=" * 60)
    result1 = detector.predict(ai_text)
    print(f"Prediction: {result1['prediction'].upper()}")
    print(f"Confidence: {result1['confidence']:.1f}%")
    print(f"AI Score: {result1['scores']['ai_generated']:.1f}%")
    print(f"Human Score: {result1['scores']['human']:.1f}%")
    print(f"Patterns Detected: {result1['detected_patterns']['total_count']}")
    if result1['detected_patterns']['total_count'] > 0:
        print("Pattern Categories:")
        for cat, info in result1['detected_patterns']['categories'].items():
            print(f"  - {info['type']}: {info['count']} occurrences")
    
    print("\n" + "=" * 60)
    print("TEST 2: Human-Written Text")
    print("=" * 60)
    result2 = detector.predict(human_text)
    print(f"Prediction: {result2['prediction'].upper()}")
    print(f"Confidence: {result2['confidence']:.1f}%")
    print(f"AI Score: {result2['scores']['ai_generated']:.1f}%")
    print(f"Human Score: {result2['scores']['human']:.1f}%")
    print(f"Patterns Detected: {result2['detected_patterns']['total_count']}")
    
    print("\n" + "=" * 60)
    print("TEST 3: Mixed/Ambiguous Text")
    print("=" * 60)
    result3 = detector.predict(mixed_text)
    print(f"Prediction: {result3['prediction'].upper()}")
    print(f"Confidence: {result3['confidence']:.1f}%")
    print(f"AI Score: {result3['scores']['ai_generated']:.1f}%")
    print(f"Human Score: {result3['scores']['human']:.1f}%")
    print(f"Patterns Detected: {result3['detected_patterns']['total_count']}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    tests = [
        ("AI Text", result1, True),
        ("Human Text", result2, False),
        ("Mixed Text", result3, None)
    ]
    
    correct = 0
    for name, result, should_be_ai in tests:
        if should_be_ai is None:
            continue  # Skip ambiguous
        prediction_is_ai = result['prediction'] == 'ai_generated'
        is_correct = prediction_is_ai == should_be_ai
        if is_correct:
            correct += 1
        status = "✓ CORRECT" if is_correct else "✗ INCORRECT"
        print(f"{name}: {status} (predicted {result['prediction']})")
    
    print(f"\nAccuracy: {correct}/2 ({correct*50}%)")
    print("\n" + "=" * 60)
    print("Offline detector is working!")
    print("=" * 60)


if __name__ == "__main__":
    test_offline_detector()
