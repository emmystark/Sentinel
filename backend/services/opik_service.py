"""
Opik Monitoring Service - LLM Observability & Performance Tracking
Integrates with Opik (Comet ML) for monitoring AI model performance
Tracks: Receipt parsing, categorization, financial advice, chat
"""

import os
import logging
from typing import Any, Dict, Optional
from functools import wraps
import time

logger = logging.getLogger(__name__)

# ==================== OPIK CONFIGURATION ====================

OPIK_ENABLED = False
OPIK_CONFIGURED = False
OPIK_AVAILABLE=True

try:
    import opik
    from opik import track, configure
    from opik.evaluation.metrics import Hallucination, AnswerRelevance
    
    # Configure Opik based on environment
    # Option 1: Cloud (Comet.com) - requires COMET_API_KEY and COMET_WORKSPACE
    # Option 2: Self-hosted - requires OPIK_URL_OVERRIDE
    # Option 3: Local - use configure(use_local=True)
    
    COMET_API_KEY = os.getenv("COMET_API_KEY")
    COMET_WORKSPACE = os.getenv("COMET_WORKSPACE")
    OPIK_URL = os.getenv("OPIK_URL_OVERRIDE")  # For self-hosted
    USE_LOCAL_OPIK = os.getenv("USE_LOCAL_OPIK", "false").lower() == "true"
    
    if USE_LOCAL_OPIK:
        # Local self-hosted Opik instance
        logger.info("🏠 Configuring Opik for local deployment...")
        configure(use_local=True)
        OPIK_ENABLED = True
        OPIK_CONFIGURED = True
        logger.info("✅ Opik configured for local instance at http://localhost:5173")
        
    elif COMET_API_KEY and COMET_WORKSPACE:
        # Cloud-hosted on Comet.com
        logger.info("☁️ Configuring Opik for Comet.com cloud...")
        configure(
            api_key=COMET_API_KEY,
            workspace=COMET_WORKSPACE
        )
        OPIK_ENABLED = True
        OPIK_CONFIGURED = True
        logger.info(f"✅ Opik configured for Comet.com workspace: {COMET_WORKSPACE}")
        
    elif OPIK_URL:
        # Self-hosted Opik instance
        logger.info(f"🔧 Configuring Opik for self-hosted instance at {OPIK_URL}...")
        configure(url=OPIK_URL)
        OPIK_ENABLED = True
        OPIK_CONFIGURED = True
        logger.info(f"✅ Opik configured for self-hosted instance: {OPIK_URL}")
        
    else:
        logger.warning("⚠️ Opik not configured - missing credentials")
        logger.info("To enable Opik monitoring, set one of:")
        logger.info("  1. COMET_API_KEY + COMET_WORKSPACE (for Comet.com)")
        logger.info("  2. OPIK_URL_OVERRIDE (for self-hosted)")
        logger.info("  3. USE_LOCAL_OPIK=true (for local Docker)")
        OPIK_ENABLED = False
        
except ImportError as e:
    logger.warning(f"⚠️ Opik not installed: {e}")
    logger.info("Install Opik: pip install opik")
    OPIK_ENABLED = False
    
except Exception as e:
    logger.error(f"❌ Failed to configure Opik: {e}")
    logger.info("Opik monitoring will be disabled")
    OPIK_ENABLED = False


# ==================== FALLBACK DECORATOR ====================

def _create_fallback_track():
    """Create a fallback @track decorator when Opik is not available."""
    def track_decorator(
        name: Optional[str] = None,
        tags: Optional[list] = None,
        metadata: Optional[dict] = None,
        project_name: Optional[str] = None
    ):
        """Fallback decorator that does nothing but log."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Log function call
                logger.debug(f"[OPIK-FALLBACK] Calling {func.__name__}")
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    logger.debug(f"[OPIK-FALLBACK] {func.__name__} completed in {duration:.2f}ms")
                    return result
                except Exception as e:
                    logger.error(f"[OPIK-FALLBACK] {func.__name__} failed: {e}")
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                logger.debug(f"[OPIK-FALLBACK] Calling {func.__name__}")
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    duration = (time.time() - start_time) * 1000
                    logger.debug(f"[OPIK-FALLBACK] {func.__name__} completed in {duration:.2f}ms")
                    return result
                except Exception as e:
                    logger.error(f"[OPIK-FALLBACK] {func.__name__} failed: {e}")
                    raise
            
            # Return appropriate wrapper based on function type
            import asyncio
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper
        
        return decorator
    
    return track_decorator


# Assign track decorator (real or fallback)
if OPIK_ENABLED:
    # Use real Opik track decorator
    logger.info("✅ Using Opik @track decorator for monitoring")
else:
    # Use fallback decorator
    track = _create_fallback_track()
    logger.info("⚠️ Using fallback @track decorator (Opik disabled)")


# ==================== OPIK METRICS ====================

def get_hallucination_metric():
    """Get Opik's Hallucination metric for evaluation."""
    if OPIK_ENABLED:
        try:
            from opik.evaluation.metrics import Hallucination
            return Hallucination()
        except ImportError:
            logger.warning("Hallucination metric not available")
    return None


def get_answer_relevance_metric():
    """Get Opik's AnswerRelevance metric for evaluation."""
    if OPIK_ENABLED:
        try:
            from opik.evaluation.metrics import AnswerRelevance
            return AnswerRelevance()
        except ImportError:
            logger.warning("AnswerRelevance metric not available")
    return None


