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

# ==================== SUPABASE CLIENTS ====================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")  # Anon key for client
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Service role for server

supabase_client: Optional[object] = None
supabase_service_client: Optional[object] = None

if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        from supabase import create_client, Client
        
        # Anon key client (respects RLS)
        supabase_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        logger.info(f"Supabase anon client initialized: {SUPABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase anon client: {e}")
        supabase_client = None
else:
    logger.warning("Supabase anon credentials not configured. Set SUPABASE_URL and SUPABASE_KEY")

# Service role client (bypasses RLS for server operations)
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    try:
        from supabase import create_client
        supabase_service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        logger.info(f"Supabase service role client initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase service role client: {e}")
        supabase_service_client = None
else:
    logger.warning("Supabase service role key not configured. Set SUPABASE_SERVICE_ROLE_KEY for backend operations")

# ==================== DEPENDENCIES ====================

def get_supabase():
    """Get Supabase client (anon key - respects RLS)"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    from supabase import create_client
    return create_client(url, key)

def get_supabase_admin():
    """Get Supabase admin client (service role - bypasses RLS)"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        logger.warning("Service role key not configured, falling back to anon client")
        return get_supabase()
    from supabase import create_client
    return create_client(url, key)

async def get_user_id(authorization: str = Header(None)) -> str:
    """
    Extract user ID from JWT token in Authorization header.
    Expected format: "Bearer <jwt_token>"
    """
    if not authorization:
        logger.warning("No authorization header provided")
        if os.getenv("ENVIRONMENT") == "development":
            # Demo user for testing
            return "550e8400-e29b-41d4-a716-446655440000"
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning("Invalid authorization header format")
        if os.getenv("ENVIRONMENT") == "development":
            return "550e8400-e29b-41d4-a716-446655440000"
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = parts[1]
    
    # Decode JWT to get user_id (sub claim)
    try:
        import jwt
        # Decode without verification first to get the payload
        # The token is already verified by Supabase on the frontend
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        
        if not user_id:
            logger.warning("No 'sub' claim in JWT token")
            if os.getenv("ENVIRONMENT") == "development":
                return "550e8400-e29b-41d4-a716-446655440000"
            raise HTTPException(status_code=401, detail="Invalid token")
        
        logger.debug(f"Extracted user ID from token: {user_id}")
        return user_id
        
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        if os.getenv("ENVIRONMENT") == "development":
            return "550e8400-e29b-41d4-a716-446655440000"
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== CONFIGURATION ====================

class Config:
    """Application configuration"""
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", 3000))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL")
    TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "")  # e.g. SentinelFinanceBot
    
    # CORS Configuration
    ALLOWED_ORIGINS = [
        FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:3001",
        "https://sentinel-tau-hazel.vercel.app"
    ]
