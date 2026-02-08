"""
Monitoring and Opik Traces Endpoint
Provides access to AI model performance metrics and operation traces
"""
from fastapi import APIRouter, HTTPException, Depends
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

from config import get_user_id
from services.opik_service import OPIK_AVAILABLE

router = APIRouter(tags=["monitoring"])
logger = logging.getLogger(__name__)

# In-memory trace storage for demo (in production, use database or Opik backend)
MAX_TRACES = 500
trace_store = deque(maxlen=MAX_TRACES)
trace_categories = defaultdict(int)


class TraceEvent:
    """Represents an operation trace"""
    def __init__(
        self,
        operation: str,
        status: str = "success",
        model: Optional[str] = None,
        latency_ms: Optional[float] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        self.operation = operation
        self.status = status
        self.model = model
        self.latency_ms = latency_ms
        self.input_data = input_data or {}
        self.output_data = output_data or {}
        self.error = error
        self.user_id = user_id
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "status": self.status,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "input": self.input_data,
            "output": self.output_data,
            "error": self.error,
            "user_id": self.user_id,
            "timestamp": self.timestamp
        }


def log_trace(
    operation: str,
    status: str = "success",
    model: Optional[str] = None,
    latency_ms: Optional[float] = None,
    input_data: Optional[Dict[str, Any]] = None,
    output_data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None,
    user_id: Optional[str] = None
):
    """
    Log an operation trace locally.
    In production, this would send to Opik backend.
    """
    trace = TraceEvent(
        operation=operation,
        status=status,
        model=model,
        latency_ms=latency_ms,
        input_data=input_data,
        output_data=output_data,
        error=error,
        user_id=user_id
    )
    trace_store.append(trace)
    trace_categories[operation] += 1
    
    # Log to file
    log_level = logging.ERROR if status == "error" else logging.INFO
    logger.log(
        log_level,
        f"[{operation}] {status} | latency: {latency_ms}ms | model: {model}"
    )


@router.get("/health")
async def monitoring_health():
    """Check monitoring system status"""
    return {
        "status": "ok",
        "opik_available": OPIK_AVAILABLE,
        "traces_stored": len(trace_store),
        "max_traces": MAX_TRACES
    }


@router.get("/traces")
async def get_traces(
    operation: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    user_id: str = Depends(get_user_id)
):
    """
    Get operation traces/logs.
    Filters by operation type or status.
    
    Args:
        operation: Filter by operation name (e.g., "receipt_parsing", "categorization")
        status: Filter by status ("success", "error", "pending")
        limit: Max number of traces to return (default 50)
    
    Returns:
        List of trace events with metadata
    """
    try:
        traces = list(trace_store)
        
        # Filter by operation
        if operation:
            traces = [t for t in traces if t.operation == operation]
        
        # Filter by status
        if status:
            traces = [t for t in traces if t.status == status]
        
        # Most recent first, limit results
        traces = sorted(traces, key=lambda t: t.timestamp, reverse=True)[:limit]
        
        return {
            "success": True,
            "total": len(traces),
            "limit": limit,
            "traces": [t.to_dict() for t in traces],
            "filtered_by": {
                "operation": operation,
                "status": status
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces/summary")
async def get_traces_summary(user_id: str = Depends(get_user_id)):
    """
    Get summary stats of recent operations.
    Useful for monitoring dashboard.
    """
    try:
        traces = list(trace_store)
        
        if not traces:
            return {
                "total_operations": 0,
                "success_rate": 0,
                "avg_latency_ms": 0,
                "operations_by_type": {},
                "recent_24h": 0
            }
        
        # Calculate statistics
        total = len(traces)
        successful = sum(1 for t in traces if t.status == "success")
        success_rate = (successful / total * 100) if total > 0 else 0
        
        # Average latency for successful operations
        successful_traces = [t for t in traces if t.status == "success" and t.latency_ms]
        avg_latency = (
            sum(t.latency_ms for t in successful_traces) / len(successful_traces)
            if successful_traces else 0
        )
        
        # Count by operation
        operations_by_type = {}
        for trace in traces:
            operations_by_type[trace.operation] = operations_by_type.get(trace.operation, 0) + 1
        
        # Count recent (last 24 hours)
        now = datetime.utcnow()
        recent_24h = sum(
            1 for t in traces 
            if datetime.fromisoformat(t.timestamp) > (now - timedelta(hours=24))
        )
        
        return {
            "total_operations": total,
            "success_rate": round(success_rate, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "operations_by_type": operations_by_type,
            "recent_24h": recent_24h,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error generating trace summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces/operations/{operation_name}")
async def get_operation_traces(
    operation_name: str,
    limit: int = 100,
    user_id: str = Depends(get_user_id)
):
    """Get all traces for a specific operation type"""
    try:
        traces = [
            t for t in trace_store 
            if t.operation == operation_name
        ]
        traces = sorted(traces, key=lambda t: t.timestamp, reverse=True)[:limit]
        
        if not traces:
            return {
                "operation": operation_name,
                "total": 0,
                "traces": [],
                "message": f"No traces found for operation: {operation_name}"
            }
        
        # Calculate stats for this operation
        successful = sum(1 for t in traces if t.status == "success")
        failed = sum(1 for t in traces if t.status == "error")
        successful_traces = [t for t in traces if t.status == "success" and t.latency_ms]
        avg_latency = (
            sum(t.latency_ms for t in successful_traces) / len(successful_traces)
            if successful_traces else 0
        )
        
        return {
            "operation": operation_name,
            "total": len(traces),
            "successful": successful,
            "failed": failed,
            "avg_latency_ms": round(avg_latency, 2),
            "traces": [t.to_dict() for t in traces],
            "query_timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving operation traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces/latest")
async def get_latest_traces(
    limit: int = 20,
    user_id: str = Depends(get_user_id)
):
    """Get the most recent operation traces"""
    try:
        traces = sorted(
            trace_store,
            key=lambda t: t.timestamp,
            reverse=True
        )[:limit]
        
        return {
            "total_available": len(trace_store),
            "returned": len(traces),
            "traces": [t.to_dict() for t in traces],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error retrieving latest traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces/clear")
async def clear_traces(user_id: str = Depends(get_user_id)):
    """Clear all stored traces (admin/testing only)"""
    try:
        count = len(trace_store)
        trace_store.clear()
        trace_categories.clear()
        
        logger.warning(f"Traces cleared by user {user_id}. {count} traces removed.")
        
        return {
            "success": True,
            "cleared": count,
            "message": f"Cleared {count} traces from storage"
        }
    except Exception as e:
        logger.error(f"Error clearing traces: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export
__all__ = ["router", "log_trace", "TraceEvent", "trace_store"]
