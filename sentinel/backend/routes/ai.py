from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from config import get_supabase, get_user_id
from services.qwen_service import (
    parse_receipt_with_qwen,
    analyze_transaction_with_qwen
)
from services.financial_advice_service import (
    analyze_spending_patterns,
    generate_financial_advice,
    get_health_score,
    get_transaction_advice
)
from services.notification_service import (
    send_notification,
    send_budget_alert,
    send_spending_insight,
    send_health_tip,
    send_weekly_summary,
    send_high_risk_alert,
    NotificationChannel,
    NotificationType
)
import logging
import base64

from supabase import Client


logger = logging.getLogger(__name__)
router = APIRouter()

class AnalyzeReceiptRequest(BaseModel):
    image_url: Optional[str] = None
    image_base64: Optional[str] = None

class CategorizeRequest(BaseModel):
    merchant: str
    amount: Optional[float] = None
    description: Optional[str] = ""

class AnalyzeSpendingRequest(BaseModel):
    monthly_income: float
    fixed_bills: float
    savings_goal: float

class ChatRequest(BaseModel):
    message: str
    transactions: Optional[List[dict]] = []
    monthlyIncome: Optional[float] = None

class FinancialHealthRequest(BaseModel):
    monthly_income: float
    fixed_bills: float
    savings_goal: float

class TransactionAnalysisRequest(BaseModel):
    merchant: str
    amount: float
    category: str
    description: Optional[str] = ""

class TelegramSettingsRequest(BaseModel):
    telegram_chat_id: Optional[int] = None
    bot_token: Optional[str] = None
    enable_notifications: Optional[bool] = True

