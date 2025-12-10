from sqlalchemy import Column, String, Boolean, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime, timedelta

Base = declarative_base()

class APIKey(Base):
    """Model for storing API keys"""
    __tablename__ = "api_keys"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=365))
    rate_limit = Column(Integer, default=1000)  # Requests per day
    
    @property
    def is_valid(self):
        return self.is_active and datetime.utcnow() < self.expires_at
    
    @classmethod
    def generate_key(cls, name: str, rate_limit: int = 1000, days_valid: int = 365):
        """Generate a new API key"""
        from app.security.api_auth import generate_api_key
        return cls(
            key=generate_api_key(),
            name=name,
            rate_limit=rate_limit,
            expires_at=datetime.utcnow() + timedelta(days=days_valid)
        )
