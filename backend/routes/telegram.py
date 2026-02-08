from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import httpx
import os
import re
import logging
import secrets
from datetime import datetime, timedelta
from config import get_user_id, get_supabase
from services.qwen_chat_service import chat_with_advisor, categorize_transaction

router = APIRouter(tags=["telegram"])
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = os.getenv("TELEGRAM_API_BASE_URL", "https://api.telegram.org")

# Pending link codes: code -> {telegram_id, telegram_username, first_name, expires}
# In production, use Redis or DB
pending_codes: dict = {}

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict = None
    callback_query: dict = None

class VerificationRequest(BaseModel):
    telegram_id: str
    username: str = None

class LinkWithCodeRequest(BaseModel):
    code: str

@router.get("/verify")
async def verify_telegram_bot():
    """Check if bot token is valid"""
    if not BOT_TOKEN:
        return {
            "verified": False,
            "optional": True,
            "message": "Telegram not configured. You can still use the app without it."
        }
    
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            response = await client.get(
                f"{TELEGRAM_API}/bot{BOT_TOKEN}/getMe",
                timeout=10.0
            )
            
            if response.status_code == 200:
                bot_info = response.json()
                result = bot_info.get("result", {})
                # Bot username from API or env (for t.me links)
                bot_username = result.get("username") or os.getenv("TELEGRAM_BOT_USERNAME", "")
                return {
                    "verified": True,
                    "optional": False,
                    "bot": result,
                    "username": bot_username,
                    "bot_username": bot_username  # for Connect button link
                }
            else:
                return {
                    "verified": False,
                    "optional": True,
                    "error": f"API returned {response.status_code}",
                    "message": "Telegram verification failed, but you can still use the app."
                }
    except httpx.ConnectError as e:
        logger.warning(f"Telegram API connection error: {e}")
        return {
            "verified": False,
            "optional": True,
            "error": "Cannot connect to Telegram API",
            "message": "Telegram integration not available, but you can still use the app."
        }
    except httpx.TimeoutException as e:
        logger.warning(f"Telegram API timeout: {e}")
        return {
            "verified": False,
            "optional": True,
            "error": "Telegram API request timed out",
            "message": "Telegram integration not available, but you can still use the app."
        }
    except Exception as e:
        logger.warning(f"Error verifying Telegram: {e}")
        return {
            "verified": False,
            "optional": True,
            "error": f"Verification failed: {str(e)}",
            "message": "Telegram integration not available, but you can still use the app."
        }

def _parse_transaction_text(text: str) -> tuple[str | None, float | None]:
    """Parse 'Merchant 4500' or '4500 Merchant' or 'Food 5000 Chicken Republic' -> (merchant, amount)"""
    text = text.strip()
    if not text or len(text) < 3:
        return None, None
    # Match number (with optional decimals, commas)
    num_pattern = r"(\d+(?:[.,]\d+)?)"
    matches = list(re.finditer(num_pattern, text))
    if not matches:
        return None, None
    # Take last number as amount (most likely total)
    last_match = matches[-1]
    try:
        amount = float(last_match.group(1).replace(",", "."))
    except ValueError:
        return None, None
    if amount <= 0:
        return None, None
    # Rest is merchant
    merchant = (text[:last_match.start()] + text[last_match.end():]).strip()
    merchant = re.sub(r"\s+", " ", merchant).strip()
    if not merchant:
        merchant = "Telegram expense"
    return merchant, amount


