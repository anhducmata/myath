#!/usr/bin/env python3
"""
Authentication Bypass Demo for Math Homework Backend
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_auth_bypass():
    """Demonstrate authentication bypass in development mode"""
    print("🔓 Authentication Bypass Demo")
    print("=" * 50)
    
    # Test 1: Root endpoint with dev info
    print("\n1. 🏠 Root endpoint (shows dev info)")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    data = response.json()
    if "🔓 auth_bypass" in data:
        print("   ✅ Authentication bypass enabled")
        print(f"   💡 Tips: {data['💡 tips']}")
    
    # Test 2: Auth test endpoint (no authentication required)
    print("\n2. 🔓 Auth test endpoint (no auth required)")
    response = requests.get(f"{BASE_URL}/v1/problems/dev/auth-test")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data['message']}")
        print(f"   👤 User: {data['user']['email']}")
    
    # Test 3: Create test problem (no file upload, no auth)
    print("\n3. 🧪 Create test problem (no file upload, no auth)")
    response = requests.post(f"{BASE_URL}/v1/problems/dev/test")
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        problem_id = data['problem_id']
        print(f"   ✅ Created problem: {problem_id}")
        
        # Test 4: Retrieve the problem (ownership check bypassed)
        print("\n4. 📄 Retrieve problem (ownership bypass)")
        response = requests.get(f"{BASE_URL}/v1/problems/{problem_id}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Retrieved problem: {data['problem_id']}")
            print(f"   📊 Status: {data['status']}")
            print(f"   🔍 OCR Text: {data['ocr_result']['text']}")
    
    # Test 5: Create custom problem
    print("\n5. 🔢 Create custom math problem")
    custom_equation = "solve 2x^2 - 4x + 1 = 0"
    response = requests.post(f"{BASE_URL}/v1/problems/dev/test?text={custom_equation}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        problem_id = data['problem_id']
        print(f"   ✅ Created custom problem: {problem_id}")
        print(f"   🧮 Equation: {custom_equation}")
    
    # Test 6: Test with bypass token
    print("\n6. 🎫 Test with bypass token")
    headers = {"Authorization": "Bearer dev"}
    response = requests.get(f"{BASE_URL}/v1/problems/dev/auth-test", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Token 'dev' accepted")
        print(f"   👤 User: {data['user']['name']}")
    
    print("\n" + "=" * 50)
    print("✅ Authentication Bypass Summary:")
    print("   🔓 No Authorization header required")
    print("   🎫 Can use 'dev', 'test', or 'bypass' as token")
    print("   👥 Ownership checks disabled in dev mode")
    print("   🧪 Special dev endpoints available")
    print("   📱 All Firebase operations mocked")
    print("\n🚀 Ready for frontend development!")

if __name__ == "__main__":
    try:
        test_auth_bypass()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("   Make sure the FastAPI server is running on http://localhost:8000")
        print("   Run: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
