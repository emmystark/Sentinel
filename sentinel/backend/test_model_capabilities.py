#!/usr/bin/env python3
"""
Test if Qwen on HuggingFace actually supports vision
"""

import os
import json
import httpx

HF_TOKEN = os.getenv('HF_TOKEN', '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')
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct:together"
API_URL = "https://router.huggingface.co/v1/chat/completions"

print("Test: Text-only request (no images)")
print("="*60)

payload = {
    "model": MODEL_ID,
    "temperature": 0,
    "max_tokens": 100,
    "messages": [
        {
            "role": "user",
            "content": "Reply with only this JSON: {\"test\": 123}"
        }
    ]
}

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

response = httpx.post(API_URL, json=payload, headers=headers, timeout=30)
print(f"Status: {response.status_code}")
data = response.json()
print(f"Content: {data['choices'][0]['message']['content']}")

# Now try to request info about vision capabilities
print("\n\nTest: Ask Qwen about vision support")
print("="*60)

payload2 = {
    "model": MODEL_ID,
    "temperature": 0,
    "max_tokens": 200,
    "messages": [
        {
            "role": "user",
            "content": "Do you support image/vision capabilities? Reply with only YES or NO."
        }
    ]
}

response2 = httpx.post(API_URL, json=payload2, headers=headers, timeout=30)
print(f"Status: {response2.status_code}")
data2 = response2.json()
print(f"Content: {data2['choices'][0]['message']['content']}")
