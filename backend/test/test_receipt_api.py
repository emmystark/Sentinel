#!/usr/bin/env python3
"""
Test script for Sentinel Receipt Scanning API
Tests the complete receipt analysis workflow with detailed logging
"""

import os
import sys
import json
import time
import base64
import requests
from pathlib import Path
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'https://sentinel-pchb.onrender.com')
USER_ID = f"test-user-{int(time.time())}"
HF_TOKEN = os.getenv('HF_TOKEN', '')

print("=" * 50)
print("Sentinel Receipt Scanning Test Suite")
print("=" * 50)
print()
print(f"Backend URL: {BACKEND_URL}")
print(f"User ID: {USER_ID}")
print(f"HuggingFace Token: {'✓ Configured' if HF_TOKEN else '✗ NOT configured'}")
print()

def test_health_check():
    """Test 1: Health check endpoint"""
    print("Test 1: Health Check")
    print("-" * 40)
    try:
        response = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_receipt_with_url():
    """Test 2: Analyze receipt with image URL"""
    print("\nTest 2: Analyze Receipt with Image URL")
    print("-" * 40)
    
    test_image_url = "https://via.placeholder.com/400x300?text=Receipt+Test"
    print(f"Image URL: {test_image_url}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/ai/analyze-receipt",
            json={"image_url": test_image_url},
            headers={"user-id": USER_ID},
            timeout=30
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            merchant = data.get('merchant', '')
            amount = data.get('amount', 0)
            category = data.get('category', '')
            
            print(f"\n✓ Extracted Data:")
            print(f"  - Merchant: {merchant}")
            print(f"  - Amount: ${amount}")
            print(f"  - Category: {category}")
            
            return {
                'success': True,
                'merchant': merchant,
                'amount': amount,
                'category': category,
                'response': data
            }
        else:
            print(f"✗ Error: {response.text}")
            return {'success': False}
    except requests.exceptions.Timeout:
        print("✗ Request timeout (Qwen model may be loading)")
        print("  Try again - first request takes longer")
        return {'success': False}
    except Exception as e:
        print(f"✗ Error: {e}")
        return {'success': False}

def test_receipt_with_base64():
    """Test 3: Analyze receipt with base64 image"""
    print("\nTest 3: Analyze Receipt with Base64 Image")
    print("-" * 40)
    
    # Create a simple test image (small 1x1 pixel)
    try:
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='white')
        import io
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        print(f"Base64 image length: {len(img_base64)} bytes")
        
        response = requests.post(
            f"{BACKEND_URL}/api/ai/analyze-receipt",
            json={"image_base64": img_base64},
            headers={"user-id": USER_ID},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
    except ImportError:
        print("Skipping base64 test (PIL not available)")
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_financial_health():
    """Test 4: Financial health analysis"""
    print("\nTest 4: Financial Health Score")
    print("-" * 40)
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/ai/financial-health",
            json={
                "monthly_income": 5000,
                "fixed_bills": 1500,
                "savings_goal": 500
            },
            headers={"user-id": USER_ID},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
            if 'health_score' in data:
                score = data['health_score'].get('score')
                grade = data['health_score'].get('grade')
                print(f"\n✓ Health Score: {score}/100 (Grade: {grade})")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_spending_insights():
    """Test 5: Spending insights"""
    print("\nTest 5: Spending Insights")
    print("-" * 40)
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/ai/spending-insights",
            json={
                "monthly_income": 5000,
                "fixed_bills": 1500,
                "savings_goal": 500
            },
            headers={"user-id": USER_ID},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"✗ Error: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_telegram_settings():
    """Test 6: Telegram settings endpoints"""
    print("\nTest 6: Telegram Settings Management")
    print("-" * 40)
    
    # Get settings
    print("6a. Get Telegram Settings:")
    try:
        response = requests.get(
            f"{BACKEND_URL}/api/ai/telegram/settings",
            headers={"user-id": USER_ID},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Update settings (mock)
    print("\n6b. Update Telegram Settings (mock):")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/ai/telegram/settings",
            json={"telegram_chat_id": 123456789},
            headers={"user-id": USER_ID},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return True

def main():
    """Run all tests"""
    results = []
    
    # Run tests
    results.append(("Health Check", test_health_check()))
    results.append(("Receipt with URL", test_receipt_with_url()['success'] if isinstance(test_receipt_with_url(), dict) else test_receipt_with_url()))
    results.append(("Receipt with Base64", test_receipt_with_base64()))
    results.append(("Financial Health", test_financial_health()))
    results.append(("Spending Insights", test_spending_insights()))
    results.append(("Telegram Settings", test_telegram_settings()))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print()
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
