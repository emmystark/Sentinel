# Sentinel Backend - Deployment & Setup Guide

## 🚀 Quick Setup

### 1. **Database Migration** (CRITICAL - Do This First)
The database is missing the `telegram_chat_id` column. You MUST run this migration:

```bash
# Option A: Run migration via Python script
cd backend
python database/migrate.py

# Option B: Run SQL directly in Supabase Console
# Go to Supabase > SQL Editor and run the contents of:
# database/migration_fix_telegram.sql
```

### 2. **Environment Setup**

Create/update `.env` file in backend directory:
```env
# Supabase
SUPABASE_URL=https://acbyuwvskzvxceozkpla.supabase.co
SUPABASE_KEY=your_supabase_service_key

# Telegram Bot
TELEGRAM_BOT_TOKEN=8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU
TELEGRAM_BOT_USERNAME=Sentinel_budget_bot
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/telegram/webhook

# AI APIs
GEMINI_API_KEY=your_gemini_key
HF_TOKEN=your_huggingface_token

# Backend Config
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:3001
ENVIRONMENT=production
```

### 3. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

### 4. **Run Backend**
```bash
# Development with auto-reload
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Production
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app
```

---

## 🔧 Fixing Key Issues

### Issue 1: Missing `telegram_chat_id` Column
**Error**: `column user_profiles.telegram_chat_id does not exist`
**Solution**: Run the migration (see step 1 above)

### Issue 2: Auth Signup Not Working
**Causes**: 
- Profile creation fails after auth
- Database trigger not firing
**Solution**: Updated auth route handles both cases and logs errors

### Issue 3: Telegram Linking
**Your Telegram ID**: `7873003581`

```bash
# Direct link (for testing):
curl -X POST http://localhost:8000/api/telegram/link-direct-admin \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_id": 7873003581,
    "user_id": "YOUR_USER_UUID"
  }'
```

### Issue 4: Chatbot Error
**Problem**: Chat endpoint returning 404
**Solution**: 
- Ensure `/api/ai/chat` endpoint is called correctly
- Check backend is running on correct port
- Verify `GEMINI_API_KEY` and `HF_TOKEN` are set

### Issue 5: Push Notifications
**Setup**:
1. Users can link Telegram account → notifications via Telegram
2. In-app notifications saved to `notifications` table
3. Push notifications ready for Firebase integration

---

## 📱 Telegram Bot Setup

### Step 1: Create Bot
1. Message `@BotFather` on Telegram
2. Create new bot: `/newbot`
3. Copy bot token

### Step 2: Set Webhook
```bash
# Update TELEGRAM_BOT_TOKEN in .env, then:
curl https://api.telegram.org/bot{TOKEN}/setWebhook \
  -F "url=https://your-domain.com/api/telegram/webhook"  \
  -F "allowed_updates=[\"message\", \"callback_query\"]"
```

### Step 3: Verify Bot
```bash
curl http://localhost:8000/api/telegram/verify
```

---

## 📊 API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

### Telegram Integration
- `GET /api/telegram/verify` - Check bot status
- `POST /api/telegram/link-with-code` - Link via code
- `POST /api/telegram/link-direct-admin` - Direct link (dev)
- `POST /api/telegram/webhook` - Bot receives messages

### AI & Chat
- `POST /api/ai/chat` - Chat with financial advisor
- `POST /api/ai/analyze-receipt` - Parse receipt image
- `GET /api/ai/telegram/settings` - Get telegram settings
- `POST /api/ai/telegram/settings` - Update telegram settings

### Transactions
- `GET /api/transactions` - List transactions
- `POST /api/transactions` - Create transaction
- `DELETE /api/transactions/{id}` - Delete transaction

---

## 🚢 Production Deployment

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", "app:app"]
```

### Deploy to Cloud
- **Heroku**: `git push heroku main`
- **Railway**: Connect GitHub repo
- **Render**: Set up from repository
- **AWS**: Use ECR + ECS or Lambda
- **GCP**: Cloud Run

### Environment Variables in Production
- Set all env vars in your platform's console
- Use secrets management (never hardcode values)
- Rotate keys regularly

---

## ✅ Testing Checklist

- [ ] Database migration successful
- [ ] Auth signup works and creates profile
- [ ] Telegram bot connects via `/start`
- [ ] Linking code generation works
- [ ] Chat endpoint responds (Gemini or Qwen)
- [ ] Transactions can be logged
- [ ] Notifications send to Telegram
- [ ] Receipt upload works (OCR + Qwen)
- [ ] Financial health score calculates
- [ ] Weekly summary sends correctly

---

## 🐛 Debugging

### View Backend Logs
```bash
# Development
tail -f backend/app.log

# Docker
docker logs -f sentinel-backend
```

### Test Telegram Bot
```bash
# Check bot info
curl https://api.telegram.org/bot{TOKEN}/getMe

# Send test message
curl -X POST https://api.telegram.org/bot{TOKEN}/sendMessage \
  -d "chat_id=7873003581" \
  -d "text=Test%20message"
```

### Database Queries
```python
# Test if column exists
supabase.table("user_profiles").select("telegram_chat_id").limit(1).execute()
```

---

## 📝 Notes

- **Keep `.env` file safe** - contains sensitive keys
- **Backup database regularly** - especially before migrations  
- **Monitor token usage** - Gemini & HuggingFace have quotas
- **Test notifications** - Use `/api/ai/telegram/test` endpoint
- **Update bot username** - In config if you rename the bot

---

## 🆘 Support

Check logs:
```bash
# Backend errors
grep "ERROR" app.log

# Database issues  
# Check Supabase dashboard > Logs

# Telegram issues
# Check webhook in Telegram Bot API docs
```
