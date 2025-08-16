import requests
import logging
import tempfile
import os
import asyncio
from typing import Optional
from config.settings import settings
from app.models import OCRResult

logger = logging.getLogger(__name__)


class MistralOCRService:
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
                    text='No text extracted',
                    latex=None,
                    confidence=0.0,
                    method='mistral_failed'
                )
                
        except Exception as e:
            logger.error(f"Mistral OCR processing failed: {e}")
            return OCRResult(
                text='',
                latex=None,
                confidence=0.0,
                method='mistral_error'
            )
    
    async def _process_with_vision_model(self, image_content: bytes) -> Optional[OCRResult]:
        """Process image using Mistral's vision model with chat completions"""
        try:
            import base64
            
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
            logger.info(f"Mistral API response: {result}")
            
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
    
    async def _upload_file_and_process(self, image_content: bytes) -> Optional[OCRResult]:
        """Alternative method: Upload file first, then process with OCR endpoint"""
        try:
            # Step 1: Upload file
            file_id = await self._upload_file(image_content)
            if not file_id:
                logger.error("Failed to upload file to Mistral")
                return None
            
            # Step 2: Process with OCR endpoint
            return await self._process_uploaded_file(file_id)
            
        except Exception as e:
            logger.error(f"File upload and OCR processing failed: {e}")
            return None
    
    async def _upload_file(self, file_content: bytes) -> Optional[str]:
        """Upload file to Mistral Files API"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                with open(temp_file_path, 'rb') as f:
                    files = {
                        'file': ('math_problem.png', f, 'image/png'),
                        'purpose': (None, 'batch')  # Changed from 'ocr' to 'batch'
                    }
                    
                    response = requests.post(
                        f"{self.base_url}/files",
                        headers=headers,
                        files=files,
                        timeout=30
                    )
                    
                    logger.info(f"File upload response: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        file_id = result.get('id')
                        logger.info(f"File uploaded successfully with ID: {file_id}")
                        return file_id
                    else:
                        logger.error(f"File upload failed: {response.status_code} - {response.text}")
                        return None
                        
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
        except Exception as e:
            logger.error(f"Failed to upload file to Mistral: {e}")
            return None
    
    async def _process_uploaded_file(self, file_id: str) -> Optional[OCRResult]:
        """Process uploaded file using Mistral OCR endpoint"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Try different OCR request formats
            data = {
                "model": "pixtral-large-latest",
                "document": {
                    "type": "file",
                    "file_id": file_id
                },
                "include_image_base64": False,
                "image_limit": 1
            }
            
            response = requests.post(
                f"{self.base_url}/ocr",
                json=data,
                headers=headers,
                timeout=30
            )
            
            logger.info(f"OCR response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"OCR processing failed: {response.status_code} - {response.text}")
                return None
            
            result = response.json()
            logger.info(f"OCR result: {result}")
            
            # Parse OCR response
            extracted_text = ""
            if "document_annotation" in result:
                extracted_text = result["document_annotation"]
            elif "bbox_annotations" in result and result["bbox_annotations"]:
                extracted_text = " ".join([
                    ann.get("text", "") if isinstance(ann, dict) else str(ann)
                    for ann in result["bbox_annotations"]
                ])
            
            if extracted_text and extracted_text.strip():
                return OCRResult(
                    text=extracted_text.strip(),
                    latex=None,
                    confidence=0.9,
                    method="mistral_ocr"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            return None


# Global instance
mistral_ocr_service = MistralOCRService()
