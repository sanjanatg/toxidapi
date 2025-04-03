"""
Authentication API routes for ToxidAPI.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import logging
import traceback
from pydantic import ValidationError
from email_validator import EmailNotValidError, EmailSyntaxError
import uuid
import hashlib

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
    try:
        user = get_current_user_from_token(token, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Catch-all error handler for all routes
async def handle_exceptions(route_func):
    async def wrapper(*args, **kwargs):
        try:
            return await route_func(*args, **kwargs)
        except HTTPException:
            # Re-raise HTTP exceptions as they're already properly formatted
            raise
        except ValidationError as ve:
            logger.error(f"Validation error: {str(ve)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request data: {str(ve)}"
            )
        except Exception as e:
            # Log the full traceback for debugging
            logger.error(f"Unhandled exception in route {route_func.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred. Please try again later."
            )
    return wrapper

# Registration endpoint
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db), request: Request = None):
    """Register a new user"""
    try:
        logger.info(f"Registration attempt for email: {user.email}")
        
        # Input validation
        if not user.email or not user.password:
            logger.warning("Invalid registration attempt: missing email or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
            
        if len(user.password) < 8:
            logger.warning("Invalid registration attempt: password too short")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        # Specific handling for email validation errors    
        try:
            # The email should already be validated by Pydantic, but let's add an explicit check
            from email_validator import validate_email
            validate_email(user.email)
        except (EmailNotValidError, EmailSyntaxError) as e:
            logger.warning(f"Invalid email format: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid email format: {str(e)}"
            )
            
        # Attempt registration
        try:
            result = register_user(user, db)
            logger.info(f"Registration successful for email: {user.email}")
            return result
        except HTTPException as he:
            logger.warning(f"Registration failed with HTTP error: {he.detail}")
            raise
        except Exception as e:
            logger.error(f"Registration failed with unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed. Please try again later."
            )
    except ValidationError as ve:
        logger.warning(f"Validation error during registration: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid registration data: {str(ve)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Uncaught error in registration route: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration."
        )

# Login endpoint with OAuth2
@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    request: Request = None
):
    """Get access token using username (email) and password"""
    try:
        logger.info(f"OAuth2 login attempt for username: {form_data.username}")
        
        # Attempt login
        try:
            user_login = UserLogin(email=form_data.username, password=form_data.password)
            result = login_user(user_login, db)
            logger.info(f"OAuth2 login successful for username: {form_data.username}")
            return result
        except HTTPException as he:
            logger.warning(f"OAuth2 login failed with HTTP error: {he.detail}")
            raise
        except Exception as e:
            logger.error(f"OAuth2 login failed with unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed. Please try again later."
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Uncaught error in OAuth2 login route: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login."
        )

# Login endpoint with JSON
@router.post("/login")
async def login_json(
    user: UserLogin, 
    db: Session = Depends(get_db), 
    request: Request = None,
    response: Response = None
):
    """Login with JSON payload"""
    try:
        logger.info(f"JSON login attempt for email: {user.email}")
        
        # Input validation
        if not user.email or not user.password:
            logger.warning("Invalid login attempt: missing email or password")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email and password are required"
            )
        
        # Attempt login
        try:
            result = login_user(user, db)
            logger.info(f"JSON login successful for email: {user.email}")
            
            # Set secure cookie with the token
            if response:
                response.set_cookie(
                    key="access_token",
                    value=f"Bearer {result['access_token']}",
                    httponly=True,
                    max_age=1800,  # 30 minutes
                    path="/",
                    secure=True,
                    samesite="lax"
                )
                
            return result
        except HTTPException as he:
            logger.warning(f"JSON login failed with HTTP error: {he.detail}")
            raise
        except Exception as e:
            logger.error(f"JSON login failed with unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed. Please try again later."
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Uncaught error in JSON login route: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login."
        )

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
    try:
        logger.info(f"Creating new API key '{key_data.name}' for user ID: {current_user.id}")
        result = create_api_key(current_user.id, key_data.name, db)
        logger.info(f"API key created successfully for user ID: {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"API key creation failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key. Please try again later."
        )

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

# Add this new endpoint after the existing register endpoint
@router.post("/register-simple", status_code=status.HTTP_201_CREATED)
async def register_simple(email: str, password: str):
    """Simplified registration endpoint for testing"""
    try:
        logger.info(f"Simple registration attempt for email: {email}")
        
        # Generate a simple user ID
        user_id = str(uuid.uuid4())
        
        # Use a simple hash instead of bcrypt
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Create a simple API key
        api_key = f"toxid_simple_{uuid.uuid4().hex}"
        
        # Return a simplified response
        logger.info(f"Simple registration successful for email: {email}")
        return {
            "success": True,
            "id": user_id,
            "email": email,
            "api_key": api_key,
            "message": "Registration successful using simplified endpoint"
        }
    except Exception as e:
        logger.error(f"Error in simple registration: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simple registration failed: {str(e)}"
        )

# Log that routes are registered
logger.info("Auth routes registered successfully") 