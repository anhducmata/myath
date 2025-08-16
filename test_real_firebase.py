#!/usr/bin/env python3
"""
Test Firebase connection with real credentials
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firebase_connection():
    """Test Firebase connection with real credentials"""
    print("=" * 60)
    print("Testing Firebase Connection")
    print("=" * 60)
    
    # Print configuration
    print(f"Project ID: {settings.firebase_project_id}")
    print(f"Storage Bucket: {settings.firebase_storage_bucket}")
    print(f"Credentials Path: {settings.firebase_credentials_path}")
    
    # Check if credentials file exists
    if not os.path.exists(settings.firebase_credentials_path):
        print(f"❌ Credentials file not found: {settings.firebase_credentials_path}")
        return False
    
    print(f"✅ Credentials file found")
    
    try:
        # Try to initialize Firebase service
        from app.services.firebase import firebase_service
        
        if firebase_service._mock_mode:
            print("⚠️  Firebase is running in mock mode")
            print("   This means the credentials couldn't be loaded properly")
            return False
        else:
            print("✅ Firebase initialized successfully!")
            print("✅ Connected to real Firebase project")
            return True
            
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        return False

async def test_firebase_operations():
    """Test basic Firebase operations"""
    try:
        from app.services.firebase import firebase_service
        
        if firebase_service._mock_mode:
            print("Skipping operations test - running in mock mode")
            return
        
        print("\nTesting Firebase operations...")
        
        # Test create problem
        problem_data = {
            'user_id': 'test-user',
            'status': 'queued',
            'created_at': '2025-08-16T14:40:00.000Z',
            'file_url': 'https://test.com/file.jpg'
        }
        
        problem_id = await firebase_service.create_problem(problem_data)
        print(f"✅ Created test problem: {problem_id}")
        
        # Test get problem
        retrieved = await firebase_service.get_problem(problem_id)
        if retrieved:
            print(f"✅ Retrieved problem: {retrieved['problem_id']}")
        else:
            print("❌ Failed to retrieve problem")
            
        # Test update problem
        await firebase_service.update_problem(problem_id, {'status': 'completed'})
        print(f"✅ Updated problem status")
        
        print("✅ All Firebase operations successful!")
        
    except Exception as e:
        print(f"❌ Firebase operations failed: {e}")

if __name__ == "__main__":
    # Test connection
    success = test_firebase_connection()
    
    if success:
        # Test operations
        import asyncio
        asyncio.run(test_firebase_operations())
    
    print("\n" + "=" * 60)
