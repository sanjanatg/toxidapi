from fastapi import APIRouter, HTTPException, Depends, Header, Request, Response
import logging
import time
from typing import Dict, Any, Optional
import os
from pydantic import BaseModel

from app.api.models import TextRequest, AnalysisResponse
from app.models.gemini_analyzer import GeminiAnalyzer
from app.api.rate_limiter import rate_limit_middleware

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["api"])

# Initialize the analyzer with API key from environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

analyzer = GeminiAnalyzer(api_key)

# Simple in-memory cache for results
result_cache = {}
CACHE_MAX_SIZE = 100

# Optional API key authentication
async def verify_api_key(
    request: Request,
    response: Response,
    x_api_key: Optional[str] = Header(None)
):
    """
    Optional API key verification middleware.
    If API_KEY_REQUIRED is set to True in environment, this will validate the key.
    Also applies rate limiting based on the API key or client IP.
    """
    # Check rate limits first
    await rate_limit_middleware(request, x_api_key)
    
    # Add rate limit headers to response
    if hasattr(request.state, 'rate_limit_headers'):
        for header, value in request.state.rate_limit_headers.items():
            response.headers[header] = value
    
    # Verify API key if required
    if os.environ.get("API_KEY_REQUIRED", "false").lower() == "true":
        if not x_api_key:
            raise HTTPException(
                status_code=401,
                detail="API key is required"
            )
        expected_key = os.environ.get("API_KEY")
        if not expected_key or x_api_key != expected_key:
            raise HTTPException(
                status_code=403,
                detail="Invalid API key"
            )
    return x_api_key

# API endpoint to analyze text
@router.post(
    "/analyze", 
    response_model=AnalysisResponse, 
    status_code=200,
    summary="Analyze text for toxicity, sentiment, and content moderation",
    description="Analyze text using Google's Gemini AI for toxicity, sentiment, and content moderation.",
    response_description="Contains toxicity analysis, sentiment analysis, flagged words, and processing time."
)
async def analyze_endpoint(
    request: TextRequest, 
    request_obj: Request, 
    response: Response,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze text using Google's Gemini AI for toxicity, sentiment, and content moderation.
    
    - **text**: The text to analyze
    
    Returns an AnalysisResponse object containing:
    - toxicity scores
    - sentiment analysis
    - flagged words
    - processing time
    """
    try:
        logger.info(f"Starting analysis request from {request_obj.client.host}")
        logger.info(f"Received text: {request.text[:50]}...")
        
        text = request.text
        start_time = time.time()
        
        # Check cache first
        if text in result_cache:
            logger.info(f"Cache hit for text: {text[:20]}...")
            cached_result = result_cache[text]
            # Update processing time
            cached_result["processing_time"] = time.time() - start_time
            return cached_result
        
        # Analyze text using Gemini
        try:
            logger.info("Calling Gemini analyzer...")
            analysis_result = analyzer.analyze(text)
            logger.info("Analysis completed successfully")
        except Exception as e:
            logger.error(f"Error during Gemini analysis: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error during text analysis: {str(e)}"
            )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Combine results
        result = {
            **analysis_result,
            "processing_time": processing_time,
            "text": text
        }
        
        # Update cache
        if len(result_cache) >= CACHE_MAX_SIZE:
            # Remove oldest entry
            result_cache.pop(next(iter(result_cache)))
        result_cache[text] = result
        
        logger.info(f"Analysis completed in {processing_time:.2f}s")
        
        # Set cache control headers
        response.headers["Cache-Control"] = "public, max-age=86400"  # Cache for 24 hours
        
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions so they keep their status codes
        raise
    except Exception as e:
        logger.error(f"Unexpected error in analyze_endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

# Stats endpoint
@router.get(
    "/stats", 
    status_code=200,
    summary="Get API usage statistics",
    description="Get statistics about API usage, cache size, and other metrics."
)
async def stats_endpoint(
    request: Request,
    response: Response,
    api_key: str = Depends(verify_api_key)
):
    """
    Get API usage statistics.
    
    Returns statistics on API usage, cache size, and other metrics.
    """
    return {
        "cache_size": len(result_cache),
        "cache_max_size": CACHE_MAX_SIZE,
        "analyzer_type": "gemini-2.0-flash"
    }

# Endpoint to flush the cache
@router.post(
    "/cache/flush", 
    status_code=200,
    summary="Flush the result cache",
    description="Clears all cached results. Requires admin API key."
)
async def flush_cache(
    request: Request,
    response: Response,
    api_key: str = Depends(verify_api_key)
):
    """
    Flush the result cache.
    
    Clears all cached results. Requires admin API key.
    """
    # Only allow if admin key is provided
    if os.environ.get("ADMIN_KEY_REQUIRED", "true").lower() == "true":
        if api_key != os.environ.get("ADMIN_API_KEY"):
            raise HTTPException(
                status_code=403,
                detail="Admin API key required for this operation"
            )
    
    global result_cache
    cache_size = len(result_cache)
    result_cache = {}
    
    return {
        "status": "success",
        "message": f"Cache flushed successfully. {cache_size} entries removed."
    }

# Batch analysis endpoint
@router.post(
    "/analyze/batch",
    status_code=200,
    summary="Analyze multiple texts in batch",
    description="Analyze multiple text items at once. Returns analysis results for each text."
)
async def batch_analyze_endpoint(
    request: Dict[str, list],
    request_obj: Request,
    response: Response,
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze multiple texts in batch mode.
    
    - **texts**: List of texts to analyze
    
    Returns a list of analysis results.
    """
    if "texts" not in request or not isinstance(request["texts"], list):
        raise HTTPException(
            status_code=400,
            detail="Request must include a 'texts' field with a list of strings"
        )
        
    batch_size = len(request["texts"])
    if batch_size > 10:
        raise HTTPException(
            status_code=400,
            detail="Batch size limit is 10 texts"
        )
        
    logger.info(f"Batch analysis request with {batch_size} texts")
    start_time = time.time()
    
    results = []
    for text in request["texts"]:
        if not isinstance(text, str):
            continue
            
        try:
            # Check cache first
            if text in result_cache:
                results.append(result_cache[text])
                continue
                
            # Analyze text
            analysis_result = analyzer.analyze(text)
            
            # Combine results
            result = {
                **analysis_result,
                "processing_time": 0.0,  # Will be updated later
                "text": text
            }
            
            # Add to cache
            if len(result_cache) >= CACHE_MAX_SIZE:
                result_cache.pop(next(iter(result_cache)))
            result_cache[text] = result
            
            results.append(result)
        except Exception as e:
            logger.error(f"Error analyzing text in batch: {str(e)}")
            results.append({
                "error": str(e),
                "text": text
            })
    
    # Update processing time
    processing_time = time.time() - start_time
    for result in results:
        if "processing_time" in result:
            result["processing_time"] = processing_time / batch_size
    
    logger.info(f"Batch analysis completed in {processing_time:.2f}s")
    return {"results": results} 