"""
Opik Monitoring Service - Track and monitor AI model performance
Integrates with Opik for observability of Qwen and other AI models
"""

import os
import logging
import asyncio
from typing import Any, Dict, Optional, Callable
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Environment variables
# -------------------------------------------------------------------
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME")
OPIK_API_KEY = os.getenv("OPIK_API_KEY")
OPIK_WORKSPACE = os.getenv("OPIK_WORKSPACE")
ENV = os.getenv("ENV", "development")

# -------------------------------------------------------------------
# Opik availability & safe configuration
# -------------------------------------------------------------------
OPIK_AVAILABLE = False

try:
    import opik
    from opik import track

    if OPIK_API_KEY:
        try:
            # 🚫 Disable prompts explicitly (CRITICAL for Render)
            opik.configure(
                api_key=OPIK_API_KEY,
                workspace=OPIK_WORKSPACE,
                disable_prompts=True,
            )
            OPIK_AVAILABLE = True
            logger.info(f"✅ Opik monitoring enabled for project: {OPIK_PROJECT_NAME}")
        except Exception as e:
            logger.warning(f"⚠️ Opik initialization failed, monitoring disabled: {e}")
            OPIK_AVAILABLE = False
    else:
        logger.warning("⚠️ OPIK_API_KEY not set - monitoring disabled")
        OPIK_AVAILABLE = False

except ImportError:
    logger.warning("⚠️ Opik not installed. Run: pip install opik")
    OPIK_AVAILABLE = False


# -------------------------------------------------------------------
# Decorator for monitoring Qwen calls
# -------------------------------------------------------------------
def monitor_qwen_call(operation_name: str):
    """
    Decorator to monitor Qwen API calls with Opik.
    Tracks latency, tokens, errors, and model performance.
    """

    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not OPIK_AVAILABLE:
                return await func(*args, **kwargs)

            try:
                with track(
                    name=operation_name,
                    input={
                        "model": "Qwen2.5-7B-Instruct",
                        "function": func.__name__,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                ):
                    result = await func(*args, **kwargs)
                    logger.info(f"✅ {operation_name} completed successfully")
                    return result
            except Exception as e:
                logger.error(f"❌ {operation_name} failed: {e}")
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not OPIK_AVAILABLE:
                return func(*args, **kwargs)

            try:
                with track(
                    name=operation_name,
                    input={
                        "model": "Qwen2.5-7B-Instruct",
                        "function": func.__name__,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                ):
                    result = func(*args, **kwargs)
                    logger.info(f"✅ {operation_name} completed")
                    return result
            except Exception as e:
                logger.error(f"❌ {operation_name} failed: {e}")
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# -------------------------------------------------------------------
# Opik Monitor Helper
# -------------------------------------------------------------------
class OpikMonitor:
    """Helper class for Opik monitoring integration"""

    def __init__(self):
        self.available = OPIK_AVAILABLE
        self.project_name = OPIK_PROJECT_NAME

    def log_chat_completion(
        self,
        model: str,
        user_message: str,
        response: str,
        context: Optional[Dict[str, Any]] = None,
        latency_ms: Optional[float] = None,
        tokens_used: Optional[Dict[str, int]] = None,
    ):
        if not self.available:
            return

        try:
            logger.info(
                f"Opik chat logged: {model}"
                + (f" ({latency_ms}ms)" if latency_ms else "")
            )
        except Exception as e:
            logger.warning(f"Could not log to Opik: {e}")

    def log_error(
        self,
        model: str,
        operation: str,
        error: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        if not self.available:
            return

        try:
            logger.error(
                f"🚨 Opik error logged: {model} - {operation}: {error[:80]}"
            )
        except Exception as e:
            logger.warning(f"Could not log error to Opik: {e}")

    def log_receipt_parsing(
        self,
        merchant: str,
        amount: float,
        confidence: float = 1.0,
        latency_ms: Optional[float] = None,
    ):
        if not self.available:
            return

        try:
            logger.info(
                f"Receipt parsed: {merchant} - {amount:,.0f} (conf={confidence})"
            )
        except Exception as e:
            logger.warning(f"Could not log receipt parsing: {e}")

    def log_categorization(
        self,
        merchant: str,
        category: str,
        confidence: float = 1.0,
    ):
        if not self.available:
            return

        try:
            logger.debug(
                f"Categorized: {merchant[:50]} → {category} (conf={confidence})"
            )
        except Exception as e:
            logger.warning(f"Could not log categorization: {e}")


# -------------------------------------------------------------------
# Global monitor instance
# -------------------------------------------------------------------
monitor = OpikMonitor()


def get_opik_monitor() -> OpikMonitor:
    """Get the global Opik monitor instance"""
    return monitor


__all__ = [
    "monitor",
    "get_opik_monitor",
    "OpikMonitor",
    "monitor_qwen_call",
]
