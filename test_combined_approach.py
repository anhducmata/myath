#!/usr/bin/env python3
"""
Test the new combined OCR + Image approach
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).parent))

from app.services.parser import ParserService

async def test_combined_approach():
    """Test the new combined OCR text + image approach"""
    
    # Sample MCQ text from the math-2.png image
    mcq_text = """2. The figure below is made up of 20 identical small rectangles.

What percentage of the figure is shaded?

(1) 35%

(2) 20%

(3) 3%

(4) 7%"""

    print("🧪 Testing New Combined OCR + Image Approach")
    print("=" * 60)
    print(f"📝 OCR Input text:\n{mcq_text}")
    print("=" * 60)
    
    # Initialize parser service
    parser_service = ParserService()
    
    try:
        # Read the image file
        with open("math-2.png", "rb") as f:
            image_content = f.read()
        
        print("📸 Image loaded successfully")
        print()
        
        # Test the combined approach
        print("🔍 Step 1: Parsing with combined OCR text + image...")
        parsed_problem = await parser_service.parse_problem(
            ocr_text=mcq_text,
            image_content=image_content
        )
        
        print(f"✅ Parsed successfully!")
        print(f"   Type: {parsed_problem.type}")
        print(f"   Statement: {parsed_problem.statement[:100]}...")
        print(f"   Options: {parsed_problem.options}")
        print(f"   Asks: {parsed_problem.asks}")
        print(f"   Variables: {parsed_problem.variables}")
        print(f"   Visual Elements: {getattr(parsed_problem, 'visual_elements', 'N/A')}")
        print()
        
        # Also test text-only for comparison
        print("🔍 Step 2: Testing text-only approach for comparison...")
        parsed_text_only = await parser_service._parse_text_only(mcq_text)
        
        print(f"✅ Text-only parsed successfully!")
        print(f"   Type: {parsed_text_only.type}")
        print(f"   Statement: {parsed_text_only.statement[:100]}...")
        print(f"   Options: {parsed_text_only.options}")
        print()
        
        print("🎉 Both approaches completed successfully!")
        print("📊 Comparison:")
        print(f"   Combined approach type: {parsed_problem.type}")
        print(f"   Text-only approach type: {parsed_text_only.type}")
        print(f"   Same result: {parsed_problem.type == parsed_text_only.type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_combined_approach())
    if success:
        print("🎉 Test completed successfully!")
    else:
        print("💥 Test failed!")
        sys.exit(1)
