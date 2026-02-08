"""
OCR Service for Receipt Processing
Supports both local development and Render cloud deployment
Uses Tesseract OCR + AI for intelligent receipt parsing
"""

import logging
import re
import base64
import io
from typing import Dict, Optional, List
from datetime import datetime
from PIL import Image
import pytesseract
import requests

logger = logging.getLogger(__name__)

class OCRService:
    """
    Handles OCR extraction from receipt images.
    Works on both local and cloud environments (Render).
    """
    
    def __init__(self):
        """Initialize OCR service with Tesseract configuration."""
        # Tesseract configuration for better receipt reading
        self.tesseract_config = r'--oem 3 --psm 6'
        
        # Common merchant patterns
        self.merchant_patterns = [
            r'(?:merchant|store|shop|restaurant|cafe|market|mall|supermarket|pharmacy)[\s:]*([A-Za-z\s&]+)',
            r'^([A-Z][A-Za-z\s&]{2,30})(?:\n|$)',  # Capitalized name at start
        ]
        
        # Amount patterns (supports ₦, $, NGN, USD)
        self.amount_patterns = [
            r'(?:total|amount|sum|pay|grand\s*total|net\s*total)[\s:]*[₦$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'[₦$]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:total|only)?',
            r'NGN\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:NGN|USD)',
        ]
        
        # Date patterns
        self.date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})',
        ]
    
    def extract_text_from_image(self, image_source: str) -> str:
        """
        Extract text from image using Tesseract OCR.
        
        Args:
            image_source: Either base64 data URI or image URL
            
        Returns:
            Extracted text string
        """
        try:
            # Load image
            image = self._load_image(image_source)
            
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            
            logger.info(f"OCR extracted {len(text)} characters")
            return text.strip()
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    def _load_image(self, image_source: str) -> Image.Image:
        """Load image from base64 or URL."""
        try:
            if image_source.startswith('data:image'):
                # Base64 data URI
                base64_data = image_source.split(',')[1]
                image_bytes = base64.b64decode(base64_data)
                return Image.open(io.BytesIO(image_bytes))
            elif image_source.startswith('http'):
                # URL
                response = requests.get(image_source, timeout=10)
                response.raise_for_status()
                return Image.open(io.BytesIO(response.content))
            else:
                # Assume raw base64
                image_bytes = base64.b64decode(image_source)
                return Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            raise Exception(f"Invalid image source: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        - Convert to grayscale
        - Increase contrast
        - Resize if too small
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to grayscale
            image = image.convert('L')
            
            # Resize if image is too small
            min_width = 800
            if image.width < min_width:
                ratio = min_width / image.width
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def parse_receipt_text(self, text: str) -> Dict:
        """
        Parse extracted OCR text to extract receipt fields.
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary with merchant, amount, date, items, etc.
        """
        result = {
            "merchant": "Unknown",
            "amount": 0,
            "currency": "NGN",
            "date": None,
            "description": "",
            "items": [],
            "category": "Other"
        }
        
        try:
            lines = text.split('\n')
            clean_lines = [line.strip() for line in lines if line.strip()]
            
            # Extract merchant (usually first few lines)
            merchant = self._extract_merchant(clean_lines)
            if merchant:
                result["merchant"] = merchant
                result["description"] = merchant
            
            # Extract amount
            amount = self._extract_amount(text)
            if amount:
                result["amount"] = amount
            
            # Extract date
            date = self._extract_date(text)
            if date:
                result["date"] = date
            
            # Extract items (line items)
            items = self._extract_items(clean_lines)
            if items:
                result["items"] = items
            
            logger.info(f"Parsed receipt: merchant={result['merchant']}, amount={result['amount']}")
            
        except Exception as e:
            logger.error(f"Receipt parsing error: {e}")
        
        return result
    
    def _extract_merchant(self, lines: List[str]) -> Optional[str]:
        """Extract merchant name from receipt lines."""
        # Try first 5 lines for merchant name
        for line in lines[:5]:
            # Skip common header words
            if any(word in line.lower() for word in ['receipt', 'invoice', 'tax', 'vat', 'date']):
                continue
            
            # Look for capitalized business names
            if len(line) > 3 and len(line) < 40:
                # Remove special characters and numbers
                cleaned = re.sub(r'[^A-Za-z\s&\'-]', '', line).strip()
                if cleaned and len(cleaned) > 3:
                    return cleaned
        
        return None
    
    def _extract_amount(self, text: str) -> float:
        """Extract total amount from receipt text."""
        amounts = []
        
        for pattern in self.amount_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    # Extract numeric value
                    amount_str = match.group(1).replace(',', '')
                    amount = float(amount_str)
                    amounts.append(amount)
                except (ValueError, IndexError):
                    continue
        
        # Return the largest amount found (likely the total)
        return max(amounts) if amounts else 0
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text."""
        for pattern in self.date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Try to parse and standardize date format
                try:
                    # Try different date formats
                    for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d %b %Y', '%d %B %Y']:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            return dt.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                except Exception:
                    pass
                
                # Return raw date string if parsing fails
                return date_str
        
        return None
    
    def _extract_items(self, lines: List[str]) -> List[Dict]:
        """Extract line items from receipt."""
        items = []
        
        # Pattern for line items: description followed by amount
        item_pattern = r'^(.+?)\s+[₦$]?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*$'
        
        for line in lines:
            match = re.match(item_pattern, line)
            if match:
                try:
                    description = match.group(1).strip()
                    amount = float(match.group(2).replace(',', ''))
                    
                    # Filter out unlikely items
                    if len(description) > 2 and amount > 0:
                        items.append({
                            "description": description,
                            "amount": amount
                        })
                except (ValueError, IndexError):
                    continue
        
        return items[:20]  # Limit to 20 items max


# Singleton instance
_ocr_service = None

def get_ocr_service() -> OCRService:
    """Get or create OCR service instance."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service


async def extract_receipt_data(image_source: str) -> Dict:
    """
    Main function to extract receipt data from image.
    
    Args:
        image_source: Base64 data URI or image URL
        
    Returns:
        Dictionary with extracted receipt data
    """
    ocr = get_ocr_service()
    
    # Step 1: Extract text using OCR
    text = ocr.extract_text_from_image(image_source)
    
    if not text or len(text) < 10:
        logger.warning("OCR extracted minimal text")
        raise Exception("Could not extract text from receipt image")
    
    # Step 2: Parse the extracted text
    receipt_data = ocr.parse_receipt_text(text)
    
    return receipt_data