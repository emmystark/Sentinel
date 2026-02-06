# Sentinel Backend - Python Migration Guide

This is the Python/FastAPI version of the Sentinel backend, replacing the original Express.js implementation. It includes full Gemini 1.5 Flash integration for AI-powered expense analysis and budget monitoring.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip or conda
- Supabase account
- Google Gemini API key
- Telegram Bot Token (optional, for Telegram integration)

### Installation

1. **Navigate to the backend-py directory:**
```bash
cd finetuned-chatbot/backend-py
```

2. **Create a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env .env.local
```

Edit `.env.local` and add your credentials:
- `SUPABASE_URL` - From Supabase dashboard
- `SUPABASE_KEY` - From Supabase dashboard
- `GEMINI_API_KEY` - From Google AI Studio (https://aistudio.google.com)
- `TELEGRAM_BOT_TOKEN` - From BotFather on Telegram (optional)
- `FRONTEND_URL` - Your frontend URL

5. **Run the server:**
```bash
python main.py
```

Server will start on http://localhost:3000 (or custom `BACKEND_PORT`)

## 🏗️ Project Structure

```
backend-py/
├── main.py                 # FastAPI app initialization
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
├── routes/
│   ├── __init__.py
│   ├── auth.py            # Authentication endpoints
│   ├── transactions.py    # Transaction CRUD endpoints
│   ├── ai.py             # AI/Gemini integration endpoints
│   └── telegram.py       # Telegram bot endpoints
├── services/
│   ├── __init__.py
│   ├── gemini_service.py # Gemini API integration
│   └── telegram_service.py # Telegram bot service
└── models/
    └── (database models if needed)
```

## 📚 API Endpoints

### Authentication (`/api/auth`)
- `POST /signup` - Register new user
- `POST /login` - Login user
- `POST /logout` - Logout user
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile

### Transactions (`/api/transactions`)
- `GET /` - List user transactions (with pagination)
- `GET /{id}` - Get single transaction
- `POST /` - Create transaction
- `PUT /{id}` - Update transaction
- `DELETE /{id}` - Delete transaction
- `GET /stats/summary` - Get spending statistics

### AI Analysis (`/api/ai`)
- `POST /analyze-receipt` - Analyze receipt image (URL or base64)
- `POST /analyze-receipt-upload` - Upload and analyze receipt
- `POST /categorize` - Categorize transaction with AI
- `POST /analyze-spending` - Full spending pattern analysis
- `POST /get-advice` - Get personalized spending advice
- `POST /budget-alert` - Check budget alert status

### Telegram (`/api/telegram`)
- `GET /verify` - Check Telegram connection status
- `POST /connect` - Connect Telegram account
- `POST /disconnect` - Disconnect Telegram account
- `POST /send-alert` - Send budget alert via Telegram
- `POST /send-advice` - Send spending advice via Telegram
- `POST /webhook` - Handle Telegram webhook messages
- `POST /init-bot` - Initialize Telegram bot

## 🤖 Gemini 1.5 Flash Integration

The AI features use Google's **Gemini 1.5 Flash** model for:

### 1. **Receipt Parsing**
Automatically extracts from receipt images:
- Merchant name
- Transaction amount
- Date of purchase
- Items purchased
- Automatic categorization

```python
# Example usage
extracted_data = await parse_receipt(image_base64_or_url)
# Returns: {merchant, amount, currency, date, items, category, description}
```

### 2. **Transaction Categorization**
Smart categorization into:
- Food, Transport, Entertainment
- Shopping, Bills, Utilities
- Health, Education, Other

### 3. **Spending Analysis**
Comprehensive analysis including:
- Spending pattern insights
- Category breakdowns
- Overspending areas
- Cost reduction opportunities
- Monthly savings potential

### 4. **Personalized Advice**
Context-aware recommendations:
- Financial situation assessment
- Positive habit identification
- Key focus areas
- Practical, actionable tips
- Motivation toward goals

### 5. **Budget Alerts** (Financial Smoke Detector)
Real-time monitoring:
- Budget usage percentage tracking
- Alert levels: low, medium, high, critical
- Category-level spending alerts
- Proactive warnings before overspending

## 💰 Key Features

### Financial Smoke Detector
Monitors spending velocity in real-time:
- Tracks daily/weekly spending patterns
- Identifies unusual spending spikes
- Proactive alerts before budget breakage
- Specific recommendations for this spending pattern

### AI-Powered Insights
- **Receipt Scanning**: Upload images and auto-extract transactions
- **Smart Categorization**: AI-powered expense categorization
- **Spending Analysis**: Pattern recognition and trend analysis
- **Cost Reduction**: Personalized recommendations based on actual habits
- **Budget Monitoring**: Real-time budget alerts and warnings

### Telegram Integration
- Real-time notifications via Telegram
- Budget alerts
- Spending advice delivery
- Interactive bot commands

## 🔧 Configuration

### Supabase Database Schema

Required tables:
```sql
-- user_profiles
- id (UUID)
- email (string)
- name (string)
- monthly_income (numeric)
- fixed_bills (numeric)
- savings_goal (numeric)
- telegram_connected (boolean)
- telegram_username (string)
- telegram_user_id (string)

