import os
import logging
import base64
import json
from typing import Dict, Any, Optional
from PIL import Image
from io import BytesIO
from config import Config
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)

# Gemini models
VISION_MODEL = "gemini-2.0-flash"
CHAT_MODEL = "gemini-2.5-flash"

# Categories for expense classification
CATEGORIES = [
    "Food", "Transport", "Entertainment", "Shopping", 
    "Bills", "Utilities", "Health", "Education", "Other"
]

async def parse_receipt(image_source: str) -> Dict[str, Any]:
    """
    Parse receipt image and extract transaction details using Gemini Vision 1.5 Flash.
    
    Args:
        image_source: Either base64 encoded image or URL
        
    Returns:
        Dict with merchant, amount, date, items, category, description
    """
    try:
        model = genai.GenerativeModel(VISION_MODEL)
        
        # Prepare image data
        if image_source.startswith("data:image"):
            # Handle base64 encoded image
            header, data = image_source.split(",", 1)
            image_data = base64.b64decode(data)
            image = Image.open(BytesIO(image_data))
        else:
            # Handle URL
            import urllib.request
            urllib.request.urlretrieve(image_source, "/tmp/receipt.jpg")
            image = Image.open("/tmp/receipt.jpg")
        
        # Create detailed prompt for receipt parsing with better instructions
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
1. merchant: Extract the business name (required)
2. amount: Extract the TOTAL (not subtotal). Must be a number, not null.
3. currency: IMPORTANT - Detect currency from receipt:
   - Look for: ₦, Naira, NGN, N (Nigerian currency symbol/text) → Use "NGN"
   - Look for: $, USD, US Dollar → Use "USD"
   - Look for: €, EUR, Euro → Use "EUR"
   - Look for: £, GBP, British Pound → Use "GBP"
   - Look for: ¥, CNY/JPY → Use "CNY" or "JPY"
   - If no currency symbol found → DEFAULT TO "NGN"
   - Only use 3-letter ISO 4217 currency codes
4. date: Extract date if visible, else null
5. items: List what was purchased
6. category: Based on merchant type, pick the best matching category

Return ONLY JSON, no explanations or markdown."""
        
        response = model.generate_content([extraction_prompt, image])
        
        # Parse response
        response_text = response.text.strip()
        
        # Extract JSON from response
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            json_str = response_text[start:end]
            extracted_data = json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Could not parse JSON from response: {response_text}, error: {e}")
            extracted_data = {
                "merchant": "Unknown",
                "amount": 0,
                "currency": "NGN",
                "date": None,
                "items": [],
                "category": "Other"
            }
        
        # Validate and ensure required fields exist
        extracted_data.setdefault("merchant", "Unknown Merchant")
        extracted_data.setdefault("amount", 0)
        extracted_data.setdefault("currency", "NGN")  # Default to Nigerian Naira
        extracted_data.setdefault("date", None)
        extracted_data.setdefault("items", [])
        extracted_data.setdefault("category", "Other")
        
        # Ensure amount is a number
        try:
            amount = float(extracted_data.get("amount", 0))
            extracted_data["amount"] = amount
        except (ValueError, TypeError):
            extracted_data["amount"] = 0
        
        # Ensure category is valid
        if extracted_data.get("category") not in CATEGORIES:
            extracted_data["category"] = "Other"
        
        # Create description from items
        items = extracted_data.get("items", [])
        description = ", ".join(items[:3]) if items else extracted_data.get("merchant", "")
        extracted_data["description"] = description
        
        return extracted_data
        
    except Exception as e:
        logger.error(f"Error parsing receipt: {e}")
        raise Exception(f"Failed to parse receipt: {str(e)}")

async def categorize_transaction(merchant: str, description: str = "") -> str:
    """
    Categorize a transaction using Gemini 1.5 Flash.
    
    Args:
        merchant: Merchant/store name
        description: Transaction description
        
    Returns:
        Category name
    """
    try:
        model = genai.GenerativeModel(CHAT_MODEL)
        
        categories_str = ", ".join(CATEGORIES)
        prompt = f"""You are a transaction categorizer. Categorize this into ONE category ONLY.

Categories: {categories_str}

Merchant: {merchant}
Description: {description}

Rules:
- Return ONLY the category name
- No explanation
- If unsure, return 'Other'
- Pick the most specific match

