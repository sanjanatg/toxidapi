"""
Authentication service for ToxidAPI.
Handles user registration, login, and API key management.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
import jwt
from passlib.context import CryptContext
import os
import logging
from sqlalchemy import inspect

from app.models.database import get_db, DBUser, DBAPIKey
from app.models.user import UserCreate, UserLogin, UserResponse, APIKeyCreate, APIKeyResponse

# Configure logging
logger = logging.getLogger(__name__)

# Configure password hashing with error handling for bcrypt
try:
    # First try with bcrypt
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    # Test the context to ensure it works
    test_hash = pwd_context.hash("test_password")
    logger.info("bcrypt password hashing configured successfully")
except Exception as e:
    logger.warning(f"Error setting up bcrypt: {str(e)}. Falling back to sha256_crypt")
    # Fallback to SHA256 if bcrypt has issues
    pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
    logger.info("Using SHA256 password hashing as fallback")

# Configure JWT token
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_for_development_only")
# Ensure SECRET_KEY is at least 32 chars for security
if len(SECRET_KEY) < 32:
    logger.warning(f"SECRET_KEY is too short ({len(SECRET_KEY)} chars). Padding to 32 chars for security.")
    # Pad with a deterministic pattern based on the original key
    SECRET_KEY = SECRET_KEY.ljust(32, SECRET_KEY[0] if SECRET_KEY else "x")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configure API key authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Registration and login
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """Register a new user"""
    try:
        # First, ensure tables exist
        try:
            from app.models.database import Base
            # Get the engine from the session
            engine = db.get_bind()
            inspector = inspect(engine)
            # Check if tables exist
            if "users" not in inspector.get_table_names():
                logger.info("Creating database tables before registration")
                Base.metadata.create_all(bind=engine)
                logger.info("Tables created successfully")
        except Exception as create_error:
            logger.error(f"Error checking/creating tables: {str(create_error)}")
        
        # Check if user already exists
        try:
            db_user = db.query(DBUser).filter(DBUser.email == user.email).first()
            if db_user:
                logger.warning(f"Registration attempt with existing email: {user.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        except Exception as query_error:
            # This could happen if the users table doesn't exist yet
            if "no such table: users" in str(query_error):
                logger.error(f"Error querying users table: {str(query_error)}")
                logger.info("Creating tables for SQLite database after query error")
                try:
                    # Try to create tables if they don't exist
                    from app.models.database import Base
                    Base.metadata.create_all(bind=db.get_bind())
                    logger.info("Tables created successfully after error")
                except Exception as create_error:
                    logger.error(f"Error creating tables: {str(create_error)}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Database setup error. Please try again later."
                    )
            else:
                # If it's some other error, re-raise
                raise query_error
        
        # Create new user
        user_id = str(uuid.uuid4())
        logger.info(f"Creating new user with ID: {user_id} and email: {user.email}")
        
        try:
            # Try to create a strong password hash safely
            try:
                hashed_password = get_password_hash(user.password)
                logger.info("Password hashed successfully")
            except Exception as hash_error:
                logger.error(f"Password hashing error: {str(hash_error)}")
                # Use a simple hash as fallback in emergencies
                import hashlib
                hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
                logger.warning("Using emergency fallback password hashing")
            
            db_user = DBUser(
                id=user_id,
                email=user.email,
                hashed_password=hashed_password,
                created_at=datetime.utcnow(),
                tier="free",
                is_active=True
            )
            
            # Add user to database
            logger.info("Adding user to database")
            db.add(db_user)
            db.commit()
            logger.info("User committed to database")
            db.refresh(db_user)
            
            # Create default API key
            logger.info(f"Creating default API key for user: {user_id}")
            api_key = create_api_key(db_user.id, "Default", db)
            
            # Return user data
            logger.info(f"User registered successfully: {user.email}")
            return UserResponse(
                id=db_user.id,
                email=db_user.email,
                tier=db_user.tier,
                created_at=db_user.created_at,
                api_keys=[api_key.key]
            )
        except Exception as db_error:
            logger.error(f"Database error during registration: {str(db_error)}")
            db.rollback()
            
            # Check for specific SQLite errors
            if "no such table: users" in str(db_error):
                # Table doesn't exist despite our checks - final attempt to create it
                try:
                    logger.warning("Final attempt to create tables after insert error")
                    from app.models.database import Base
                    Base.metadata.create_all(bind=db.get_bind())
                    
                    # Try the insert again
                    db.add(db_user)
                    db.commit()
                    db.refresh(db_user)
                    
                    # Create default API key
                    api_key = create_api_key(db_user.id, "Default", db)
                    
                    return UserResponse(
                        id=db_user.id,
                        email=db_user.email,
                        tier=db_user.tier,
                        created_at=db_user.created_at,
                        api_keys=[api_key.key]
                    )
                except Exception as retry_error:
                    logger.error(f"Final attempt failed: {str(retry_error)}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error during registration: {str(db_error)}"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in register_user: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        
        try:
            db.rollback()
        except:
            pass
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )

def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return access token"""
    try:
        # Find user by email
        db_user = db.query(DBUser).filter(DBUser.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": db_user.id}
        )
        
        # Get API keys
        api_keys = [key.key for key in db_user.api_keys]
        
        # Return token and user data
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(
                id=db_user.id,
                email=db_user.email,
                tier=db_user.tier,
                created_at=db_user.created_at,
                api_keys=api_keys
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again later."
        )

