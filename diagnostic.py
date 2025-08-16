#!/usr/bin/env python3
"""
Diagnostic script to check what's happening with the parsing
"""

import requests
import json

# Configuration
API_BASE = "http://localhost:8000"
API_KEY = "math-api-key-2025"
headers = {"X-API-Key": API_KEY}

def check_last_problem():
    """Check the most recent problem to see what went wrong"""
    
    # Get the last processed problem ID
    problem_id = "MsBuEbMcp2hHm1OTj7EN"  # From the last test
    
    print(f"🔍 Checking problem {problem_id}")
    print("=" * 50)
    
    response = requests.get(f"{API_BASE}/v1/problems/{problem_id}", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        print("📝 OCR Result:")
        ocr = data.get("ocr_result", {})
        print(f"  Text: {ocr.get('text', 'None')[:200]}...")
        print(f"  Method: {ocr.get('method', 'None')}")
        print(f"  Confidence: {ocr.get('confidence', 'None')}")
        
        print("\n🤖 Parsed Problem:")
        parsed = data.get("parsed_problem", {})
        print(f"  Type: {parsed.get('type', 'None')}")
        print(f"  Statement: {parsed.get('statement', 'None')[:200]}...")
        print(f"  Options: {parsed.get('options', [])}")
        print(f"  Asks: {parsed.get('asks', [])}")
        
        print("\n🔧 Solution:")
        solution = data.get("solution", {})
        print(f"  Method: {solution.get('method', 'None')}")
        print(f"  Confidence: {solution.get('confidence', 'None')}")
        print(f"  Result: {str(solution.get('result', 'None'))[:200]}...")
        
        print("\n🔍 Analysis:")
        if parsed.get('type') != 'mcq':
            print(f"❌ Problem: Type detected as '{parsed.get('type')}' instead of 'mcq'")
            print("   This explains why MCQ solver wasn't used")
        else:
            print("✅ Type correctly detected as MCQ")
            print("❌ But solver still failed - check MCQ implementation")
            
    else:
        print(f"❌ Failed to get problem: {response.status_code}")

if __name__ == "__main__":
    check_last_problem()