Category:"""
        
        response = model.generate_content(prompt)
        category = response.text.strip().strip('.').strip()
        
        # Validate category
        if category not in CATEGORIES:
            # Try case-insensitive match
            for cat in CATEGORIES:
                if category.lower() == cat.lower():
                    return cat
            # Try partial match
            category_lower = category.lower()
            for cat in CATEGORIES:
                if cat.lower() in category_lower:
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
    """
    Analyze spending patterns and provide advice using Gemini.
    
    Args:
        transactions: List of transaction objects
        monthly_income: User's monthly income
        fixed_bills: User's fixed monthly bills
        savings_goal: User's savings goal
        
    Returns:
        Analysis with patterns, alerts, and recommendations
    """
    try:
        model = genai.GenerativeModel(CHAT_MODEL)
        
        # Format transactions for analysis
        transaction_summary = "\n".join([
            f"- {t.get('merchant', 'Unknown')}: ${t.get('amount', 0):.2f} ({t.get('category', 'Other')})"
            for t in transactions[-30:]  # Last 30 days
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
        
        response = model.generate_content(analysis_prompt)
        
        return {
            "analysis": response.text,
            "recommendation_count": 5
        }
        
    except Exception as e:
        logger.error(f"Error analyzing spending: {e}")
        raise Exception(f"Failed to analyze spending: {str(e)}")

async def get_spending_advice(
    user_context: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Get personalized spending advice based on user's financial context.
    
    Args:
        user_context: Dictionary with spending data, income, goals
        
    Returns:
        Personalized advice from AI
    """
    try:
        model = genai.GenerativeModel(CHAT_MODEL)
        
        prompt = f"""You are a financial advisor helping someone reduce their spending. Here's their context:

{json.dumps(user_context, indent=2)}

Provide warm, encouraging advice that:
1. Acknowledges their financial situation
2. Highlights positive spending habits
3. Identifies 2-3 key areas to focus on
4. Provides specific, practical tips
5. Motivates them toward their savings goal

Be conversational and empathetic."""
        
        response = model.generate_content(prompt)
        
        return {
            "advice": response.text,
            "generated_at": None  # Will be set by caller
        }
        
    except Exception as e:
        logger.error(f"Error generating spending advice: {e}")
        raise Exception(f"Failed to generate advice: {str(e)}")
async def chat_with_advisor(
    user_message: str,
    user_context: Dict[str, Any],
    conversation_history: list = None
) -> str:
    """
    Chat with financial advisor using Gemini 1.5 Flash.
    
    Args:
        user_message: User's question or message
        user_context: User's financial context (spending, income, goals)
        conversation_history: Previous messages for context
        
    Returns:
        Advisor's response
    """
    try:
        model = genai.GenerativeModel(CHAT_MODEL)
        
        # Build conversation context
        history_text = ""
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages for context
                role = "User" if msg.get("role") == "user" else "Advisor"
                history_text += f"{role}: {msg.get('content', '')}\n"
        
        tx_summary = user_context.get("transactionSummary", "")
        system_prompt = f"""You are Sentinel, a friendly and knowledgeable financial advisor.
        
User's Financial Profile (expected budget):
- Monthly Income: ${user_context.get('monthlyIncome', 0):.2f}
- Fixed Bills (monthly expected): ${user_context.get('fixedBills', 0):.2f}
- Savings Goal: ${user_context.get('savingsGoal', 0):.2f}
- Actual Total Spent (from uploaded transactions): ${user_context.get('totalSpent', 0):.2f}
{tx_summary}

Your role:
1. Analyze their spending patterns based on ACTUAL uploaded transactions
2. Compare actual spending vs expected (fixed bills + savings goal)
3. Provide personalized, actionable advice
4. Be encouraging and non-judgmental
5. Help them reach their financial goals

Guidelines:
- Be conversational and warm
- Give specific, measurable suggestions using their real transaction data
- Compare actual spending to their budget (fixed bills, savings goal)
- Celebrate their financial wins

Previous conversation:
{history_text}

IMPORTANT: Base advice on ACTUAL uploaded transactions vs their expected monthly expenses. Be specific.

Now respond to the user's message. Keep responses focused and helpful."""

        full_prompt = f"{system_prompt}\n\nUser: {user_message}"
        
        response = model.generate_content(full_prompt)
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise Exception(f"Chat failed: {str(e)}")