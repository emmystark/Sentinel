import os
import logging
import base64
import json
from typing import Dict, Any, Optional
from groq import Groq
from config import Config

logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=Config.GROQ_API_KEY)

# Groq models
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # supports vision
CHAT_MODEL = "llama-3.3-70b-versatile"

# Categories for expense classification
CATEGORIES = [
    "Food", "Transport", "Entertainment", "Shopping",
    "Bills", "Utilities", "Health", "Education", "Other"
]


async def parse_receipt(image_source: str) -> Dict[str, Any]:
    try:
        # Prepare base64 image
        if image_source.startswith("data:image"):
            header, data = image_source.split(",", 1)
            media_type = header.split(";")[0].split(":")[1]  # e.g. image/jpeg
            image_data_b64 = data
        else:
            import urllib.request
            urllib.request.urlretrieve(image_source, "/tmp/receipt.jpg")
            with open("/tmp/receipt.jpg", "rb") as f:
                image_data_b64 = base64.b64encode(f.read()).decode("utf-8")
            media_type = "image/jpeg"

        extraction_prompt = """You are a receipt analyzer. Extract ALL information from this receipt and return ONLY valid JSON.
Return this exact JSON structure:
{
    "merchant": "store/restaurant name",
    "amount": total_amount_as_number,
    "currency": "NGN",
    "date": "YYYY-MM-DD or null",
    "items": ["item1", "item2"],
    "category": "Food/Transport/Entertainment/Shopping/Bills/Utilities/Health/Education/Other"
}
CRITICAL RULES:
- merchant: Extract the business name (required)
- amount: Extract the TOTAL (not subtotal). Must be a number, not null.
- currency: Detect from receipt symbols (₦/NGN → NGN, $ → USD, € → EUR, £ → GBP). Default: NGN
- date: Extract if visible, else null
- items: List what was purchased
- category: Pick the best matching category
Return ONLY JSON, no explanations or markdown."""

        response = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_data_b64}"
                            }
                        },
                        {"type": "text", "text": extraction_prompt}
                    ]
                }
            ],
            max_tokens=1000,
        )

        response_text = response.choices[0].message.content.strip()

        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_str = response_text[start:end]
            extracted_data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Could not parse JSON: {response_text}, error: {e}")
            extracted_data = {
                "merchant": "Unknown", "amount": 0, "currency": "NGN",
                "date": None, "items": [], "category": "Other"
            }

        extracted_data.setdefault("merchant", "Unknown Merchant")
        extracted_data.setdefault("amount", 0)
        extracted_data.setdefault("currency", "NGN")
        extracted_data.setdefault("date", None)
        extracted_data.setdefault("items", [])
        extracted_data.setdefault("category", "Other")

        try:
            extracted_data["amount"] = float(extracted_data.get("amount", 0))
        except (ValueError, TypeError):
            extracted_data["amount"] = 0

        if extracted_data.get("category") not in CATEGORIES:
            extracted_data["category"] = "Other"

        items = extracted_data.get("items", [])
        extracted_data["description"] = ", ".join(items[:3]) if items else extracted_data.get("merchant", "")

        return extracted_data

    except Exception as e:
        logger.error(f"Error parsing receipt: {e}")
        raise Exception(f"Failed to parse receipt: {str(e)}")


async def categorize_transaction(merchant: str, description: str = "") -> str:
    try:
        categories_str = ", ".join(CATEGORIES)
        prompt = f"""You are a transaction categorizer. Categorize this into ONE category ONLY.
Categories: {categories_str}
Merchant: {merchant}
Description: {description}
Rules:
- Return ONLY the category name
- No explanation
- If unsure, return 'Other'
Category:"""

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
        )

        category = response.choices[0].message.content.strip().strip('.').strip()

        if category not in CATEGORIES:
            for cat in CATEGORIES:
                if category.lower() == cat.lower():
                    return cat
            for cat in CATEGORIES:
                if cat.lower() in category.lower():
                    return cat
            return "Other"

        return category

    except Exception as e:
        logger.error(f"Error categorizing transaction: {e}")
        return "Other"


async def analyze_spending(
    transactions: list,
    monthly_income: float,
    fixed_bills: float,
    savings_goal: float
) -> Dict[str, Any]:
    try:
        transaction_summary = "\n".join([
            f"- {t.get('merchant', 'Unknown')}: ${t.get('amount', 0):.2f} ({t.get('category', 'Other')})"
            for t in transactions[-30:]
        ])

        analysis_prompt = f"""Analyze this spending data and provide actionable advice to reduce costs:

Monthly Income: ${monthly_income:.2f}
Fixed Bills: ${fixed_bills:.2f}
Savings Goal: ${savings_goal:.2f}

Recent Transactions:
{transaction_summary}

Please provide:
1. Spending pattern analysis
2. Categories where they're overspending
3. 3-5 specific, actionable recommendations to reduce costs
4. Estimated monthly savings potential
5. Risk alert if they might break their budget

Be specific and personalized based on their actual spending."""

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": analysis_prompt}],
            max_tokens=1500,
        )

        return {
            "analysis": response.choices[0].message.content,
            "recommendation_count": 5
        }

    except Exception as e:
        logger.error(f"Error analyzing spending: {e}")
        raise Exception(f"Failed to analyze spending: {str(e)}")


async def get_spending_advice(user_context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        prompt = f"""You are a financial advisor helping someone reduce their spending. Here's their context:
{json.dumps(user_context, indent=2)}

Provide warm, encouraging advice that:
- Acknowledges their financial situation
- Highlights positive spending habits
- Identifies 2-3 key areas to focus on
- Provides specific, practical tips
- Motivates them toward their savings goal

Be conversational and empathetic."""

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
        )

        return {
            "advice": response.choices[0].message.content,
            "generated_at": None
        }

    except Exception as e:
        logger.error(f"Error generating spending advice: {e}")
        raise Exception(f"Failed to generate advice: {str(e)}")


async def chat_with_advisor(
    user_message: str,
    user_context: Dict[str, Any],
    conversation_history: list = None
) -> str:
    try:
        tx_summary = user_context.get("transactionSummary", "")

        system_prompt = f"""You are Sentinel, a friendly and knowledgeable financial advisor.

User's Financial Profile:
- Monthly Income: ${user_context.get('monthlyIncome', 0):.2f}
- Fixed Bills (monthly expected): ${user_context.get('fixedBills', 0):.2f}
- Savings Goal: ${user_context.get('savingsGoal', 0):.2f}
- Actual Total Spent: ${user_context.get('totalSpent', 0):.2f}
{tx_summary}

Your role:
- Analyze spending based on ACTUAL uploaded transactions
- Compare actual vs expected (fixed bills + savings goal)
- Provide personalized, actionable advice
- Be encouraging and non-judgmental

Guidelines:
- Be conversational and warm
- Give specific, measurable suggestions
- Celebrate financial wins

IMPORTANT: Base advice on ACTUAL uploaded transactions vs expected monthly expenses."""

        # Build messages list
        messages = [{"role": "system", "content": system_prompt}]

        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            max_tokens=1000,
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise Exception(f"Chat failed: {str(e)}")