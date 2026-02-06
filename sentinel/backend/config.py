"""
Configuration and dependency management
"""
import os
from dotenv import load_dotenv
from fastapi import HTTPException, Header
from typing import Optional
import logging
import ssl

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# ==================== SUPABASE CLIENT ====================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase_client: Optional[object] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        # Import supabase here to avoid connection issues
        from supabase import create_client, Client
        
        # Create a custom SSL context if needed
        # This helps with DNS resolution issues
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"Supabase client initialized: {SUPABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase_client = None
else:
    logger.warning("Supabase credentials not configured. Set SUPABASE_URL and SUPABASE_KEY")

# ==================== DEPENDENCIES ====================

def get_supabase():
    """Get Supabase client"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    return create_client(url, key)

async def get_user_id(user_id: str = Header(None, alias="user-id")) -> str:
    """Extract user ID from request headers"""
    if not user_id:
        # For development, allow a default user
        if os.getenv("ENVIRONMENT") == "development":
            return "default-user"
        raise HTTPException(status_code=401, detail="User ID required")
    return user_id

# ==================== CONFIGURATION ====================

class Config:
    """Application configuration"""
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", 3000))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")
    
    # CORS Configuration
    ALLOWED_ORIGINS = [
        FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:3001"
    ]
