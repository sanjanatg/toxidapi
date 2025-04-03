from datetime import datetime, timedelta
from typing import Optional, List
import uuid
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:
    def __init__(self, email: str, password: str):
        self.id = str(uuid.uuid4())
        self.email = email
        self.hashed_password = pwd_context.hash(password)
        self.created_at = datetime.utcnow()
        self.api_keys: List[APIKey] = []
        self.tier = "free"  # free, pro, enterprise
        self.is_active = True

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

class APIKey:
    def __init__(self, user_id: str, name: str = "Default"):
        self.id = str(uuid.uuid4())
        self.key = f"toxid_{uuid.uuid4().hex}"
        self.user_id = user_id
        self.name = name
        self.created_at = datetime.utcnow()
        self.last_used = None
        self.is_active = True
        self.requests_this_hour = 0
        self.last_reset = datetime.utcnow()

    def reset_counter(self):
        """Reset the request counter if an hour has passed"""
        now = datetime.utcnow()
        if now - self.last_reset > timedelta(hours=1):
            self.requests_this_hour = 0
            self.last_reset = now

    def increment_usage(self):
        """Increment the request counter"""
        self.reset_counter()  # Check if we need to reset first
        self.requests_this_hour += 1
        self.last_used = datetime.utcnow()

# User models
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword"
            }
        }

class UserLogin(UserBase):
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword"
            }
        }

class UserResponse(UserBase):
    id: str
    tier: str
    created_at: datetime
    api_keys: List[str] = []
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "email": "user@example.com",
                "tier": "free",
                "created_at": "2023-01-01T00:00:00",
                "api_keys": ["toxid_a1b2c3d4e5f6"]
            }
        }

# API Key models
class APIKeyCreate(BaseModel):
    name: str = Field(..., description="A friendly name for this API key")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "My App"
            }
        }

class APIKeyResponse(BaseModel):
    id: str
    key: str
    name: str
    created_at: datetime
    last_used: Optional[datetime] = None
    requests_this_hour: int = 0
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "key": "toxid_a1b2c3d4e5f6",
                "name": "My App",
                "created_at": "2023-01-01T00:00:00",
                "last_used": "2023-01-01T01:00:00",
                "requests_this_hour": 42
            }
        } 