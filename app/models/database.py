from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
import logging
import time
import json

# Configure logging
logger = logging.getLogger(__name__)

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./toxidapi.db")

# For PostgreSQL with SSL (required for Neon and other cloud providers)
if DATABASE_URL.startswith("postgres"):
    # Add SSL parameters if not already present
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"
    logger.info(f"Using PostgreSQL connection with sslmode=require")

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

# Functions to handle database connections with retries
def create_db_engine():
    """Create database engine with retries for cloud environments like Vercel"""
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting database connection (attempt {attempt+1}/{max_retries})")
            # Mask the connection string password for logging
            log_url = DATABASE_URL.split("://")
            if len(log_url) > 1 and "@" in log_url[1]:
                auth_part = log_url[1].split("@")[0]
                if ":" in auth_part:
                    # Mask the password
                    masked_url = log_url[0] + "://" + auth_part.split(":")[0] + ":***@" + log_url[1].split("@")[1]
                    logger.info(f"Database provider: {masked_url.split('://')[0]}")
            
            # Create the engine
            engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
            
            # Test the connection
            connection = engine.connect()
            connection.close()
            
            logger.info("Database connection established successfully")
            return engine
        
        except Exception as e:
            logger.error(f"Database connection error (attempt {attempt+1}): {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                logger.error("All database connection attempts failed")
                # Fallback to SQLite
                logger.warning("Falling back to SQLite database")
                sqlite_url = "sqlite:///./fallback.db"
                return create_engine(sqlite_url)

# Create SQLAlchemy engine and session
try:
    engine = create_db_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.critical(f"Critical database initialization error: {str(e)}")
    # Emergency fallback
    fallback_url = "sqlite:///./emergency.db"
    engine = create_engine(fallback_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.warning(f"Using emergency fallback database: {fallback_url}")

# Function to get a database session
def get_db():
    """Get a database session with error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

# Create tables
def create_tables():
    """Create database tables with error handling"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        logger.error("Application may not function correctly")

# Initialize database on import
create_tables() 