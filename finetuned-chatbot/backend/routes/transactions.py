from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from config import get_supabase, get_user_id
import logging
from supabase import Client


logger = logging.getLogger(__name__)
router = APIRouter()

class TransactionCreate(BaseModel):
    merchant: str
    amount: float
    category: str
    description: Optional[str] = ""
    date: Optional[str] = None

class TransactionUpdate(BaseModel):
    merchant: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None

@router.get("/")
async def get_transactions(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all transactions for a user"""
    try:
        response = supabase.table("transactions").select(
            "*"
        ).eq("user_id", user_id).order("date", desc=True).range(offset, offset + limit - 1).execute()
        
        return response.data or []
        
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        # Return empty array on error for demo purposes
        return []

@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Get a single transaction"""
    try:
        response = supabase.table("transactions").select(
            "*"
        ).eq("id", transaction_id).eq("user_id", user_id).single().execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        return response.data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching transaction: {e}")
        raise HTTPException(status_code=500, detail="Error fetching transaction")

@router.post("/")
async def create_transaction(
    transaction: TransactionCreate,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Create a new transaction"""
    try:
        transaction_date = transaction.date or datetime.utcnow().isoformat()
        
        data = {
            "user_id": user_id,
            "merchant": transaction.merchant,
            "amount": transaction.amount,
            "category": transaction.category,
            "description": transaction.description or "",
            "date": transaction_date,
            "created_at": datetime.utcnow().isoformat()
        }
        
        response = supabase.table("transactions").insert(data).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to create transaction")
        
        return {
            "success": True,
            "transaction": response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        raise HTTPException(status_code=500, detail="Error creating transaction")

@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    transaction: TransactionUpdate,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Update a transaction"""
    try:
        # Verify ownership
        existing = supabase.table("transactions").select(
            "id"
        ).eq("id", transaction_id).eq("user_id", user_id).single().execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Prepare update data (only non-None values)
        update_data = {}
        if transaction.merchant is not None:
            update_data["merchant"] = transaction.merchant
        if transaction.amount is not None:
            update_data["amount"] = transaction.amount
        if transaction.category is not None:
            update_data["category"] = transaction.category
        if transaction.description is not None:
            update_data["description"] = transaction.description
        if transaction.date is not None:
            update_data["date"] = transaction.date
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("transactions").update(update_data).eq("id", transaction_id).execute()
        
        return {
            "success": True,
            "transaction": response.data[0] if response.data else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating transaction: {e}")
        raise HTTPException(status_code=500, detail="Error updating transaction")

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Delete a transaction"""
    try:
        # Verify ownership
        existing = supabase.table("transactions").select(
            "id"
        ).eq("id", transaction_id).eq("user_id", user_id).single().execute()
        
        if not existing.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        supabase.table("transactions").delete().eq("id", transaction_id).execute()
        
        return {
            "success": True,
            "message": "Transaction deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction: {e}")
        raise HTTPException(status_code=500, detail="Error deleting transaction")

@router.get("/stats/summary")
async def get_transaction_stats(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Get transaction statistics"""
    try:
        transactions = supabase.table("transactions").select(
            "amount, category, date"
        ).eq("user_id", user_id).execute()
        
        if not transactions.data:
            return {
                "total_spent": 0,
                "transaction_count": 0,
                "average_transaction": 0,
                "by_category": {}
            }
        
        transactions_list = transactions.data
        total_spent = sum(t["amount"] for t in transactions_list)
        
        # Group by category
        by_category = {}
        for t in transactions_list:
            category = t.get("category", "Other")
            by_category[category] = by_category.get(category, 0) + t["amount"]
        
        return {
            "total_spent": total_spent,
            "transaction_count": len(transactions_list),
            "average_transaction": total_spent / len(transactions_list),
            "by_category": by_category
        }
        
    except Exception as e:
        logger.error(f"Error calculating stats: {e}")
        raise HTTPException(status_code=500, detail="Error calculating stats")
