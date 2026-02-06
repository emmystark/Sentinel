#!/bin/bash

# Sentinel Backend - API Testing Guide
# ====================================
# Run these curl commands to test all API endpoints
# Make sure the backend is running on http://localhost:3000

set -e

BASE_URL="http://localhost:3000"
USER_ID=""  # Will be set after signup

echo "🧪 Sentinel Backend API Testing"
echo "================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

function test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local user_header=$5
    
    echo -e "${YELLOW}Testing: $name${NC}"
    echo "Method: $method"
    echo "Endpoint: $endpoint"
    
    if [ -n "$data" ]; then
        echo "Data: $data"
        response=$(curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "user-id: $user_header" \
            -d "$data")
    else
        response=$(curl -s -X "$method" "$BASE_URL$endpoint" \
            -H "user-id: $user_header")
    fi
    
    echo "Response:"
    echo "$response" | jq . 2>/dev/null || echo "$response"
    echo ""
    echo "---"
    echo ""
}

# Test 1: Health Check
echo -e "${GREEN}1. HEALTH CHECK${NC}"
echo ""
curl -s "$BASE_URL/api/health" | jq .
echo ""
echo "---"
echo ""

# Test 2: Auth - Signup
echo -e "${GREEN}2. AUTHENTICATION - SIGNUP${NC}"
echo ""
test_endpoint \
    "Signup" \
    "POST" \
    "/api/auth/signup" \
    '{
        "email": "testuser@example.com",
        "password": "password123",
        "name": "Test User"
    }' \
    ""

# Extract user ID from signup response (for testing)
# You'll need to manually set this based on the signup response
echo "📝 Please note the user ID from signup response above"
echo "   You'll need it for subsequent requests"
echo ""
echo "   Example: USER_ID='550e8400-e29b-41d4-a716-446655440000'"
echo ""
echo "---"
echo ""

# Test 3: Auth - Login
echo -e "${GREEN}3. AUTHENTICATION - LOGIN${NC}"
echo ""
test_endpoint \
    "Login" \
    "POST" \
    "/api/auth/login" \
    '{
        "email": "testuser@example.com",
        "password": "password123"
    }' \
    ""

echo ""
echo "===== IMPORTANT ====="
echo "From this point forward, replace USER_ID with the actual ID from signup"
echo "Or set it: export USER_ID='your-id-here'"
echo "===================="
echo ""

# Create test transaction (requires USER_ID)
if [ -z "$USER_ID" ]; then
    echo "⚠️  USER_ID not set. Skipping tests that require user_id header"
    echo ""
    echo "To run remaining tests:"
    echo "1. Set USER_ID from signup response: export USER_ID='your-id'"
    echo "2. Run this script again"
    exit 0
fi

# Test 4: Transactions - Create
echo -e "${GREEN}4. TRANSACTIONS - CREATE${NC}"
echo ""
test_endpoint \
    "Create Transaction" \
    "POST" \
    "/api/transactions" \
    '{
        "merchant": "Starbucks",
        "amount": 5.50,
        "category": "Food",
        "description": "Coffee"
    }' \
    "$USER_ID"

# Test 5: Transactions - List
echo -e "${GREEN}5. TRANSACTIONS - LIST${NC}"
echo ""
test_endpoint \
    "List Transactions" \
    "GET" \
    "/api/transactions" \
    "" \
    "$USER_ID"

# Test 6: AI - Categorize
echo -e "${GREEN}6. AI - CATEGORIZE TRANSACTION${NC}"
echo ""
test_endpoint \
    "Categorize Transaction" \
    "POST" \
    "/api/ai/categorize" \
    '{
        "merchant": "Whole Foods Market",
        "amount": 50.00,
        "description": "Weekly groceries"
    }' \
    "$USER_ID"

# Test 7: AI - Analyze Receipt (with sample image URL)
echo -e "${GREEN}7. AI - ANALYZE RECEIPT${NC}"
echo ""
test_endpoint \
    "Analyze Receipt" \
    "POST" \
    "/api/ai/analyze-receipt" \
    '{
        "image_url": "https://via.placeholder.com/400x300?text=Receipt"
    }' \
    "$USER_ID"

# Test 8: AI - Analyze Spending
echo -e "${GREEN}8. AI - ANALYZE SPENDING PATTERNS${NC}"
echo ""
test_endpoint \
    "Analyze Spending" \
    "POST" \
    "/api/ai/analyze-spending" \
    '{
        "monthly_income": 3000,
        "fixed_bills": 800,
        "savings_goal": 500
    }' \
    "$USER_ID"

# Test 9: AI - Get Advice
echo -e "${GREEN}9. AI - GET PERSONALIZED ADVICE${NC}"
echo ""
test_endpoint \
    "Get Advice" \
    "POST" \
    "/api/ai/get-advice" \
    '' \
    "$USER_ID"

# Test 10: AI - Budget Alert
echo -e "${GREEN}10. AI - CHECK BUDGET ALERT${NC}"
echo ""
test_endpoint \
    "Budget Alert" \
    "POST" \
    "/api/ai/budget-alert" \
    '' \
    "$USER_ID"

# Test 11: Telegram - Verify
echo -e "${GREEN}11. TELEGRAM - VERIFY CONNECTION${NC}"
echo ""
test_endpoint \
    "Verify Telegram" \
    "GET" \
    "/api/telegram/verify" \
    "" \
    "$USER_ID"

# Test 12: Telegram - Connect
echo -e "${GREEN}12. TELEGRAM - CONNECT ACCOUNT${NC}"
echo ""
test_endpoint \
    "Connect Telegram" \
    "POST" \
    "/api/telegram/connect" \
    '{
        "telegram_username": "testuser",
        "telegram_user_id": "123456789"
    }' \
    "$USER_ID"

# Test 13: Get Profile
echo -e "${GREEN}13. AUTH - GET PROFILE${NC}"
echo ""
test_endpoint \
    "Get Profile" \
    "GET" \
    "/api/auth/profile" \
    "" \
    "$USER_ID"

# Test 14: Update Profile
echo -e "${GREEN}14. AUTH - UPDATE PROFILE${NC}"
echo ""
test_endpoint \
    "Update Profile" \
    "PUT" \
    "/api/auth/profile" \
    '{
        "monthly_income": 3500,
        "savings_goal": 600
    }' \
    "$USER_ID"

# Test 15: Transaction Stats
echo -e "${GREEN}15. TRANSACTIONS - GET STATS${NC}"
echo ""
test_endpoint \
    "Get Stats" \
    "GET" \
    "/api/transactions/stats/summary" \
    "" \
    "$USER_ID"

echo ""
echo "========================================="
echo "✅ Testing Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✓ Health Check"
echo "  ✓ Authentication (signup, login)"
echo "  ✓ Transactions (CRUD, stats)"
echo "  ✓ AI Analysis (categorize, analyze receipt, spending patterns)"
echo "  ✓ Personalized Advice"
echo "  ✓ Budget Alerts (Financial Smoke Detector)"
echo "  ✓ Telegram Integration"
echo ""
echo "Next Steps:"
echo "  1. Verify all responses are successful"
echo "  2. Check Supabase dashboard for created data"
echo "  3. Test with real images for receipt analysis"
echo "  4. Configure Telegram bot for notifications"
echo ""
