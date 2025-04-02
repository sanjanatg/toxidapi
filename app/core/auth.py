from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Dict, Optional, List
import os
import time
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

# API key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Path to the API keys file
API_KEYS_FILE = Path("api_keys.json")

class ApiKey(BaseModel):
    key: str
    user_id: str
    name: str
    created_at: float
    rate_limit: int = 100  # Requests per hour
    is_active: bool = True
    permissions: List[str] = ["analyze"]

class ApiKeyManager:
    def __init__(self):
        self.api_keys: Dict[str, ApiKey] = {}
        self.request_counts: Dict[str, Dict[str, int]] = {}  # key -> {hour -> count}
        self.load_api_keys()
    
    def load_api_keys(self):
        """Load API keys from file"""
        if API_KEYS_FILE.exists():
            try:
                with open(API_KEYS_FILE, "r") as f:
                    keys_data = json.load(f)
                    for key_data in keys_data:
                        key = key_data.pop("key")
                        self.api_keys[key] = ApiKey(key=key, **key_data)
                logger.info(f"Loaded {len(self.api_keys)} API keys")
            except Exception as e:
                logger.error(f"Error loading API keys: {str(e)}")
        else:
            # Create default admin key if no keys exist and ADMIN_API_KEY is set
            admin_key = os.environ.get("ADMIN_API_KEY")
            if admin_key:
                self.api_keys[admin_key] = ApiKey(
                    key=admin_key,
                    user_id="admin",
                    name="Admin Key",
                    created_at=time.time(),
                    rate_limit=1000,
                    permissions=["analyze", "admin"]
                )
                self.save_api_keys()
            else:
                logger.warning("ADMIN_API_KEY environment variable not set. No default admin key created.")
    
    def save_api_keys(self):
        """Save API keys to file"""
        try:
            keys_data = []
            for key, api_key in self.api_keys.items():
                keys_data.append(api_key.dict())
            
            with open(API_KEYS_FILE, "w") as f:
                json.dump(keys_data, f, indent=2)
            logger.info(f"Saved {len(self.api_keys)} API keys")
        except Exception as e:
            logger.error(f"Error saving API keys: {str(e)}")
    
    def validate_key(self, api_key: str) -> Optional[ApiKey]:
        """Validate an API key"""
        if api_key not in self.api_keys:
            return None
        
        key_data = self.api_keys[api_key]
        if not key_data.is_active:
            return None
        
        return key_data
    
    def check_rate_limit(self, api_key: str) -> bool:
        """Check if the API key has exceeded its rate limit"""
        if api_key not in self.api_keys:
            return False
        
        key_data = self.api_keys[api_key]
        current_hour = int(time.time() / 3600)
        
        if api_key not in self.request_counts:
            self.request_counts[api_key] = {}
        
        if current_hour not in self.request_counts[api_key]:
            # Clean up old hours
            self.request_counts[api_key] = {current_hour: 0}
        
        # Increment request count
        self.request_counts[api_key][current_hour] += 1
        
        # Check if rate limit exceeded
        return self.request_counts[api_key][current_hour] <= key_data.rate_limit
    
    def create_api_key(self, user_id: str, name: str, rate_limit: int = 100, permissions: List[str] = ["analyze"]) -> ApiKey:
        """Create a new API key"""
        import secrets
        
        # Generate a random API key
        key = f"toxid-{secrets.token_hex(16)}"
        
        api_key = ApiKey(
            key=key,
            user_id=user_id,
            name=name,
            created_at=time.time(),
            rate_limit=rate_limit,
            permissions=permissions
        )
        
        self.api_keys[key] = api_key
        self.save_api_keys()
        
        return api_key
    
    def revoke_api_key(self, key: str) -> bool:
        """Revoke an API key"""
        if key not in self.api_keys:
            return False
        
        self.api_keys[key].is_active = False
        self.save_api_keys()
        
        return True

# Create a global API key manager
api_key_manager = ApiKeyManager()

async def get_api_key(api_key_header: str = Security(API_KEY_HEADER)) -> ApiKey:
    """Dependency to get and validate API key"""
    if api_key_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    api_key = api_key_manager.validate_key(api_key_header)
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if not api_key_manager.check_rate_limit(api_key_header):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
    
    return api_key

def has_permission(permission: str):
    """Dependency to check if API key has a specific permission"""
    async def check_permission(api_key: ApiKey = Depends(get_api_key)):
        if permission not in api_key.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"API key does not have permission: {permission}",
            )
        return api_key
    return check_permission 