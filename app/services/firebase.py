import firebase_admin
from firebase_admin import credentials, firestore, storage, messaging
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Dict, Any, Optional, List
import logging
import os
from config.settings import settings

logger = logging.getLogger(__name__)


class FirebaseService:
    def __init__(self):
        self._app = None
        self._db = None
        self._bucket = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if we have valid credentials
            if not os.path.exists(settings.firebase_credentials_path):
                raise FileNotFoundError(f"Firebase credentials file not found at {settings.firebase_credentials_path}")
                
            # Load credentials
            cred = credentials.Certificate(settings.firebase_credentials_path)
                
            if not firebase_admin._apps:
                self._app = firebase_admin.initialize_app(cred, {
                    'storageBucket': settings.firebase_storage_bucket
                })
            else:
                self._app = firebase_admin.get_app()
            
            self._db = firestore.client()
            self._bucket = storage.bucket()
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    async def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify Firebase ID token and return user info"""
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
        """Upload file to Firebase Storage"""
        try:
            blob = self._bucket.blob(f"problems/{file_name}")
            blob.upload_from_string(file_content, content_type=content_type)
            blob.make_public()
            logger.info(f"File uploaded to Firebase Storage: {file_name}")
            return blob.public_url
        except Exception as e:
            logger.error(f"Failed to upload file to Firebase Storage: {e}")
            raise
    
    async def create_problem(self, problem_data: Dict[str, Any]) -> str:
        """Create a problem document in Firestore"""
        try:
            doc_ref = self._db.collection('problems').document()
            problem_data['problem_id'] = doc_ref.id
            doc_ref.set(problem_data)
            logger.info(f"Created problem with ID {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Failed to create problem: {e}")
            raise
    
    async def get_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get problem document from Firestore"""
        try:
            doc_ref = self._db.collection('problems').document(problem_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                logger.warning(f"Problem {problem_id} not found")
                return None
        except Exception as e:
            logger.error(f"Failed to get problem: {e}")
            raise
    
    async def update_problem(self, problem_id: str, updates: Dict[str, Any]) -> None:
        """Update problem document in Firestore"""
        try:
            doc_ref = self._db.collection('problems').document(problem_id)
            doc_ref.update(updates)
            logger.info(f"Updated problem {problem_id}")
        except Exception as e:
            logger.error(f"Failed to update problem: {e}")
            raise
    
    async def list_user_problems(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """List problems for a user"""
        try:
            # Query problems for the user, ordered by creation date (newest first)
            from google.cloud.firestore_v1.base_query import FieldFilter
            query = (self._db.collection('problems')
                    .where(filter=FieldFilter('user_id', '==', user_id))
                    .order_by('created_at', direction='DESCENDING')
                    .limit(limit)
                    .offset(offset))
            
            docs = query.stream()
            problems = []
            for doc in docs:
                problem_data = doc.to_dict()
                problems.append(problem_data)
            
            logger.info(f"Retrieved {len(problems)} problems for user {user_id}")
            return problems
        except Exception as e:
            logger.error(f"Failed to list user problems: {e}")
            raise

    async def send_notification(self, user_token: str, title: str, body: str, data: Dict[str, str] = None) -> None:
        """Send FCM notification to user"""
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
            raise


# Global instance
firebase_service = FirebaseService()
