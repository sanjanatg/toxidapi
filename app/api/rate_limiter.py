"""
Rate limiting module for ToxidAPI.
Implements rate limiting using Redis for persistent storage.
"""

import time
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException
import os
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

# In-memory store for fallback when Redis is unavailable
in_memory_store = {}

# Default settings
DEFAULT_RATE_LIMIT = int(os.getenv("RATE_LIMIT", "100"))  # requests per time window
DEFAULT_RATE_WINDOW = int(os.getenv("RATE_WINDOW", "3600"))  # seconds (1 hour)
PRO_RATE_LIMIT = int(os.getenv("PRO_RATE_LIMIT", "1000"))  # requests per time window for pro users

# Redis client will be initialized later if Redis is available
redis_client = None

# Try to import Redis and connect safely, but don't crash if it's not available
try:
    import redis
    # Redis configuration
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    try:
        redis_client = redis.from_url(REDIS_URL)
        # Test connection
        redis_client.ping()
        logger.info("Successfully connected to Redis")
    except Exception as e:
        logger.warning(f"Failed to connect to Redis: {str(e)}. Using in-memory fallback.")
        redis_client = None
except ImportError:
    logger.warning("Redis package not installed. Using in-memory fallback for rate limiting.")
    redis_client = None

def get_client_identifier(request: Request, api_key: Optional[str] = None) -> str:
    """
    Get a unique identifier for the client, preferring API key if available.
    
    Args:
        request: The FastAPI request object
        api_key: The API key from the X-API-Key header
        
    Returns:
        A string identifier for rate limiting
    """
    if api_key:
        # If API key is provided, use it as the identifier
        return f"key:{api_key}"
    
    # Otherwise, use the client IP
    try:
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    except Exception:
        # Fallback if client info can't be accessed
        return "ip:unknown"

def get_rate_limit(api_key: Optional[str] = None) -> Tuple[int, int]:
    """
    Get rate limit and window for the client.
    
    Args:
        api_key: Optional API key
        
    Returns:
        Tuple of (rate_limit, window_seconds)
    """
    if api_key and redis_client:
        try:
            # Check if this is a pro API key
            key_data = redis_client.get(f"api_key:{api_key}")
            if key_data:
                key_info = json.loads(key_data)
                if key_info.get("tier") == "pro":
                    return PRO_RATE_LIMIT, DEFAULT_RATE_WINDOW
        except Exception as e:
            logger.error(f"Error getting rate limit: {str(e)}")
    
    return DEFAULT_RATE_LIMIT, DEFAULT_RATE_WINDOW

def check_rate_limit(identifier: str, limit: int, window: int) -> Tuple[bool, int, int, int]:
    """
    Check if the client has exceeded their rate limit.
    
    Args:
        identifier: Client identifier
        limit: Rate limit
        window: Time window in seconds
        
    Returns:
        Tuple of (is_allowed, remaining_requests, limit, reset_time)
    """
    # Use Redis if available
    if redis_client:
        try:
            now = datetime.utcnow()
            key = f"rate_limit:{identifier}"
            
            # Get current usage
            usage_data = redis_client.get(key)
            if not usage_data:
                # Initialize usage data
                usage_data = {
                    "count": 1,
                    "reset_time": (now + timedelta(seconds=window)).timestamp()
                }
                redis_client.setex(key, window, json.dumps(usage_data))
                return True, limit - 1, limit, window
            
            usage = json.loads(usage_data)
            
            # Check if window has expired
            if now.timestamp() > usage["reset_time"]:
                # Reset usage
                usage = {
                    "count": 1,
                    "reset_time": (now + timedelta(seconds=window)).timestamp()
                }
                redis_client.setex(key, window, json.dumps(usage))
                return True, limit - 1, limit, window
            
            # Check if limit exceeded
            if usage["count"] >= limit:
                reset_time = int(usage["reset_time"] - now.timestamp())
                return False, 0, limit, reset_time
            
            # Increment usage
            usage["count"] += 1
            redis_client.setex(key, window, json.dumps(usage))
            return True, limit - usage["count"], limit, int(usage["reset_time"] - now.timestamp())
        except Exception as e:
            logger.error(f"Redis error in check_rate_limit: {str(e)}")
            # Fall back to in-memory rate limiting
    
    # In-memory fallback
    current_time = int(time.time())
    
    # Initialize if not exists
    if identifier not in in_memory_store:
        in_memory_store[identifier] = {
            "count": 1,
            "reset_time": current_time + window
        }
        return True, limit - 1, limit, window
    
    # Check if window has expired
    if current_time > in_memory_store[identifier]["reset_time"]:
        # Reset usage
        in_memory_store[identifier] = {
            "count": 1,
            "reset_time": current_time + window
        }
        return True, limit - 1, limit, window
    
    # Check if limit exceeded
    if in_memory_store[identifier]["count"] >= limit:
        reset_time = in_memory_store[identifier]["reset_time"] - current_time
        return False, 0, limit, reset_time
    
    # Increment usage
    in_memory_store[identifier]["count"] += 1
    return True, limit - in_memory_store[identifier]["count"], limit, in_memory_store[identifier]["reset_time"] - current_time

async def rate_limit_middleware(request: Request, api_key: Optional[str] = None):
    """
    FastAPI dependency for rate limiting.
    
    Args:
        request: The FastAPI request object
        api_key: Optional API key from authentication
        
    Returns:
        None if allowed, raises HTTPException if rate limited
        
    Raises:
        HTTPException: When the client exceeds rate limits
    """
    try:
        # Skip rate limiting for certain paths
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json", "/"]:
            return
        
        # Get the client identifier
        identifier = get_client_identifier(request, api_key)
        
        # Get rate limit settings
        limit, window = get_rate_limit(api_key)
        
        # Check rate limit
        is_allowed, remaining, limit, reset = check_rate_limit(identifier, limit, window)
        
        # Add rate limit headers
        request.state.rate_limit_headers = {
            "X-Rate-Limit-Limit": str(limit),
            "X-Rate-Limit-Remaining": str(remaining),
            "X-Rate-Limit-Reset": str(reset)
        }
        
        # Raise exception if rate limited
        if not is_allowed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "too_many_requests",
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": f"Rate limit exceeded. Try again in {reset} seconds.",
                    "details": {
                        "limit": limit,
                        "remaining": 0,
                        "reset": reset
                    }
                }
            )
    except Exception as e:
        # Log but don't crash the application
        logger.error(f"Error in rate limiting middleware: {str(e)}")
        # Still allow the request to continue
        return 