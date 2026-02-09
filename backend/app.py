"""
Sentinel Backend - AI-powered Financial Smoke Detector
Production-ready FastAPI application for Render deployment
"""

from dotenv import load_dotenv
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import routes (after env loading)
from routes import auth, transactions, ai, telegram, monitoring
from config import Config, get_supabase, get_user_id
from services.scheduler_service import initialize_scheduler, stop_scheduler

# ==================== APP LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("🚀 Sentinel Backend starting up...")
    logger.info(f"   Environment: {os.getenv('ENVIRONMENT', 'production')}")
    logger.info(f"   Port: {os.getenv('PORT', '8000')}")
    
    try:
        # Initialize scheduler for periodic tasks
        initialize_scheduler()
        logger.info("✅ Scheduler initialized")
    except Exception as e:
        logger.error(f"⚠️ Scheduler initialization failed: {e}")
    
    # Check critical services
    try:
        supabase = get_supabase()
        logger.info("✅ Database connection verified")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
    
    # Check Opik monitoring
    try:
        from services.opik_monitoring import check_opik_health
        opik_health = check_opik_health()
        if opik_health['enabled']:
            logger.info(f"✅ Opik monitoring enabled ({opik_health.get('mode', 'unknown')} mode)")
        else:
            logger.warning("⚠️ Opik monitoring disabled")
    except Exception as e:
        logger.warning(f"⚠️ Opik monitoring check failed: {e}")
    
    logger.info("✅ Backend startup complete!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Sentinel Backend shutting down...")
    try:
        stop_scheduler()
        logger.info("✅ Scheduler stopped")
    except Exception as e:
        logger.error(f"⚠️ Scheduler shutdown error: {e}")
    
    logger.info("✅ Backend shutdown complete")


# ==================== FASTAPI APP ====================

app = FastAPI(
    title="Sentinel Backend",
    description="AI-powered Financial Smoke Detector with OCR and LLM Monitoring",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",  # Swagger UI
    redoc_url="/api/redoc",  # ReDoc
)

# ==================== CORS MIDDLEWARE ====================

# Get allowed origins from config or environment
allowed_origins = Config.ALLOWED_ORIGINS if hasattr(Config, 'ALLOWED_ORIGINS') else [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://sentinel-pchb.onrender.com",
    "https://*.onrender.com",  # Allow all Render subdomains
]

# Add environment-specific origins
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url and frontend_url not in allowed_origins:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

logger.info(f"📡 CORS enabled for origins: {allowed_origins}")

# ==================== HEALTH CHECK ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint - API status."""
    return {
        "service": "Sentinel Backend",
        "status": "running",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint for monitoring and Render."""
    health_status = {
        "status": "ok",
        "message": "Backend is running",
        "environment": os.getenv("ENVIRONMENT", "production"),
    }
    
    # Check database
    try:
        supabase = get_supabase()
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        health_status["database"] = "error"
        health_status["status"] = "degraded"
    
    # Check Opik monitoring
    try:
        from services.opik_monitoring import OPIK_AVAILABLE
        health_status["monitoring"] = "enabled" if OPIK_AVAILABLE else "disabled"
    except Exception:
        health_status["monitoring"] = "unavailable"
    
    return health_status


@app.get("/api/status")
async def detailed_status():
    """Detailed status endpoint for debugging."""
    status = {
        "service": "Sentinel Backend",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "port": os.getenv("PORT", "8000"),
    }
    
    # Database status
    try:
        supabase = get_supabase()
        status["database"] = {
            "status": "connected",
            "url": os.getenv("SUPABASE_URL", "not_set")[:30] + "..."
        }
    except Exception as e:
        status["database"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Opik monitoring status
    try:
        from services.opik_monitoring import check_opik_health
        status["monitoring"] = check_opik_health()
    except Exception as e:
        status["monitoring"] = {
            "status": "error",
            "error": str(e)
        }
    
    # OCR status
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        status["ocr"] = {
            "status": "available",
            "tesseract_version": str(version)
        }
    except Exception as e:
        status["ocr"] = {
            "status": "unavailable",
            "error": str(e)
        }
    
    # AI models status
    status["ai_models"] = {
        "huggingface_token": "configured" if os.getenv("HF_TOKEN") else "missing",
        "qwen_model": "Qwen2.5-7B-Instruct"
    }
    
    return status


# ==================== ROUTE REGISTRATION ====================

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["telegram"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])

logger.info("✅ All routes registered")

# ==================== ERROR HANDLING ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv("ENVIRONMENT") == "development" else "An error occurred",
            "status_code": 500
        }
    )


# ==================== STARTUP INFO ====================

@app.on_event("startup")
async def log_startup_info():
    """Log startup information."""
    logger.info("=" * 50)
    logger.info("🎯 Sentinel Backend - AI Financial Tracker")
    logger.info("=" * 50)
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'production')}")
    logger.info(f"Port: {os.getenv('PORT', '8000')}")
    logger.info(f"Docs: /api/docs")
    logger.info(f"Health: /api/health")
    logger.info("=" * 50)


# ==================== MAIN ENTRY POINT ====================

if __name__ == "__main__":
    # Get port from environment (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    # Get host (0.0.0.0 for Render, localhost for local dev)
    host = "0.0.0.0" if os.getenv("ENVIRONMENT") == "production" else "127.0.0.1"
    
    logger.info(f"Starting server on {host}:{port}")
    
    uvicorn.run(
        "main:app",  # Use string reference for auto-reload
        host=host,
        port=port,
        log_level="info",
        reload=os.getenv("ENVIRONMENT") != "production",  # Disable reload in production
        workers=1  # Single worker for free tier
    )