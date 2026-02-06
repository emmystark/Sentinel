#!/usr/bin/env python3
"""
Test receipt scanning with a realistic receipt image
"""

import sys
sys.path.insert(0, '/Volumes/Stark/AI/sentinel/backend')

from services.qwen_service import parse_receipt_with_qwen
import asyncio
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

async def test():
    # Create a test image that looks like a receipt
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add some receipt-like text
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
        "",
        "Thank you!"
    ]
    
    y_position = 20
    for line in text_lines:
        draw.text((20, y_position), line, fill='black')
        y_position += 15
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    print(f"Receipt image created: {len(img_base64)} bytes base64")
    
    # Pass to Qwen service
    result = await parse_receipt_with_qwen(img_base64)
    print(f"\nExtracted Data:")
    print(f"  Merchant: {result.get('merchant')}")
    print(f"  Amount: ${result.get('amount')}")
    print(f"  Currency: {result.get('currency')}")
    print(f"  Category: {result.get('category')}")
    print(f"  Items: {result.get('items')}")
    print(f"  Date: {result.get('date')}")

asyncio.run(test())
