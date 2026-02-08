import os
import logging
import base64
import json
from typing import Dict, Any, Optional
from PIL import Image
from io import BytesIO
import requests
from config import Config
from openai import OpenAI
import pytesseract

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

# Qwen model identifier (TEXT-ONLY - NO VISION SUPPORT!)
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct:together"

# OCR module - extract text from images since Qwen doesn't support vision
def extract_text_from_image(image_source: str) -> str:
    """
    Extract text from image using Tesseract OCR.
    Supports base64 encoded images and URLs.
    """
    try:
        # Handle different image formats
        if image_source.startswith('http'):
            # Download image from URL
            logger.info(f"Downloading image from URL: {image_source[:50]}...")
            response = requests.get(image_source, timeout=10)
            image = Image.open(BytesIO(response.content))
        elif 'data:' in image_source:
            # Base64 with data URI
            base64_str = image_source.split(',')[1]
            image_data = base64.b64decode(base64_str)
            image = Image.open(BytesIO(image_data))
        else:
            # Raw base64
            image_data = base64.b64decode(image_source)
            image = Image.open(BytesIO(image_data))
        
        # Extract text using Tesseract OCR
        logger.info("Extracting text from image using OCR...")
        extracted_text = pytesseract.image_to_string(image)
        logger.info(f"OCR extracted {len(extracted_text)} characters")
        return extracted_text if extracted_text.strip() else ""
        
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return ""


# Categories for expense classification
CATEGORIES = [
    "Food", "Transport", "Entertainment", "Shopping", 
    "Bills", "Utilities", "Health", "Education", "Other"
]


async def parse_receipt_with_qwen(image_source: str) -> Dict[str, Any]:
    """
    Parse receipt image using OCR + Qwen text analysis.
    
    IMPORTANT: Qwen2.5-7B on HuggingFace router does NOT support vision/image inputs.
    Solution: Extract text using Tesseract OCR, then analyze the text with Qwen.
    """
    try:
        if not client:
            logger.error("HuggingFace client not initialized")
            return _get_default_extraction()
        
        # Validate image source
        if not image_source:
            logger.error("No image source provided")
            return _get_default_extraction()
        
        logger.info(f"Processing receipt image, source type: {'url' if image_source.startswith('http') else 'base64'}")
        
        # Step 1: Extract text from image using OCR
        ocr_text = extract_text_from_image(image_source)
        
        if not ocr_text:
            logger.warning("OCR extraction returned empty text")
            return _get_default_extraction()
        
        logger.info(f"OCR extracted text ({len(ocr_text)} chars): {ocr_text[:200]}...")
        
        # Step 2: Build prompt for Qwen to structure the OCR text  
        extraction_prompt = f"""CRITICAL: You are a receipt data extraction system. Analyze the receipt text below.

YOUR TASK: Extract receipt information and respond with ONLY valid JSON. Nothing else.

OCR TEXT FROM RECEIPT:
{ocr_text}

STRICT JSON OUTPUT FORMAT - RESPOND ONLY WITH THIS EXACT STRUCTURE:
{{
  "merchant": "extracted business/store name - MUST NOT BE EMPTY",
  "amount": extracted_total_amount_as_positive_number,
  "currency": "currency code like USD, EUR, GBP",
  "date": "YYYY-MM-DD format or null if not visible",
  "items": ["item name", "item name"],
  "category": "Food OR Transport OR Entertainment OR Shopping OR Bills OR Utilities OR Health OR Education OR Other",
  "description": "brief description of purchase"
}}

EXTRACTION RULES:
1. merchant: Business/store name MUST be identified - cannot be empty or 'Unknown'
2. amount: TOTAL transaction amount - must be a positive number, not text
3. currency: Auto-detect currency (USD, EUR, GBP, etc.)
4. date: Extract as YYYY-MM-DD if visible, else null (not string "null")
5. items: List of items purchased - provide at least main items
6. category: Must be exactly one of the listed categories based on merchant type
7. description: One sentence summary of the purchase

CRITICAL INSTRUCTIONS:
- Return ONLY valid JSON - no markdown, no code blocks, no explanations
- Do not include backticks or json language tags
- Ensure all string values are properly quoted
- Ensure amount is a number not a string
- If date not visible, use null (not "null")
- Items array must contain strings
- Respond with ONLY the JSON object"""

        try:
            # Step 3: Call Qwen API with extracted text (NO images - text only!)
            api_payload = {
                "model": MODEL_ID,
                "temperature": 0,  # CRITICAL: Use 0 for deterministic JSON output
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": extraction_prompt  # TEXT ONLY - no image_url!
                    }
                ]
            }
            
            logger.info("Calling Qwen API with OCR-extracted text...")
            completion = client.chat.completions.create(**api_payload)
            
            response_text = completion.choices[0].message.content
            logger.info(f"Qwen response received: {response_text[:300]}...")
            
            # Step 4: Parse Qwen's JSON response
            extracted_data = _parse_json_response(response_text)
            
            if extracted_data:
                # Validate and ensure required fields
                extracted_data = _validate_extraction(extracted_data)
                
                # Ensure items are converted to description
                items = extracted_data.get("items", [])
                if items and isinstance(items, list):
                    extracted_data["description"] = ", ".join(str(item) for item in items if item)
                
                logger.info(f"Receipt parsed successfully: merchant='{extracted_data.get('merchant')}', amount={extracted_data.get('amount')}, category={extracted_data.get('category')}")
                return extracted_data
            else:
                logger.warning("Failed to parse JSON from Qwen response")
                return _get_default_extraction()
        
        except Exception as e:
            logger.error(f"Error calling Qwen API: {e}", exc_info=True)
            return _get_default_extraction()
        
    except Exception as e:
        logger.error(f"Error parsing receipt with Qwen: {e}")
        return _get_default_extraction()


