import os
import uuid
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class LocalStorageService:
    """Simple local file storage service for development/testing"""
    
    def __init__(self):
        self.storage_dir = Path("./storage")
        self.problems_dir = self.storage_dir / "problems"
        self.files_dir = self.storage_dir / "files"
        self.db_file = self.storage_dir / "problems.json"
        
        # Create directories
        self.storage_dir.mkdir(exist_ok=True)
        self.problems_dir.mkdir(exist_ok=True)
        self.files_dir.mkdir(exist_ok=True)
        
        # Initialize database file
        if not self.db_file.exists():
            self._save_db({})
    
    def _load_db(self) -> Dict[str, Any]:
        """Load problems database from JSON file"""
        try:
            with open(self.db_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_db(self, data: Dict[str, Any]) -> None:
        """Save problems database to JSON file"""
        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    async def upload_file(self, file_content: bytes, file_name: str, content_type: str) -> str:
        """Upload file to local storage and return file URL"""
        try:
            file_path = self.files_dir / file_name
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Return local file URL
            return f"file://storage/files/{file_name}"
        except Exception as e:
            logger.error(f"File upload failed: {e}")
            raise
    
    async def create_problem(self, problem_data: Dict[str, Any]) -> str:
        """Create a problem document"""
        try:
            problem_id = str(uuid.uuid4())
            problem_data['problem_id'] = problem_id
            
            db = self._load_db()
            db[problem_id] = problem_data
            self._save_db(db)
            
            logger.info(f"Created problem {problem_id}")
            return problem_id
        except Exception as e:
            logger.error(f"Failed to create problem: {e}")
            raise
    
    async def get_problem(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Get problem document"""
        try:
            db = self._load_db()
            return db.get(problem_id)
        except Exception as e:
            logger.error(f"Failed to get problem: {e}")
            raise
    
    async def update_problem(self, problem_id: str, updates: Dict[str, Any]) -> None:
        """Update problem document"""
        try:
            db = self._load_db()
            if problem_id in db:
                db[problem_id].update(updates)
                db[problem_id]['updated_at'] = datetime.utcnow().isoformat()
                self._save_db(db)
                logger.info(f"Updated problem {problem_id}")
            else:
                logger.warning(f"Problem {problem_id} not found for update")
        except Exception as e:
            logger.error(f"Failed to update problem: {e}")
            raise
    
    async def send_notification(self, user_token: str, title: str, body: str, data: Dict[str, str] = None) -> None:
        """Mock notification service"""
        logger.info(f"📱 Notification: {title} - {body} (to: {user_token})")


# Global instance
storage_service = LocalStorageService()
