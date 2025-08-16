import requests
import logging
import base64
import tempfile
import os
from typing import Optional
from config.settings import settings
from app.models import OCRResult

logger = logging.getLogger(__name__)


class OCRService:
    """Simplified OCR service using only Mistral AI"""
    
    def __init__(self):
        self.api_key = settings.mistral_api_key
        self.base_url = "https://api.mistral.ai/v1"
        
        if not self.api_key:
            logger.warning("Mistral API key not configured")
    
    async def process_image(self, image_content: bytes) -> OCRResult:
        """Process image with Mistral AI vision model"""
        try:
            logger.info("Processing image with Mistral AI vision model")
            
            if not self.api_key:
                raise Exception("Mistral API key not configured")
            
            # Use Mistral's vision model for OCR
            result = await self._process_with_vision_model(image_content)
            
            if result and result.text.strip():
                logger.info(f"Mistral OCR successful: {result.text[:100]}...")
                return result
            else:
                logger.warning("Mistral OCR returned empty result")
                return OCRResult(
                    text='No text extracted from image',
                    latex=None,
                    confidence=0.0,
                    method='mistral_no_text'
                )
                
        except Exception as e:
            logger.error(f"Mistral OCR processing failed: {e}")
            return OCRResult(
                text='OCR processing failed',
                latex=None,
                confidence=0.0,
                method='mistral_error'
            )
    
    
    async def _process_with_vision_model(self, image_content: bytes) -> Optional[OCRResult]:
        """Process image using Mistral's vision model with chat completions"""
        try:
            # Convert image to base64
            image_b64 = base64.b64encode(image_content).decode()
            
            # Use Mistral's chat completions with vision
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the request for Mistral's vision model
            data = {
                "model": "pixtral-large-latest",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all mathematical text and equations from this image. Return the mathematical content as plain text, preserving mathematical notation and symbols. If there are equations, include them exactly as they appear."
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
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            # Make the API call
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"Mistral API response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Mistral API error: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            logger.debug(f"Mistral API response: {result}")
            
            # Extract text from response
            if "choices" in result and result["choices"]:
                choice = result["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    extracted_text = choice["message"]["content"]
                    
                    if extracted_text and extracted_text.strip():
                        logger.info(f"Mistral vision model successful: {extracted_text[:200]}...")
                        
                        return OCRResult(
                            text=extracted_text.strip(),
                            latex=None,  # Could parse LaTeX from text if needed
                            confidence=0.9,  # High confidence for Mistral
                            method="mistral_vision"
                        )
            
            logger.warning("No text extracted from Mistral vision model response")
            return None
            
        except Exception as e:
            logger.error(f"Mistral vision model processing failed: {e}")
            return None


# Global instance
ocr_service = OCRService()
