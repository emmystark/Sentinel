from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from config import get_supabase, get_user_id
from services.qwen_service import (
    parse_receipt_with_qwen,
    analyze_transaction_with_qwen
)
from services.qwen_chat_service import (
    chat_with_advisor,
    categorize_transaction,
    analyze_spending_pattern
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
    fixedBills: Optional[float] = None
    savingsGoal: Optional[float] = None

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

class HealthTipsRequest(BaseModel):
    transactions: Optional[List[dict]] = []
    monthlyIncome: Optional[float] = 0
    fixedBills: Optional[float] = 0
    savingsGoal: Optional[float] = 0
    categoryTotals: Optional[dict] = {}

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


@router.post("/categorize")
async def categorize_transaction_endpoint(
    request: CategorizeRequest,
    user_id: str = Depends(get_user_id)
):
    """
    Categorize a transaction by merchant/description using AI.
    """
    try:
        category = await categorize_transaction(
            request.merchant,
            request.description or ""
        )
        return {
            "success": True,
            "category": category
        }
    except Exception as e:
        logger.error(f"Error categorizing: {e}")
        return {
            "success": False,
            "category": "Other"
        }


@router.post("/chat")
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Financial advisor chat using uploaded transactions and profile expenses.
    Uses actual transaction data vs monthly expected (fixedBills, savingsGoal) from profile.
    """
    import time
    start = time.time()
    try:
        # Compute total spent from uploaded transactions
        total_spent = 0
        if request.transactions:
            for t in request.transactions:
                amt = t.get("amount", 0) or 0
                total_spent += abs(float(amt)) if amt else 0

        # Build user context: actual spending (transactions) vs expected (profile)
        user_context = {
            "monthlyIncome": request.monthlyIncome or 0,
            "fixedBills": request.fixedBills or 0,
            "savingsGoal": request.savingsGoal or 0,
            "totalSpent": total_spent,
        }

        # Fetch profile if frontend didn't send full context
        if (request.fixedBills is None or request.savingsGoal is None or request.monthlyIncome is None) and supabase:
            try:
                profile = supabase.table("user_profiles").select(
                    "monthly_income, fixed_bills, savings_goal"
                ).eq("id", user_id).execute()
                if profile.data and len(profile.data) > 0:
                    profile_data = profile.data[0]
                    user_context["monthlyIncome"] = user_context["monthlyIncome"] or float(profile_data.get("monthly_income") or 0)
                    user_context["fixedBills"] = request.fixedBills if request.fixedBills is not None else float(profile_data.get("fixed_bills") or 0)
                    user_context["savingsGoal"] = request.savingsGoal if request.savingsGoal is not None else float(profile_data.get("savings_goal") or 0)
                    logger.info(f"Fetched profile for user {user_id}: income={user_context['monthlyIncome']}")
            except Exception as e:
                logger.warning(f"Could not fetch profile: {e}")

        # Fetch additional transactions from database if not provided
        if not request.transactions or len(request.transactions) < 5:
            try:
                tx_response = supabase.table("transactions").select(
                    "merchant, amount, category"
                ).eq("user_id", user_id).order("created_at", desc=True).limit(20).execute()
                
                if tx_response.data:
                    request.transactions = request.transactions or []
                    for tx in tx_response.data:
                        if len(request.transactions) < 20:
                            request.transactions.append(tx)
                    logger.info(f"Fetched {len(tx_response.data)} transactions from database")
            except Exception as e:
                logger.debug(f"Could not fetch transactions from DB: {e}")

        # Add transaction summary for the AI
        tx_summary = ""
        if request.transactions and len(request.transactions) > 0:
            tx_summary = "\nRecent transactions (actual spending):\n" + "\n".join([
                f"- {t.get('merchant', 'Unknown')}: {t.get('amount', 0)} ({t.get('category', 'Other')})"
                for t in (request.transactions[-20:])  # last 20
            ])
            user_context["transactionSummary"] = tx_summary
            logger.info(f"Chat context prepared: {len(request.transactions)} transactions")

        advice = await chat_with_advisor(
            request.message,
            user_context,
            conversation_history=None
        )
        duration = round((time.time() - start) * 1000)
        return {
            "success": True,
            "advice": advice,
            "duration": duration
        }
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "advice": None
        }


@router.post("/health-tips")
async def get_health_tips_endpoint(
    request: HealthTipsRequest,
    user_id: str = Depends(get_user_id),
    supabase: Client = Depends(get_supabase)
):
    """
    Get personalized financial health improvement tips based on user spending.
    Accepts POST with transaction data for more dynamic tips.
    """
    try:
        transactions = request.transactions or []
        monthly_income = request.monthlyIncome or 0
        fixed_bills = request.fixedBills or 0
        savings_goal = request.savingsGoal or 0
        category_totals = request.categoryTotals or {}
        
        tips = []
        
        # If no transactions, return basic tips
        if not transactions:
            return {
                "success": True,
                "tips": [
                    "Start logging expenses to get personalized financial tips!",
                    "Track 10+ transactions to unlock detailed spending insights.",
                    "Set spending budgets by category to stay on track."
                ]
            }
        
        # Calculate total spent
        total_spent = sum(abs(t.get("amount", 0)) for t in transactions)
        
        # Tip 1: Income vs Spending ratio
        if monthly_income > 0:
            spending_ratio = (total_spent / monthly_income) * 100
            if spending_ratio > 90:
                tips.append(f"⚠️ You're spending {spending_ratio:.0f}% of your income. Try to reduce discretionary spending.")
            elif spending_ratio > 70:
                tips.append(f"You're spending {spending_ratio:.0f}% of your income. Consider setting aside more for savings.")
            else:
                tips.append(f"Good job! You're spending only {spending_ratio:.0f}% of your income.")
        
        # Tip 2: Highest spending category
        if category_totals:
            highest_category = max(category_totals.items(), key=lambda x: x[1])
            category_name = highest_category[0]
            category_amount = highest_category[1]
            tips.append(f"💰 Your highest spending is in {category_name}: ₦{category_amount:,.0f}. Look for ways to optimize this category.")
        
        # Tip 3: Savings goal progress
        if savings_goal > 0:
            monthly_after_bills = monthly_income - fixed_bills - total_spent
            if monthly_after_bills >= savings_goal:
                tips.append(f"✅ Great! You can save ₦{monthly_after_bills:,.0f} this month, exceeding your goal of ₦{savings_goal:,.0f}.")
            else:
                remaining_needed = savings_goal - monthly_after_bills
                tips.append(f"📊 You need to save ₦{remaining_needed:,.0f} more to reach your monthly savings goal of ₦{savings_goal:,.0f}.")
        
        # Tip 4: Transaction count insight
        transaction_count = len(transactions)
        if transaction_count < 5:
            tips.append("📝 Track at least 10-15 transactions for better spending pattern analysis.")
        elif transaction_count > 30:
            tips.append("📈 You have detailed transaction history! Review weekly for better insights.")
        
        # Tip 5: Category diversity
        if category_totals:
            num_categories = len(category_totals)
            if num_categories < 3:
                tips.append("🎯 Consider diversifying your spending across more categories for better budgeting.")
            else:
                tips.append(f"Good diversification across {num_categories} spending categories.")
        
        # Tip 6: General financial advice
        if monthly_income > 0 and fixed_bills > 0:
            bills_ratio = (fixed_bills / monthly_income) * 100
            if bills_ratio > 50:
                tips.append("🏠 Your fixed bills are high. Explore ways to reduce housing or utility costs.")
            else:
                tips.append(f"Your fixed bills are {bills_ratio:.0f}% of income - well managed!")
        
        return {
            "success": True,
            "tips": tips[:6]  # Return top 6 tips
        }
        
    except Exception as e:
        logger.error(f"Error generating health tips: {e}")
        # Return fallback tips instead of error
        return {
            "success": True,
            "tips": [
                "Keep tracking your expenses!",
                "Review your spending patterns weekly.",
                "Set up budget alerts for each category.",
                "Use the Telegram bot to log expenses on the go.",
                "Schedule monthly financial reviews."
            ]
        }


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
        # Don't use .single() as it fails with 0 rows
        response = supabase.table("user_profiles").select(
            "telegram_chat_id"
        ).eq("id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            telegram_chat_id = response.data[0].get("telegram_chat_id")
            return {
                "success": True,
                "telegram_chat_id": telegram_chat_id,
                "notifications_enabled": telegram_chat_id is not None
            }
        
        # Try with service role if not found
        logger.warning(f"Telegram settings not found with anon client for user {user_id}")
        from config import get_supabase_admin
        admin_supabase = get_supabase_admin()
        response = admin_supabase.table("user_profiles").select(
            "telegram_chat_id"
        ).eq("id", user_id).execute()
        
        if response.data and len(response.data) > 0:
            telegram_chat_id = response.data[0].get("telegram_chat_id")
            return {
                "success": True,
                "telegram_chat_id": telegram_chat_id,
                "notifications_enabled": telegram_chat_id is not None
            }
        
        # Return default if profile not found
        logger.warning(f"Telegram settings profile not found for user {user_id}, returning defaults")
        return {
            "success": True,
            "telegram_chat_id": None,
            "notifications_enabled": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching Telegram settings: {e}", exc_info=True)
        # Return safe default instead of error
        return {
            "success": True,
            "telegram_chat_id": None,
            "notifications_enabled": False
        }


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
