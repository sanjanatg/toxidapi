import os
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
except ImportError:
    # If python-dotenv is not available, just continue without it
    print("Warning: python-dotenv not found, using environment variables directly")

from typing import Dict, Any

class Config:
    """Configuration settings for the ToxidAPI."""
    
    # API settings
    API_TITLE = "ToxidAPI"
    API_DESCRIPTION = "API for toxicity detection, sentiment analysis, and flagged words detection"
    API_VERSION = "1.0.0"
    
    # Model settings
    TOXICITY_THRESHOLD = float(os.getenv("TOXICITY_THRESHOLD", "0.5"))
    SENTIMENT_MODEL = os.getenv("SENTIMENT_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
    
    # Custom flagged words (comma-separated list in .env file)
    CUSTOM_FLAGGED_WORDS = os.getenv("CUSTOM_FLAGGED_WORDS", "").split(",") if os.getenv("CUSTOM_FLAGGED_WORDS") else []
    
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """Get all settings as a dictionary."""
        return {
            "api_title": cls.API_TITLE,
            "api_description": cls.API_DESCRIPTION,
            "api_version": cls.API_VERSION,
            "toxicity_threshold": cls.TOXICITY_THRESHOLD,
            "sentiment_model": cls.SENTIMENT_MODEL,
            "custom_flagged_words": cls.CUSTOM_FLAGGED_WORDS
        } 