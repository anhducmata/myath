#!/usr/bin/env python3
"""
Test the complete math homework pipeline using math-test.png
"""

import requests
import json
import time
import os

# Configuration
BASE_URL = "http://localhost:8000/v1"
API_KEY = "math-api-key-2025"
TEST_IMAGE_PATH = "./math-test.png"

def test_complete_pipeline():
    """Test the complete math homework processing pipeline"""
    print("=" * 60)
    print("Testing Complete Math Homework Pipeline")
    print("Using image: math-test.png")
    print("=" * 60)
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"❌ Test image not found: {TEST_IMAGE_PATH}")
        return
    
    headers = {"X-API-Key": API_KEY}
    
    # Step 1: Upload the math image
    print("\n🔄 Step 1: Uploading math image...")
    
    with open(TEST_IMAGE_PATH, 'rb') as file:
        files = {"file": ("math-test.png", file, "image/png")}
        response = requests.post(f"{BASE_URL}/problems", headers=headers, files=files)
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"Error: {response.text}")
        return
    
    problem_data = response.json()
    problem_id = problem_data['problem_id']
    print(f"✅ Upload successful! Problem ID: {problem_id}")
    
    # Step 2: Wait and check processing status
    print(f"\n🔄 Step 2: Monitoring processing status...")
    
    max_attempts = 20  # Wait up to 2 minutes
    for attempt in range(max_attempts):
        print(f"   Checking status (attempt {attempt + 1}/{max_attempts})...")
        
        # Get problem status
        response = requests.get(f"{BASE_URL}/problems/{problem_id}", headers=headers)
        if response.status_code == 200:
            problem = response.json()
            status = problem.get('status')
            print(f"   Status: {status}")
            
            if status == 'completed':
                print("✅ Processing completed!")
                
                # Display results
                print("\n📊 Results:")
                print("-" * 40)
                
                if problem.get('ocr_result'):
                    ocr = problem['ocr_result']
                    print(f"📝 OCR Text: {ocr.get('text', 'N/A')}")
                    print(f"🔗 OCR Method: {ocr.get('method', 'N/A')}")
                    print(f"📊 Confidence: {ocr.get('confidence', 'N/A')}")
                
                if problem.get('parsed_problem'):
                    parsed = problem['parsed_problem']
                    print(f"🎯 Problem Type: {parsed.get('type', 'N/A')}")
                    print(f"📋 Description: {parsed.get('description', 'N/A')}")
                
                if problem.get('solution'):
                    solution = problem['solution']
                    print(f"✅ Answer: {solution.get('answer', 'N/A')}")
                    print(f"📝 Steps: {solution.get('steps', 'N/A')}")
                    print(f"🔍 Method: {solution.get('method', 'N/A')}")
                
                # Show file URL
                print(f"🔗 File URL: {problem.get('file_url', 'N/A')}")
                
                return problem
                
            elif status == 'failed':
                print("❌ Processing failed!")
                error_msg = problem.get('error_message', 'Unknown error')
                print(f"Error: {error_msg}")
                return None
            
            elif status in ['queued', 'processing']:
                # Continue waiting
                time.sleep(6)  # Wait 6 seconds between checks
                continue
        else:
            print(f"❌ Failed to get status: {response.status_code}")
            break
    
    print("⏰ Processing timeout - check manually later")
    return None

def test_task_status(problem_id):
    """Test the task status endpoint"""
    print(f"\n🔄 Checking background task status...")
    
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/problems/{problem_id}/task-status", headers=headers)
    
    if response.status_code == 200:
        task_data = response.json()
        print(f"📋 Task Status: {task_data.get('task_status')}")
        if task_data.get('error'):
            print(f"❌ Task Error: {task_data.get('error')}")
    else:
        print(f"❌ Failed to get task status: {response.status_code}")

def main():
    """Main test function"""
    try:
        # Test the complete pipeline
        result = test_complete_pipeline()
        
        if result:
            print("\n🎉 Test completed successfully!")
            # Test task status endpoint
            test_task_status(result['problem_id'])
        else:
            print("\n❌ Test failed or incomplete")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
