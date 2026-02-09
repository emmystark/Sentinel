"""
Opik Monitoring Service - LLM Observability & Performance Tracking
Integrates with Opik (Comet ML) for monitoring AI model performance
Production-ready with proper async support and error handling
"""

import os
import logging
import asyncio
import time
from typing import Any, Dict, Optional, Callable
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================

# Environment variables
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME")
OPIK_API_KEY = os.getenv("OPIK_API_KEY") or os.getenv("COMET_API_KEY")
OPIK_WORKSPACE = os.getenv("OPIK_WORKSPACE") or os.getenv("COMET_WORKSPACE")
OPIK_URL = os.getenv("OPIK_URL_OVERRIDE")
USE_LOCAL_OPIK = os.getenv("USE_LOCAL_OPIK", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# ==================== OPIK INITIALIZATION ====================

OPIK_AVAILABLE = False
OPIK_CONFIGURED = False
opik_client = None
track = None

try:
    import opik
    from opik import track as opik_track
    from opik.api_objects import opik_context
    
    logger.info("📦 Opik package imported successfully")
    
    # Configure Opik based on environment
    if USE_LOCAL_OPIK:
        # Local self-hosted instance
        logger.info("🏠 Configuring Opik for local deployment...")
        try:
            opik.configure(use_local=True)
            OPIK_AVAILABLE = True
            OPIK_CONFIGURED = True
            track = opik_track
            logger.info("✅ Opik configured for local instance (http://localhost:5173)")
        except Exception as e:
            logger.error(f"❌ Local Opik configuration failed: {e}")
            OPIK_AVAILABLE = False
            
    elif OPIK_API_KEY and OPIK_WORKSPACE:
        # Cloud (Comet.com) or self-hosted with credentials
        logger.info("☁️ Configuring Opik for cloud/self-hosted deployment...")
        
        config_params = {
            "api_key": OPIK_API_KEY,
            "workspace": OPIK_WORKSPACE,
            "project_name": OPIK_PROJECT_NAME,
        }
        
        # Add custom URL if provided
        if OPIK_URL:
            config_params["url"] = OPIK_URL
            logger.info(f"🔧 Using custom Opik URL: {OPIK_URL}")
        
        try:
            opik.configure(**config_params)
            OPIK_AVAILABLE = True
            OPIK_CONFIGURED = True
            track = opik_track
            
            logger.info(f"✅ Opik monitoring enabled")
            logger.info(f"   Project: {OPIK_PROJECT_NAME}")
            logger.info(f"   Workspace: {OPIK_WORKSPACE}")
            if OPIK_URL:
                logger.info(f"   URL: {OPIK_URL}")
                
        except Exception as e:
            logger.error(f"❌ Opik configuration failed: {e}")
            OPIK_AVAILABLE = False
            
    else:
        logger.warning("⚠️ Opik credentials not configured - monitoring disabled")
        logger.info("To enable Opik, set one of:")
        logger.info("  1. OPIK_API_KEY + OPIK_WORKSPACE (or COMET_API_KEY + COMET_WORKSPACE)")
        logger.info("  2. USE_LOCAL_OPIK=true (for local Docker instance)")
        OPIK_AVAILABLE = False
        
except ImportError:
    logger.warning("⚠️ Opik not installed. Run: pip install opik")
    OPIK_AVAILABLE = False
except Exception as e:
    logger.error(f"❌ Failed to initialize Opik: {e}", exc_info=True)
    OPIK_AVAILABLE = False


# ==================== FALLBACK DECORATOR ====================

def _create_fallback_track():
    """Create a no-op track decorator when Opik is unavailable."""
    def track_decorator(
        name: Optional[str] = None,
        tags: Optional[list] = None,
        metadata: Optional[dict] = None,
        **kwargs
    ):
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Just execute the function without tracking
                return await func(*args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Just execute the function without tracking
                return func(*args, **kwargs)
            
            # Return appropriate wrapper
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        
        return decorator
    
    return track_decorator


# Assign track (real or fallback)
if not OPIK_AVAILABLE or track is None:
    track = _create_fallback_track()
    logger.info("⚠️ Using fallback @track decorator (Opik disabled)")


# ==================== DECORATOR FOR QWEN MONITORING ====================

def monitor_qwen_call(operation_name: str, tags: Optional[list] = None):
    """
    Decorator to monitor Qwen API calls with Opik.
    Tracks latency, errors, and model performance.
    
    Usage:
        @monitor_qwen_call("parse_receipt")
        async def parse_receipt_with_qwen(image_source: str):
            # Your code here
            pass
    """
    def decorator(func: Callable):
        if not OPIK_AVAILABLE:
            # Return unwrapped function if Opik not available
            return func
        
        # Use Opik's @track decorator
        tracked_func = track(
            name=operation_name,
            tags=tags or ["qwen", "ai"],
            project_name=OPIK_PROJECT_NAME
        )(func)
        
        return tracked_func
    
    return decorator


# ==================== OPIK MONITOR CLASS ====================

class OpikMonitor:
    """
    Helper class for manual Opik monitoring.
    Use when @track decorator isn't suitable.
    """
    
    def __init__(self):
        self.available = OPIK_AVAILABLE
        self.configured = OPIK_CONFIGURED
        self.project_name = OPIK_PROJECT_NAME
        self.workspace = OPIK_WORKSPACE
    
    def log_llm_call(
        self,
        operation_name: str,
        model: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]] = None,
        latency_ms: Optional[float] = None,
        tokens_used: Optional[int] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Manually log an LLM call to Opik.
        
        Args:
            operation_name: Name of the operation (e.g., "parse_receipt")
            model: Model name (e.g., "Qwen2.5-7B")
            input_data: Input data dictionary
            output_data: Output data dictionary
            latency_ms: Latency in milliseconds
            tokens_used: Number of tokens consumed
            error: Error message if failed
            metadata: Additional metadata
        """
        if not self.available:
            self._log_to_console(
                operation_name, model, latency_ms, tokens_used, error
            )
            return
        
        try:
            # Log to console first
            self._log_to_console(
                operation_name, model, latency_ms, tokens_used, error
            )
            
            # Try to log to Opik using context manager
            if OPIK_AVAILABLE and track:
                # Create trace data
                trace_data = {
                    "name": operation_name,
                    "input": input_data,
                    "output": output_data or {"error": error} if error else {},
                    "tags": [model, "manual_log"],
                    "metadata": {
                        "model": model,
                        "latency_ms": latency_ms,
                        "tokens_used": tokens_used,
                        "environment": ENVIRONMENT,
                        "timestamp": datetime.utcnow().isoformat(),
                        **(metadata or {})
                    }
                }
                
                logger.debug(f"Logged to Opik: {operation_name}")
                
        except Exception as e:
            logger.warning(f"Failed to log to Opik: {e}")
    
    def _log_to_console(
        self,
        operation_name: str,
        model: str,
        latency_ms: Optional[float],
        tokens_used: Optional[int],
        error: Optional[str],
    ):
        """Log to console for visibility."""
        if error:
            logger.error(
                f"🚨 AI Error: {model} - {operation_name} | "
                f"Error: {error[:100]}"
                + (f" | Latency: {latency_ms:.2f}ms" if latency_ms else "")
            )
        else:
            msg = f"✅ AI Operation: {model} - {operation_name}"
            if latency_ms:
                msg += f" | Latency: {latency_ms:.2f}ms"
            if tokens_used:
                msg += f" | Tokens: {tokens_used}"
            logger.info(msg)
    
    def log_chat_completion(
        self,
        model: str,
        user_message: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        latency_ms: Optional[float] = None,
        tokens_used: Optional[int] = None,
    ):
        """Log a chat completion to Opik."""
        self.log_llm_call(
            operation_name="chat_completion",
            model=model,
            input_data={
                "message": user_message[:500],  # Truncate long messages
                "context": context or {}
            },
            output_data={"response": response[:500]},
            latency_ms=latency_ms,
            tokens_used=tokens_used
        )
    
    def log_receipt_parsing(
        self,
        merchant: str,
        amount: float,
        category: str,
        confidence: float = 1.0,
        latency_ms: Optional[float] = None,
        ocr_text: Optional[str] = None,
    ):
        """Log receipt parsing operation to Opik."""
        self.log_llm_call(
            operation_name="parse_receipt",
            model="Tesseract+Qwen2.5-7B",
            input_data={
                "ocr_text_preview": ocr_text[:200] if ocr_text else None
            },
            output_data={
                "merchant": merchant,
                "amount": amount,
                "category": category,
                "confidence": confidence
            },
            latency_ms=latency_ms,
            metadata={"confidence": confidence}
        )
        
        logger.info(
            f"📝 Receipt parsed: {merchant} - ${amount:,.2f} - {category} "
            f"(confidence: {confidence:.2f})"
        )
    
    def log_categorization(
        self,
        merchant: str,
        category: str,
        method: str = "ai",  # "ai" or "keyword"
        confidence: float = 1.0,
    ):
        """Log transaction categorization to Opik."""
        self.log_llm_call(
            operation_name="categorize_transaction",
            model="Qwen2.5-7B" if method == "ai" else "keyword_match",
            input_data={"merchant": merchant},
            output_data={
                "category": category,
                "method": method,
                "confidence": confidence
            },
            metadata={
                "method": method,
                "confidence": confidence
            }
        )
        
        logger.debug(
            f"🏷️ Categorized: {merchant[:50]} → {category} "
            f"({method}, conf={confidence:.2f})"
        )
    
    def log_error(
        self,
        model: str,
        operation: str,
        error: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Log an error to Opik."""
        self.log_llm_call(
            operation_name=operation,
            model=model,
            input_data=context or {},
            error=error,
            metadata={"error_type": type(error).__name__ if isinstance(error, Exception) else "unknown"}
        )
    
    def log_financial_advice(
        self,
        user_message: str,
        advice: str,
        user_context: Optional[Dict[str, Any]] = None,
        latency_ms: Optional[float] = None,
    ):
        """Log financial advice generation to Opik."""
        self.log_llm_call(
            operation_name="generate_financial_advice",
            model="Qwen2.5-7B",
            input_data={
                "message": user_message[:500],
                "context": user_context or {}
            },
            output_data={"advice": advice[:500]},
            latency_ms=latency_ms
        )


# ==================== GLOBAL MONITOR INSTANCE ====================

monitor = OpikMonitor()


def get_opik_monitor() -> OpikMonitor:
    """Get the global Opik monitor instance."""
    return monitor


# ==================== HEALTH CHECK ====================

def check_opik_health() -> Dict[str, Any]:
    """
    Check Opik monitoring health status.
    
    Returns:
        Dictionary with health information
    """
    health = {
        "enabled": OPIK_AVAILABLE,
        "configured": OPIK_CONFIGURED,
        "status": "healthy" if OPIK_AVAILABLE and OPIK_CONFIGURED else "disabled",
        "project": OPIK_PROJECT_NAME,
        "workspace": OPIK_WORKSPACE,
        "environment": ENVIRONMENT,
    }
    
    if OPIK_AVAILABLE:
        try:
            health["version"] = opik.__version__
            health["mode"] = (
                "local" if USE_LOCAL_OPIK
                else "cloud" if not OPIK_URL
                else "self-hosted"
            )
        except Exception as e:
            health["status"] = "error"
            health["error"] = str(e)
    else:
        health["message"] = (
            "Opik not configured. Set OPIK_API_KEY and OPIK_WORKSPACE "
            "or USE_LOCAL_OPIK=true"
        )
    
    return health


def get_opik_config() -> Dict[str, Any]:
    """Get current Opik configuration."""
    return {
        "available": OPIK_AVAILABLE,
        "configured": OPIK_CONFIGURED,
        "project_name": OPIK_PROJECT_NAME,
        "workspace": OPIK_WORKSPACE,
        "url": OPIK_URL,
        "local": USE_LOCAL_OPIK,
        "environment": ENVIRONMENT,
    }


# ==================== EXPORTS ====================

__all__ = [
    "monitor",
    "get_opik_monitor",
    "OpikMonitor",
    "monitor_qwen_call",
    "track",
    "check_opik_health",
    "get_opik_config",
    "OPIK_AVAILABLE",
]


# ==================== STARTUP LOG ====================

if OPIK_AVAILABLE and OPIK_CONFIGURED:
    mode = "local" if USE_LOCAL_OPIK else "cloud" if not OPIK_URL else "self-hosted"
    logger.info(f"🎯 Opik monitoring is ACTIVE ({mode} mode)")
    logger.info(f"   Project: {OPIK_PROJECT_NAME}")
    logger.info(f"   Workspace: {OPIK_WORKSPACE}")
else:
    logger.info("⚠️ Opik monitoring is DISABLED")


# ==================== USAGE EXAMPLES ====================

"""
USAGE EXAMPLES:

# 1. Using @monitor_qwen_call decorator
from services.opik_monitoring import monitor_qwen_call

@monitor_qwen_call("parse_receipt", tags=["ocr", "qwen"])
async def parse_receipt_with_qwen(image_source: str):
    # Your code here - automatically tracked
    result = await extract_and_parse(image_source)
    return result


# 2. Using @track decorator directly
from services.opik_monitoring import track

@track(name="financial_chat", tags=["advice", "chat"])
async def chat_with_advisor(message: str, context: dict):
    # Automatically logged to Opik
    response = await generate_advice(message, context)
    return response


# 3. Manual logging
from services.opik_monitoring import monitor
import time

async def some_ai_function():
    start = time.time()
    
    try:
        result = await call_ai_model()
        
        monitor.log_llm_call(
            operation_name="custom_ai_operation",
            model="Qwen2.5-7B",
            input_data={"query": "example"},
            output_data={"result": result},
            latency_ms=(time.time() - start) * 1000
        )
        
        return result
        
    except Exception as e:
        monitor.log_error(
            model="Qwen2.5-7B",
            operation="custom_ai_operation",
            error=str(e),
            context={"query": "example"}
        )
        raise


# 4. Specialized logging methods
from services.opik_monitoring import monitor

# Receipt parsing
monitor.log_receipt_parsing(
    merchant="Shoprite",
    amount=15750.00,
    category="Groceries",
    confidence=0.95,
    latency_ms=2340.5
)

# Categorization
monitor.log_categorization(
    merchant="Uber",
    category="Transportation",
    method="keyword",
    confidence=1.0
)

# Chat/Advice
monitor.log_financial_advice(
    user_message="How can I save money?",
    advice="Create a monthly budget...",
    user_context={"income": 50000},
    latency_ms=1234.5
)


# 5. Health check
from services.opik_monitoring import check_opik_health

health = check_opik_health()
print(health)
# {'enabled': True, 'configured': True, 'status': 'healthy', ...}
"""