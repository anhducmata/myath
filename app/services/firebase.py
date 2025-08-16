import firebase_admin
from firebase_admin import credentials, firestore, storage, messaging
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Dict, Any, Optional
import logging
import os
from config.settings import settings

logger = logging.getLogger(__name__)


class FirebaseService:
    def __init__(self):
        self._app = None
        self._db = None
        self._bucket = None
        self._mock_mode = True  # Default to mock mode
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # In production, you'll need to replace the firebase-service-account.json 
            # with your actual Firebase service account credentials
            if not os.path.exists(settings.firebase_credentials_path):
                logger.warning("Firebase credentials file not found. Running in mock mode.")
                self._mock_mode = True
                return
                
            # Check if we have valid credentials by attempting to load them
            try:
                cred = credentials.Certificate(settings.firebase_credentials_path)
            except Exception as cred_error:
                logger.warning(f"Invalid Firebase credentials: {cred_error}. Running in mock mode.")
                self._mock_mode = True
                return
                
            if not firebase_admin._apps:
                self._app = firebase_admin.initialize_app(cred, {
                    'storageBucket': settings.firebase_storage_bucket
                })
            else:
                self._app = firebase_admin.get_app()
            
            self._db = firestore.client()
            self._bucket = storage.bucket()
            self._mock_mode = False
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Firebase: {e}. Running in mock mode.")
            self._mock_mode = True
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Firebase ID token and return user info"""
        if self._mock_mode:
            # Return mock user data in development mode
            return {
                'uid': 'mock-user-id',
                'email': 'test@example.com',
                'name': 'Test User'
            }
            
        try:
            from firebase_admin import auth
            decoded_token = auth.verify_id_token(token)
            return {
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name'),
                'verified': decoded_token.get('email_verified', False)
            }
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise ValueError("Invalid token")
    
    async def upload_file(self, file_content: bytes, file_name: str, content_type: str) -> str:
        """Upload file to Firebase Storage and return download URL"""
        if self._mock_mode:
            # Return mock URL in development mode
            logger.info(f"Mock: Uploading file {file_name}")
            return f"https://mock-storage.googleapis.com/problems/{file_name}"
        
        try:
            blob = self._bucket.blob(f"problems/{file_name}")
            blob.upload_from_string(file_content, content_type=content_type)
            blob.make_public()
            return blob.public_url
        except Exception as e:
            # If Firebase Storage fails (e.g., billing not enabled), fall back to local storage
            logger.warning(f"Firebase Storage failed: {e}")
            logger.info("Falling back to local file storage")
            
            # Save to local storage directory
            import os
            storage_dir = "./storage/files"
            os.makedirs(storage_dir, exist_ok=True)
            
            file_path = os.path.join(storage_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Return a local URL
            return f"http://localhost:8000/storage/files/{file_name}"
    
    async def create_problem(self, problem_data: Dict[str, Any]) -> str:
        """Create a problem document in Firestore"""
        if self._mock_mode:
            # Generate mock problem ID
            import uuid
            problem_id = str(uuid.uuid4())
            problem_data['problem_id'] = problem_id
            logger.info(f"Mock: Created problem with ID {problem_id}")
            return problem_id
            
        try:
            doc_ref = self._db.collection('problems').document()
            problem_data['problem_id'] = doc_ref.id
            doc_ref.set(problem_data)
            return doc_ref.id
        except Exception as e:
            logger.error(f"Failed to create problem: {e}")
            raise
    
    async def get_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get problem document from Firestore"""
        if self._mock_mode:
            # Return mock problem data with proper structure
            from datetime import datetime
            return {
                'problem_id': problem_id,
                'user_id': 'dev-user-123',
                'status': 'queued',  # Use valid ProblemStatus enum value
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'file_url': f'https://mock-storage.googleapis.com/problems/{problem_id}.jpg',
                'ocr_result': {
                    'text': 'x^2 + 2x + 1 = 0',
                    'latex': 'x^2 + 2x + 1 = 0',
                    'confidence': 0.95,
                    'method': 'mock'
                }
            }
            
        try:
            doc_ref = self._db.collection('problems').document(problem_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            logger.error(f"Failed to get problem: {e}")
            raise
    
    async def update_problem(self, problem_id: str, updates: Dict[str, Any]) -> None:
        """Update problem document in Firestore"""
        if self._mock_mode:
            logger.info(f"Mock: Updated problem {problem_id} with {updates}")
            return
            
        try:
            doc_ref = self._db.collection('problems').document(problem_id)
            doc_ref.update(updates)
        except Exception as e:
            logger.error(f"Failed to update problem: {e}")
            raise
    
    async def send_notification(self, user_token: str, title: str, body: str, data: Dict[str, str] = None) -> None:
        """Send FCM notification to user"""
        if self._mock_mode:
            logger.info(f"Mock: Sending notification '{title}' to {user_token}")
            return
            
        try:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                token=user_token
            )
            response = messaging.send(message)
            logger.info(f"Notification sent successfully: {response}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")


# Global instance
firebase_service = FirebaseService()
