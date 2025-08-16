#!/usr/bin/env python3
"""
Test the simplified Mistral-only OCR service
"""
import asyncio
import sys
import os

# Add project root to Python path
sys.path.insert(0, '/Users/duc.nguyen/flutter')

from app.services.ocr import ocr_service

async def test_mistral_ocr():
    """Test Mistral OCR with the math test image"""
    try:
        # Read the test image
        image_path = "/Users/duc.nguyen/flutter/math-test.png"
        
        if not os.path.exists(image_path):
            print(f"Test image not found: {image_path}")
            return
        
        with open(image_path, 'rb') as f:
            image_content = f.read()
        
        print(f"Testing Mistral OCR with image: {image_path}")
        print(f"Image size: {len(image_content)} bytes")
        
        # Process the image
        result = await ocr_service.process_image(image_content)
        
        print("\n=== OCR RESULT ===")
        print(f"Method: {result.method}")
        print(f"Confidence: {result.confidence}")
        print(f"Text: {result.text}")
        print(f"LaTeX: {result.latex}")
        
        if result.text and result.text.strip() and result.method.startswith('mistral'):
            print("\n✅ SUCCESS: Mistral OCR extracted text!")
        else:
            print("\n❌ FAILED: No text extracted or error occurred")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mistral_ocr())
