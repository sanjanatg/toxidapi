from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, inspect, OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
import logging
import time
import json

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./toxidapi.db")
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

# Function to create a fresh connection engine
def create_db_engine():
    """Create a fresh database engine - no connection pooling for serverless"""
    try:
        # For PostgreSQL, use special parameters optimized for serverless
        connect_args = {}
        if DATABASE_URL.startswith("postgres"):
            # Add serverless-friendly parameters
            if "?" in DATABASE_URL:
                db_url = DATABASE_URL + "&statement_timeout=5000&connect_timeout=5"
            else:
                db_url = DATABASE_URL + "?statement_timeout=5000&connect_timeout=5"
                
            logger.info("Creating PostgreSQL engine with serverless optimizations")
        else:
            db_url = DATABASE_URL
            logger.info(f"Creating {db_url.split('://')[0]} engine")
        
        # Create a new engine without connection pooling
        engine = create_engine(
            db_url,
            echo=False,
            poolclass=None,  # Disable connection pooling for serverless
            connect_args=connect_args
        )
        
        # Test connection - quick and simple
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            logger.info("Database connection test successful")
        except Exception as conn_error:
            logger.error(f"Database connection test failed: {str(conn_error)}")
            
        return engine
    except Exception as e:
        logger.error(f"Fatal error creating database engine: {str(e)}")
        # Fall back to SQLite
        logger.warning("Falling back to SQLite in-memory database")
        return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

# Simple function to get a fresh session
def get_db():
    """Get a fresh database session for each request"""
    try:
        # Create a new engine for each session in serverless environment
        engine = create_db_engine()
        
        # Create tables if needed
        try:
            Base.metadata.create_all(bind=engine)
        except Exception as schema_error:
            logger.error(f"Error creating schema: {str(schema_error)}")
        
        # Create a new session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            yield db
        finally:
            db.close()
            engine.dispose()  # Explicitly close all connections
    except Exception as session_error:
        logger.error(f"Session error: {str(session_error)}")
        # If we can't create a real DB session, create an in-memory one
        engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
            engine.dispose()

# Import the NullPool class
from sqlalchemy.pool import NullPool 