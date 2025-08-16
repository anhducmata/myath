import requests
import logging
import base64
from typing import Optional
from config.settings import settings
from app.models import OCRResult

logger = logging.getLogger(__name__)


class OCRService:
    """
    Clean OCR Service using ONLY Mistral AI Vision Model
    Pipeline: System → Celery Queue → Mistral OCR → OpenAI
    """
    
    def __init__(self):
        self.api_key = settings.mistral_api_key
        self.base_url = "https://api.mistral.ai/v1"
        
        if not self.api_key:
            logger.warning("⚠️ Mistral API key not configured")
    
    async def process_image(self, image_content: bytes) -> OCRResult:
        """
        Process image using ONLY Mistral AI Vision Model
        
        Args:
            image_content: Raw bytes of the image file
            
        Returns:
            OCRResult with extracted text or error
        """
        try:
            logger.info("🔍 Starting Mistral Vision OCR processing...")
            
            if not self.api_key:
                raise Exception("Mistral API key not configured")
            
            # Process with Mistral Vision Model
            result = await self._process_with_mistral_vision(image_content)
            
            if result and result.text.strip():
                logger.info(f"✅ Mistral OCR successful: {result.text[:100]}...")
                return result
            else:
                logger.warning("⚠️ Mistral OCR returned empty result")
                return OCRResult(
                    text='No text extracted from image',
                    latex=None,
                    confidence=0.0,
                    method='mistral_no_text'
                )
                
        except Exception as e:
            logger.error(f"❌ Mistral OCR processing failed: {e}")
            return OCRResult(
                text='OCR processing failed',
                latex=None,
                confidence=0.0,
                method='mistral_error'
            )
    
    async def _process_with_mistral_vision(self, image_content: bytes) -> Optional[OCRResult]:
        """
        Process image using Mistral's pixtral-large-latest vision model
        """
        try:
            # Convert image to base64
            image_b64 = base64.b64encode(image_content).decode()
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the vision request
            data = {
                "model": "pixtral-large-latest",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all mathematical text, equations, and problems from this image. Return the mathematical content as plain text, preserving mathematical notation, symbols, and formatting. Include all visible text and mathematical expressions exactly as they appear."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_b64}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.1  # Low temperature for consistent OCR results
            }
            
            logger.info("📡 Sending request to Mistral Vision API...")
            
            # Make the API call
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=60  # Increased timeout for vision processing
            )
            
            logger.info(f"📡 Mistral API response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"❌ Mistral API error: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            logger.debug(f"📋 Mistral API response: {result}")
            
            # Extract text from response
            if "choices" in result and result["choices"]:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    extracted_text = choice["message"]["content"]
                    
                    if extracted_text and extracted_text.strip():
                        logger.info(f"✅ Mistral vision extraction successful: {extracted_text[:200]}...")
                        
                        return OCRResult(
                            text=extracted_text.strip(),
                            latex=None,  # Mistral provides text, OpenAI will handle LaTeX conversion
                            confidence=0.9,  # High confidence for Mistral vision model
                            method="mistral_vision"
                        )
            
            logger.warning("⚠️ No text extracted from Mistral vision model response")
            return None
            
        except Exception as e:
            logger.error(f"❌ Mistral vision model processing failed: {e}")
            return None


# Global instance
ocr_service = OCRService()