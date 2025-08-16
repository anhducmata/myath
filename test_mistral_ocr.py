#!/usr/bin/env python3
"""
Test Mistral OCR integration specifically
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.services.ocr import ocr_service
import logging

logging.basicConfig(level=logging.INFO)

async def test_mistral_ocr():
    """Test Mistral OCR with a real image"""
    print("=" * 60)
    print("Testing Mistral OCR Integration")
    print("=" * 60)
    
    # Load the test PDF file
    test_file_path = "./P5_Maths_2023_SA2_acsprimary.pdf"
    
    if not os.path.exists(test_file_path):
        print(f"❌ Test file not found: {test_file_path}")
        return
    
    try:
        # Read the file
        with open(test_file_path, 'rb') as f:
            file_content = f.read()
        
        print(f"✅ Loaded test file: {len(file_content)} bytes")
        
        # Test OCR processing
        print("🔍 Processing with OCR service...")
        result = await ocr_service.process_image(file_content)
        
        if result:
            print("✅ OCR processing successful!")
            print(f"Method used: {result.method}")
            print(f"Confidence: {result.confidence}")
            print(f"Text length: {len(result.text)} characters")
            print(f"Text preview: {result.text[:200]}...")
            if result.latex:
                print(f"LaTeX: {result.latex[:100]}...")
        else:
            print("❌ OCR processing failed")
            
    except Exception as e:
        print(f"❌ Error during OCR test: {e}")

if __name__ == "__main__":
    asyncio.run(test_mistral_ocr())
