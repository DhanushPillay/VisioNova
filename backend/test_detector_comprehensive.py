"""
Comprehensive test of the AI text detector to identify issues.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from text_detector import AIContentDetector


def test_detector_comprehensive():
    """Test detector with various AI and human text samples."""
    
    print("=" * 70)
    print("COMPREHENSIVE AI TEXT DETECTOR TEST")
    print("=" * 70)
    
    # Initialize detector
    detector = AIContentDetector(use_ml_model=False)
    print("\n[OK] Detector initialized in OFFLINE mode\n")
    
    # Test cases with expected results
    test_cases = [
        # Clear AI-generated text
        {
            "name": "ChatGPT-style AI text (clear)",
            "text": """It's important to note that artificial intelligence has revolutionized 
            numerous industries. Furthermore, the technology continues to evolve at a rapid pace. 
            In conclusion, we must delve into both the benefits and potential risks of AI adoption. 
            Additionally, it's crucial to implement proper safeguards. Moreover, organizations should 
            carefully consider the ethical implications. In today's world, AI is transforming 
            the landscape of technology.""",
            "expected": "ai_generated"
        },
        # Clear human-written text
        {
            "name": "Casual human text (clear)",
            "text": """Went to the store today and milk was super expensive! Can't believe 
            the prices. My dog's being weird lately lol - keeps barking at nothing. Maybe I should 
            take him to the vet or he's just being dramatic as usual.""",
            "expected": "human"
        },
        # Professional human writing
        {
            "name": "Professional human writing",
            "text": """The project has hit a snag with the database migration. We need to 
            rollback to the previous version asap. I'm annoyed - this wasn't supposed to happen. 
            Let me know when you've fixed it. The client's getting impatient.""",
            "expected": "human"
        },
        # Simple sentence
        {
            "name": "Simple human sentence",
            "text": "I went to the grocery store and bought milk and eggs.",
            "expected": "human"
        },
        # GPT-like formal text
        {
            "name": "GPT-like formal response",
            "text": """To elaborate on this matter, we must consider the multitude of factors 
            that contribute to this phenomenon. As previously mentioned, the landscape of modern 
            technology presents both opportunities and challenges. It is therefore essential to 
            navigate these complexities with caution and foresight.""",
            "expected": "ai_generated"
        },
        # Mixed but lean human
        {
            "name": "Mixed but human-leaning",
            "text": """The conference was good. They had some interesting speakers but honestly 
            it went too long. I got bored in the afternoon sessions. Still, worth going I guess.""",
            "expected": "human"
        },
        # Very short text (should be hard to classify)
        {
            "name": "Very short text",
            "text": "Hello world",
            "expected": None  # Don't test this strictly
        }
    ]
    
    results = []
    correct = 0
    total = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test_case['name']}")
        print(f"{'='*70}")
        
        text = test_case['text']
        expected = test_case['expected']
        
        # Show sample of text
        print(f"Text preview: {text[:100]}...")
        
        # Run detection
        result = detector.predict(text)
        
        prediction = result['prediction']
        confidence = result['confidence']
        ai_score = result['scores']['ai_generated']
        human_score = result['scores']['human']
        patterns = result['detected_patterns']['total_count']
        
        print(f"\nResults:")
        print(f"  Prediction: {prediction}")
        print(f"  Confidence: {confidence:.1f}%")
        print(f"  AI Score: {ai_score:.1f}%")
        print(f"  Human Score: {human_score:.1f}%")
        print(f"  Patterns Found: {patterns}")
        
        # Check if correct
        if expected is not None:
            is_correct = prediction == expected
            status = "[OK] CORRECT" if is_correct else "[FAIL] INCORRECT"
            print(f"\nExpected: {expected}")
            print(f"Status: {status}")
            
            if is_correct:
                correct += 1
            total += 1
            results.append({
                "test": test_case['name'],
                "expected": expected,
                "predicted": prediction,
                "correct": is_correct,
                "confidence": confidence,
                "ai_score": ai_score
            })
        
        # Show top patterns if any
        if patterns > 0 and 'categories' in result['detected_patterns']:
            print("\nTop patterns:")
            for category, info in list(result['detected_patterns']['categories'].items())[:3]:
                print(f"  - {info['type']}: {info['count']} times")
    
    # Summary
    print(f"\n\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    
    if total > 0:
        accuracy = (correct / total) * 100
        print(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    else:
        print("No valid tests to summarize")
    
    print(f"\nDetailed Results:")
    print(f"{'Test':<40} {'Expected':<15} {'Predicted':<15} {'Status':<10}")
    print("-" * 80)
    for r in results:
        status = "[OK]" if r['correct'] else "[FAIL]"
        print(f"{r['test']:<40} {r['expected']:<15} {r['predicted']:<15} {status:<10}")
    
    # Analysis
    print(f"\n{'='*70}")
    print("ANALYSIS")
    print(f"{'='*70}")
    
    if total > 0:
        failed_tests = [r for r in results if not r['correct']]
        if failed_tests:
            print(f"\n[WARN] Failed tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  - {test['test']}")
                print(f"    Expected: {test['expected']}, Got: {test['predicted']}")
                print(f"    AI Score: {test['ai_score']:.1f}% (confidence: {test['confidence']:.1f}%)")
        else:
            print("\n[OK] All tests passed!")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    test_detector_comprehensive()
