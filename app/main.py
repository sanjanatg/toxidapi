from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import logging
import time
from pathlib import Path
import os

# Import the API routers
from app.api.routes import router as api_router
from app.api.rate_limiter import rate_limit_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ToxidAPI",
    description="""
    AI-powered API for analyzing text toxicity, sentiment, and content moderation.
    Powered by Google's Gemini AI for accurate and efficient analysis.
    
    ## Features
    
    - **Toxicity Analysis**: Detect toxic content with scores for multiple categories
    - **Sentiment Analysis**: Determine positive, negative, or neutral sentiment
    - **Content Moderation**: Identify and categorize flagged words
    
    ## API Versioning
    
    The API is versioned through the URL path:
    - v1: `/api/v1/analyze` (Deprecated)
    - v2: `/api/v2/analyze` (Current)
    
    ## Authentication
    
    API keys are required for all endpoints. Include your API key in the `X-API-Key` header.
    
    ## Rate Limiting
    
    Rate limits are applied per API key:
    - Free tier: 100 requests/hour
    - Pro tier: 1000 requests/hour
    
    ## API Usage
    
    Use the `/api/v2/analyze` endpoint to analyze text content:
    
    ```
    POST /api/v2/analyze
    {
        "text": "Your text here"
    }
    ```
    
    For detailed documentation, see the [API Documentation](/api) or [Markdown Docs](/static/api_docs.md).
    """,
    version="2.0.0",
    docs_url=None,
    redoc_url="/docs",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include API routes
app.include_router(api_router)

# Add middleware to measure processing time
@app.middleware("http")
async def process_middleware(request: Request, call_next):
    # Measure processing time
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Add processing time header
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
            
    return response

# Custom Swagger UI
@app.get("/api", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API Documentation",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

# Root endpoint redirects to demo page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    """
    Root endpoint to serve demo page.
    
    Returns:
        HTML: Demo interface for ToxidAPI
    """
    try:
        # Try to read modern.html first (our new UI)
        html_path = Path(__file__).parent / "static" / "modern.html"
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        try:
            # Fallback to simple.html
            html_path = Path(__file__).parent / "static" / "simple.html"
            with open(html_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            # Fallback to embedded HTML if all else fails
            return """
            <!DOCTYPE html>
            <html>
                <head>
                    <title>ToxidAPI Demo</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                </head>
                <body>
                    <h1>ToxidAPI Demo</h1>
                    <p>The demo interface is not available. Please check the <a href="/docs">API documentation</a>.</p>
                </body>
            </html>
            """

# Health check endpoint
@app.get("/health", include_in_schema=False)
async def health_check():
    """
    Simple health check endpoint to verify the API is online.
    """
    try:
        return {
            "status": "online",
            "version": app.version,
            "api_version": "v2",
            "model": os.getenv("SENTIMENT_MODEL", "default")
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return {
            "status": "degraded",
            "error": str(e)
        }

# Documentation redirection
@app.get("/swagger", include_in_schema=False)
async def swagger_ui_redirect():
    return RedirectResponse(url="/api")

# API specification as JSON
@app.get("/api.json", include_in_schema=False)
async def api_spec():
    return RedirectResponse(url="/openapi.json")

# Update the __init__.py file to make imports easier
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 