async def analyze_transaction_with_qwen(
    merchant: str,
    amount: float,
    category: str,
    description: str
) -> Dict[str, Any]:
    """
    Analyze a transaction and provide insights using Qwen.
    
    Args:
        merchant: Merchant name
        amount: Transaction amount
        category: Transaction category
        description: Transaction description
        
    Returns:
        Analysis with insights and tips
    """
    try:
        if not client:
            logger.error("HuggingFace client not initialized")
            return _get_default_analysis()
        
        # Strict JSON prompt for transaction analysis
        analysis_prompt = f"""CRITICAL: You are a financial transaction analyzer. Respond with ONLY valid JSON.

ANALYZE THIS TRANSACTION:
Merchant: {merchant}
Amount: ${amount:.2f}
Category: {category}
Description: {description}

RESPOND WITH ONLY THIS JSON STRUCTURE:
{{
    "insight": "brief insight about this transaction",
    "risk_level": "low OR medium OR high",
    "recommendation": "one sentence recommendation",
    "is_unusual": true OR false
}}

CRITICAL INSTRUCTIONS:
- Return ONLY valid JSON - no markdown or explanations
- Ensure risk_level is exactly one of: low, medium, high
- Ensure is_unusual is a boolean true or false (not string)
- No code blocks or backticks"""
        
        try:
            completion = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                max_tokens=200,
                temperature=0  # Deterministic JSON output
            )
            
            response_text = completion.choices[0].message.content
            logger.debug(f"Transaction analysis response: {response_text[:200]}")
            
            # Parse JSON response
            analysis = _parse_json_response(response_text)
            if analysis:
                return analysis
            else:
                logger.warning("Failed to parse transaction analysis JSON")
                return _get_default_analysis()
        
        except Exception as e:
            logger.error(f"Error calling Qwen API for transaction analysis: {e}")
            return _get_default_analysis()
        
    except Exception as e:
        logger.error(f"Error analyzing transaction with Qwen: {e}")
        return _get_default_analysis()