# ==================== MANUAL LOGGING ====================

def log_ai_operation(
    operation_name: str,
    model_name: str,
    input_data: Dict[str, Any],
    output_data: Optional[Dict[str, Any]] = None,
    latency_ms: Optional[float] = None,
    error: Optional[str] = None,
    user_id: Optional[str] = None,
    tokens_used: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Manually log AI operations to Opik and local logs.
    Useful for operations that can't use @track decorator.
    
    Args:
        operation_name: Name of the operation (e.g., "parse_receipt")
        model_name: AI model used (e.g., "Qwen2.5-7B")
        input_data: Input data dictionary
        output_data: Output data dictionary
        latency_ms: Operation latency in milliseconds
        error: Error message if failed
        user_id: User identifier
        tokens_used: Number of tokens consumed
        metadata: Additional metadata
    """
    # Structured log data
    log_entry = {
        "operation": operation_name,
        "model": model_name,
        "user_id": user_id,
        "status": "error" if error else "success",
        "latency_ms": latency_ms,
        "tokens_used": tokens_used,
        "timestamp": time.time(),
        "metadata": metadata or {}
    }
    
    # Log to console
    if error:
        logger.error(
            f"🚨 AI Error: {model_name} - {operation_name} | "
            f"User: {user_id} | Error: {error[:100]} | "
            f"Latency: {latency_ms:.2f}ms" if latency_ms else ""
        )
    else:
        log_msg = (
            f"✅ AI Operation: {model_name} - {operation_name} | "
            f"User: {user_id}"
        )
        if latency_ms:
            log_msg += f" | Latency: {latency_ms:.2f}ms"
        if tokens_used:
            log_msg += f" | Tokens: {tokens_used}"
        logger.info(log_msg)
    
    # Log to Opik if enabled
    if OPIK_ENABLED and OPIK_CONFIGURED:
        try:
            # Use Opik's logging API
            opik.log_traces(
                name=operation_name,
                input=input_data,
                output=output_data or {"error": error} if error else {},
                tags=[model_name, "manual_log"],
                metadata={
                    **log_entry,
                    **(metadata or {})
                }
            )
            logger.debug(f"Logged to Opik: {operation_name}")
        except Exception as e:
            logger.warning(f"Failed to log to Opik: {e}")
    
    return log_entry


# ==================== HEALTH CHECK ====================

def check_opik_health() -> Dict[str, Any]:
    """
    Check Opik monitoring health status.
    
    Returns:
        Dictionary with health status
    """
    health = {
        "enabled": OPIK_ENABLED,
        "configured": OPIK_CONFIGURED,
        "status": "healthy" if OPIK_ENABLED and OPIK_CONFIGURED else "disabled"
    }
    
    if OPIK_ENABLED:
        try:
            # Try to ping Opik
            import opik
            # Add actual health check if Opik provides one
            health["version"] = opik.__version__
            health["status"] = "healthy"
        except Exception as e:
            health["status"] = "error"
            health["error"] = str(e)
    else:
        health["message"] = "Opik not configured - set COMET_API_KEY or USE_LOCAL_OPIK=true"
    
    return health


# ==================== CONFIGURATION INFO ====================

def get_opik_config_info() -> Dict[str, Any]:
    """Get current Opik configuration information."""
    return {
        "enabled": OPIK_ENABLED,
        "configured": OPIK_CONFIGURED,
        "mode": (
            "local" if os.getenv("USE_LOCAL_OPIK", "").lower() == "true" 
            else "cloud" if os.getenv("COMET_API_KEY") 
            else "self-hosted" if os.getenv("OPIK_URL_OVERRIDE")
            else "not_configured"
        ),
        "workspace": os.getenv("COMET_WORKSPACE"),
        "url": os.getenv("OPIK_URL_OVERRIDE"),
        "local": os.getenv("USE_LOCAL_OPIK", "false").lower() == "true"
    }


# ==================== EXAMPLE USAGE ====================

"""
Example usage of Opik monitoring:

# 1. Using @track decorator (recommended)
from services.opik_monitoring import track

@track(name="parse_receipt", tags=["ocr", "qwen"])
async def parse_receipt_with_qwen(image_source: str):
    # Your code here
    pass

# 2. Manual logging
from services.opik_monitoring import log_ai_operation

start = time.time()
try:
    result = await some_ai_function()
    log_ai_operation(
        operation_name="categorize_transaction",
        model_name="Qwen2.5-7B",
        input_data={"merchant": "Shoprite"},
        output_data={"category": "Groceries"},
        latency_ms=(time.time() - start) * 1000,
        user_id=user_id
    )
except Exception as e:
    log_ai_operation(
        operation_name="categorize_transaction",
        model_name="Qwen2.5-7B",
        input_data={"merchant": "Shoprite"},
        error=str(e),
        latency_ms=(time.time() - start) * 1000,
        user_id=user_id
    )

# 3. Check health
from services.opik_monitoring import check_opik_health
health = check_opik_health()
print(health)
"""

# Log startup status
if OPIK_ENABLED and OPIK_CONFIGURED:
    logger.info(f"🎯 Opik monitoring is ACTIVE - {get_opik_config_info()['mode']} mode")
else:
    logger.info("⚠️ Opik monitoring is DISABLED")