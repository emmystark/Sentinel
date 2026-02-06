#!/bin/bash

# Test script for Sentinel Receipt Scanning API
# Tests the complete receipt analysis workflow

echo "=========================================="
echo "Sentinel Receipt Scanning Test Suite"
echo "=========================================="
echo ""

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
USER_ID="${USER_ID:-test-user-$(date +%s)}"
TEST_IMAGE_URL="https://via.placeholder.com/400x300?text=Receipt+Test"

echo "Backend URL: $BACKEND_URL"
echo "User ID: $USER_ID"
echo "Test Image URL: $TEST_IMAGE_URL"
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "-------------------"
curl -s -X GET "$BACKEND_URL/api/health" | jq '.' || echo "Health check failed"
echo ""

# Test 2: Analyze Receipt with URL (with proper error handling)
echo "Test 2: Analyze Receipt with Image URL"
echo "--------------------------------------"
RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/ai/analyze-receipt" \
  -H "Content-Type: application/json" \
  -H "user-id: $USER_ID" \
  -d "{\"image_url\": \"$TEST_IMAGE_URL\"}")

echo "$RESPONSE" | jq '.' || echo "$RESPONSE"
MERCHANT=$(echo "$RESPONSE" | jq -r '.merchant // empty')
AMOUNT=$(echo "$RESPONSE" | jq -r '.amount // 0')
echo "Extracted - Merchant: $MERCHANT, Amount: $AMOUNT"
echo ""

# Test 3: Create Transaction from scanned receipt
echo "Test 3: Create Transaction"
echo "------------------------"
if [ ! -z "$MERCHANT" ] && [ "$AMOUNT" != "0" ]; then
  RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/transactions" \
    -H "Content-Type: application/json" \
    -H "user-id: $USER_ID" \
    -d "{
      \"merchant\": \"$MERCHANT\",
      \"amount\": $AMOUNT,
      \"category\": \"Shopping\",
      \"description\": \"Test receipt scan\"
    }")
  
  echo "$RESPONSE" | jq '.' || echo "$RESPONSE"
  echo ""
fi

# Test 4: Get Financial Health
echo "Test 4: Get Financial Health Score"
echo "---------------------------------"
curl -s -X POST "$BACKEND_URL/api/ai/financial-health" \
  -H "Content-Type: application/json" \
  -H "user-id: $USER_ID" \
  -d "{
    \"monthly_income\": 5000,
    \"fixed_bills\": 1500,
    \"savings_goal\": 500
  }" | jq '.' || echo "Health score request failed"
echo ""

# Test 5: Get Spending Insights
echo "Test 5: Get Spending Insights"
echo "----------------------------"
curl -s -X POST "$BACKEND_URL/api/ai/spending-insights" \
  -H "Content-Type: application/json" \
  -H "user-id: $USER_ID" \
  -d "{
    \"monthly_income\": 5000,
    \"fixed_bills\": 1500,
    \"savings_goal\": 500
  }" | jq '.' || echo "Insights request failed"
echo ""

# Test 6: Test Telegram Settings
echo "Test 6: Get Telegram Settings"
echo "----------------------------"
curl -s -X GET "$BACKEND_URL/api/ai/telegram/settings" \
  -H "user-id: $USER_ID" | jq '.' || echo "Telegram settings request failed"
echo ""

echo "=========================================="
echo "Test Suite Complete"
echo "=========================================="
echo ""
echo "Summary:"
echo "- Backend URL: $BACKEND_URL"
echo "- User ID: $USER_ID"
echo ""
echo "Next steps:"
echo "1. Check logs above for any errors"
echo "2. If receipt parsing failed, ensure HF_TOKEN is set in .env"
echo "3. If Telegram tests failed, that's expected - not yet configured"
echo "4. Run frontend and test UI receipt upload"
