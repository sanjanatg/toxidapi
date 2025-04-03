from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.pool import NullPool
import os
from datetime import datetime
import logging
import time
import json
import re
import sys

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Check if we're running in a serverless environment
IS_SERVERLESS = os.getenv("VERCEL") == "1" or "AWS_LAMBDA" in os.environ

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:" if IS_SERVERLESS else "sqlite:///./toxidapi.db")

# Check if the DATABASE_URL is a template variable (${...}) and handle it
if re.match(r'^\${.*}$', DATABASE_URL):
    logger.warning(f"DATABASE_URL contains template variable: {DATABASE_URL}")
    logger.warning("This may indicate environment variables aren't properly configured")
    # Always use in-memory SQLite for serverless environments
    DATABASE_URL = "sqlite:///:memory:"
    logger.info(f"Using in-memory SQLite database")
elif IS_SERVERLESS and DATABASE_URL.startswith("sqlite:///") and not DATABASE_URL.startswith("sqlite:///:memory:"):
    # Force in-memory SQLite for any file-based SQLite in serverless
    logger.warning(f"Converting file-based SQLite to in-memory for serverless environment")
    DATABASE_URL = "sqlite:///:memory:"
else:
    logger.info(f"Database type: {DATABASE_URL.split('://')[0] if '://' in DATABASE_URL else 'unknown'}")

# Create base class for models
Base = declarative_base()

# Define database models
class DBUser(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    tier = Column(String, default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with API keys
    api_keys = relationship("DBAPIKey", back_populates="user", cascade="all, delete-orphan")

class DBAPIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    name = Column(String)
    user_id = Column(String, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)
    
    # Relationship with user
    user = relationship("DBUser", back_populates="api_keys")

# Store in-memory engine globally for serverless
_engine = None
_session_factory = None

def get_global_engine():
    """Get or create a global engine for in-memory SQLite."""
    global _engine, _session_factory
    
    if _engine is None:
        logger.info("Creating global in-memory SQLite engine")
        _engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=NullPool
        )
        
        # Create tables immediately
        Base.metadata.create_all(bind=_engine)
        logger.info("Created tables in global in-memory SQLite database")
        
        # Create session factory
        _session_factory = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    
    return _engine

# Function to create a fresh connection engine
def create_db_engine():
    """Create a fresh database engine with NullPool for serverless"""
    # For in-memory SQLite in serverless environment, use global engine
    if DATABASE_URL == "sqlite:///:memory:" or DATABASE_URL.startswith("sqlite:///:memory:"):
        return get_global_engine()
    
    retry_count = 0
    max_retries = 3
    retry_delay = 1  # seconds
    last_error = None
    
    while retry_count < max_retries:
        try:
            # For PostgreSQL, use special parameters optimized for serverless
            connect_args = {}
            if DATABASE_URL.startswith("postgres"):
                # Build URL with proper parameters
                base_url = DATABASE_URL.split("?")[0] if "?" in DATABASE_URL else DATABASE_URL
                params = ["sslmode=require", "connect_timeout=5"]
                db_url = f"{base_url}?{'&'.join(params)}"
                logger.info("Creating PostgreSQL engine with serverless optimizations")
            else:
                db_url = DATABASE_URL
                if db_url.startswith("sqlite"):
                    connect_args["check_same_thread"] = False
                logger.info(f"Creating {db_url.split('://')[0]} engine")
            
            # Create engine with NullPool - critical for serverless
            engine = create_engine(
                db_url,
                echo=False,
                poolclass=NullPool,  # Explicitly use NullPool for serverless
                connect_args=connect_args
            )
            
            # Test connection - quick and simple
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))  # Use text() for SQLAlchemy 2.0 compatibility
                logger.info("Database connection test successful")
                
                # Ensure tables exist
                Base.metadata.create_all(bind=engine)
                logger.info("Database tables verified/created")
                
                return engine
            except Exception as conn_error:
                logger.error(f"Database connection test failed: {str(conn_error)}")
                last_error = conn_error
                retry_count += 1
                if retry_count < max_retries:
                    logger.info(f"Retrying connection in {retry_delay} seconds... (Attempt {retry_count+1}/{max_retries})")
                    time.sleep(retry_delay)
                continue
                
        except Exception as e:
            logger.error(f"Error creating database engine: {str(e)}")
            last_error = e
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds... (Attempt {retry_count+1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                break
    
    # All attempts failed, fall back to in-memory SQLite
    logger.error(f"All database connection attempts failed after {max_retries} retries. Last error: {str(last_error)}")
    logger.warning("Falling back to SQLite in-memory database")
    return get_global_engine()

# Simple function to get a fresh session
def get_db():
    """Get a fresh database session for each request"""
    global _session_factory
    
    try:
        # For in-memory SQLite, use the global session factory
        if DATABASE_URL == "sqlite:///:memory:" or DATABASE_URL.startswith("sqlite:///:memory:"):
            if _session_factory is None:
                # Initialize if not already done
                get_global_engine()
            
            db = _session_factory()
            try:
                yield db
            finally:
                db.close()
            return
            
        # For other databases, create a new engine for each session in serverless environment
        engine = create_db_engine()
        
        # Create a new session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Verify tables exist before yielding session
        inspector = inspect(engine)
        if "users" not in inspector.get_table_names():
            logger.warning("Tables not found in database, creating them now")
            Base.metadata.create_all(bind=engine)
        
        try:
            yield db
        finally:
            db.close()
            if engine and engine != _engine:  # Don't dispose global engine
                engine.dispose()  # Explicitly close all connections
    except Exception as session_error:
        logger.error(f"Session error: {session_error}")
        # If we can't create a real DB session, create an in-memory one
        engine = get_global_engine()  # Use global engine for consistency
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close() 