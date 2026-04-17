from fastapi import Header, HTTPException, Depends
from typing import Optional
from .config import settings


def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")) -> str:
    """
    Verify the API key from the request header.
    Returns the user_id if valid.
    Raises HTTPException(401) if invalid or missing.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing X-API-Key header"
        )
    
    if x_api_key != settings.AGENT_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # In production, you might extract user_id from the API key or a separate header
    # For now, we'll use a simple approach - derive user_id from the key
    return "default_user"


def get_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-ID")) -> str:
    """
    Extract user ID from header (optional).
    If not provided, returns default user.
    """
    return x_user_id or "default_user"