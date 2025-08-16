#!/usr/bin/env python3
"""
Test the clean Mistral-only OCR pipeline
Pipeline: System → Celery → Mistral OCR → OpenAI
"""

import asyncio
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE = "http://localhost:8000"
API_KEY = "math-api-key-2025"

async def test_complete_pipeline():
    """Test the complete pipeline: Upload → Celery → Mistral OCR → OpenAI"""
    
    print("🧪 Testing Complete Pipeline: System → Celery → Mistral OCR → OpenAI")
    print("=" * 70)
    
    # Step 1: Upload file with API key
    print("\n📤 Step 1: Uploading math problem image...")
    
    headers = {"X-API-Key": API_KEY}
    
    with open("math-2.png", "rb") as f:
        files = {"file": ("math-2.png", f, "image/png")}
        response = requests.post(f"{API_BASE}/v1/problems", headers=headers, files=files)
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return
        
    data = response.json()
    problem_id = data["problem_id"]
    print(f"✅ File uploaded successfully! Problem ID: {problem_id}")
    
    # Step 2: Check problem status (should be queued)
    print(f"\n📋 Step 2: Checking initial problem status...")
    response = requests.get(f"{API_BASE}/v1/problems/{problem_id}", headers=headers)
    
    if response.status_code == 200:
        problem_data = response.json()
        print(f"✅ Problem status: {problem_data.get('status', 'unknown')}")
        print(f"📁 File URL: {problem_data.get('file_url', 'none')}")
    else:
        print(f"❌ Failed to get problem: {response.status_code}")
        return
    
    # Step 3: Monitor Celery task processing
    print(f"\n⚙️ Step 3: Monitoring Celery background processing...")
    print("This will take 30-60 seconds as the task processes through:")
    print("  🔄 Celery Queue → 🔍 Mistral OCR → 🤖 OpenAI → 💾 Firebase")
    
    # Wait for processing to complete
    import time
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
                    print(f"🔍 Mistral OCR Text: {ocr_result.get('text', 'none')[:200]}...")
                
                # Show parsed result
                parsed_problem = problem_data.get('parsed_problem', {})
                if parsed_problem:
                    print(f"\n🤖 OpenAI Parsed Type: {parsed_problem.get('type', 'unknown')}")
                    print(f"🤖 OpenAI Problem Statement: {parsed_problem.get('statement', 'none')[:200]}...")
                    print(f"🤖 OpenAI Asks: {parsed_problem.get('asks', [])}")
                
                # Show solution
                solution = problem_data.get('solution', {})
                if solution:
                    print(f"\n💡 Solution Steps: {len(solution.get('steps', []))} steps")
                    print(f"💡 Final Answer: {solution.get('answer', 'none')}")
                
                return True
                
            elif status == 'failed':
                print(f"❌ Processing failed!")
                return False
                
        time.sleep(5)
        wait_time += 5
    
    print(f"⏰ Timeout after {max_wait} seconds")
    return False

if __name__ == "__main__":
    asyncio.run(test_complete_pipeline())
