import os
import logging
import asyncio
from typing import Optional
# from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder

from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config
from services.gemini_service import get_spending_advice
import json


from telegram import BotCommand
from telegram import Update


from supabase import Client


logger = logging.getLogger(__name__)

# Telegram Bot Configuration
TELEGRAM_TOKEN = Config.TELEGRAM_BOT_TOKEN
TELEGRAM_WEBHOOK_URL = Config.TELEGRAM_WEBHOOK_URL

# Store for managing conversations
user_conversations = {}

async def send_telegram_message(username: str, message: str) -> bool:
    """
    Send a direct message to a Telegram user.
    Note: This requires the bot to know the user's ID.
    """
    try:
        if not TELEGRAM_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN not configured")
            return False
        
        # Note: Telegram Bot API doesn't support sending messages by username directly
        # You would need to store user IDs when they authenticate
        logger.info(f"Would send message to {username}: {message}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False

async def send_budget_alert(
    username: str,
    total_spent: float,
    available_budget: float,
    budget_percentage: float
) -> bool:
    """
    Send a budget alert to user via Telegram.
    """
    try:
        if not TELEGRAM_TOKEN:
            return False
        
        alert_message = f"""🚨 Budget Alert 🚨

You've spent ${total_spent:.2f} out of your ${available_budget:.2f} budget.

Budget used: {budget_percentage:.1f}%

"""
        
        if budget_percentage >= 100:
            alert_message += "⚠️ You've exceeded your budget!"
        elif budget_percentage >= 80:
            alert_message += "⚠️ You're approaching your budget limit. Be careful with remaining expenses."
        
        return await send_telegram_message(username, alert_message)
        
    except Exception as e:
        logger.error(f"Error sending budget alert: {e}")
        return False

async def send_spending_advice(
    username: str,
    user_id: str,
    monthly_income: float,
    fixed_bills: float,
    savings_goal: float,
    supabase: Client
) -> bool:
    """
    Send personalized spending advice via Telegram.
    """
    try:
        if not TELEGRAM_TOKEN:
            return False
        
        # Get recent transactions
        transactions_response = supabase.table("transactions").select(
            "merchant, amount, category, date"
        ).eq("user_id", user_id).order("date", desc=True).limit(50).execute()
        
        transactions = transactions_response.data or []
        total_spent = sum(t["amount"] for t in transactions) if transactions else 0
        
        # Build context
        user_context = {
            "monthly_income": monthly_income,
            "fixed_bills": fixed_bills,
            "savings_goal": savings_goal,
            "recent_transactions_count": len(transactions),
            "total_recent_spent": total_spent,
            "spending_by_category": {}
        }
        
        # Calculate category breakdown
        for t in transactions:
            cat = t.get("category", "Other")
            user_context["spending_by_category"][cat] = user_context["spending_by_category"].get(cat, 0) + t["amount"]
        
        # Get AI advice
        advice_data = await get_spending_advice(user_context)
        advice_text = advice_data.get("advice", "No advice available")
        
        # Format message
        message = f"""💡 Your Personalized Spending Advice 💡

{advice_text}

---
Your Profile:
• Monthly Income: ${monthly_income:.2f}
• Fixed Bills: ${fixed_bills:.2f}
• Savings Goal: ${savings_goal:.2f}
"""
        
        return await send_telegram_message(username, message)
        
    except Exception as e:
        logger.error(f"Error sending spending advice: {e}")
        return False

async def initialize_telegram_bot():
    """
    Initialize the Telegram bot with handlers and commands.
    """
    try:
        if not TELEGRAM_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN not configured")
            return None
        
        # Create bot instance
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Create application
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("budget", budget_command))
        application.add_handler(CommandHandler("advice", advice_command))
        
        # Add message handler for text messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Set bot commands
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help information"),
            BotCommand("budget", "Check your budget status"),
            BotCommand("advice", "Get spending advice"),
        ]
        await bot.set_my_commands(commands)
        
        logger.info("Telegram bot initialized successfully")
        return application
        
    except Exception as e:
        logger.error(f"Error initializing Telegram bot: {e}")
        return None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """👋 Welcome to Sentinel - Your AI Financial Smoke Detector!

I'm here to help you monitor your spending and reduce costs.

Use these commands:
• /budget - Check your current budget status
• /advice - Get personalized spending advice
• /help - Show all available commands
"""
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """📚 Available Commands:

/start - Start the bot
/budget - Get your budget status and alerts
/advice - Receive personalized spending advice
/help - Show this help message

💡 Features:
• Receipt scanning and expense extraction
• Automatic expense categorization
• Budget monitoring and alerts
• AI-powered spending advice
• Cost reduction recommendations
"""
    await update.message.reply_text(help_message)

async def budget_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /budget command"""
    user_id = update.effective_user.id
    
    message = """📊 Budget Status

To view your budget status, please connect your Telegram account in the app.

Once connected, you'll receive:
• Real-time budget alerts
• Spending category breakdowns
• Cost-saving recommendations
"""
    await update.message.reply_text(message)

async def advice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /advice command"""
    user_id = update.effective_user.id
    
    message = """💡 Spending Advice

Connect your account to receive personalized spending advice based on:
• Your income and expenses
• Your spending habits
• Your savings goals

The AI will identify areas where you can save money and provide specific recommendations.
"""
    await update.message.reply_text(message)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    user_message = update.message.text
    user_id = update.effective_user.id
    
    # Simple echo for now - can be expanded with more NLP
    response = f"""Thanks for your message: "{user_message}"

I'm currently in beta. For now, please use the available commands:
/budget - Check budget
/advice - Get advice
/help - Show help
"""
    await update.message.reply_text(response)

async def setup_telegram_webhook(webhook_url: str):
    """
    Setup webhook for Telegram bot.
    Call this if you prefer webhooks over polling.
    """
    try:
        if not TELEGRAM_TOKEN:
            logger.warning("TELEGRAM_BOT_TOKEN not configured")
            return False
        
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.set_webhook(url=webhook_url)
        logger.info(f"Telegram webhook set to {webhook_url}")
        return True
        
    except Exception as e:
        logger.error(f"Error setting up webhook: {e}")
        return False
