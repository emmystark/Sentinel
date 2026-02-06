#!/usr/bin/env python3
"""
Diagnostic script to test the complete receipt scanning pipeline
Simulates exact frontend API call to debug JSON parsing issues
"""

import requests
import base64
import json
from PIL import Image
import io

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"
USER_ID = "test-user-diagnostic"

print("=" * 60)
print("Sentinel Receipt Scanning Diagnostic")
print("=" * 60)
print()

# Test 1: Create a real test image
print("Test 1: Creating test image...")
try:
    img = Image.new('RGB', (100, 100), color='white')
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    print(f"✓ Image created: {len(img_base64)} bytes base64")
except Exception as e:
    print(f"✗ Image creation failed: {e}")
    exit(1)

# Test 2: Simulate frontend request (with proper JSON stringification)
print("\nTest 2: Sending receipt with proper JSON...")
payload = {
    "image_base64": img_base64
}
print(f"Payload type: {type(payload)}")
print(f"Payload image_base64 type: {type(payload['image_base64'])}")

try:
    response = requests.post(
        f"{BACKEND_URL}/api/ai/analyze-receipt",
        json=payload,  # Using json parameter ensures proper serialization
        headers={"user-id": USER_ID},
        timeout=30
    )
    data = response.json()
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    # Check if parsing succeeded
    if data.get("merchant") == "Unknown Merchant" and data.get("amount") == 0:
        print("\n❌ Receipt parsing failed - returned default values")
        print("This indicates Qwen API call failed")
    else:
        print("\n✓ Receipt parsing succeeded!")
        print(f"   Merchant: {data['merchant']}")
        print(f"   Amount: {data['amount']}")
        print(f"   Category: {data['category']}")
except requests.exceptions.Timeout:
    print("⏱️  Request timeout (Qwen model may be loading)")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Check backend logs for details
print("\nTest 3: Checking backend logs...")
import subprocess
result = subprocess.run(
    "tail -50 /tmp/backend.log | grep -i 'qwen\\|error\\|json\\|parsing' | tail -20",
    shell=True,
    capture_output=True,
    text=True
)
if result.stdout:
    print("Recent log entries:")
    print(result.stdout)
else:
    print("No relevant log entries found")

print("\n" + "=" * 60)
print("Diagnostic complete. Check logs above for details.")
print("=" * 60)
