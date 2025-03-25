"""
Rate limiting module for ToxidAPI.
Implements in-memory rate limiting for API endpoints.
"""

import time
from typing import Dict, Tuple, Optional
from fastapi import Request, HTTPException
import os

# Rate limit configuration
DEFAULT_RATE_LIMIT = int(os.environ.get("RATE_LIMIT", "100"))  # requests per time window
DEFAULT_RATE_WINDOW = int(os.environ.get("RATE_WINDOW", "3600"))  # seconds (1 hour)

# Storage for rate limiting (in-memory)
# In production, consider using Redis or another external store
# Format: {key: [(timestamp1, count1), (timestamp2, count2), ...]}
rate_limit_store: Dict[str, list] = {}


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
    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"


def check_rate_limit(
    identifier: str, 
    limit: int = DEFAULT_RATE_LIMIT,
    window: int = DEFAULT_RATE_WINDOW
) -> Tuple[bool, int, int, int]:
    """
    Check if a request should be rate limited.
    
    Args:
        identifier: Client identifier (API key or IP)
        limit: Maximum number of requests allowed in the time window
        window: Time window in seconds
        
    Returns:
        Tuple of (is_allowed, remaining, limit, reset)
    """
    current_time = int(time.time())
    
    # Initialize if not exists
    if identifier not in rate_limit_store:
        rate_limit_store[identifier] = []
    
    # Clean up old entries
    rate_limit_store[identifier] = [
        (ts, count) for ts, count in rate_limit_store[identifier]
        if current_time - ts < window
    ]
    
    # Calculate total count in the current time window
    total_count = sum(count for _, count in rate_limit_store[identifier])
    
    # Check if over limit
    if total_count >= limit:
        # Calculate reset time
        if rate_limit_store[identifier]:
            oldest_ts = min(ts for ts, _ in rate_limit_store[identifier])
            reset_time = oldest_ts + window - current_time
        else:
            reset_time = window
            
        return False, 0, limit, reset_time
    
    # Record this request
    rate_limit_store[identifier].append((current_time, 1))
    
    # Calculate remaining
    remaining = limit - (total_count + 1)
    
    # Calculate reset time from now
    reset_time = window
    
    return True, remaining, limit, reset_time


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
    # Skip rate limiting for certain paths
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return
    
    # Get the client identifier
    identifier = get_client_identifier(request, api_key)
    
    # Apply different rate limits based on authentication
    if api_key:
        # Authenticated clients get higher limits
        limit = int(os.environ.get("AUTH_RATE_LIMIT", "1000"))
        window = int(os.environ.get("AUTH_RATE_WINDOW", "3600"))
    else:
        # Unauthenticated clients get lower limits
        limit = DEFAULT_RATE_LIMIT
        window = DEFAULT_RATE_WINDOW
    
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
            detail=f"Rate limit exceeded. Try again in {reset} seconds."
        ) 