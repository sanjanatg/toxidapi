"""
Authentication API routes for ToxidAPI.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging

from app.models.database import get_db
from app.models.user import UserCreate, UserLogin, UserResponse, APIKeyCreate, APIKeyResponse
from app.api.auth import (
    register_user, login_user, create_api_key, 
    get_user_api_keys, delete_api_key,
    get_current_user_from_token
)

# Configure logging
logger = logging.getLogger(__name__)
logger.info("Initializing authentication routes")

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Helper to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Registration endpoint
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db), request: Request = None):
    """Register a new user"""
    logger.info(f"Registration attempt for email: {user.email}")
    try:
        result = register_user(user, db)
        logger.info(f"Registration successful for email: {user.email}")
        return result
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise

# Login endpoint with OAuth2
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Get access token using username (email) and password"""
    logger.info(f"OAuth2 login attempt for username: {form_data.username}")
    try:
        user_login = UserLogin(email=form_data.username, password=form_data.password)
        result = login_user(user_login, db)
        logger.info(f"OAuth2 login successful for username: {form_data.username}")
        return result
    except Exception as e:
        logger.error(f"OAuth2 login failed: {str(e)}")
        raise

# Login endpoint with JSON
@router.post("/login")
async def login_json(user: UserLogin, db: Session = Depends(get_db), request: Request = None):
    """Login with JSON payload"""
    logger.info(f"JSON login attempt for email: {user.email}")
    try:
        result = login_user(user, db)
        logger.info(f"JSON login successful for email: {user.email}")
        return result
    except Exception as e:
        logger.error(f"JSON login failed: {str(e)}")
        raise

# Get user profile
@router.get("/me", response_model=UserResponse)
async def get_user_profile(current_user = Depends(get_current_user)):
    """Get current user profile"""
    logger.info(f"Retrieving profile for user ID: {current_user.id}")
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        tier=current_user.tier,
        created_at=current_user.created_at,
        api_keys=[key.key for key in current_user.api_keys]
    )

# API Key management
@router.post("/api-keys", response_model=APIKeyResponse)
async def create_new_api_key(
    key_data: APIKeyCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new API key for current user"""
    logger.info(f"Creating new API key '{key_data.name}' for user ID: {current_user.id}")
    try:
        result = create_api_key(current_user.id, key_data.name, db)
        logger.info(f"API key created successfully for user ID: {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"API key creation failed: {str(e)}")
        raise

@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all API keys for current user"""
    logger.info(f"Listing API keys for user ID: {current_user.id}")
    try:
        result = get_user_api_keys(current_user.id, db)
        logger.info(f"Retrieved {len(result)} API keys for user ID: {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"API key listing failed: {str(e)}")
        raise

@router.delete("/api-keys/{key_id}", response_model=bool)
async def remove_api_key(
    key_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an API key"""
    logger.info(f"Deleting API key ID: {key_id} for user ID: {current_user.id}")
    try:
        result = delete_api_key(key_id, current_user.id, db)
        if not result:
            logger.warning(f"API key ID: {key_id} not found for user ID: {current_user.id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        logger.info(f"API key ID: {key_id} deleted successfully")
        return True
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API key deletion failed: {str(e)}")
        raise

# Log that routes are registered
logger.info("Auth routes registered successfully") 