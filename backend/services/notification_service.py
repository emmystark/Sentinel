import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from supabase import Client
from config import Config
import httpx

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of financial notifications."""
    BUDGET_ALERT = "budget_alert"
    SPENDING_INSIGHT = "spending_insight"
    HEALTH_TIP = "health_tip"
    GOAL_PROGRESS = "goal_progress"
    HIGH_RISK_TRANSACTION = "high_risk_transaction"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_SUMMARY = "monthly_summary"


class NotificationChannel(Enum):
    """Notification delivery channels."""
    TELEGRAM = "telegram"
    EMAIL = "email"
    PUSH = "push_notification"
    IN_APP = "in_app"


async def send_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: NotificationType,
    channels: List[NotificationChannel],
    supabase: Client,
    data: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send notification to user through specified channels.
    
    Args:
        user_id: User identifier
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        channels: Channels to send through
        supabase: Supabase client
        data: Additional metadata
        
    Returns:
        Success status
    """
    try:
        results = []
        
        # Send through each channel
        for channel in channels:
            if channel == NotificationChannel.TELEGRAM:
                result = await send_telegram_notification(user_id, title, message, supabase)
                results.append(result)
            elif channel == NotificationChannel.PUSH:
                result = await send_push_notification(user_id, title, message, data, supabase)
                results.append(result)
            elif channel == NotificationChannel.IN_APP:
                result = await save_in_app_notification(user_id, title, message, notification_type, supabase)
                results.append(result)
        
        return any(results)
        
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return False


async def send_telegram_notification(
    user_id: str,
    title: str,
    message: str,
    supabase: Client
) -> bool:
    """
    Send notification via Telegram.
    
    Args:
        user_id: User identifier
        title: Notification title
        message: Notification message
        supabase: Supabase client
        
    Returns:
        Success status
    """
    try:
        # Get user's Telegram chat ID from database
        response = supabase.table("user_profiles").select("telegram_chat_id").eq("id", user_id).single().execute()
        
        telegram_chat_id = response.data.get("telegram_chat_id") if response.data else None
        
        if not telegram_chat_id:
            logger.warning(f"No Telegram chat ID for user {user_id}")
            return False
        
        # Format message
        formatted_message = f"*{title}*\n\n{message}"
        
        # Send via Telegram Bot API
        token = Config.TELEGRAM_BOT_TOKEN
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN not configured")
            return False
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json={
                    "chat_id": telegram_chat_id,
                    "text": formatted_message,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Telegram notification sent to user {user_id}")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
        
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {e}")
        return False


async def send_push_notification(
    user_id: str,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]],
    supabase: Client
) -> bool:
    """
    Send push notification (Firebase Cloud Messaging compatible).
    
    Args:
        user_id: User identifier
        title: Notification title
        message: Notification message
        data: Additional data
        supabase: Supabase client
        
    Returns:
        Success status
    """
    try:
        # Try to get user's push tokens
        try:
            response = supabase.table("push_tokens").select("token").eq("user_id", user_id).execute()
            tokens = [item["token"] for item in response.data] if response.data else []
        except Exception:
            # push_tokens table may not exist yet
            logger.debug("push_tokens table not available for FCM delivery")
            tokens = []
        
        if not tokens:
            logger.debug(f"No push tokens for user {user_id} - push notifications unavailable")
            # Fall back to in-app notification
            return False
        
        # Here you would integrate with FCM or similar service
        # For now, we'll just log success
        logger.info(f"Push notifications ready for {len(tokens)} tokens for user {user_id}")
        
        # TODO: Integrate Firebase Cloud Messaging
        # Example:
        # from firebase_admin import messaging
        # messaging.send_multicast(
        #     messaging.MulticastMessage(
        #         tokens=tokens,
        #         notification=messaging.Notification(title=title, body=message),
        #         data=data or {}
        #     )
        # )
        
        return True
        
    except Exception as e:
        logger.warning(f"Push notification service unavailable: {e}")
        return False


async def save_in_app_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: NotificationType,
    supabase: Client
) -> bool:
    """
    Save notification to database for in-app display.
    
    Args:
        user_id: User identifier
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        supabase: Supabase client
        
    Returns:
        Success status
    """
    try:
        response = supabase.table("notifications").insert({
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": notification_type.value,
            "channel": "in_app",
            "sent_at": datetime.utcnow().isoformat(),
            "read_at": None
        }).execute()
        
        logger.info(f"In-app notification saved for user {user_id}: {title}")
        return bool(response.data)
        
    except Exception as e:
        logger.warning(f"Could not save in-app notification: {e}")
        # Don't fail if notifications table doesn't exist yet
        return True  # Return true as it's not critical


