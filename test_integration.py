#!/usr/bin/env python3
"""
Integration test script for Math Homework Backend
Tests API key authentication and file upload functionality
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/v1"
API_KEY = "math-api-key-2025"
TEST_IMAGE_PATH = "./P5_Maths_2023_SA2_acsprimary.pdf"

def test_api_key_auth():
    """Test API key authentication"""
    print("Testing API key authentication...")
    
    # Test without API key
    response = requests.get(f"{BASE_URL}/problems/test-id")
    print(f"Without API key: {response.status_code}")
    
    # Test with invalid API key
    headers = {"X-API-Key": "invalid-key"}
    response = requests.get(f"{BASE_URL}/problems/test-id", headers=headers)
    print(f"With invalid API key: {response.status_code}")
    
    # Test with valid API key
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/problems/test-id", headers=headers)
    print(f"With valid API key: {response.status_code}")

def test_file_upload():
    """Test file upload and problem creation"""
    print("\nTesting file upload...")
    
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"Test file not found: {TEST_IMAGE_PATH}")
        return
    
    headers = {"X-API-Key": API_KEY}
    
    with open(TEST_IMAGE_PATH, 'rb') as file:
        files = {"file": (TEST_IMAGE_PATH, file, "application/pdf")}
        response = requests.post(f"{BASE_URL}/problems", headers=headers, files=files)
        
    print(f"File upload status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"Created problem ID: {data.get('problem_id')}")
        return data.get('problem_id')
    else:
        print(f"Error: {response.text}")
        return None

def test_problem_retrieval(problem_id):
    """Test problem retrieval"""
    if not problem_id:
        return
        
    print(f"\nTesting problem retrieval for ID: {problem_id}")
    
    headers = {"X-API-Key": API_KEY}
    response = requests.get(f"{BASE_URL}/problems/{problem_id}", headers=headers)
    
    print(f"Problem retrieval status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Problem status: {data.get('status')}")
        print(f"File URL: {data.get('file_url')}")
    else:
        print(f"Error: {response.text}")

def main():
    """Main test function"""
    print("=" * 50)
    print("Math Homework Backend Integration Test")
    print("=" * 50)
    
    try:
        # Test authentication
        test_api_key_auth()
        
        # Test file upload
        problem_id = test_file_upload()
        
        # Test problem retrieval
        test_problem_retrieval(problem_id)
        
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to server. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    main()
