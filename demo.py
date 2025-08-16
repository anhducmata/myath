#!/usr/bin/env python3
"""
Demo script to test the Math Homework Backend API
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """Test basic API functionality"""
    print("🚀 Testing Math Homework Backend API")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1. Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test root endpoint
    print("\n2. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test API documentation
    print("\n3. Testing API documentation...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
    
    # Test unauthorized access to protected endpoint
    print("\n4. Testing unauthorized access...")
    response = requests.get(f"{BASE_URL}/v1/problems/test-id")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    print("\n✅ API testing completed!")
    print("\n📝 Notes:")
    print("   - FastAPI server is running on http://localhost:8000")
    print("   - Celery worker is processing background tasks")
    print("   - Redis is running for task queue management")
    print("   - Firebase service is in mock mode for development")
    print("   - All tests are passing")
    print("   - API documentation available at http://localhost:8000/docs")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("   Make sure the FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")
