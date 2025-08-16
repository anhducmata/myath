#!/usr/bin/env python3
"""
Detailed test script that logs all prompts and API calls
"""

import asyncio
import sys
import json
from pathlib import Path

# Add the project root to sys.path
sys.path.append(str(Path(__file__).parent))

from app.services.parser import ParserService
from app.services.solver import SolverService
from app.services.ocr_clean import OCRService

class DetailedLogger:
    def __init__(self):
        self.step_counter = 0
        self.api_calls = []
        
    def log_step(self, title, content=""):
        self.step_counter += 1
        print(f"\n{'='*60}")
        print(f"🔍 STEP {self.step_counter}: {title}")
        print(f"{'='*60}")
        if content:
            print(content)
            
    def log_api_call(self, service, model, prompt, response):
        call_info = {
            "step": self.step_counter,
            "service": service,
            "model": model,
            "prompt": prompt,
            "response": response
        }
        self.api_calls.append(call_info)
        
        print(f"\n🤖 API CALL: {service} ({model})")
        print(f"📤 PROMPT:")
        print("-" * 40)
        print(prompt)
        print("-" * 40)
        print(f"📥 RESPONSE:")
        print("-" * 40)
        print(response)
        print("-" * 40)

async def test_with_detailed_logging():
    """Test with detailed logging of all steps and prompts"""
    
    logger = DetailedLogger()
    
    # Read the math-3.png image
    image_path = "math-3.png"
    with open(image_path, "rb") as f:
        image_content = f.read()
    
    logger.log_step("IMAGE LOADED", f"📁 File: {image_path}\n📏 Size: {len(image_content)} bytes")
    
    # Initialize services
    ocr_service = OCRService()
    parser_service = ParserService()
    solver_service = SolverService()
    
    try:
        # Step 1: OCR Processing
        logger.log_step("OCR PROCESSING")
        print("🔍 Starting Mistral Vision OCR...")
        
        # We'll capture the OCR prompt by modifying the service temporarily
        # For now, let's see what text we get
        ocr_result = await ocr_service.extract_text(image_content)
        
        print(f"✅ OCR Result:")
        print(f"   Text: {ocr_result.text}")
        print(f"   Method: {ocr_result.method}")
        print(f"   Confidence: {ocr_result.confidence}")
        
        # Log the OCR API call (approximated)
        logger.log_api_call(
            "Mistral Vision OCR",
            "mistral-medium-2312",
            "Extract mathematical text from this image with high accuracy...",
            ocr_result.text
        )
        
        # Step 2: Problem Parsing
        logger.log_step("PROBLEM PARSING")
        print("🤖 Starting OpenAI parsing...")
        
        # We need to capture the actual prompts. Let me create a custom parser
        # that logs the prompts before sending them
        original_create_method = parser_service.client.chat.completions.create
        
        def logged_create(*args, **kwargs):
            messages = kwargs.get('messages', [])
            model = kwargs.get('model', 'unknown')
            
            # Extract the prompt content
            user_content = ""
            for msg in messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    if isinstance(content, list):
                        # Vision API format
                        for item in content:
                            if item.get('type') == 'text':
                                user_content += item.get('text', '')
                    else:
                        user_content = content
            
            # Call the original method
            response = original_create_method(*args, **kwargs)
            
            # Log the interaction
            response_content = response.choices[0].message.content if response.choices else "No response"
            logger.log_api_call("OpenAI", model, user_content, response_content)
            
            return response
        
        # Replace the method temporarily
        parser_service.client.chat.completions.create = logged_create
        
        # Now parse with logging
        parsed_problem = await parser_service.parse_problem(
            ocr_result.text, 
            ocr_result.latex,
            image_content=image_content
        )
        
        # Restore original method
        parser_service.client.chat.completions.create = original_create_method
        
        print(f"✅ Parsing Result:")
        print(f"   Type: {parsed_problem.type}")
        print(f"   Statement: {parsed_problem.statement}")
        print(f"   Options: {parsed_problem.options}")
        print(f"   Asks: {parsed_problem.asks}")
        
        # Step 3: Problem Solving
        logger.log_step("PROBLEM SOLVING")
        print("🧮 Starting problem solving...")
        
        solution = await solver_service.solve_problem(parsed_problem)
        
        print(f"✅ Solution Result:")
        print(f"   Result: {solution.result}")
        print(f"   Method: {solution.method}")
        print(f"   Confidence: {solution.confidence}")
        print(f"   Verified: {solution.verification_passed}")
        print(f"   Steps: {len(solution.steps)} steps")
        
        # Step 4: Summary
        logger.log_step("SUMMARY")
        print(f"🎯 Final Answer: {solution.result}")
        print(f"📊 Total API Calls: {len(logger.api_calls)}")
        
        for i, call in enumerate(logger.api_calls, 1):
            print(f"\n📞 API Call {i}: {call['service']} - {call['model']}")
            prompt_preview = call['prompt'][:100] + "..." if len(call['prompt']) > 100 else call['prompt']
            print(f"   Prompt: {prompt_preview}")
            response_preview = call['response'][:100] + "..." if len(call['response']) > 100 else call['response']
            print(f"   Response: {response_preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_with_detailed_logging())
    if success:
        print("\n🎉 Detailed test completed successfully!")
    else:
        print("\n💥 Detailed test failed!")
        sys.exit(1)