@router.post("/analyze-receipt")
async def analyze_receipt_endpoint(
    request: AnalyzeReceiptRequest,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Analyze a receipt image using Qwen model via HuggingFace API.
    Extracts transaction details: merchant, amount, date, category, items.
    Supports both image URL and base64 encoded images.
    
    Features:
    - Strict JSON parsing with fallbacks
    - Retries on transient failures  
    - Detailed error logging for debugging
    """
    try:
        if not request.image_url and not request.image_base64:
            logger.error("Receipt analysis: No image provided")
            raise HTTPException(
                status_code=400,
                detail="Image URL or base64 required"
            )
        
        image_source = request.image_base64 or request.image_url
        
        logger.info(f"Receipt analysis started for user {user_id}, source type: {'base64' if request.image_base64 else 'url'}")
        
        # Parse receipt using Qwen with OCR + text-based analysis
        extracted_data = await parse_receipt_with_qwen(image_source)
        
        logger.info(f"Receipt analysis complete: merchant='{extracted_data.get('merchant')}', amount={extracted_data.get('amount')}")
        
        return {
            "success": True,
            "merchant": extracted_data.get("merchant", "Unknown"),
            "amount": extracted_data.get("amount", 0),
            "currency": extracted_data.get("currency", "USD"),
            "date": extracted_data.get("date"),
            "description": extracted_data.get("description", ""),
            "items": extracted_data.get("items", []),
            "category": extracted_data.get("category", "Other"),
            "model": "Qwen2.5-7B-Instruct"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing receipt: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Receipt analysis failed: {str(e)}")

@router.post("/analyze-receipt-upload")
async def analyze_receipt_upload(
    file: UploadFile = File(...),
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Analyze an uploaded receipt image using Qwen model.
    """
    try:
        # Read and encode file to base64
        contents = await file.read()
        base64_image = base64.b64encode(contents).decode('utf-8')
        
        # Determine mime type
        mime_type = file.content_type or "image/jpeg"
        image_data = f"data:{mime_type};base64,{base64_image}"
        
        # Parse receipt with Qwen
        extracted_data = await parse_receipt_with_qwen(image_data)
        
        return {
            "success": True,
            "merchant": extracted_data.get("merchant", "Unknown"),
            "amount": extracted_data.get("amount", 0),
            "currency": extracted_data.get("currency", "USD"),
            "date": extracted_data.get("date"),
            "description": extracted_data.get("description", ""),
            "items": extracted_data.get("items", []),
            "category": extracted_data.get("category", "Other"),
            "model": "Qwen2.5-7B-Instruct"
        }
        
    except Exception as e:
        logger.error(f"Error analyzing uploaded receipt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/financial-health")
async def get_financial_health_endpoint(
    request: FinancialHealthRequest,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Calculate user's financial health score based on spending patterns.
    Returns a score from 0-100 with detailed breakdowns.
    """
    try:
        health_score = await get_health_score(
            user_id,
            supabase,
            request.monthly_income,
            request.fixed_bills,
            request.savings_goal
        )
        
        return {
            "success": True,
            "health_score": health_score
        }
        
    except Exception as e:
        logger.error(f"Error calculating financial health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/spending-insights")
async def get_spending_insights_endpoint(
    request: FinancialHealthRequest,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Get detailed spending insights and personalized recommendations.
    """
    try:
        # Analyze spending patterns
        analysis = await analyze_spending_patterns(user_id, supabase, months=1)
        
        # Generate financial advice
        advice = await generate_financial_advice(
            user_id,
            supabase,
            request.monthly_income,
            request.fixed_bills,
            request.savings_goal
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "advice": advice
        }
        
    except Exception as e:
        logger.error(f"Error generating spending insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-transaction")
async def analyze_transaction_endpoint(
    request: TransactionAnalysisRequest,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Analyze a specific transaction and provide AI-powered insights.
    """
    try:
        analysis = await get_transaction_advice(
            request.merchant,
            request.amount,
            request.category,
            request.description
        )
        
        return {
            "success": True,
            "transaction_analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-tips")
async def get_health_tips_endpoint(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Get personalized financial health improvement tips.
    """
    try:
        # Analyze spending
        analysis = await analyze_spending_patterns(user_id, supabase, months=1)
        
        tips = []
        
        # Generate tips based on spending patterns
        if analysis.get("high_risk_categories"):
            for category_data in analysis["high_risk_categories"]:
                category = category_data.get("category")
                tips.append(f"Try to reduce spending in {category}. Look for alternatives or discounts.")
        
        if analysis.get("total_transactions", 0) < 10:
            tips.append("Track more transactions to get better insights into your spending habits.")
        
        if analysis.get("largest_transaction"):
            largest = analysis["largest_transaction"]
            tips.append(f"Your largest transaction was ${largest.get('amount', 0):.2f} at {largest.get('merchant', 'Unknown')}. Consider if this was necessary.")
        
        # Add general tips
        tips.extend([
            "Set up budget categories and review them weekly.",
            "Use the notification feature to track real-time spending alerts.",
            "Schedule weekly reviews of your financial data to stay on top of your budget.",
            "Build an emergency fund equal to 3-6 months of expenses.",
            "Automate your savings by setting up automatic transfers."
        ])
        
        return {
            "success": True,
            "tips": tips[:5]  # Return top 5 tips
        }
        
    except Exception as e:
        logger.error(f"Error generating health tips: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-budget-alert/{category}")
async def send_budget_alert_endpoint(
    category: str,
    spent_amount: float,
    budget_amount: float,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Send a budget alert notification to the user.
    """
    try:
        from services.notification_service import send_budget_alert
        
        success = await send_budget_alert(
            user_id,
            spent_amount,
            budget_amount,
            category,
            supabase
        )
        
        return {
            "success": success,
            "message": "Budget alert sent" if success else "Failed to send alert"
        }
        
    except Exception as e:
        logger.error(f"Error sending budget alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-health-notification")
async def send_health_notification_endpoint(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Send a periodic financial health improvement notification.
    """
    try:
        from services.notification_service import send_health_tip
        
        # Get a health tip
        tips_response = await get_health_tips_endpoint(user_id, supabase)
        tips = tips_response.get("tips", [])
        
        if tips:
            tip = tips[0]
            success = await send_health_tip(user_id, tip, supabase)
            
            return {
                "success": success,
                "tip": tip
            }
        else:
            return {
                "success": False,
                "message": "No tips available"
            }
        
    except Exception as e:
        logger.error(f"Error sending health notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-weekly-summary")
async def send_weekly_summary_endpoint(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Send a weekly spending summary notification.
    """
    try:
        from services.notification_service import send_weekly_summary
        
        # Get transactions from this week
        analysis = await analyze_spending_patterns(user_id, supabase, months=1)
        
        total_spent = analysis.get("total_spent", 0)
        transactions = analysis.get("total_transactions", 1)
        avg_daily = (total_spent / 7) if transactions > 0 else 0
        category_breakdown = analysis.get("category_breakdown", {})
        
        success = await send_weekly_summary(
            user_id,
            total_spent,
            avg_daily,
            category_breakdown,
            supabase
        )
        
        return {
            "success": success,
            "summary": {
                "total_spent": total_spent,
                "avg_daily": avg_daily,
                "categories": category_breakdown
            }
        }
        
    except Exception as e:
        logger.error(f"Error sending weekly summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/telegram/settings")
async def update_telegram_settings(
    request: TelegramSettingsRequest,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Update Telegram notification settings for a user.
    Allows users to configure their Telegram chat ID and enable/disable notifications.
    """
    try:
        # Update user profile with Telegram settings
        response = supabase.table("user_profiles").update({
            "telegram_chat_id": request.telegram_chat_id
        }).eq("id", user_id).execute()
        
        if response.data:
            return {
                "success": True,
                "message": "Telegram settings updated successfully",
                "telegram_chat_id": request.telegram_chat_id,
                "notifications_enabled": request.enable_notifications
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update settings")
        
    except Exception as e:
        logger.error(f"Error updating Telegram settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/telegram/settings")
async def get_telegram_settings(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Get current Telegram notification settings for a user.
    """
    try:
        response = supabase.table("user_profiles").select(
            "telegram_chat_id"
        ).eq("id", user_id).single().execute()
        
        if response.data:
            telegram_chat_id = response.data.get("telegram_chat_id")
            return {
                "success": True,
                "telegram_chat_id": telegram_chat_id,
                "notifications_enabled": telegram_chat_id is not None
            }
        else:
            raise HTTPException(status_code=404, detail="User profile not found")
        
    except Exception as e:
        logger.error(f"Error fetching Telegram settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/telegram/test")
async def test_telegram_connection(
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Send a test notification to verify Telegram connection is working.
    """
    try:
        from services.notification_service import send_health_tip
        
        test_tip = "🧪 Test notification: Your Telegram integration is working perfectly!"
        
        success = await send_health_tip(user_id, test_tip, supabase)
        
        return {
            "success": success,
            "message": "Test notification sent" if success else "Failed to send test notification"
        }
        
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))
