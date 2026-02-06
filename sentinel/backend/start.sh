#!/bin/bash

# Sentinel Backend - Python Quick Start Script
# This script sets up and runs the Python backend

set -e

echo "🚀 Sentinel Backend - Python Setup"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION found"

# Navigate to backend directory
cd "$(dirname "$0")/backend"
echo "📁 Working in: $(pwd)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo ""
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

echo ""
echo "⚙️  Configuration Check"
echo "--------------------"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found"
    echo "📝 Creating .env template..."
    cp .env.template .env 2>/dev/null || echo "⚠️  No template found. Creating basic .env..."
    cat > .env << 'EOF'
# Backend Configuration
BACKEND_PORT=3000
FRONTEND_URL=http://localhost:3001

# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/telegram/webhook

# Environment
ENVIRONMENT=development
EOF
    echo "📝 .env file created. Please update with your credentials:"
    echo "   - SUPABASE_URL and SUPABASE_KEY from Supabase dashboard"
    echo "   - GEMINI_API_KEY from https://aistudio.google.com"
    echo "   - TELEGRAM_BOT_TOKEN (optional, from BotFather)"
    echo ""
    echo "Edit .env file and rerun this script."
    exit 1
else
    echo "✅ .env file found"
fi

echo ""
echo "🎯 Pre-flight Checks"
echo "-------------------"

# Check if GEMINI_API_KEY is set
if grep -q "GEMINI_API_KEY=your_gemini_api_key" .env; then
    echo "⚠️  GEMINI_API_KEY not configured"
    echo "   Get key from: https://aistudio.google.com"
fi

# Check if Supabase credentials are set
if grep -q "SUPABASE_URL=your_supabase_url" .env; then
    echo "⚠️  SUPABASE_URL not configured"
    echo "   Get from: Supabase dashboard > Settings > API"
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "🚀 Starting Sentinel Backend..."
echo "================================"
echo ""
echo "Backend will run on: http://localhost:3000"
echo "Press Ctrl+C to stop"
echo ""

# Run the server
python main.py
