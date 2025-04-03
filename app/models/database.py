from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import NullPool
import os
from datetime import datetime
import logging
import time
import json
import re

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./toxidapi.db")

# Check if the DATABASE_URL is a template variable (${...}) and handle it
if re.match(r'^\${.*}$', DATABASE_URL):
    logger.warning(f"DATABASE_URL contains template variable: {DATABASE_URL}")
    logger.warning("This may indicate environment variables aren't properly configured")
    # Use SQLite as fallback
    DATABASE_URL = "sqlite:///./toxidapi.db"
    logger.info(f"Using fallback database: {DATABASE_URL}")
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

# Maximum retry attempts for database connection
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

# Function to create a fresh connection engine
def create_db_engine():
    """Create a fresh database engine with NullPool for serverless"""
    retry_count = 0
    last_error = None
    
    while retry_count < MAX_RETRIES:
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
                if retry_count < MAX_RETRIES:
                    logger.info(f"Retrying connection in {RETRY_DELAY} seconds... (Attempt {retry_count+1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                continue
                
        except Exception as e:
            logger.error(f"Error creating database engine: {str(e)}")
            last_error = e
            retry_count += 1
            if retry_count < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds... (Attempt {retry_count+1}/{MAX_RETRIES})")
                time.sleep(RETRY_DELAY)
            else:
                break
    
    # All attempts failed, fall back to SQLite
    logger.error(f"All database connection attempts failed after {MAX_RETRIES} retries. Last error: {str(last_error)}")
    logger.warning("Falling back to SQLite in-memory database")
    sqlite_engine = create_engine("sqlite:///:memory:", 
                        connect_args={"check_same_thread": False},
                        poolclass=NullPool)
    
    # Create all tables in SQLite
    try:
        Base.metadata.create_all(bind=sqlite_engine)
        logger.info("Created tables in SQLite fallback database")
    except Exception as schema_error:
        logger.error(f"Error creating schema in SQLite: {str(schema_error)}")
    
    return sqlite_engine

# Simple function to get a fresh session
def get_db():
    """Get a fresh database session for each request"""
    engine = None
    try:
        # Create a new engine for each session in serverless environment
        engine = create_db_engine()
        
        # Create a new session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            yield db
        finally:
            db.close()
            if engine:
                engine.dispose()  # Explicitly close all connections
    except Exception as session_error:
        logger.error(f"Session error: {session_error}")
        # If we can't create a real DB session, create an in-memory one
        try:
            in_memory_engine = create_engine(
                "sqlite:///:memory:", 
                connect_args={"check_same_thread": False},
                poolclass=NullPool
            )
            Base.metadata.create_all(bind=in_memory_engine)
            logger.info("Created tables in emergency fallback SQLite database")
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=in_memory_engine)
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
                in_memory_engine.dispose()
        except Exception as fallback_error:
            logger.critical(f"Critical fallback error: {str(fallback_error)}")
            # At this point, we can't do much more
            yield None 