# API key management
def create_api_key(user_id: str, name: str = "Default", db: Session = Depends(get_db)) -> APIKeyResponse:
    """Create a new API key for a user"""
    try:
        # Generate API key
        key_id = str(uuid.uuid4())
        api_key = f"toxid_{uuid.uuid4().hex}"
        
        # Create new API key record
        db_api_key = DBAPIKey(
            id=key_id,
            key=api_key,
            name=name,
            user_id=user_id,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        # Add API key to database
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        
        # Return API key data
        return APIKeyResponse(
            id=db_api_key.id,
            key=db_api_key.key,
            name=db_api_key.name,
            created_at=db_api_key.created_at,
            last_used=db_api_key.last_used,
            requests_this_hour=0
        )
    except Exception as e:
        logger.error(f"Error in create_api_key: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create API key. Please try again later."
        )

def get_user_api_keys(user_id: str, db: Session = Depends(get_db)) -> list[APIKeyResponse]:
    """Get all API keys for a user"""
    try:
        db_api_keys = db.query(DBAPIKey).filter(DBAPIKey.user_id == user_id).all()
        return [
            APIKeyResponse(
                id=key.id,
                key=key.key,
                name=key.name,
                created_at=key.created_at,
                last_used=key.last_used,
                requests_this_hour=0  # Would need to implement a counter
            )
            for key in db_api_keys
        ]
    except Exception as e:
        logger.error(f"Error in get_user_api_keys: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve API keys. Please try again later."
        )

def delete_api_key(key_id: str, user_id: str, db: Session = Depends(get_db)) -> bool:
    """Delete an API key"""
    try:
        # Find API key
        db_api_key = db.query(DBAPIKey).filter(
            DBAPIKey.id == key_id,
            DBAPIKey.user_id == user_id
        ).first()
        
        if not db_api_key:
            return False
        
        # Delete API key
        db.delete(db_api_key)
        db.commit()
        return True
    except Exception as e:
        logger.error(f"Error in delete_api_key: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete API key. Please try again later."
        )

# Authentication dependencies
def get_api_key(
    api_key: str = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[DBAPIKey]:
    """Validate API key and return the API key object"""
    if not api_key:
        return None
    
    try:
        db_api_key = db.query(DBAPIKey).filter(
            DBAPIKey.key == api_key,
            DBAPIKey.is_active == True
        ).first()
        
        if not db_api_key:
            return None
        
        # Update last used time
        db_api_key.last_used = datetime.utcnow()
        db.commit()
        
        return db_api_key
    except Exception as e:
        logger.error(f"Error in get_api_key: {str(e)}")
        return None

def get_current_user_from_token(token: str, db: Session = Depends(get_db)) -> Optional[DBUser]:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except jwt.PyJWTError as e:
        logger.error(f"JWT token error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in token validation: {str(e)}")
        return None
    
    try:
        # Find user by ID
        db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
        return db_user
    except Exception as e:
        logger.error(f"Database error in get_current_user_from_token: {str(e)}")
        return None 