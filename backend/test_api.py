"""
Test the Flask API directly
"""
import json
from app import app

# Create test client
client = app.test_client()

# Test data
test_cases = [
    {
        "name": "Human text",
        "text": "hey whats up? yeah i totally get what you mean lol. like when i was trying to learn python last year"
    },
    {
        "name": "AI text",
        "text": "Furthermore, it is important to note that learning programming requires dedication. Additionally, one should leverage available resources."
    }
]

print("="*70)
print("TESTING FLASK API - /api/detect-ai")
print("="*70)

for test in test_cases:
    print(f"\nTest: {test['name']}")
    print(f"Text length: {len(test['text'])} chars")
    
    # Make request
    import time
    start = time.time()
    response = client.post('/api/detect-ai', 
                          data=json.dumps({"text": test['text']}),
                          content_type='application/json')
    elapsed = time.time() - start
    
    print(f"Response time: {elapsed:.3f}s")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"Success: {data.get('success')}")
        print(f"Prediction: {data.get('prediction')}")
        print(f"Confidence: {data.get('confidence')}%")
    else:
        print(f"Error: {response.get_data(as_text=True)[:200]}")

print("\n" + "="*70)
print("API test complete")
print("="*70)
