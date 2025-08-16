#!/usr/bin/env python3
"""
Test the complete pipeline with math-2.png
Pipeline: System → Celery → Mistral OCR → OpenAI
"""

import asyncio
import requests
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE = "http://localhost:8000"
API_KEY = "math-api-key-2025"
TEST_IMAGE = "math-2.png"

async def test_math_2_pipeline():
    """Test the complete pipeline with math-2.png"""
    
    print("🧪 Testing Complete Pipeline with math-2.png")
    print("=" * 70)
    print(f"📁 Test file: {TEST_IMAGE}")
    
    # Step 1: Upload math-2.png
    print("\n📤 Step 1: Uploading math-2.png...")
    
    headers = {"X-API-Key": API_KEY}
    
    with open(TEST_IMAGE, "rb") as f:
        files = {"file": (TEST_IMAGE, f, "image/png")}
        response = requests.post(f"{API_BASE}/v1/problems", headers=headers, files=files)
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return
        
    data = response.json()
    problem_id = data["problem_id"]
    print(f"✅ File uploaded successfully! Problem ID: {problem_id}")
    
    # Step 2: Check problem status
    print(f"\n📋 Step 2: Checking initial problem status...")
    response = requests.get(f"{API_BASE}/v1/problems/{problem_id}", headers=headers)
    
    if response.status_code == 200:
        problem_data = response.json()
        print(f"✅ Problem status: {problem_data.get('status', 'unknown')}")
        print(f"📁 File URL: {problem_data.get('file_url', 'none')}")
    else:
        print(f"❌ Failed to get problem: {response.status_code}")
        return
    
    # Step 3: Monitor processing
    print(f"\n⚙️ Step 3: Monitoring Celery background processing...")
    print("Processing through: 🔄 Celery → 🔍 Mistral OCR → 🤖 OpenAI → 💾 Firebase")
    
    max_wait = 120  # 2 minutes
    wait_time = 0
    
    while wait_time < max_wait:
        response = requests.get(f"{API_BASE}/v1/problems/{problem_id}", headers=headers)
        
        if response.status_code == 200:
            problem_data = response.json()
            status = problem_data.get('status', 'unknown')
            
            print(f"  📊 Status: {status} (waited {wait_time}s)")
            
            if status == 'completed':
                print("\n🎉 Processing completed! Results:")
                print("=" * 50)
                
                # Show OCR result
                ocr_result = problem_data.get('ocr_result', {})
                if ocr_result:
                    print(f"🔍 Mistral OCR Method: {ocr_result.get('method', 'unknown')}")
                    print(f"🔍 Mistral OCR Confidence: {ocr_result.get('confidence', 0)}")
                    ocr_text = ocr_result.get('text', '')
                    print(f"🔍 Mistral OCR Text (first 300 chars):")
                    print(f"   {ocr_text[:300]}{'...' if len(ocr_text) > 300 else ''}")
                
                # Show parsed result
                parsed_problem = problem_data.get('parsed_problem', {})
                if parsed_problem:
                    print(f"\n🤖 OpenAI Parsed Type: {parsed_problem.get('type', 'unknown')}")
                    print(f"🤖 OpenAI Problem Statement:")
                    print(f"   {parsed_problem.get('statement', 'none')[:200]}{'...' if len(parsed_problem.get('statement', '')) > 200 else ''}")
                    print(f"🤖 OpenAI Asks: {parsed_problem.get('asks', [])}")
                    if parsed_problem.get('options'):
                        print(f"🤖 OpenAI Options: {len(parsed_problem.get('options', []))} choices")
                    if parsed_problem.get('variables'):
                        print(f"🤖 OpenAI Variables: {parsed_problem.get('variables', [])}")
                
                # Show solution
                solution = problem_data.get('solution', {})
                if solution:
                    print(f"\n💡 Solution Method: {solution.get('method', 'none')}")
                    print(f"💡 Solution Confidence: {solution.get('confidence', 0)}")
                    print(f"💡 Solution Steps: {len(solution.get('steps', []))} steps")
                    
                    # Show solution result details
                    result = solution.get('result', {})
                    if isinstance(result, dict):
                        if result.get('correct_answer'):
                            print(f"💡 Correct Answer: {result.get('correct_answer')}")
                        if result.get('question_type'):
                            print(f"💡 Question Type: {result.get('question_type')}")
                    else:
                        print(f"💡 Final Answer: {result}")
                    
                    # Show first few steps
                    steps = solution.get('steps', [])
                    if steps:
                        print(f"\n📝 Solution Steps:")
                        for step in steps[:3]:  # Show first 3 steps
                            print(f"   Step {step.get('step_number', '?')}: {step.get('description', 'no description')}")
                            if step.get('explanation'):
                                explanation = step.get('explanation', '')
                                print(f"     → {explanation[:150]}{'...' if len(explanation) > 150 else ''}")
                
                return True
                
            elif status == 'failed':
                print(f"❌ Processing failed!")
                error_msg = problem_data.get('error_message', 'Unknown error')
                print(f"Error: {error_msg}")
                return False
                
        time.sleep(5)
        wait_time += 5
    
    print(f"⏰ Timeout after {max_wait} seconds")
    return False

if __name__ == "__main__":
    asyncio.run(test_math_2_pipeline())
