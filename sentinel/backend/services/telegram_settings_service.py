"""
Telegram settings and connection management service.
"""

import logging
from typing import Dict, Any, Optional
from supabase import Client
from config import Config

logger = logging.getLogger(__name__)


async def get_telegram_settings(user_id: str, supabase: Client) -> Dict[str, Any]:
    """
    Retrieve Telegram settings for a user.
    
    Args:
        user_id: User identifier
        supabase: Supabase client
        
    Returns:
        Dictionary with Telegram settings
    """
    try:
        response = supabase.table("user_profiles").select(
            "telegram_chat_id"
        ).eq("id", user_id).single().execute()
        
        if response.data:
            telegram_chat_id = response.data.get("telegram_chat_id")
            return {
                "telegram_chat_id": telegram_chat_id,
                "has_settings": telegram_chat_id is not None,
                "notifications_enabled": telegram_chat_id is not None
            }
        
        return {
            "telegram_chat_id": None,
            "has_settings": False,
            "notifications_enabled": False
        }
        
    except Exception as e:
        logger.error(f"Error getting Telegram settings: {e}")
        return {
            "telegram_chat_id": None,
            "has_settings": False,
            "notifications_enabled": False,
            "error": str(e)
        }


async def update_telegram_settings(
    user_id: str,
    telegram_chat_id: Optional[int],
    supabase: Client
) -> Dict[str, Any]:
    """
    Update Telegram settings for a user.
    
    Args:
        user_id: User identifier
        telegram_chat_id: Telegram chat ID (None to disable)
        supabase: Supabase client
        
    Returns:
        Update result
    """
    try:
        response = supabase.table("user_profiles").update({
            "telegram_chat_id": telegram_chat_id
        }).eq("id", user_id).execute()
        
        if response.data:
            return {
                "success": True,
                "telegram_chat_id": telegram_chat_id,
                "message": "Settings updated successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to update settings"
            }
        
    except Exception as e:
        logger.error(f"Error updating Telegram settings: {e}")
        return {
            "success": False,
            "message": str(e)
        }


async def disconnect_telegram(user_id: str, supabase: Client) -> Dict[str, Any]:
    """
    Disconnect Telegram from user profile.
    
    Args:
        user_id: User identifier
        supabase: Supabase client
        
    Returns:
        Disconnect result
    """
    try:
        response = supabase.table("user_profiles").update({
            "telegram_chat_id": None
        }).eq("id", user_id).execute()
        
        if response.data:
            return {
                "success": True,
                "message": "Telegram disconnected successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to disconnect Telegram"
            }
        
    except Exception as e:
        logger.error(f"Error disconnecting Telegram: {e}")
        return {
            "success": False,
            "message": str(e)
        }


def verify_telegram_token(token: str) -> bool:
    """
    Verify if Telegram bot token is valid.
    Format: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
    
    Args:
        token: Telegram bot token
        
    Returns:
        True if token format is valid
    """
    if not token or not isinstance(token, str):
        return False
    
    parts = token.split(":")
    if len(parts) != 2:
        return False
    
    token_id, token_hash = parts
    if not token_id.isdigit() or len(token_hash) < 20:
        return False
    
    return True


def verify_telegram_chat_id(chat_id: int) -> bool:
    """
    Verify if Telegram chat ID is valid.
    
    Args:
        chat_id: Telegram chat ID
        
    Returns:
        True if chat ID is valid
    """
    if not chat_id or not isinstance(chat_id, int):
        return False
    
    return True
