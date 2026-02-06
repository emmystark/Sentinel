from dotenv import load_dotenv
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import Config, get_supabase, get_user_id
from services.scheduler_service import initialize_scheduler, stop_scheduler


load_dotenv()
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# App lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Backend starting up...")
    initialize_scheduler()
    yield
    # Shutdown
    logger.info("Backend shutting down...")
    stop_scheduler()

# Initialize FastAPI app
app = FastAPI(
    title="Sentinel Backend",
    description="AI-powered Financial Smoke Detector",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "message": "Backend is running"
    }

# ==================== IMPORTS AFTER APP INIT ====================

from routes import auth, transactions, ai, telegram

# ==================== ROUTE REGISTRATION ====================

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(telegram.router, prefix="/api/telegram", tags=["telegram"])

# ==================== ERROR HANDLING ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="localhost",
        port=Config.BACKEND_PORT,
        log_level="info"
    )
