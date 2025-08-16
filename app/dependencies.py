from fastapi import Depends, HTTPException, status, Header
from typing import Dict, Any, Optional
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Verify API key authentication
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Check against configured API keys (you can have multiple)
    valid_api_keys = settings.valid_api_keys_list
    if x_api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    # Return user info based on API key
    return {
        'api_key': x_api_key,
        'user_type': 'api_user',
        'permissions': ['upload', 'process', 'retrieve']
    }


# Alias for compatibility
get_current_user = verify_api_key


def verify_file_type(content_type: str) -> bool:
    """Verify if uploaded file type is allowed"""
    from config.settings import settings
    return content_type in settings.allowed_file_types_list


def verify_file_size(file_size: int) -> bool:
    """Verify if uploaded file size is within limits"""
    from config.settings import settings
    return file_size <= settings.max_file_size_bytes
