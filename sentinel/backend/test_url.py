#!/usr/bin/env python3
"""
Test receipt scanning with URL instead of base64
"""

import sys
sys.path.insert(0, '/Volumes/Stark/AI/sentinel/backend')

from services.qwen_service import parse_receipt_with_qwen
import asyncio
import logging

# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

async def test():
    # Use a public image URL
    image_url = "https://via.placeholder.com/400x300?text=Coffee+5.99"
    
    print(f"Testing with URL: {image_url}")
    
    # Pass to Qwen service
    result = await parse_receipt_with_qwen(image_url)
    print(f"Result: {result}")

asyncio.run(test())
