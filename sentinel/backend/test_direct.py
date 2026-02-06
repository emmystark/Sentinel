#!/usr/bin/env python3
"""
Test receipt scanning with direct file logging
"""

import sys
import os
sys.path.insert(0, '/Volumes/Stark/AI/sentinel/backend')

from services.qwen_service import parse_receipt_with_qwen
import asyncio
import base64
from PIL import Image
import io
import logging

# Set up logging to file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/qwen_test.log'),
        logging.StreamHandler()
    ]
)

async def test():
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='white')
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    print(f"Image base64 length: {len(img_base64)}")
    print(f"Image base64 type: {type(img_base64)}")
    
    # Pass to Qwen service
    result = await parse_receipt_with_qwen(img_base64)
    print(f"Result: {result}")

asyncio.run(test())