-- transactions
- id (UUID)
- user_id (UUID, FK)
- merchant (string)
- amount (numeric)
- category (string)
- description (string)
- date (timestamp)
- created_at (timestamp)
```

### Gemini API Key
1. Go to https://aistudio.google.com
2. Click "Get API key"
3. Create new API key
4. Add to `.env` file as `GEMINI_API_KEY`

### Telegram Bot Setup
1. Open Telegram and chat with @BotFather
2. Use `/newbot` command
3. Get your bot token
4. Add to `.env` as `TELEGRAM_BOT_TOKEN`

## 🚀 Migration from Express.js

Key differences from the original Express backend:

| Feature | Express | Python |
|---------|---------|--------|
| Framework | Express.js | FastAPI |
| AI Model | HuggingFace | Gemini 1.5 Flash |
| Image Processing | HF Models | Gemini Vision |
| Async | Callbacks | Native async/await |
| Type Safety | Runtime | Pydantic models |

All endpoint paths remain the same for frontend compatibility.

## 📋 Frontend Integration

Update your frontend `.env` to point to Python backend:

```env
NEXT_PUBLIC_API_URL=http://localhost:3000
```

All API endpoints work identically:
```javascript
// Works the same with Python backend
const response = await fetch('http://localhost:3000/api/transactions', {
  headers: {
    'user-id': userId
  }
})
```

## 🔐 Security Notes

- Always use HTTPS in production
- Store sensitive keys in environment variables
- Use Supabase row-level security policies
- Validate input on both frontend and backend
- Rate limit API endpoints

## 🐛 Troubleshooting

### "GEMINI_API_KEY not configured"
- Add `GEMINI_API_KEY` to `.env` file
- Restart the server

### "Supabase credentials not configured"
- Ensure `SUPABASE_URL` and `SUPABASE_KEY` are set
- Check credentials are correct from Supabase dashboard

### Receipt parsing not working
- Ensure image is clear and readable
- Try different image formats (JPEG, PNG)
- Check Gemini API quota

### Telegram not sending messages
- Verify `TELEGRAM_BOT_TOKEN` is correct
- Check bot is not banned
- Ensure webhook URL is accessible (if using webhooks)

## 📝 Development

### Run in development mode:
```bash
# With auto-reload
pip install uvicorn[standard]
uvicorn main:app --reload
```

### Testing endpoints:
```bash
# Health check
curl http://localhost:3000/api/health

# Analyze receipt (with base64)
curl -X POST http://localhost:3000/api/ai/analyze-receipt \
  -H "Content-Type: application/json" \
  -H "user-id: user-123" \
  -d '{"image_base64": "..."}'
```

## 📦 Deployment

### Docker
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000"]
```

### Environment Variables (Production)
- Use secure secret management (AWS Secrets, HashiCorp Vault, etc.)
- Never commit `.env` files
- Use different keys for staging/production

## 🤝 Contributing

When adding new AI features:
1. Add to appropriate service (`gemini_service.py`)
2. Create new endpoint in relevant route file
3. Update this README with documentation
4. Test thoroughly before committing

## 📄 License

Same as parent project

## 🆘 Support

For issues:
1. Check the troubleshooting section
2. Review Gemini API documentation
3. Check Supabase status
4. Review logs in terminal

---

**Note**: This backend is fully compatible with the existing Next.js frontend. Simply update the API base URL to use the Python backend.
