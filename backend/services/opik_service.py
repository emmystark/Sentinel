"""
Opik Monitoring Service - Track and monitor AI model performance
Integrates with Opik for observability of Qwen and other AI models
"""

import os
import logging
from typing import Any, Dict, Optional, Callable
from datetime import datetime
from functools import wraps

logger = logging.getLogger(__name__)

# Configure Opik - automatically detects API key from environment
OPIK_ENABLED = False
track = None  # Will be imported if available
OPIK_AVAILABLE= True
try:
    from opik import configure, track
    
    # Initialize Opik using environment variables
    # Set OPIK_API_KEY in your .env file
    configure()
    OPIK_ENABLED = True
    logger.info("✅ Opik AI monitoring initialized successfully")
except ImportError:
    logger.warning("⚠️ Opik not installed. Run: pip install opik")
    OPIK_ENABLED = False
    
    # Fallback: mock decorator if Opik not available
    def track(func=None):
        """Mock decorator for when Opik is not installed"""
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
            return wrapper
        
        if func is None:
            return decorator
        return decorator(func)
except Exception as e:
    logger.warning(f"⚠️ Failed to configure Opik: {e}")
    OPIK_ENABLED = False
    
    # Fallback decorator
    def track(func=None):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
            return wrapper
        if func is None:
            return decorator
        return decorator(func)


# Example: Decorated AI functions for tracking
# Usage: Simply add @track decorator to your AI functions

example_tracked_functions = '''
# Example 1: Financial advice generation with tracking
@track
def generate_financial_advice(spending_data: dict) -> str:
    """Generate AI-powered financial advice"""
    from openai import OpenAI
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a financial advisor specializing in personal finance."},
            {"role": "user", "content": f"Analyze my spending: {spending_data}"}
        ]
    )
    return response.choices[0].message.content

# Example 2: Receipt parsing with tracking
@track
async def parse_receipt_tracked(image_data: str) -> dict:
    """Parse receipt with tracking"""
    from services.gemini_service import parse_receipt
    return await parse_receipt(image_data)

# Example 3: Category prediction with tracking
@track
def predict_transaction_category(merchant: str, description: str) -> str:
    """Predict category using Qwen"""
    from services.qwen_service import predict_category
    return predict_category(merchant, description)
'''


# Helper function to log AI operations manually
def log_ai_operation(
    operation_name: str,
    model_name: str,
    input_data: Dict[str, Any],
    output_data: Optional[Dict[str, Any]] = None,
    latency_ms: Optional[float] = None,
    error: Optional[str] = None,
    user_id: Optional[str] = None,
    tokens_used: Optional[int] = None
):
    """Log AI operation for monitoring and debugging"""
    
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
    
    # Structured logging for analytics
    operation_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation_name,
        "model": model_name,
        "user_id": user_id,
        "status": "error" if error else "success",
        "latency_ms": latency_ms,
        "tokens_used": tokens_used,
        "input_preview": str(input_data)[:100] if input_data else None,
        "error_message": error if error else None
    }
    
    return operation_log
