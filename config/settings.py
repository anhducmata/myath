from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Firebase
    firebase_project_id: str
    firebase_storage_bucket: str
    firebase_credentials_path: str = "./config/firebase-service-account.json"
    firebase_web_api_key: str = ""
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/v1"
    
    # Task Queue
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # OCR
    mathpix_app_id: str = ""
    mathpix_app_key: str = ""
    tesseract_path: str = "/usr/bin/tesseract"
    
    # Mistral OCR
    mistral_api_key: str = ""
    mistral_ocr_url: str = "https://api.mistral.ai/v1/ocr"
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4"
    
    # File Upload
    max_file_size_mb: int = 10
    allowed_file_types: str = "image/jpeg,image/png,image/gif,application/pdf"
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Authentication
    valid_api_keys: str = "your-api-key-here,another-api-key"  # Comma-separated list
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        return self.allowed_file_types.split(",")
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def valid_api_keys_list(self) -> List[str]:
        return [key.strip() for key in self.valid_api_keys.split(",") if key.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
