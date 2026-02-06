from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import httpx
import os
import logging
from datetime import datetime
from config import get_user_id

router = APIRouter(tags=["telegram"])
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API = os.getenv("TELEGRAM_API_BASE_URL", "https://api.telegram.org")

# Store verified users (in production, use database)
verified_users = {}

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict = None
    callback_query: dict = None

class VerificationRequest(BaseModel):
    telegram_id: str
    username: str = None

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
                return {
                    "verified": True,
                    "optional": False,
                    "bot": bot_info.get("result", {}),
                    "username": bot_info.get("result", {}).get("username")
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

@router.post("/webhook")
async def telegram_webhook(update: TelegramUpdate):
    """Receive updates from Telegram"""
    try:
        if update.message:
            chat_id = update.message.get("chat", {}).get("id")
            text = update.message.get("text", "")
            user = update.message.get("from", {})
            
            # Handle /start command
            if text.startswith("/start"):
                await send_message(
                    chat_id,
                    f"Welcome {user.get('first_name', 'User')}! 🎉\n\n"
                    f"I'm your Sentinel Finance Bot.\n\n"
                    f"Your Telegram ID: `{chat_id}`\n"
                    f"Use this ID to link your account."
                )
                return {"status": "ok"}
            
            # Handle verification codes
            if text.startswith("/verify"):
                parts = text.split()
                if len(parts) > 1:
                    code = parts[1]
                    # Store verification (implement your logic)
                    verified_users[str(chat_id)] = {
                        "verified_at": datetime.utcnow(),
                        "username": user.get("username"),
                        "first_name": user.get("first_name")
                    }
                    await send_message(
                        chat_id,
                        "✅ Verification successful!\n\n"
                        "Your Telegram account is now linked."
                    )
                else:
                    await send_message(
                        chat_id,
                        "❌ Invalid verification code.\n\n"
                        "Usage: /verify YOUR_CODE"
                    )
                return {"status": "ok"}
        
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

@router.post("/link-account")
async def link_telegram_account(request: VerificationRequest):
    """Link Telegram account to user"""
    try:
        # Check if user exists in verified_users
        if request.telegram_id in verified_users:
            return {
                "success": True,
                "message": "Account linked successfully",
                "user": verified_users[request.telegram_id]
            }
        else:
            return {
                "success": False,
                "error": "User not verified. Please send /start to the bot first."
            }
    except Exception as e:
        logger.error(f"Error linking account: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check-link/{telegram_id}")
async def check_telegram_link(telegram_id: str):
    """Check if Telegram account is linked"""
    is_linked = telegram_id in verified_users
    return {
        "linked": is_linked,
        "user": verified_users.get(telegram_id) if is_linked else None
    }