#!/usr/bin/env python3
"""
Test receipt scanning through REST API
"""

import requests
import base64
from PIL import Image, ImageDraw
import io

# Create test receipt image
img = Image.new('RGB', (400, 300), color='white')
draw = ImageDraw.Draw(img)

text_lines = [
    "STARBUCKS COFFEE",
    "123 Main St, City",
    "",
    "2025-02-06 10:30 AM",
    "",
    "Espresso Shot      $2.50",
    "Caramel Macch     $5.99",
    "Pastry             $4.50",
    "",
    "Subtotal          $12.99",
    "Tax                $1.04",
    "Total             $14.03",
]

y_position = 20
for line in text_lines:
    draw.text((20, y_position), line, fill='black')
    y_position += 15

buffered = io.BytesIO()
img.save(buffered, format="JPEG")
img_base64 = base64.b64encode(buffered.getvalue()).decode()

print("Testing Receipt Scanning API")
print("=" * 60)

# Make API request
payload = {"image_base64": img_base64}
headers = {"user-id": "test-user"}

response = requests.post(
    "http://127.0.0.1:8000/api/ai/analyze-receipt",
    json=payload,
    headers=headers,
    timeout=60
)

print(f"Status: {response.status_code}")
data = response.json()

print(f"\nExtracted Data:")
print(f"  Merchant: {data.get('merchant')}")
print(f"  Amount: ${data.get('amount')}")
print(f"  Currency: {data.get('currency')}")
print(f"  Category: {data.get('category')}")
print(f"  Items: {data.get('items')}")
print(f"  Date: {data.get('date')}")
print(f"  Description: {data.get('description')}")

if data.get('merchant') != 'Unknown Merchant':
    print("\n✓ SUCCESS: Receipt extraction working!")
else:
    print("\n❌ FAILED: No data extracted")
