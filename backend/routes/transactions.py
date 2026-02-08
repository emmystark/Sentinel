from fastapi import APIRouter, HTTPException, Depends, Query, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from config import get_supabase, get_user_id
import logging
from supabase import Client
import base64
from io import BytesIO
import time
from routes.monitoring import log_trace

logger = logging.getLogger(__name__)
router = APIRouter()

class TransactionCreate(BaseModel):
    merchant: str
    amount: float
    category: str
    description: Optional[str] = ""
    date: Optional[str] = None
    currency: str = "NGN"  # Default to Naira, but can be any ISO 4217 code

class TransactionUpdate(BaseModel):
    merchant: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    currency: Optional[str] = None

# FIXED: Removed duplicate route decorator
@router.get("/")
async def get_transactions(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get all transactions for a user"""
    try:
        logger.info(f"🔍 Fetching transactions for user: {user_id}, limit: {limit}, offset: {offset}")
        
        # Try with anon client first (respects RLS)
        response = None
        try:
            response = supabase.table("transactions").select(
                "*"
            ).eq("user_id", user_id).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
            
            if response.data and len(response.data) > 0:
                logger.info(f"✅ Anon client returned {len(response.data)} transactions for user {user_id}")
                return response.data
        except Exception as anon_error:
            logger.warning(f"⚠️ Anon client failed, trying service role: {anon_error}")
        
        # Fallback: use service role client (bypasses RLS)
        from config import get_supabase_admin
        admin_supabase = get_supabase_admin()
        response = admin_supabase.table("transactions").select(
            "*"
        ).eq("user_id", user_id).order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        
        logger.info(f"✅ Service role returned {len(response.data) if response.data else 0} transactions for user {user_id}")
        
        return response.data or []
        
    except Exception as e:
        logger.error(f"❌ Database error fetching transactions for user {user_id}: {e}", exc_info=True)
        # Return empty array on error (don't crash)
        return []

@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Get a single transaction"""
    try:
        # Try with anon client first
        try:
            response = supabase.table("transactions").select(
                "*"
            ).eq("id", transaction_id).eq("user_id", user_id).single().execute()
            
            if response.data:
                return response.data
        except Exception as anon_error:
            logger.warning(f"Anon client failed for transaction {transaction_id}, trying service role: {anon_error}")
        
        # Fallback to service role client
        from config import get_supabase_admin
        admin_supabase = get_supabase_admin()
        response = admin_supabase.table("transactions").select(
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

# FIXED: Removed duplicate route decorator
@router.post("/receipt-upload")
async def upload_receipt(
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Upload a receipt image and extract transaction data using Gemini Vision"""
    start_time = time.time()
    try:
        # Read file contents
        contents = await file.read()
        
        if not contents:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Encode to base64
        base64_image = base64.b64encode(contents).decode('utf-8')
        image_data = f"data:{file.content_type};base64,{base64_image}"
        
        # Use Gemini to parse receipt
        from services.gemini_service import parse_receipt
        extracted_data = await parse_receipt(image_data)
        
        # Create transaction in database
        transaction_date = extracted_data.get("date") or datetime.utcnow().isoformat()
        
        # Get currency from receipt, default to NGN
        currency = extracted_data.get("currency", "NGN").upper()
        if len(currency) != 3:
            currency = "NGN"
        
        data = {
            "user_id": user_id,
            "merchant": extracted_data.get("merchant", "Unknown Merchant"),
            "amount": float(extracted_data.get("amount", 0)),
            "category": extracted_data.get("category", "Other"),
            "description": extracted_data.get("description", ""),
            "date": transaction_date,
            "currency": currency,
            "source": "receipt",
            "ai_categorized": True,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Try with anon first, fallback to service role
        response = None
        try:
            response = supabase.table("transactions").insert(data).execute()
            if not response.data or len(response.data) == 0:
                raise Exception("Anon insert returned no data")
        except Exception as anon_error:
            logger.warning(f"Anon insert failed for receipt, trying with service role: {anon_error}")
            from config import get_supabase_admin
            admin_supabase = get_supabase_admin()
            response = admin_supabase.table("transactions").insert(data).execute()
        
        if not response.data or len(response.data) == 0:
            logger.error(f"Supabase insert failed for user {user_id}: {response}")
            # Log trace for failed receipt
            latency_ms = (time.time() - start_time) * 1000
            log_trace(
                operation="receipt_parsing",
                status="error",
                model="Gemini Vision",
                latency_ms=latency_ms,
                input_data={"merchant": extracted_data.get("merchant"), "file": file.filename},
                error="Failed to insert transaction",
                user_id=user_id
            )
            raise HTTPException(status_code=400, detail="Failed to create transaction from receipt")
        
        created_transaction = response.data[0]
        logger.info(f"Receipt processed for user {user_id}: {created_transaction.get('id')}")
        
        # Log successful trace
        latency_ms = (time.time() - start_time) * 1000
        log_trace(
            operation="receipt_parsing",
            status="success",
            model="Gemini Vision",
            latency_ms=latency_ms,
            input_data={"merchant": extracted_data.get("merchant"), "file": file.filename},
            output_data={"transaction_id": created_transaction.get("id"), "amount": created_transaction.get("amount")},
            user_id=user_id
        )
        
        return {
            "success": True,
            "transaction": created_transaction,
            "extracted_data": extracted_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing receipt: {str(e)}")

# FIXED: Removed duplicate route decorator
@router.post("/")
async def create_transaction(
    transaction: TransactionCreate,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Create a new transaction"""
    start_time = time.time()
    try:
        logger.info(f"Creating transaction for user {user_id}: {transaction.merchant}")
        
        if not transaction.merchant or transaction.amount is None:
            raise HTTPException(
                status_code=400, 
                detail="Merchant and amount are required"
            )
        
        transaction_date = transaction.date or datetime.utcnow().isoformat()
        
        # Validate currency code (3 letter ISO 4217 format)
        currency = transaction.currency or "NGN"
        if len(currency) != 3:
            currency = "NGN"
        currency = currency.upper()
        
        data = {
            "user_id": user_id,
            "merchant": transaction.merchant.strip(),
            "amount": float(transaction.amount),
            "category": transaction.category or "Other",
            "description": (transaction.description or "").strip(),
            "date": transaction_date,
            "currency": currency,
            "created_at": datetime.utcnow().isoformat()
        }
        
        logger.debug(f"Transaction data prepared: {data}")
        
        # Try with anon client first (respects RLS)
        try:
            logger.info(f"Attempting to insert with anon client for user {user_id}")
            response = supabase.table("transactions").insert(data).execute()
            if response.data and len(response.data) > 0:
                created_transaction = response.data[0]
                logger.info(f"Transaction created successfully (anon) for user {user_id}: {created_transaction.get('id')}")
                
                # Log successful trace
                latency_ms = (time.time() - start_time) * 1000
                log_trace(
                    operation="transaction_create",
                    status="success",
                    model="Manual",
                    latency_ms=latency_ms,
                    input_data={"merchant": transaction.merchant, "amount": transaction.amount, "currency": currency},
                    output_data={"transaction_id": created_transaction.get("id"), "category": created_transaction.get("category")},
                    user_id=user_id
                )
                
                return {
                    "success": True,
                    "transaction": created_transaction
                }
        except Exception as anon_error:
            logger.warning(f"Anon insert failed for user {user_id}, trying with service role: {anon_error}")
            
            # Fallback to service role client (bypasses RLS)
            from config import get_supabase_admin
            admin_supabase = get_supabase_admin()
            logger.info(f"Attempting to insert with service role client for user {user_id}")
            response = admin_supabase.table("transactions").insert(data).execute()
        
        if not response.data or len(response.data) == 0:
            logger.error(f"Supabase insert failed for user {user_id}: {response}")
            # Log trace for failed transaction
            latency_ms = (time.time() - start_time) * 1000
            log_trace(
                operation="transaction_create",
                status="error",
                model="Manual",
                latency_ms=latency_ms,
                input_data={"merchant": transaction.merchant, "amount": transaction.amount},
                error="Failed to insert transaction",
                user_id=user_id
            )
            raise HTTPException(status_code=400, detail="Failed to create transaction")
        
        created_transaction = response.data[0]
        logger.info(f"Transaction created successfully (service role fallback) for user {user_id}: {created_transaction.get('id')}")
        
        # Log successful trace
        latency_ms = (time.time() - start_time) * 1000
        log_trace(
            operation="transaction_create",
            status="success",
            model="Manual",
            latency_ms=latency_ms,
            input_data={"merchant": transaction.merchant, "amount": transaction.amount, "currency": currency},
            output_data={"transaction_id": created_transaction.get("id"), "category": created_transaction.get("category")},
            user_id=user_id
        )
        
        return {
            "success": True,
            "transaction": created_transaction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating transaction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating transaction: {str(e)[:100]}")

@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    transaction: TransactionUpdate,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """Update a transaction"""
    try:
        # Verify ownership - try with anon client first
        existing = None
        try:
            existing = supabase.table("transactions").select(
                "id"
            ).eq("id", transaction_id).eq("user_id", user_id).single().execute()
            
            if existing.data:
                logger.info(f"Anon client verified ownership of transaction {transaction_id}")
        except Exception as anon_error:
            logger.warning(f"Anon client failed to verify ownership, trying service role: {anon_error}")
            # Try with service role as fallback
            from config import get_supabase_admin
            admin_supabase = get_supabase_admin()
            existing = admin_supabase.table("transactions").select(
                "id"
            ).eq("id", transaction_id).eq("user_id", user_id).single().execute()
        
        if not existing or not existing.data:
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
        if transaction.currency is not None:
            # Validate currency code
            currency = transaction.currency.upper()
            if len(currency) == 3:
                update_data["currency"] = currency
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        # Use service role for update to ensure it works
        from config import get_supabase_admin
        admin_supabase = get_supabase_admin()
        response = admin_supabase.table("transactions").update(update_data).eq("id", transaction_id).execute()
        
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
        # Verify ownership - try with anon client first
        existing = None
        try:
            existing = supabase.table("transactions").select(
                "id"
            ).eq("id", transaction_id).eq("user_id", user_id).single().execute()
            
            if existing.data:
                logger.info(f"Anon client verified ownership of transaction {transaction_id}")
        except Exception as anon_error:
            logger.warning(f"Anon client failed to verify ownership, trying service role: {anon_error}")
            # Try with service role as fallback
            from config import get_supabase_admin
            admin_supabase = get_supabase_admin()
            existing = admin_supabase.table("transactions").select(
                "id"
            ).eq("id", transaction_id).eq("user_id", user_id).single().execute()
        
        if not existing or not existing.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Use service role for delete to ensure it works
        from config import get_supabase_admin
        admin_supabase = get_supabase_admin()
        admin_supabase.table("transactions").delete().eq("id", transaction_id).execute()
        
        return {
            "success": True,
            "message": "Transaction deleted successfully"
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