#!/usr/bin/env python3
"""
Direct test of HuggingFace router API bypassing OpenAI client
"""

import os
import json
import httpx
import base64
from PIL import Image
import io

HF_TOKEN = os.getenv('HF_TOKEN', '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')
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct:together"
API_URL = "https://router.huggingface.co/v1/chat/completions"

# Create a test image
img = Image.new('RGB', (100, 100), color='white')
buffered = io.BytesIO()
img.save(buffered, format="JPEG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()

print(f"Image base64 length: {len(img_base64)}")
print(f"First 100 chars: {img_base64[:100]}")

# Test 1: With data URI
payload = {
    "model": MODEL_ID,
    "temperature": 0,
    "max_tokens": 200,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this image briefly in JSON format. Reply with ONLY valid JSON."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64}"
                    }
                }
            ]
        }
    ]
}

print("\n" + "="*60)
print("Test 1: Sending with data URI to HuggingFace Router")
print("="*60)

print(f"Payload image_url type in Python: {type(payload['messages'][0]['content'][1]['image_url']['url'])}")
print(f"Payload image_url value (first 100): {str(payload['messages'][0]['content'][1]['image_url']['url'])[:100]}")

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

try:
    response = httpx.post(API_URL, json=payload, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Without data URI (raw base64)  
payload2 = {
    "model": MODEL_ID,
    "temperature": 0,
    "max_tokens": 200,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this image briefly in JSON format. Reply with ONLY valid JSON."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": img_base64  # Raw base64 without prefix
                    }
                }
            ]
        }
    ]
}

print("\n" + "="*60)
print("Test 2: Sending raw base64 (NO data URI prefix)")
print("="*60)

try:
    response = httpx.post(API_URL, json=payload2, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: With HTTP URL
payload3 = {
    "model": MODEL_ID,
    "temperature": 0,
    "max_tokens": 200,
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Describe this image briefly in JSON format. Reply with ONLY valid JSON."
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://via.placeholder.com/100x100?text=Test"
                    }
                }
            ]
        }
    ]
}

print("\n" + "="*60)
print("Test 3: With HTTP URL")
print("="*60)

try:
    response = httpx.post(API_URL, json=payload3, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")
