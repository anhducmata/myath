#!/usr/bin/env python3
"""
Test the improved solver by uploading math-2.png again
"""

import requests
import time

# Configuration
API_BASE = "http://localhost:8000"
API_KEY = "math-api-key-2025"
headers = {"X-API-Key": API_KEY}

def test_improved_solver():
    print("🧪 Testing Improved Solver for Rectangle Percentage Problem")
    print("=" * 60)
    
    # Upload the file again
    print("\n📤 Uploading math-2.png again to test improved solver...")
    
    with open("math-2.png", "rb") as f:
        files = {"file": ("math-2.png", f, "image/png")}
        response = requests.post(f"{API_BASE}/v1/problems", headers=headers, files=files)
    
    if response.status_code != 201:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        return
    
    data = response.json()
    problem_id = data["problem_id"]
    print(f"✅ New upload successful! Problem ID: {problem_id}")
    print("⏳ Processing will start in background...")
    
    # Wait for processing
    print("\n🔄 Monitoring processing...")
    max_wait = 60  # 1 minute
    wait_time = 0
    
    while wait_time < max_wait:
        response = requests.get(f"{API_BASE}/v1/problems/{problem_id}", headers=headers)
        
        if response.status_code == 200:
            problem_data = response.json()
            status = problem_data.get("status", "unknown")
            
            print(f"  📊 Status: {status} (waited {wait_time}s)")
            
            if status == "completed":
                print("\n🎉 Processing completed! NEW SOLVER RESULTS:")
                print("=" * 50)
                
                # Show solution with improved solver
                solution = problem_data.get("solution", {})
                result = solution.get("result", {})
                
                # Handle different result formats
                if isinstance(result, dict):
                    final_answer = result.get('correct_answer', 'None')
                    reasoning = result.get("reasoning", "No reasoning provided")
                else:
                    final_answer = str(result)
                    reasoning = "Result returned as string"
                
                print(f"🎯 Final Answer: {final_answer}")
                print(f"📊 Confidence: {solution.get('confidence', 0)}")
                print(f"🔧 Method: {solution.get('method', 'unknown')}")
                print(f"✅ Verified: {solution.get('verification_passed', False)}")
                
                # Show reasoning
                print(f"\n💭 Reasoning:\n{reasoning}")
                
                # Show solution steps
                steps = solution.get("steps", [])
                if steps:
                    print(f"\n📝 Solution Steps ({len(steps)} steps):")
                    for step in steps:
                        print(f"  Step {step.get('step_number', '?')}: {step.get('description', '')}")
                        if step.get('explanation'):
                            print(f"    → {step.get('explanation')}")
                
                # Show full result structure for debugging
                print(f"\n🔍 DEBUG - Result type: {type(result)}")
                print(f"🔍 DEBUG - Result content: {result}")
                
                return True
                
            elif status == "failed":
                print(f"❌ Processing failed!")
                return False
                
        time.sleep(3)
        wait_time += 3
    
    print(f"⏰ Timeout after {max_wait} seconds")
    return False

if __name__ == "__main__":
    test_improved_solver()
