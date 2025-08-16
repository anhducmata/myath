#!/usr/bin/env python3
"""
Parameterized test script for math problem images
Usage: python test-math.py "math-4.png"
"""

import requests
import time
import sys
import os
from pathlib import Path

def test_math_problem(image_filename):
    """Test any math problem image file"""
    
    # Configuration
    API_BASE = "http://localhost:8000"
    API_KEY = "math-api-key-2025"
    headers = {"X-API-Key": API_KEY}
    
    # Check if file exists
    if not os.path.exists(image_filename):
        print(f"❌ File not found: {image_filename}")
        return False
    
    print(f"🧪 Testing Math Problem: {image_filename}")
    print("=" * 60)
    
    # Upload the file
    print(f"\n📤 Uploading {image_filename}...")
    
    # Determine MIME type based on extension
    ext = Path(image_filename).suffix.lower()
    mime_type = "image/png" if ext == ".png" else "image/jpeg" if ext in [".jpg", ".jpeg"] else "application/pdf"
    
    try:
        with open(image_filename, "rb") as f:
            files = {"file": (image_filename, f, mime_type)}
            response = requests.post(f"{API_BASE}/v1/problems", headers=headers, files=files)
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return False
    
    data = response.json()
    problem_id = data["problem_id"]
    print(f"✅ Upload successful! Problem ID: {problem_id}")
    print("⏳ Processing will start in background...")
    
    # Wait for processing
    print("\n🔄 Monitoring processing...")
    max_wait = 60  # 1 minute
    wait_time = 0
    
    while wait_time < max_wait:
        try:
            response = requests.get(f"{API_BASE}/v1/problems/{problem_id}", headers=headers)
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            time.sleep(3)
            wait_time += 3
            continue
        
        if response.status_code == 200:
            problem_data = response.json()
            status = problem_data.get("status", "unknown")
            
            print(f"  📊 Status: {status} (waited {wait_time}s)")
            
            if status == "completed":
                print(f"\n🎉 Processing completed! RESULTS FOR {image_filename.upper()}:")
                print("=" * 50)
                
                # Show OCR results
                ocr_result = problem_data.get("ocr_result", {})
                if ocr_result:
                    ocr_text = ocr_result.get('text', 'N/A')
                    print(f"📝 OCR Text: {ocr_text[:200]}{'...' if len(ocr_text) > 200 else ''}")
                    print(f"🔍 OCR Method: {ocr_result.get('method', 'N/A')}")
                    print(f"📊 OCR Confidence: {ocr_result.get('confidence', 0)}")
                
                # Show parsed problem
                parsed_problem = problem_data.get("parsed_problem", {})
                if parsed_problem:
                    print(f"\n🧩 Problem Type: {parsed_problem.get('type', 'N/A')}")
                    statement = parsed_problem.get('statement', 'N/A')
                    print(f"📋 Statement: {statement[:150]}{'...' if len(statement) > 150 else ''}")
                    options = parsed_problem.get('options', [])
                    if options:
                        print(f"🔢 Options: {options}")
                    print(f"🎯 Asks: {parsed_problem.get('asks', [])}")
                
                # Show solution
                solution = problem_data.get("solution", {})
                if solution:
                    result = solution.get("result", {})
                    
                    # Handle different result formats
                    if isinstance(result, dict):
                        final_answer = result.get('correct_answer', result.get('answer', 'None'))
                        reasoning = result.get("reasoning", "No reasoning provided")
                    else:
                        final_answer = str(result)
                        reasoning = "Result returned as string"
                    
                    print(f"\n🎯 Final Answer: {final_answer}")
                    print(f"📊 Confidence: {solution.get('confidence', 0)}")
                    print(f"🔧 Method: {solution.get('method', 'unknown')}")
                    print(f"✅ Verified: {solution.get('verification_passed', False)}")
                    
                    # Show reasoning
                    print(f"\n💭 Reasoning:")
                    print(reasoning)
                    
                    # Show solution steps
                    steps = solution.get("steps", [])
                    if steps:
                        print(f"\n📝 Solution Steps ({len(steps)} steps):")
                        for i, step in enumerate(steps, 1):
                            print(f"  Step {i}: {step.get('description', '')}")
                            if step.get('explanation'):
                                print(f"    → {step.get('explanation')}")
                            if step.get('result'):
                                result_text = str(step.get('result'))
                                if len(result_text) > 100:
                                    result_text = result_text[:100] + "..."
                                print(f"    Result: {result_text}")
                
                return True
                
            elif status == "failed":
                print(f"❌ Processing failed!")
                error_msg = problem_data.get("error_message", "Unknown error")
                print(f"💥 Error: {error_msg}")
                return False
                
        time.sleep(3)
        wait_time += 3
    
    print(f"⏰ Timeout after {max_wait} seconds")
    return False

def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) != 2:
        print("Usage: python test-math.py <image_filename>")
        print("Examples:")
        print("  python test-math.py math-4.png")
        print("  python test-math.py math-3.png")
        print("  python test-math.py math-2.png")
        sys.exit(1)
    
    image_filename = sys.argv[1]
    
    print(f"🚀 Starting Math Problem Test")
    print(f"📁 Working Directory: {os.getcwd()}")
    print(f"📄 Target File: {image_filename}")
    
    # Check if FastAPI server is running
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ FastAPI server is running")
        else:
            print("⚠️ FastAPI server might not be running properly")
    except:
        print("❌ FastAPI server is not accessible at http://localhost:8000")
        print("Please make sure to start the server first: python main.py")
        sys.exit(1)
    
    success = test_math_problem(image_filename)
    
    if success:
        print(f"\n🎉 Test completed successfully for {image_filename}!")
    else:
        print(f"\n💥 Test failed for {image_filename}!")
        sys.exit(1)

if __name__ == "__main__":
    main()
