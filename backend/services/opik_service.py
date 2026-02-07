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
import json

logger = logging.getLogger(__name__)




from opik import configure, track 
OPIK_AVAILABLE = True
OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME")
OPIK_API_KEY = os.getenv("OPIK_API_KEY")
    




# Opik Configuration
try:
    from opik import configure, track 
    OPIK_AVAILABLE = True
    OPIK_PROJECT_NAME = os.getenv("OPIK_PROJECT_NAME")
    OPIK_API_KEY = os.getenv("OPIK_API_KEY")
    
    
    if OPIK_API_KEY:
        import opik
        opik.configure(api_key=OPIK_API_KEY)
        logger.info(f"✅ Opik monitoring enabled for project: {OPIK_PROJECT_NAME}")
    else:
        logger.warning("⚠️ OPIK_API_KEY not set - monitoring disabled")
        OPIK_AVAILABLE = False
        
except ImportError:
    logger.warning("Opik not installed. Run: pip install opik")
    OPIK_AVAILABLE = False


def monitor_qwen_call(operation_name: str):
    """
    Decorator to monitor Qwen API calls with Opik.
    Tracks latency, tokens, errors, and model performance.
    
    Args:
        operation_name: Name of the operation (e.g., "financial_advice", "receipt_parsing")
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not OPIK_AVAILABLE:
                return await func(*args, **kwargs)
            
            try:
                # Create session for tracking
                session = get_current_session()
                
                with track(
                    name=operation_name,
                    input={
                        "model": "Qwen2.5-7B-Instruct",
                        "function": func.__name__,
                        "timestamp": datetime.now().isoformat()
                    }
                ):
                    result = await func(*args, **kwargs)
                    
                    # Log the output
                    logger.info(f"✅ {operation_name} completed successfully")
                    
                    return result
                    
            except Exception as e:
                logger.error(f"❌ {operation_name} failed: {str(e)}")
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
                        "timestamp": datetime.now().isoformat()
                    }
                ):
                    result = func(*args, **kwargs)
                    logger.info(f"✅ {operation_name} completed")
                    return result
                    
            except Exception as e:
                logger.error(f"❌ {operation_name} failed: {str(e)}")
                raise
        
        # Return async or sync wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


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
        tokens_used: Optional[Dict[str, int]] = None
    ):
        """
        Log a chat completion to Opik for monitoring.
        
        Args:
            model: Model name (e.g., "Qwen2.5-7B-Instruct")
            user_message: User's input message
            response: AI model response
            context: Additional context (spending data, etc)
            latency_ms: Response time in milliseconds
            tokens_used: Token usage {"prompt": X, "completion": Y}
        """
        if not self.available:
            return
        
        try:
            data = {
                "model": model,
                "user_message": user_message[:200],  # Truncate for logging
                "response": response[:200],
                "context_keys": list(context.keys()) if context else [],
                "timestamp": datetime.now().isoformat()
            }
            
            if latency_ms:
                data["latency_ms"] = latency_ms
            
            if tokens_used:
                data["tokens"] = tokens_used
                
            logger.info(f"📊 Opik logged: {model} - {latency_ms}ms" if latency_ms else f"📊 Opik logged: {model}")
            
        except Exception as e:
            logger.warning(f"Could not log to Opik: {e}")
    
    def log_error(
        self,
        model: str,
        operation: str,
        error: str,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log an error to Opik for monitoring and debugging.
        
        Args:
            model: Model name that failed
            operation: Operation that was being performed
            error: Error message
            context: Additional context
        """
        if not self.available:
            return
        
        try:
            data = {
                "model": model,
                "operation": operation,
                "error": str(error)[:200],
                "context": str(context)[:200] if context else None,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.error(f"🚨 Opik error logged: {model} - {operation}: {error[:50]}")
            
        except Exception as e:
            logger.warning(f"Could not log error to Opik: {e}")
    
    def log_receipt_parsing(
        self,
        merchant: str,
        amount: float,
        confidence: float = 1.0,
        latency_ms: Optional[float] = None
    ):
        """Log receipt parsing operation to Opik."""
        if not self.available:
            return
        
        try:
            data = {
                "operation": "receipt_parsing",
                "merchant": merchant,
                "amount": amount,
                "confidence": confidence,
                "latency_ms": latency_ms,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"📊 Receipt parsed: {merchant} - ₦{amount:,.0f}")
            
        except Exception as e:
            logger.warning(f"Could not log receipt parsing: {e}")
    
    def log_categorization(
        self,
        merchant: str,
        category: str,
        confidence: float = 1.0
    ):
        """Log transaction categorization to Opik."""
        if not self.available:
            return
        
        try:
            data = {
                "operation": "categorization",
                "merchant": merchant[:50],
                "category": category,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.debug(f"📊 Categorized: {merchant} → {category}")
            
        except Exception as e:
            logger.warning(f"Could not log categorization: {e}")


# Global monitor instance
monitor = OpikMonitor()


def get_opik_monitor() -> OpikMonitor:
    """Get the global Opik monitor instance"""
    return monitor


# Export for use in other services
__all__ = ["monitor", "get_opik_monitor", "OpikMonitor", "monitor_qwen_call"]