@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Receive updates from Telegram - link accounts, log transactions, provide financial advice"""
    try:
        if not update.message:
            return {"status": "ok"}
        chat_id = update.message.get("chat", {}).get("id")
        text = (update.message.get("text") or "").strip()
        user = update.message.get("from", {})
        
        # Handle /start command
        if text.startswith("/start"):
            # Generate 6-digit numeric link code for connect flow
            code = str(secrets.randbelow(1000000)).zfill(6)
            pending_codes[code] = {
                "telegram_id": chat_id,
                "telegram_username": user.get("username"),
                "first_name": user.get("first_name"),
                "expires": datetime.utcnow() + timedelta(minutes=10),
            }
            await send_message(
                chat_id,
                f"🎉 Welcome {user.get('first_name', 'User')}! I'm Sentinel, your personal finance advisor.\n\n"
                f"💡 **What I do:**\n"
                f"• Track your daily expenses 💰\n"
                f"• Analyze spending patterns 📊\n"
                f"• Give personalized financial advice 🎯\n\n"
                f"🔗 **Link your account:**\n"
                f"Send `/link {code}` (or just `{code}`) to link now\n"
                f"Code expires in 10 minutes\n\n"
                f"📝 **Log expenses:**\n"
                f"• `Chicken Republic 4500`\n"
                f"• `4500 Uber`\n"
                f"• `Food 5000 Restaurant`\n\n"
                f"💬 **Ask for advice:**\n"
                f"• \"How can I save money?\"\n"
                f"• \"Am I spending too much on food?\"\n"
                f"• \"What's my spending pattern?\""
            )
            return {"status": "ok"}
        
        # Check if it's a 6-digit linking code
        if text.isalnum() and len(text) == 6:
            code = text.upper()
            if code in pending_codes:
                entry = pending_codes[code]
                if datetime.utcnow() <= entry["expires"]:
                    # Valid code - but we need user_id from app, so just confirm
                    await send_message(
                        chat_id,
                        f"✅ Code `{code}` accepted!\n\n"
                        f"Go to Sentinel app → Profile → Connect Telegram\n"
                        f"and confirm to complete linking.\n\n"
                        f"Once linked, you can:\n"
                        f"• Log expenses here\n"
                        f"• Get spending insights\n"
                        f"• Receive financial advice"
                    )
                    logger.info(f"User {chat_id} entered valid code {code}")
                    return {"status": "ok"}
                else:
                    del pending_codes[code]
                    await send_message(chat_id, "⏰ Code expired. Send /start for a new code.")
                    return {"status": "ok"}
        
        # Handle /link command with code
        if text.startswith("/link"):
            parts = text.split()
            if len(parts) > 1:
                code = parts[1].upper()
                if code in pending_codes:
                    entry = pending_codes[code]
                    if datetime.utcnow() <= entry["expires"]:
                        await send_message(
                            chat_id,
                            f"✅ Code `{code}` accepted!\n\n"
                            f"Go to Sentinel app → Profile → Connect Telegram\n"
                            f"and confirm to complete linking."
                        )
                        logger.info(f"User {chat_id} used /link with code {code}")
                        return {"status": "ok"}
                    else:
                        del pending_codes[code]
                        await send_message(chat_id, "⏰ Code expired. Send /start for a new code.")
                        return {"status": "ok"}
            await send_message(chat_id, "Usage: `/link XXXXXX` or just send the 6-digit code")
            return {"status": "ok"}
        
        # Try to parse as transaction amount and save to DB
        merchant, amount = _parse_transaction_text(text)
        if merchant and amount and amount < 1e9:  # Sanity cap
            try:
                supabase = get_supabase()
                # Find user by telegram_chat_id in user_profiles
                r = supabase.table("user_profiles").select("id, telegram_connected").eq(
                    "telegram_chat_id", chat_id
                ).execute()
                if r.data and len(r.data) > 0:
                    user_id = r.data[0]["id"]
                    # Categorize with Qwen AI
                    category = await categorize_transaction(merchant, "")
                    supabase.table("transactions").insert({
                        "user_id": user_id,
                        "merchant": merchant,
                        "amount": float(amount),
                        "category": category,
                        "description": f"Telegram: {text[:100]}",
                        "source": "telegram",
                        "ai_categorized": True,
                    }).execute()
                    await send_message(chat_id, f"✅ Logged: {merchant} – ₦{amount:,.0f} ({category})")
                else:
                    await send_message(
                        chat_id,
                        "⚠️ Account not linked.\n\n"
                        "Send /start and enter your 6-digit code to link now 🔗"
                    )
            except Exception as e:
                logger.error(f"Webhook save transaction error: {e}")
                await send_message(chat_id, "❌ Could not save expense. Try again.")
                return {"status": "ok"}
        else:
            # Not an expense format - treat as a question and use Qwen for advice
            try:
                supabase = get_supabase()
                # Find user by telegram_chat_id
                r = supabase.table("user_profiles").select("*").eq(
                    "telegram_chat_id", chat_id
                ).execute()
                if r.data and len(r.data) > 0:
                    profile = r.data[0]
                    user_id = profile["id"]
                    
                    # Get recent transactions for context
                    transactions_r = supabase.table("transactions").select("*").eq(
                        "user_id", user_id
                    ).order("created_at", desc=True).limit(20).execute()
                    
                    transactions = transactions_r.data or []
                    total_spent = sum(float(t.get("amount", 0)) for t in transactions)
                    
                    # Build context for Qwen
                    user_context = {
                        "monthlyIncome": profile.get("monthly_income", 0),
                        "fixedBills": profile.get("fixed_bills", 0),
                        "savingsGoal": profile.get("savings_goal", 0),
                        "totalSpent": total_spent,
                        "transactionSummary": "\n".join([
                            f"- {t.get('merchant', 'Unknown')}: ₦{t.get('amount', 0):,.0f} ({t.get('category', 'Other')})"
                            for t in transactions[:5]
                        ]) if transactions else "No transactions yet"
                    }
                    
                    # Get financial advice from Qwen
                    advice = await chat_with_advisor(text, user_context)
                    await send_message(chat_id, advice)
                else:
                    await send_message(
                        chat_id,
                        "📱 Please link your account first:\n\n"
                        "Send /start and enter your 6-digit code\n"
                        "Then I can help with your finances! 💰"
                    )
            except Exception as e:
                logger.error(f"Webhook Qwen advice error: {e}")
                await send_message(
                    chat_id,
                    "💭 I had trouble responding. Try:\n"
                    "• Log an expense: `Merchant 5000`\n"
                    "• Link account: /start"
                )
        
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send-message")
async def send_telegram_message(
    chat_id: str,
    message: str
):
    """Send message to user"""
    return await send_message(chat_id, message)

async def send_message(chat_id: int | str, text: str):
    """Helper function to send messages"""
    if not BOT_TOKEN:
        return {"success": False, "error": "Bot not configured"}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{TELEGRAM_API}/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                }
            )
            
            if response.status_code == 200:
                return {"success": True, "result": response.json()}
            else:
                return {"success": False, "error": response.text}
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {"success": False, "error": str(e)}

@router.post("/link-with-code")
async def link_with_code(
    request: LinkWithCodeRequest,
    user_id: str = Depends(get_user_id),
    supabase = Depends(get_supabase),
):
    """Link Telegram to user using code from /start in bot"""
    try:
        code = (request.code or "").strip().upper()
        if len(code) < 4:
            return {"success": False, "error": "Invalid code"}
        entry = pending_codes.get(code)
        if not entry:
            return {"success": False, "error": "Code expired or invalid. Send /start in Telegram for a new code."}
        if datetime.utcnow() > entry["expires"]:
            del pending_codes[code]
            return {"success": False, "error": "Code expired. Send /start in Telegram for a new code."}
        telegram_id = entry["telegram_id"]
        telegram_username = entry.get("telegram_username")
        del pending_codes[code]
        
        # Update user_profiles with telegram link
        logger.info(f"Linking telegram_id {telegram_id} to user {user_id}")
        supabase.table("user_profiles").update({
            "telegram_chat_id": telegram_id,
            "telegram_connected": True,
            "telegram_username": telegram_username,
        }).eq("id", user_id).execute()
        
        # Send confirmation message
        try:
            await send_message(
                telegram_id,
                "✅ Your Telegram account is now linked to Sentinel!\n\n"
                "You can now:\n"
                "• Log expenses by sending messages like: `Chicken Republic 4500`\n"
                "• Receive spending alerts and financial advice\n"
                "• Get notifications about your financial health\n\n"
                "Send any expense message to start tracking! 💰"
            )
        except Exception as e:
            logger.warning(f"Could not send confirmation message: {e}")
        
        logger.info(f"Successfully linked telegram {telegram_id} to user {user_id}")
        return {
            "success": True, 
            "message": "Telegram linked successfully ✅",
            "telegram_id": telegram_id,
            "telegram_username": telegram_username
        }
    except Exception as e:
        logger.error(f"Link with code error: {e}")
        return {"success": False, "error": str(e)}


@router.post("/link-account")
async def link_telegram_account(request: VerificationRequest):
    """Legacy: link by telegram_id (use link-with-code for new flow)"""
    try:
        supabase = get_supabase()
        # Would need user_id - this endpoint is for backwards compat
        return {"success": False, "error": "Use /link-with-code with the code from the bot"}
    except Exception as e:
        logger.error(f"Error linking account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class DirectTelegramLinkRequest(BaseModel):
    """For direct linking (development/admin)"""
    telegram_id: int
    user_id: str

@router.post("/link-direct-admin")
async def link_direct_admin(
    request: DirectTelegramLinkRequest
):
    """
    Direct link telegram ID to user (for admin/testing purposes).
    In production, require proper authentication.
    """
    try:
        if not request.telegram_id or not request.user_id:
            return {"success": False, "error": "Missing telegram_id or user_id"}
        
        supabase = get_supabase()
        
        # Verify user exists
        user_check = supabase.table("user_profiles").select("id").eq("id", request.user_id).execute()
        if not user_check.data:
            return {"success": False, "error": "User not found"}
        
        # Update telegram link
        logger.info(f"Direct linking telegram {request.telegram_id} to user {request.user_id}")
        supabase.table("user_profiles").update({
            "telegram_chat_id": request.telegram_id,
            "telegram_connected": True,
        }).eq("id", request.user_id).execute()
        
        logger.info(f"Successfully linked telegram {request.telegram_id} to user {request.user_id}")
        return {
            "success": True,
            "message": "Telegram linked successfully ✅",
            "telegram_id": request.telegram_id,
            "user_id": request.user_id
        }
    except Exception as e:
        logger.error(f"Error in direct link: {e}")
        return {"success": False, "error": str(e)}


@router.get("/check-link/{telegram_id}")
async def check_telegram_link(telegram_id: str, supabase = Depends(get_supabase)):
    """Check if Telegram account is linked to any user"""
    try:
        r = supabase.table("user_profiles").select("id").eq(
            "telegram_chat_id", telegram_id
        ).execute()
        is_linked = bool(r.data and len(r.data) > 0)
        return {"linked": is_linked}
    except Exception as e:
        return {"linked": False}


@router.post("/setup-webhook")
async def setup_telegram_webhook(request_body: dict = None):
    """
    Setup Telegram webhook for production.
    Call this endpoint once after deploying to production.
    
    Example:
    POST /api/telegram/setup-webhook
    
    Response shows webhook configuration status
    """
    if not BOT_TOKEN:
        return {
            "success": False,
            "error": "Telegram bot not configured (BOT_TOKEN not set)"
        }
    
    # Get webhook URL from env or defaults
    webhook_url = os.getenv("BACKEND_WEBHOOK_URL", "https://sentinel-pchb.onrender.com")
    full_webhook_url = f"{webhook_url}/api/telegram/webhook"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{TELEGRAM_API}/bot{BOT_TOKEN}/setWebhook",
                json={
                    "url": full_webhook_url,
                    "allowed_updates": ["message", "callback_query"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    logger.info(f"✅ Telegram webhook configured: {full_webhook_url}")
                    
                    # Also get webhook info to confirm
                    info_response = await client.get(
                        f"{TELEGRAM_API}/bot{BOT_TOKEN}/getWebhookInfo"
                    )
                    
                    webhook_info = {}
                    if info_response.status_code == 200:
                        info_data = info_response.json()
                        if info_data.get("ok"):
                            webhook_info = info_data.get("result", {})
                    
                    return {
                        "success": True,
                        "message": "Webhook configured successfully",
                        "webhook_url": full_webhook_url,
                        "webhook_info": {
                            "url": webhook_info.get("url"),
                            "pending_updates": webhook_info.get("pending_update_count", 0),
                            "last_error": webhook_info.get("last_error_message")
                        }
                    }
                else:
                    error_msg = result.get("description", "Unknown error")
                    logger.error(f"Webhook setup error: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg
                    }
            else:
                logger.error(f"Telegram API error {response.status_code}")
                return {
                    "success": False,
                    "error": f"Telegram API returned {response.status_code}",
                    "detail": response.text
                }
                
    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to Telegram API: {e}")
        return {
            "success": False,
            "error": "Cannot connect to Telegram API",
            "detail": str(e)
        }
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/webhook-info")
async def get_webhook_info():
    """Get current webhook information and status"""
    if not BOT_TOKEN:
        return {
            "configured": False,
            "error": "Bot token not set"
        }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{TELEGRAM_API}/bot{BOT_TOKEN}/getWebhookInfo"
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    info = result.get("result", {})
                    return {
                        "configured": True,
                        "webhook": {
                            "url": info.get("url", "Not set"),
                            "has_custom_certificate": info.get("has_custom_certificate", False),
                            "pending_update_count": info.get("pending_update_count", 0),
                            "last_error_message": info.get("last_error_message"),
                            "last_error_date": info.get("last_error_date")
                        }
                    }
            
            return {
                "configured": False,
                "error": "Could not get webhook info"
            }
            
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return {
            "configured": False,
            "error": str(e)
        }