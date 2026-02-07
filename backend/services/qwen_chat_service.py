## Qwen Chat Service - Financial Advisor using HuggingFace Qwen Model
## This service replaces Gemini for all text generation and financial advice.

import os
import logging
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
from datetime import datetime

logger = logging.getLogger(__name__)

# HuggingFace API Configuration
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN")
if not HF_TOKEN:
    logger.warning("HF_TOKEN/HUGGINGFACE_API_TOKEN not configured")

# Initialize OpenAI client pointing to HuggingFace router
try:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )
except Exception as e:
    logger.warning(f"Failed to initialize HF client: {e}")
    client = None

# Qwen model identifier
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct:together"

# Categories for expense classification
CATEGORIES = [
    "Food", "Transport", "Entertainment", "Shopping",
    "Bills", "Utilities", "Health", "Education", "Other"
]

async def chat_with_advisor(
    user_message: str,
    user_context: Dict[str, Any],
    conversation_history: list = None
) -> str:
    """
    Chat with financial advisor using Qwen 2.5 7B model.
    Provides personalized financial advice based on spending patterns.
    Args:
        user_message: User's question or message
        user_context: User's financial context (spending, income, goals)
        conversation_history: Previous messages for context
    Returns:
        Advisor's response
    """
    try:
        if not client:
            logger.error("HuggingFace client not initialized - HF_TOKEN missing")
            return "❌ AI service not configured. Please set HF_TOKEN environment variable."

        # Build conversation context
        history_text = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = "User" if msg.get("role") == "user" else "Advisor"
                history_text += f"{role}: {msg.get('content', '')}\n"

        tx_summary = user_context.get("transactionSummary", "")

        # System prompt for financial advisor (refined for brevity)
        system_prompt = f"""You are Sentinel, a friendly financial advisor AI.
User's Financial Profile:
- Monthly Income: ₦{user_context.get('monthlyIncome', 0):,.0f}
- Fixed Bills (monthly): ₦{user_context.get('fixedBills', 0):,.0f}
- Savings Goal: ₦{user_context.get('savingsGoal', 0):,.0f}
- Total Spent: ₦{user_context.get('totalSpent', 0):,.0f}
Recent Transactions:
{tx_summary if tx_summary else "No transactions recorded yet."}
Your Role:
- Analyze spending based on ACTUAL transactions.
- Compare spending vs budget.
- Give brief, actionable advice.
- Be encouraging.
Guidelines:
- Be straight to the point.
- Use 1-2 sentences max for advice.
- Base on real data only.
- No fluff; concise responses under 100 words.
Previous conversation:
{history_text}
Respond briefly to: {user_message}"""

        # Call Qwen API with text generation (reduced max_tokens for conciseness)
        api_payload = {
            "model": MODEL_ID,
            "temperature": 0.7,
            "max_tokens": 150,  # Reduced for shorter responses
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }

        logger.info(f"Calling Qwen for chat: {user_message[:50]}...")
        completion = client.chat.completions.create(**api_payload)
        response_text = completion.choices[0].message.content
        logger.info(f"Qwen response received: {len(response_text)} chars")
        return response_text

    except Exception as e:
        logger.error(f"Error in Qwen chat: {e}", exc_info=True)
        return f"⚠️ Error: {str(e)[:100]}. Try again."

async def categorize_transaction(merchant: str, description: str) -> str:
    """
    Categorize a transaction based on merchant and description using Qwen.
    Args:
        merchant: Merchant/store name
        description: Transaction description
    Returns:
        Category from CATEGORIES list
    """
    try:
        if not client:
            logger.warning("HuggingFace client not initialized")
            return "Other"

        categorization_prompt = f"""Classify transaction to ONE category.
Merchant: {merchant}
Description: {description}
Categories: {", ".join(CATEGORIES)}
Respond with ONLY the category name."""

        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": categorization_prompt}],
            max_tokens=10,  # Reduced for brevity
            temperature=0  # Deterministic
        )

        category = completion.choices[0].message.content.strip()
        if category not in CATEGORIES:
            logger.warning(f"Invalid category '{category}', defaulting to 'Other'")
            return "Other"
        return category

    except Exception as e:
        logger.error(f"Error categorizing transaction: {e}")
        return "Other"

async def analyze_spending_pattern(
    transactions: List[Dict[str, Any]],
    monthly_income: float,
    fixed_bills: float,
    savings_goal: float
) -> Dict[str, Any]:
    """
    Analyze spending patterns and provide insights using Qwen.
    Args:
        transactions: List of user transactions
        monthly_income: User's monthly income
        fixed_bills: User's fixed monthly bills
        savings_goal: User's monthly savings goal
    Returns:
        Dict with insights, risks, and recommendations
    """
    try:
        if not client or not transactions:
            return {
                "insights": ["Log more transactions for analysis"],
                "risk_level": "unknown",
                "recommendations": []
            }

        # Calculate metrics
        total_spent = sum(float(t.get("amount", 0)) for t in transactions)
        available_after_bills = monthly_income - fixed_bills - savings_goal
        overspend = total_spent - available_after_bills

        # Build transaction summary (limited to top 10 for brevity)
        transactions_text = "\n".join([
            f"- {t.get('merchant', 'Unknown')}: ₦{t.get('amount', 0):,.0f} ({t.get('category', 'Other')})"
            for t in transactions[:10]
        ])

        analysis_prompt = f"""Analyze briefly:
Income: ₦{monthly_income:,.0f}
Bills: ₦{fixed_bills:,.0f}
Savings Goal: ₦{savings_goal:,.0f}
Available: ₦{available_after_bills:,.0f}
Spent: ₦{total_spent:,.0f}
Overspent: ₦{overspend:,.0f}
Transactions:
{transactions_text}
Respond with JSON ONLY:
{{
    "insights": ["short insight 1", "short insight 2"],
    "risk_level": "low|medium|high",
    "recommendations": ["rec 1", "rec 2"]
}}"""

        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=200,  # Reduced for conciseness
            temperature=0
        )

        response_text = completion.choices[0].message.content.strip()
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                analysis = json.loads(json_str)
                return analysis
        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse JSON: {e}")
            return {
                "insights": ["Review spending"],
                "risk_level": "medium" if overspend > 0 else "low",
                "recommendations": ["Track expenses"]
            }

    except Exception as e:
        logger.error(f"Error analyzing spending: {e}")
        return {
            "insights": ["Analysis failed"],
            "risk_level": "unknown",
            "recommendations": []
        }

def _get_default_response() -> str:
    """Return default response when something fails"""
    return "Technical issue. Try again. 💭"