def _parse_json_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Robustly parse JSON from model response, handling various text formats.
    
    Args:
        response_text: Raw text response from model
        
    Returns:
        Parsed JSON dict or None if parsing fails
    """
    if not response_text or not isinstance(response_text, str):
        logger.error(f"Invalid response text: {type(response_text)}")
        return None
    
    # Clean the response
    clean_text = response_text.strip()
    logger.debug(f"Parsing response: {clean_text[:500]}")
    
    # Strategy 1: Try to parse as-is (response might already be pure JSON)
    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Extract JSON object from text (look for {...})
    try:
        start = clean_text.find("{")
        end = clean_text.rfind("}") + 1
        
        if start != -1 and end > start and end - start > 10:  # Sanity check
            json_str = clean_text[start:end]
            logger.debug(f"Extracted JSON substring: {json_str[:200]}...")
            parsed = json.loads(json_str)
            logger.info("Successfully parsed JSON from model response")
            return parsed
    except json.JSONDecodeError as e:
        logger.warning(f"JSON parsing failed for extracted substring: {e}")
    
    # Strategy 3: Try common replacements for common model errors
    try:
        # Replace common mistakes
        cleaned = clean_text.replace("'", '"')  # Single quotes to double
        cleaned = cleaned.replace("```json", "")  # Remove markdown
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.replace("\n", " ")  # Remove newlines
        
        # Try parsing again
        parsed = json.loads(cleaned)
        logger.info("Successfully parsed JSON after cleanup")
        return parsed
    except json.JSONDecodeError as e:
        logger.warning(f"Cleanup parsing failed: {e}")
    
    # Strategy 4: Manual JSON reconstruction from response
    try:
        # If response contains structured data, try to extract it manually
        if "merchant" in clean_text.lower():
            logger.debug("Attempting manual JSON reconstruction")
            # This is a fallback - log the full response for debugging
            logger.error(f"Unable to parse JSON. Full response:\n{clean_text}")
    except Exception as e:
        logger.error(f"Manual reconstruction failed: {e}")
    
    logger.error(f"All JSON parsing strategies failed. Response: {clean_text[:500]}")
    return None


def _validate_extraction(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and normalize extracted receipt data.
    Ensures all fields meet requirements and are proper types.
    
    Args:
        data: Raw extracted data from Qwen
        
    Returns:
        Validated and normalized data
    """
    # Ensure minimum required fields
    if not isinstance(data, dict):
        logger.error(f"Invalid data type: {type(data)}")
        return _get_default_extraction()
    
    # Validate and normalize each field
    merchant = str(data.get("merchant", "")).strip()
    if not merchant or merchant.lower() in ["unknown merchant", "merchant", "n/a", "none", ""]:
        logger.warning(f"Invalid merchant: '{merchant}'")
        merchant = "Unknown Merchant"
    data["merchant"] = merchant[:100]
    
    # Validate amount
    try:
        amount = float(data.get("amount", 0))
        if amount < 0:
            amount = 0
        data["amount"] = round(amount, 2)
    except (ValueError, TypeError):
        logger.warning(f"Invalid amount: {data.get('amount')}")
        data["amount"] = 0
    
    # Validate currency
    data["currency"] = str(data.get("currency", "USD"))[:3].upper()
    if len(data["currency"]) != 3:
        data["currency"] = "USD"
    
    # Validate date (can be null or string)
    date_val = data.get("date")
    if date_val is None or (isinstance(date_val, str) and date_val.lower() in ["null", "none", "", "n/a"]):
        data["date"] = None
    else:
        data["date"] = str(date_val)[:10] if date_val else None
    
    # Validate items
    items = data.get("items", [])
    if not isinstance(items, list):
        items = [str(items)] if items else []
    data["items"] = [str(item)[:50] for item in items if item][:20]  # Max 20 items
    
    # Validate category
    category = str(data.get("category", "Other")).strip()
    if category not in CATEGORIES:
        # Try to find closest match
        category_lower = category.lower()
        for cat in CATEGORIES:
            if cat.lower() in category_lower or category_lower in cat.lower():
                category = cat
                break
        if category not in CATEGORIES:
            category = "Other"
    data["category"] = category
    
    # Validate description
    description = str(data.get("description", "")).strip()
    data["description"] = description[:500]
    
    # Ensure all required fields exist
    data.setdefault("merchant", "Unknown Merchant")
    data.setdefault("amount", 0)
    data.setdefault("currency", "USD")
    data.setdefault("date", None)
    data.setdefault("items", [])
    data.setdefault("category", "Other")
    data.setdefault("description", "")
    
    return data


def _get_default_extraction() -> Dict[str, Any]:
    """Return default extraction structure when parsing fails."""
    return {
        "merchant": "Unknown Merchant",
        "amount": 0,
        "currency": "USD",
        "date": None,
        "items": [],
        "category": "Other",
        "description": ""
    }


def _get_default_analysis() -> Dict[str, Any]:
    """Return default analysis structure."""
    return {
        "insight": "Transaction recorded successfully",
        "risk_level": "medium",
        "recommendation": "Monitor your spending in this category",
        "is_unusual": False
    }
