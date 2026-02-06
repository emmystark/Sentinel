"""
Configuration and dependency management
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import HTTPException, Header
from typing import Optional
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# ==================== SUPABASE CLIENT ====================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("Supabase credentials not configured")
    supabase_client: Optional[Client] = None
else:
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==================== DEPENDENCIES ====================

def get_supabase() -> Client:
    """Get Supabase client"""
    if supabase_client is None:
        raise HTTPException(status_code=500, detail="Database not available")
    return supabase_client

async def get_user_id(user_id: str = Header(None, alias="user-id")) -> str:
    """Extract user ID from request headers"""
    if not user_id:
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
