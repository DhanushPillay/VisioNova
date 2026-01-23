"""
Extended AI detector tests with challenging edge cases.
Tests robustness against subtle AI-generated text and challenging human samples.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from text_detector import AIContentDetector


def test_extended():
    """Extended tests with edge cases and challenging samples."""
    
    print("=" * 70)
    print("EXTENDED AI TEXT DETECTOR TESTS")
    print("Testing with edge cases, subtle AI, and challenging human samples")
    print("=" * 70)
    
    detector = AIContentDetector(use_ml_model=False)
    print("\n[OK] Detector initialized in OFFLINE mode\n")
    
    test_cases = [
        # Subtle AI-generated content (harder to detect)
        {
            "name": "Subtle AI text - well-integrated patterns",
            "text": """Research indicates that AI has revolutionized technology. 
            Several studies demonstrate consistent results. Importantly, the implications are significant.
            Therefore, further investigation is warranted. In essence, these findings contribute meaningfully.""",
            "expected": "ai_generated",
            "difficulty": "hard"
        },
        # Technical human writing (not AI-like)
        {
            "name": "Technical human writing",
            "text": """Fixed the memory leak in the parser. The issue was in line 342 where
            we weren't freeing the buffer correctly. Added a test case that reliably reproduces it.
            Performance improved by about 25% after the fix.""",
            "expected": "human",
            "difficulty": "medium"
        },
        # Formal but human (CEO letter style)
        {
            "name": "Formal business human writing",
            "text": """Dear colleagues, I wanted to share some thoughts on where we're heading.
            Honestly, I'm excited but also a bit nervous. We've got some challenges ahead but
            I think we can pull it off. Let me know your thoughts in the meeting tomorrow.""",
            "expected": "human",
            "difficulty": "medium"
        },
        # Academic-style but AI
        {
            "name": "Academic AI text",
            "text": """The proliferation of digital technologies necessitates a comprehensive examination
            of contemporary paradigms. It is imperative to acknowledge the multifaceted implications
            inherent in such transformations. Furthermore, stakeholders must navigate these complexities
            with judicious consideration of both opportunities and constraints.""",
            "expected": "ai_generated",
            "difficulty": "hard"
        },
        # Very casual human
        {
            "name": "Very casual human text",
            "text": """yo so literally just burned dinner lmao. totally spaced out watching tiktok.
            anyway gonna order pizza i guess. my bad for being useless haha""",
            "expected": "human",
            "difficulty": "easy"
        },
        # Moderately formal AI
        {
            "name": "Moderately formal AI response",
            "text": """It's worth noting that technology continues to advance rapidly.
            The landscape has shifted considerably, and it's essential to remain adaptable.
            In conclusion, successful organizations must embrace innovation and foster
            a culture of continuous learning to remain competitive.""",
            "expected": "ai_generated",
            "difficulty": "medium"
        },
        # Human with some formal elements
        {
            "name": "Human mixing casual and formal",
            "text": """So I was reading about machine learning and honestly it's pretty cool.
            The algorithms are fascinating but I don't fully understand all the math.
            Anyway, I think it'll be huge in like 10 years. Probably change everything.""",
            "expected": "human",
            "difficulty": "hard"
        },
        # Stream of consciousness human
        {
            "name": "Stream of consciousness human",
            "text": """Coffee was cold this morning which sucked. Then the commute took forever 
            because of traffic. Why does everyone drive so slow? Got to work late and my boss 
            gave me that look. Whatever. Friday can't come soon enough honestly.""",
            "expected": "human",
            "difficulty": "easy"
        },
        # Carefully crafted AI to avoid patterns
        {
            "name": "AI text optimized to avoid patterns",
            "text": """Technology has changed our world significantly. Many people adapt to new systems quickly.
            The results show improvement over time. Changes bring both advantages and disadvantages.
            Organizations respond to these shifts in various ways. Success requires flexibility and innovation.""",
            "expected": "ai_generated",
            "difficulty": "hard"
        },
    ]
    
    results_by_difficulty = {"easy": [], "medium": [], "hard": []}
    total_correct = 0
    total_tests = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}: {test_case['name']} [{test_case['difficulty'].upper()}]")
        print(f"{'='*70}")
        
        text = test_case['text']
        expected = test_case['expected']
        difficulty = test_case['difficulty']
        
        print(f"Text preview: {text[:80]}...")
        
        result = detector.predict(text)
        
        prediction = result['prediction']
        confidence = result['confidence']
        ai_score = result['scores']['ai_generated']
        patterns = result['detected_patterns']['total_count']
        
        print(f"\nResults:")
        print(f"  Prediction: {prediction}")
        print(f"  Confidence: {confidence:.1f}%")
        print(f"  AI Score: {ai_score:.1f}%")
        print(f"  Patterns: {patterns}")
        
        is_correct = prediction == expected
        status = "[OK] CORRECT" if is_correct else "[FAIL] INCORRECT"
        print(f"\nExpected: {expected}")
        print(f"Status: {status}")
        
        if is_correct:
            total_correct += 1
        total_tests += 1
        
        results_by_difficulty[difficulty].append({
            "test": test_case['name'],
            "correct": is_correct,
            "confidence": confidence
        })
    
    # Summary by difficulty
    print(f"\n\n{'='*70}")
    print("SUMMARY BY DIFFICULTY")
    print(f"{'='*70}")
    
    for difficulty in ["easy", "medium", "hard"]:
        tests = results_by_difficulty[difficulty]
        if not tests:
            continue
        correct = sum(1 for t in tests if t['correct'])
        accuracy = (correct / len(tests)) * 100 if tests else 0
        print(f"\n{difficulty.upper()}: {correct}/{len(tests)} ({accuracy:.1f}%)")
        for test in tests:
            status = "[OK]" if test['correct'] else "[FAIL]"
            print(f"  {status} {test['test']}")
    
    # Overall summary
    print(f"\n\n{'='*70}")
    print("OVERALL RESULTS")
    print(f"{'='*70}")
    
    overall_accuracy = (total_correct / total_tests) * 100 if total_tests else 0
    print(f"\nTotal Accuracy: {total_correct}/{total_tests} ({overall_accuracy:.1f}%)")
    
    if overall_accuracy >= 80:
        print("[OK] EXCELLENT - Detector is working well!")
    elif overall_accuracy >= 70:
        print("[OK] GOOD - Detector is reasonably accurate")
    else:
        print("[WARN] NEEDS WORK - Detector needs improvement")
    
    print(f"\n{'='*70}\n")


if __name__ == "__main__":
    test_extended()
