#!/usr/bin/env python3
"""
Firebase Connection Test Script
Tests the connection to your Firebase project with real credentials
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firebase_credentials():
    """Test if Firebase credentials are valid"""
    print("🔥 Testing Firebase Connection")
    print("=" * 50)
    
    # Check if credentials file exists
    cred_path = settings.firebase_credentials_path
    print(f"📁 Credentials path: {cred_path}")
    
    if not os.path.exists(cred_path):
        print("❌ Credentials file not found!")
        return False
    
    # Check if credentials are valid JSON
    try:
        with open(cred_path, 'r') as f:
            creds = json.load(f)
        print("✅ Credentials file is valid JSON")
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials file: {e}")
        return False
    
    # Check required fields
    required_fields = ['type', 'project_id', 'private_key', 'client_email']
    missing_fields = []
    
    for field in required_fields:
        if field not in creds:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing required fields: {missing_fields}")
        return False
    
    print("✅ All required fields present")
    
    # Check if it's still the demo/mock credentials
    if creds.get('private_key_id') == 'demo-key-id':
        print("⚠️  Still using mock credentials - replace with real Firebase service account key")
        return False
    
    print(f"✅ Project ID: {creds['project_id']}")
    print(f"✅ Client Email: {creds['client_email']}")
    
    return True

def test_firebase_connection():
    """Test actual Firebase connection"""
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, storage
        
        print("\n🔗 Testing Firebase Connection")
        print("=" * 50)
        
        # Initialize Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            app = firebase_admin.initialize_app(cred, {
                'storageBucket': settings.firebase_storage_bucket
            })
        else:
            app = firebase_admin.get_app()
        
        print("✅ Firebase Admin SDK initialized")
        
        # Test Firestore
        try:
            db = firestore.client()
            # Try to get a collection (this will create it if it doesn't exist)
            test_doc = db.collection('test').document('connection_test')
            test_doc.set({
                'test': True,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            print("✅ Firestore connection successful")
            
            # Clean up test document
            test_doc.delete()
            
        except Exception as e:
            print(f"❌ Firestore connection failed: {e}")
            return False
        
        # Test Storage
        try:
            bucket = storage.bucket()
            print(f"✅ Storage bucket connected: {bucket.name}")
        except Exception as e:
            print(f"❌ Storage connection failed: {e}")
            return False
        
        print("\n🎉 All Firebase services connected successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Firebase Connection Test")
    print("=" * 50)
    
    # Test credentials file
    if not test_firebase_credentials():
        print("\n💡 To fix this:")
        print("1. Go to https://console.firebase.google.com/")
        print("2. Select your project: fir-demo-project")
        print("3. Go to Project Settings → Service Accounts")
        print("4. Click 'Generate new private key'")
        print("5. Download the JSON file")
        print("6. Replace config/firebase-service-account.json with the downloaded file")
        return
    
    # Test actual connection
    if test_firebase_connection():
        print("\n🚀 Firebase is ready for production use!")
    else:
        print("\n🔧 Firebase connection issues - check project settings")

if __name__ == "__main__":
    main()
