"""
Groq Chat Service - Financial Advisor using Groq LLM
Replaces HuggingFace/Qwen for all text generation and financial advice.
"""

import os
import logging
import json
from typing import Dict, Any, List
from groq import Groq


logger = logging.getLogger(__name__)

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not configured")

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    logger.warning(f"Failed to initialize Groq client: {e}")
    client = None

CHAT_MODEL = "llama-3.3-70b-versatile"

CATEGORIES = [
    "Food", "Transport", "Entertainment", "Shopping",
    "Bills", "Utilities", "Health", "Education", "Other"
]


async def chat_with_advisor(
    user_message: str,
    user_context: Dict[str, Any],
    conversation_history: list = None
) -> str:
    try:
        if not client:
            return "AI service not configured. Please set GROQ_API_KEY environment variable."

        tx_summary = user_context.get("transactionSummary", "")

        system_prompt = f"""You are Sentinel, a friendly financial advisor AI.
User's Financial Profile:
- Monthly Income: ₦{user_context.get('monthlyIncome', 0):,.0f}
- Fixed Bills (monthly): ₦{user_context.get('fixedBills', 0):,.0f}
- Savings Goal: ₦{user_context.get('savingsGoal', 0):,.0f}
- Total Spent: ₦{user_context.get('totalSpent', 0):,.0f}
Recent Transactions:
{tx_summary if tx_summary else "No transactions recorded yet."}
Guidelines:
- Be straight to the point.
- Keep responses under 100 words.
- Base advice on real transaction data only.
- Be encouraging and non-judgmental."""

        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": user_message})

        logger.info(f"Calling Groq for chat: {user_message[:50]}...")
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )

        response_text = response.choices[0].message.content
        logger.info(f"Groq response received: {len(response_text)} chars")
        return response_text

    except Exception as e:
        logger.error(f"Error in Groq chat: {e}", exc_info=True)
        return f"Error: {str(e)[:100]}. Try again."


async def categorize_transaction(merchant: str, description: str) -> str:
    try:
        if not client:
            return "Other"

        prompt = f"""Classify transaction to ONE category.
Merchant: {merchant}
Description: {description}
Categories: {", ".join(CATEGORIES)}
Respond with ONLY the category name."""

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            temperature=0,
        )

        category = response.choices[0].message.content.strip()
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
    try:
        if not client or not transactions:
            return {
                "insights": ["Log more transactions for analysis"],
                "risk_level": "unknown",
                "recommendations": []
            }

        total_spent = sum(float(t.get("amount", 0)) for t in transactions)
        available_after_bills = monthly_income - fixed_bills - savings_goal
        overspend = total_spent - available_after_bills

        transactions_text = "\n".join([
            f"- {t.get('merchant', 'Unknown')}: ₦{t.get('amount', 0):,.0f} ({t.get('category', 'Other')})"
            for t in transactions[:10]
        ])

        prompt = f"""Analyze briefly:
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

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0,
        )

        response_text = response.choices[0].message.content.strip()
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                analysis = json.loads(response_text[start:end])
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