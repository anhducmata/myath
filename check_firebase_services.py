#!/usr/bin/env python3
"""
Check Firebase services status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
from app.services.firebase import firebase_service

async def check_firebase_services():
    """Check if Firebase services are properly configured"""
    print("=" * 60)
    print("Checking Firebase Services")
    print("=" * 60)
    
    try:
        # Test Firestore
        print("Testing Firestore Database...")
        test_problem = {
            'user_id': 'test-user',
            'status': 'test',
            'created_at': '2025-08-16T14:50:00.000Z'
        }
        
        problem_id = await firebase_service.create_problem(test_problem)
        print(f"✅ Firestore working! Created test document: {problem_id}")
        
        # Clean up test document
        await firebase_service.update_problem(problem_id, {'status': 'deleted'})
        print("✅ Firestore update working!")
        
    except Exception as e:
        print(f"❌ Firestore error: {e}")
        print("Please enable Firestore Database in Firebase Console:")
        print("https://console.firebase.google.com/project/myath-73fa0/firestore")
        return False
    
    try:
        # Test Storage
        print("\nTesting Firebase Storage...")
        test_content = b"Test file content"
        file_url = await firebase_service.upload_file(test_content, "test.txt", "text/plain")
        print(f"✅ Storage working! Upload URL: {file_url}")
        
    except Exception as e:
        print(f"❌ Storage error: {e}")
        print("Please enable Firebase Storage in Firebase Console:")
        print("https://console.firebase.google.com/project/myath-73fa0/storage")
        return False
    
    print("\n✅ All Firebase services are working correctly!")
    return True

if __name__ == "__main__":
    asyncio.run(check_firebase_services())
