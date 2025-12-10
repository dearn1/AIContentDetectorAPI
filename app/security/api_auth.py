from fastapi import HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
import secrets
from datetime import datetime, timedelta
from pydantic import BaseModel, validator
import json

# Load environment variables
load_dotenv()

# Environment variable names
API_KEYS_ENV = "API_KEYS"
DEFAULT_RATE_LIMIT = 1000  # Default requests per day

class APIKeyModel(BaseModel):
    """Model for API key configuration"""
    name: str
    key: str
    is_active: bool = True
    rate_limit: int = DEFAULT_RATE_LIMIT
    expires_at: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    @validator('expires_at', pre=True, always=True)
    def set_expires_at(cls, v):
        return v or (datetime.utcnow() + timedelta(days=365))
    
    @property
    def is_valid(self) -> bool:
        return self.is_active and datetime.utcnow() < self.expires_at

def load_api_keys_from_env() -> Dict[str, APIKeyModel]:
    """Load API keys from environment variables"""
    api_keys = {}
    api_keys_json = os.getenv(API_KEYS_ENV, '[]')
    
    try:
        keys_data = json.loads(api_keys_json)
        for key_data in keys_data:
            if not isinstance(key_data, dict):
                continue
                
            # Convert string dates to datetime objects
            for date_field in ['created_at', 'expires_at']:
                if date_field in key_data and isinstance(key_data[date_field], str):
                    key_data[date_field] = datetime.fromisoformat(key_data[date_field])
            
            try:
                key_model = APIKeyModel(**key_data)
                api_keys[key_model.key] = key_model
            except Exception as e:
                print(f"Error loading API key: {e}")
                continue
                
    except json.JSONDecodeError:
        print(f"Warning: Invalid JSON in {API_KEYS_ENV} environment variable")
    
    return api_keys

# Load API keys from environment variables
API_KEYS: Dict[str, APIKeyModel] = load_api_keys_from_env()

# Load environment variables
load_dotenv()

# API Key header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Rate limit tracking (in-memory, consider Redis for production)
RATE_LIMITS: Dict[str, Dict[str, Any]] = {}

def generate_api_key() -> str:
    """Generate a new secure API key"""
    return f"rapidapi_{secrets.token_urlsafe(32)}"

def save_api_keys_to_env():
    """Save API keys to environment variable (for development only)"""
    keys_data = [
        {
            'key': key_data.key,
            'name': key_data.name,
            'is_active': key_data.is_active,
            'rate_limit': key_data.rate_limit,
            'created_at': key_data.created_at.isoformat(),
            'expires_at': key_data.expires_at.isoformat() if key_data.expires_at else None
        }
        for key_data in API_KEYS.values()
    ]
    os.environ[API_KEYS_ENV] = json.dumps(keys_data, default=str)

def create_api_key(name: str, rate_limit: int = DEFAULT_RATE_LIMIT, days_valid: int = 365) -> APIKeyModel:
    """Create and store a new API key"""
    key = generate_api_key()
    api_key = APIKeyModel(
        key=key,
        name=name,
        rate_limit=rate_limit,
        expires_at=datetime.utcnow() + timedelta(days=days_valid)
    )
    API_KEYS[key] = api_key
    save_api_keys_to_env()
    return api_key

def get_api_key(key: str) -> Optional[APIKeyModel]:
    """Get API key from environment variables"""
    return API_KEYS.get(key)

async def validate_api_key(
    api_key: str = Security(api_key_header)
) -> APIKeyModel:
    """
    Validate the API key from the request header
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        APIKeyModel: The validated API key object
        
    Raises:
        HTTPException: If the API key is invalid or rate limit is exceeded
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "API key is missing",
                "code": "missing_api_key",
                "docs": "https://docs.yourapi.com/authentication"
            },
            headers={"WWW-Authenticate": "API-Key"}
        )
    
    # Check API key in memory storage
    api_key_obj = get_api_key(api_key)
    if not api_key_obj or not api_key_obj.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "Invalid or expired API key",
                "code": "invalid_api_key",
                "docs": "https://docs.yourapi.com/authentication"
            },
            headers={"WWW-Authenticate": "API-Key"}
        )
    
    # Check rate limiting
    await check_rate_limit(api_key_obj)
    
    return api_key_obj

async def check_rate_limit(api_key: APIKeyModel) -> None:
    """Check and update rate limiting for the API key"""
    now = datetime.utcnow()
    key = api_key.key
    
    # Initialize rate limit tracking for this key if not exists
    if key not in RATE_LIMITS:
        RATE_LIMITS[key] = {
            'count': 0,
            'reset_time': now + timedelta(hours=24),  # Daily limit
            'daily_limit': api_key.rate_limit
        }
    
    # Reset counter if a new day has started or if the rate limit has changed
    if now > RATE_LIMITS[key]['reset_time'] or \
       RATE_LIMITS[key]['daily_limit'] != api_key.rate_limit:
        RATE_LIMITS[key] = {
            'count': 0,
            'reset_time': now + timedelta(hours=24),
            'daily_limit': api_key.rate_limit
        }
    
    # Check if rate limit exceeded
    if RATE_LIMITS[key]['count'] >= RATE_LIMITS[key]['daily_limit']:
        reset_time = RATE_LIMITS[key]['reset_time']
        retry_after = int((reset_time - now).total_seconds())
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "code": "rate_limit_exceeded",
                "limit": RATE_LIMITS[key]['daily_limit'],
                "remaining": 0,
                "reset": reset_time.isoformat(),
                "retry_after": retry_after,
                "docs": "https://docs.yourapi.com/rate-limiting"
            },
            headers={
                "X-RateLimit-Limit": str(RATE_LIMITS[key]['daily_limit']),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(reset_time.timestamp())),
                "Retry-After": str(retry_after)
            }
        )
    
    # Increment request count
    RATE_LIMITS[key]['count'] += 1

def rate_limit(requests_per_minute: int = 60):
    """
    Decorator for endpoint-specific rate limiting
    
    Args:
        requests_per_minute: Maximum number of requests allowed per minute
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # This is a simplified version. In production, consider using FastAPI-Limiter
            # which integrates with Redis for distributed rate limiting
            return await func(*args, **kwargs)
        return wrapper
    return decorator
