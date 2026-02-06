"""
Periodic task scheduler for sending notifications and health tips.
"""

import logging
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from config import get_supabase
from services.notification_service import (
    send_health_tip,
    send_weekly_summary,
    send_spending_insight
)
from services.financial_advice_service import (
    analyze_spending_patterns,
    generate_financial_advice,
    get_health_score
)

logger = logging.getLogger(__name__)

scheduler: Optional[AsyncIOScheduler] = None


def initialize_scheduler():
    """Initialize the APScheduler scheduler."""
    global scheduler
    try:
        scheduler = AsyncIOScheduler()
        
        # Schedule daily health tips at 9 AM
        scheduler.add_job(
            send_daily_health_tips,
            CronTrigger(hour=9, minute=0),
            id='daily_health_tips',
            name='Send daily health tips',
            replace_existing=True
        )
        
        # Schedule weekly summary every Monday at 10 AM
        scheduler.add_job(
            send_weekly_summaries,
            CronTrigger(day_of_week='mon', hour=10, minute=0),
            id='weekly_summary',
            name='Send weekly summaries',
            replace_existing=True
        )
        
        # Schedule budget check every day at 6 PM
        scheduler.add_job(
            check_budget_status,
            CronTrigger(hour=18, minute=0),
            id='budget_check',
            name='Check budget status',
            replace_existing=True
        )
        
        # Schedule monthly health assessment first day of month at 8 AM
        scheduler.add_job(
            send_monthly_assessment,
            CronTrigger(day=1, hour=8, minute=0),
            id='monthly_assessment',
            name='Send monthly assessment',
            replace_existing=True
        )
        
        scheduler.start()
        logger.info("Scheduler initialized and started")
        
    except Exception as e:
        logger.error(f"Error initializing scheduler: {e}")


async def send_daily_health_tips():
    """Send daily health tips to all users."""
    try:
        supabase = get_supabase()
        
        # Get all users
        users_response = supabase.table("user_profiles").select("id").execute()
        users = users_response.data or []
        
        health_tips = [
            "💡 Tip: Review your spending at least once a week to spot trends early.",
            "💰 Saving Tip: Try the 50/30/20 rule - 50% needs, 30% wants, 20% savings.",
            "📊 Monitoring: Set category budgets to stay in control of your spending.",
            "🎯 Goal Setting: Break your financial goals into monthly milestones.",
            "🚨 Alert: Turn on notifications to catch unusual spending patterns immediately.",
            "💎 Investment: Start an emergency fund with 3-6 months of expenses.",
            "📈 Growth: Track your spending trends to identify areas for improvement.",
            "🏦 Banking: Use separate accounts for bills, spending, and savings.",
            "🛍️ Shopping: Create a shopping list to avoid impulse purchases.",
            "📱 App Tip: Check your spending insights daily for better awareness."
        ]
        
        import random
        tip = random.choice(health_tips)
        
        for user in users:
            try:
                await send_health_tip(user["id"], tip, supabase)
            except Exception as e:
                logger.error(f"Error sending health tip to user {user['id']}: {e}")
        
        logger.info(f"Daily health tips sent to {len(users)} users")
        
    except Exception as e:
        logger.error(f"Error in send_daily_health_tips: {e}")


async def send_weekly_summaries():
    """Send weekly spending summaries to all users."""
    try:
        supabase = get_supabase()
        
        # Get all users
        users_response = supabase.table("user_profiles").select("id").execute()
        users = users_response.data or []
        
        for user in users:
            try:
                user_id = user["id"]
                
                # Get spending analysis
                analysis = await analyze_spending_patterns(user_id, supabase, months=1)
                
                total_spent = analysis.get("total_spent", 0)
                avg_daily = (total_spent / 7) if analysis.get("total_transactions", 0) > 0 else 0
                category_breakdown = analysis.get("category_breakdown", {})
                
                # Send summary
                await send_weekly_summary(
                    user_id,
                    total_spent,
                    avg_daily,
                    category_breakdown,
                    supabase
                )
            except Exception as e:
                logger.error(f"Error sending weekly summary to user {user['id']}: {e}")
        
        logger.info(f"Weekly summaries sent to {len(users)} users")
        
    except Exception as e:
        logger.error(f"Error in send_weekly_summaries: {e}")


async def check_budget_status():
    """Check budget status and send alerts if needed."""
    try:
        supabase = get_supabase()
        
        # Get all users with budget info
        users_response = supabase.table("user_profiles").select(
            "id, monthly_income, fixed_bills, savings_goal"
        ).execute()
        users = users_response.data or []
        
        from services.notification_service import send_budget_alert
        
        for user in users:
            try:
                user_id = user["id"]
                monthly_income = user.get("monthly_income", 0)
                fixed_bills = user.get("fixed_bills", 0)
                
                # Get spending analysis
                analysis = await analyze_spending_patterns(user_id, supabase, months=1)
                total_spent = analysis.get("total_spent", 0)
                
                available_for_discretionary = monthly_income - fixed_bills
                if available_for_discretionary > 0:
                    budget_percentage = (total_spent / available_for_discretionary) * 100
                    
                    # Send alert if over 70% of budget
                    if budget_percentage >= 70:
                        await send_budget_alert(
                            user_id,
                            total_spent,
                            available_for_discretionary,
                            "Discretionary",
                            supabase
                        )
            except Exception as e:
                logger.error(f"Error checking budget for user {user['id']}: {e}")
        
        logger.info(f"Budget status checked for {len(users)} users")
        
    except Exception as e:
        logger.error(f"Error in check_budget_status: {e}")


async def send_monthly_assessment():
    """Send monthly financial health assessment."""
    try:
        supabase = get_supabase()
        
        # Get all users
        users_response = supabase.table("user_profiles").select(
            "id, monthly_income, fixed_bills, savings_goal"
        ).execute()
        users = users_response.data or []
        
        for user in users:
            try:
                user_id = user["id"]
                monthly_income = user.get("monthly_income", 0)
                fixed_bills = user.get("fixed_bills", 0)
                savings_goal = user.get("savings_goal", 0)
                
                # Get health score
                health_data = await get_health_score(
                    user_id,
                    supabase,
                    monthly_income,
                    fixed_bills,
                    savings_goal
                )
                
                score = health_data.get("score", 0)
                grade = health_data.get("grade", "C")
                
                # Generate advice
                advice = await generate_financial_advice(
                    user_id,
                    supabase,
                    monthly_income,
                    fixed_bills,
                    savings_goal
                )
                
                # Send insight notification
                summary = advice.get("summary", "")
                recommendation = advice.get("recommendations", ["Maintain current spending habits"])[0]
                
                await send_spending_insight(
                    user_id,
                    f"Your monthly financial health score is {score}/100 ({grade}). {summary}",
                    recommendation,
                    supabase
                )
            except Exception as e:
                logger.error(f"Error sending monthly assessment to user {user['id']}: {e}")
        
        logger.info(f"Monthly assessments sent to {len(users)} users")
        
    except Exception as e:
        logger.error(f"Error in send_monthly_assessment: {e}")


def start_scheduler():
    """Start the scheduler if not already running."""
    global scheduler
    if scheduler and not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def stop_scheduler():
    """Stop the scheduler."""
    global scheduler
    if scheduler and scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the scheduler instance."""
    return scheduler
