# 🤖 Telegram Bot Setup Guide

## Complete Setup for @Sentinel_budget_bot

### Prerequisites
- Telegram Bot Token: `8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU`
- Backend URL: Set in TELEGRAM_WEBHOOK_URL
- Your Telegram ID: `7873003581`

---

## Step 1: Verify Bot Token

```bash
curl -X GET "https://api.telegram.org/bot8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU/getMe"
```

Expected response:
```json
{
  "ok": true,
  "result": {
    "id": 8337875351,
    "is_bot": true,
    "first_name": "Sentinel",
    "username": "Sentinel_budget_bot",
    "can_join_groups": true,
    "can_read_all_group_messages": false,
    "supports_inline_queries": false,
    "can_connect_to_business": false
  }
}
```

---

## Step 2: Check Current Webhook (Optional)

```bash
curl -X GET "https://api.telegram.org/bot8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU/getWebhookInfo"
```

---

## Step 3: Set Webhook URL

For **Local Development** (using ngrok):
```bash
# 1. Start ngrok in another terminal:
ngrok http 8000

# 2. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

# 3. Set webhook:
curl -X POST "https://api.telegram.org/bot8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU/setWebhook" \
  -F "url=https://abc123.ngrok.io/api/telegram/webhook" \
  -F "allowed_updates=[\"message\", \"callback_query\"]"
```

For **Production** (your domain):
```bash
curl -X POST "https://api.telegram.org/bot8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU/setWebhook" \
  -F "url=https://your-domain.com/api/telegram/webhook" \
  -F "allowed_updates=[\"message\", \"callback_query\"]"
```

Expected response:
```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

---

## Step 4: Update .env

```env
TELEGRAM_BOT_TOKEN=8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU
TELEGRAM_BOT_USERNAME=Sentinel_budget_bot
TELEGRAM_WEBHOOK_URL=https://your-ngrok-url-or-domain.com/api/telegram/webhook
```

---

## Step 5: Test in Telegram

1. Open Telegram
2. Search for and open: **@Sentinel_budget_bot**
3. Send: `/start`
4. You should get a code (e.g., `A1B2C3`)
5. Use the code in the web app to link your account

---

## Testing Endpoints (Local)

```bash
# 1. Verify bot
curl http://localhost:8000/api/telegram/verify

# 2. Check webhook setup
curl -X GET "https://api.telegram.org/bot8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU/getWebhookInfo"

# 3. Send test message
curl -X POST "https://api.telegram.org/bot8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU/sendMessage" \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 7873003581,
    "text": "🧪 Test message from Sentinel"
  }'
```

---

## Troubleshooting

### "getMe" returns 404
- **Issue**: Bot token is invalid
- **Fix**: Verify token with @BotFather: `/token` → select bot → check token

### Webhook returns 400
- **Issue**: URL formatting issue
- **Fix**: Ensure URL is HTTPS and TLS certificate is valid

### Messages not received
- **Issue**: Webhook not set correctly
- **Fix**: 
  1. Check webhook info: `getWebhookInfo`
  2. Check if backend URL is accessible
  3. Check firewall/security groups
  4. Ensure backend is running

### Getting "pending_update_count"
- **Issue**: Backend isn't receiving webhook calls
- **Fix**: 
  ```bash
  # Delete current webhook
  curl -X POST "https://api.telegram.org/bot{TOKEN}/setWebhook" \
    -F "url=" \
    -F "drop_pending_updates=True"
  
  # Set new webhook
  curl -X POST "https://api.telegram.org/bot{TOKEN}/setWebhook" \
    -F "url=YOUR_URL/api/telegram/webhook"
  ```

---

## Using ngrok for Local Testing

```bash
# Install ngrok (Mac):
brew install ngrok

# Start ngrok
ngrok http 8000

# Copy HTTPS URL from output
# Set as webhook (see Step 3)

# Backend must be running:
uvicorn app:app --reload
```

---

## Manual Bot Commands

```bash
# Send message
curl -X POST https://api.telegram.org/bot{TOKEN}/sendMessage \
  -H "Content-Type: application/json" \
  -d '{
    "chat_id": 7873003581,
    "text": "Hello!",
    "parse_mode": "Markdown"
  }'

# Simulate incoming message
curl -X POST http://localhost:8000/api/telegram/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456,
    "message": {
      "message_id": 1,
      "date": '$(date +%s)',
      "chat": {"id": 7873003581},
      "from": {"id": 7873003581, "is_bot": false, "first_name": "Test", "username": "testuser"},
      "text": "/start"
    }
  }'
```

---

## Production Considerations

1. **HTTPS Required**: Telegram only accepts HTTPS webhooks
2. **DNS Records**: Ensure your domain resolves correctly
3. **SSL Certificate**: Use valid certificate (Let's Encrypt recommended)
4. **Firewall**: Allow port 443 (HTTPS) for Telegram IPs
5. **Rate Limits**: Telegram has API rate limits - implement queue if needed
6. **Error Handling**: Always return 200 OK quickly, process async
7. **Logging**: Log all webhook events for debugging
8. **Monitoring**: Setup alerts for webhook failures

---

## Environment Variables

Add these to your `.env`:

```env
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8337875351:AAFfygVA3F9RLOJ2I5bndQYa0SJrsBpn4aU
TELEGRAM_BOT_USERNAME=Sentinel_budget_bot
TELEGRAM_WEBHOOK_URL=https://your-domain.com/api/telegram/webhook

# For Opik monitoring (optional)
OPIK_API_KEY=your_opik_key
OPIK_PROJECT_NAME=Sentinel

# For Qwen (required)
HF_TOKEN=your_huggingface_token

# Rest...
SUPABASE_URL=...
SUPABASE_KEY=...
```

---

## Architecture

```
Telegram Bot (@Sentinel_budget_bot)
           ↓
   Telegram Bot API
           ↓
   Your Backend Webhook
  (/api/telegram/webhook)
           ↓
   Routes Handler
  (/routes/telegram.py)
           ↓
  Save to Database
  (Supabase)
           ↓
  Notify User
  (In-app/Telegram)
```

---

## Next: Web App Linking Flow

1. User opens web app → Profile section
2. Clicks "Open Telegram Bot"
3. Sends `/start` to bot
4. Bot generates 6-char code
5. User enters code in web app
6. Web app verifies code
7. Links user account to Telegram ID
8. Shows "✅ Connected" status

See [../page.tsx](../../../frontend/src/app/page.tsx) for frontend implementation.

---

**Status**: ✅ Ready to setup webhook
**Bot**: @Sentinel_budget_bot
**Your ID**: 7873003581
