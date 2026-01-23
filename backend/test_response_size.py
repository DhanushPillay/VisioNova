"""
Check response size and structure
"""
import json
import sys
from app import app

client = app.test_client()

# Medium length text
text = """Furthermore, it is important to note that learning programming requires dedication and consistent practice. Additionally, one should leverage available resources such as online tutorials and documentation. In conclusion, the journey of learning to code is both challenging and rewarding. Moreover, it is crucial to maintain patience throughout the process."""

print("="*70)
print("RESPONSE SIZE ANALYSIS")
print("="*70)

# Make request
response = client.post('/api/detect-ai', 
                      data=json.dumps({"text": text}),
                      content_type='application/json')

data = response.get_json()
response_str = json.dumps(data, indent=2)
response_bytes = len(response_str.encode('utf-8'))

print(f"\nResponse size: {response_bytes} bytes ({response_bytes/1024:.2f} KB)")
print(f"\nTop-level keys: {list(data.keys())}")

# Analyze each section
print("\n" + "="*70)
print("BREAKDOWN BY SECTION:")
print("="*70)

for key in data.keys():
    if key != "success":
        section_str = json.dumps(data[key], indent=2)
        section_bytes = len(section_str.encode('utf-8'))
        print(f"{key:25} : {section_bytes:6} bytes ({section_bytes/1024:.3f} KB)")

# Check if detailed is enabled
if 'sentence_analysis' in data:
    print(f"\nsentence_analysis items: {len(data['sentence_analysis'])}")
    if data['sentence_analysis']:
        first_item_str = json.dumps(data['sentence_analysis'][0], indent=2)
        print(f"First item size: {len(first_item_str.encode('utf-8'))} bytes")
