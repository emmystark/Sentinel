#!/bin/bash
# Sentinel Quick Start Script
# This script helps you set up and run the Sentinel application

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🚀 Sentinel Backend - Quick Start Setup 🚀         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: Please run this script from the backend directory${NC}"
    exit 1
fi

# 1. Check Python
echo -e "${YELLOW}1️⃣  Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $(python3 --version | cut -d' ' -f2) found${NC}\n"

# 2. Create virtual environment
echo -e "${YELLOW}2️⃣  Setting up virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate venv
source venv/bin/activate

echo -e "${GREEN}✅ Virtual environment activated${NC}\n"

# 3. Install dependencies
echo -e "${YELLOW}3️⃣  Installing Python dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies installed${NC}\n"

# 4. Check .env file
echo -e "${YELLOW}4️⃣  Checking configuration...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Created .env from template. Please update with your values:${NC}"
        echo "   SUPABASE_URL, SUPABASE_KEY, TELEGRAM_BOT_TOKEN, GEMINI_API_KEY, HF_TOKEN"
        echo ""
    else
        echo -e "${RED}❌ .env file not found. Create it with your API keys${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✅ Configuration file ready${NC}\n"

# 5. Run setup validator
echo -e "${YELLOW}5️⃣  Validating setup...${NC}"
python setup_validator.py || {
    echo -e "${RED}⚠️  Setup validation had issues. Review the output above.${NC}"
    echo "   You may need to:"
    echo "   - Update .env with correct API keys"
    echo "   - Run database migration: python database/migrate.py"
    echo "   - Check your internet connection"
}

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           ✅ Setup Complete! Ready to run.                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "1️⃣  Run database migration (if needed):"
echo -e "   ${GREEN}python database/migrate.py${NC}"
echo ""
echo "2️⃣  Start the backend server:"
echo -e "   ${GREEN}uvicorn app:app --reload --host 0.0.0.0 --port 8000${NC}"
echo ""
echo "3️⃣  In another terminal, start the frontend:"
echo -e "   ${GREEN}cd ../frontend && npm run dev${NC}"
echo ""
echo "4️⃣  Open your browser to:"
echo -e "   ${GREEN}http://localhost:3001${NC}"
echo ""

# Offer to run the backend
echo -e "${YELLOW}Would you like to start the backend now? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Starting backend...${NC}"
    uvicorn app:app --reload --host 0.0.0.0 --port 8000
else
    echo -e "${GREEN}Backend ready! Run 'uvicorn app:app --reload' to start${NC}"
fi