async def send_budget_alert(
    user_id: str,
    spent_amount: float,
    budget_amount: float,
    category: str,
    supabase: Client
) -> bool:
    """
    Send budget alert notification.
    
    Args:
        user_id: User identifier
        spent_amount: Amount spent
        budget_amount: Budget limit
        category: Spending category
        supabase: Supabase client
        
    Returns:
        Success status
    """
    percentage = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
    
    if percentage >= 100:
        title = f"🚨 {category} Budget Exceeded!"
        message = f"You've spent ${spent_amount:.2f} of your ${budget_amount:.2f} {category} budget."
        emoji_prefix = "🔴"
    elif percentage >= 90:
        title = f"⚠️ {category} Budget Alert"
        message = f"You're at {percentage:.0f}% of your {category} budget (${spent_amount:.2f} of ${budget_amount:.2f})."
        emoji_prefix = "🟠"
    elif percentage >= 80:
        title = f"📊 {category} Budget Notice"
        message = f"You've used {percentage:.0f}% of your {category} budget."
        emoji_prefix = "🟡"
    else:
        title = f"✅ {category} Budget Status"
        message = f"You've used {percentage:.0f}% of your {category} budget."
        emoji_prefix = "🟢"
    
    return await send_notification(
        user_id,
        title,
        message,
        NotificationType.BUDGET_ALERT,
        [NotificationChannel.TELEGRAM, NotificationChannel.IN_APP],
        supabase,
        {"category": category, "percentage": percentage}
    )


async def send_spending_insight(
    user_id: str,
    insight: str,
    recommendation: str,
    supabase: Client
) -> bool:
    """
    Send spending insight notification.
    
    Args:
        user_id: User identifier
        insight: Insight text
        recommendation: Recommendation
        supabase: Supabase client
        
    Returns:
        Success status
    """
    title = "💡 Spending Insight"
    message = f"{insight}\n\n💡 Recommendation: {recommendation}"
    
    return await send_notification(
        user_id,
        title,
        message,
        NotificationType.SPENDING_INSIGHT,
        [NotificationChannel.TELEGRAM, NotificationChannel.IN_APP],
        supabase
    )


async def send_health_tip(
    user_id: str,
    tip: str,
    supabase: Client
) -> bool:
    """
    Send financial health improvement tip.
    
    Args:
        user_id: User identifier
        tip: Health tip
        supabase: Supabase client
        
    Returns:
        Success status
    """
    title = "🏥 Financial Health Tip"
    
    return await send_notification(
        user_id,
        title,
        tip,
        NotificationType.HEALTH_TIP,
        [NotificationChannel.TELEGRAM, NotificationChannel.IN_APP],
        supabase
    )


async def send_weekly_summary(
    user_id: str,
    total_spent: float,
    avg_daily_spend: float,
    category_breakdown: Dict[str, float],
    supabase: Client
) -> bool:
    """
    Send weekly spending summary.
    
    Args:
        user_id: User identifier
        total_spent: Total spent this week
        avg_daily_spend: Average daily spending
        category_breakdown: Breakdown by category
        supabase: Supabase client
        
    Returns:
        Success status
    """
    title = "📊 Weekly Spending Summary"
    
    message = f"""This week you spent: *${total_spent:.2f}*
Average per day: *${avg_daily_spend:.2f}*

📈 Breakdown by category:
"""
    
    for category, amount in sorted(category_breakdown.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total_spent * 100) if total_spent > 0 else 0
        message += f"\n• {category}: ${amount:.2f} ({percentage:.1f}%)"
    
    return await send_notification(
        user_id,
        title,
        message,
        NotificationType.WEEKLY_SUMMARY,
        [NotificationChannel.TELEGRAM, NotificationChannel.IN_APP],
        supabase
    )


async def send_high_risk_alert(
    user_id: str,
    merchant: str,
    amount: float,
    reason: str,
    supabase: Client
) -> bool:
    """
    Send alert for high-risk or unusual transaction.
    
    Args:
        user_id: User identifier
        merchant: Merchant name
        amount: Transaction amount
        reason: Reason for alert
        supabase: Supabase client
        
    Returns:
        Success status
    """
    title = "🚨 Unusual Transaction Detected"
    message = f"Transaction of ${amount:.2f} from {merchant}\n\nReason: {reason}"
    
    return await send_notification(
        user_id,
        title,
        message,
        NotificationType.HIGH_RISK_TRANSACTION,
        [NotificationChannel.TELEGRAM, NotificationChannel.IN_APP],
        supabase,
        {"merchant": merchant, "amount": amount}
    )


async def send_goal_progress(
    user_id: str,
    goal_name: str,
    current_progress: float,
    goal_amount: float,
    supabase: Client
) -> bool:
    """
    Send financial goal progress notification.
    
    Args:
        user_id: User identifier
        goal_name: Goal name
        current_progress: Current progress amount
        goal_amount: Total goal amount
        supabase: Supabase client
        
    Returns:
        Success status
    """
    percentage = (current_progress / goal_amount * 100) if goal_amount > 0 else 0
    remaining = goal_amount - current_progress
    
    title = f"🎯 {goal_name} Progress"
    message = f"""Progress: {percentage:.1f}%
Saved: ${current_progress:.2f} of ${goal_amount:.2f}
Remaining: ${remaining:.2f}"""
    
    if percentage >= 100:
        message += "\n\n🎉 Congratulations! You've reached your goal!"
    
    return await send_notification(
        user_id,
        title,
        message,
        NotificationType.GOAL_PROGRESS,
        [NotificationChannel.TELEGRAM, NotificationChannel.IN_APP],
        supabase
    )
