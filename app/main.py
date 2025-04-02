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
async def root():
    """
    Serves the HTML demo interface for testing the API.
    """
    try:
        # Read the index.html file (demo UI)
        index_html_path = Path(__file__).parent / "static" / "index.html"
        if index_html_path.exists():
            try:
                with open(index_html_path, "r", encoding="utf-8") as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading index.html: {str(e)}")
                # Continue to fallback
                
        # Fallback to embedded HTML if index.html doesn't exist or couldn't be read
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
    
    # Fallback to embedded HTML
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ToxidAPI - Text Analysis with AI</title>
        <style>
            /* Simplified dark theme CSS for fallback */
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #121212;
                color: #FFFFFF;
                margin: 0;
                padding: 20px;
                line-height: 1.6;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #1E1E1E;
                border-radius: 8px;
            }
            h1, h2 { color: #9D4EDD; }
            a { color: #9D4EDD; }
            p { margin-bottom: 16px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ToxidAPI</h1>
            <p>AI-powered text analysis for toxicity, sentiment, and content moderation.</p>
            <h2>Error Loading UI</h2>
            <p>The full UI couldn't be loaded. You can still access the API directly.</p>
            <p>Please check the <a href="/docs">API documentation</a> for more information.</p>
        </div>
    </body>
    </html>
    """

@app.get("/analyze", response_class=HTMLResponse)
async def analyze_page():
    """Serves the analyze page"""
    try:
        analyze_html_path = Path(__file__).parent / "static" / "analyze.html"
        if analyze_html_path.exists():
            with open(analyze_html_path, "r", encoding="utf-8") as file:
                return file.read()
    except Exception as e:
        logger.error(f"Error reading analyze.html: {str(e)}")
        return RedirectResponse(url="/")

@app.get("/docs", response_class=HTMLResponse)
async def docs_page():
    """Serves the documentation page"""
    try:
        docs_html_path = Path(__file__).parent / "static" / "docs.html"
        if docs_html_path.exists():
            with open(docs_html_path, "r", encoding="utf-8") as file:
                return file.read()
    except Exception as e:
        logger.error(f"Error reading docs.html: {str(e)}")
        return RedirectResponse(url="/")

@app.get("/keys", response_class=HTMLResponse)
async def keys_page():
    """Serves the API keys page"""
    try:
        keys_html_path = Path(__file__).parent / "static" / "keys.html"
        if keys_html_path.exists():
            with open(keys_html_path, "r", encoding="utf-8") as file:
                return file.read()
    except Exception as e:
        logger.error(f"Error reading keys.html: {str(e)}")
        return RedirectResponse(url="/")

@app.get("/version", response_class=HTMLResponse)
async def version_page():
    """Serves the API version page"""
    try:
        version_html_path = Path(__file__).parent / "static" / "version.html"
        if version_html_path.exists():
            with open(version_html_path, "r", encoding="utf-8") as file:
                return file.read()
    except Exception as e:
        logger.error(f"Error reading version.html: {str(e)}")
        return RedirectResponse(url="/")

@app.get("/limits", response_class=HTMLResponse)
async def limits_page():
    """Serves the rate limits page"""
    try:
        limits_html_path = Path(__file__).parent / "static" / "limits.html"
        if limits_html_path.exists():
            with open(limits_html_path, "r", encoding="utf-8") as file:
                return file.read()
    except Exception as e:
        logger.error(f"Error reading limits.html: {str(e)}")
        return RedirectResponse(url="/")

@app.get("/signin", response_class=HTMLResponse)
async def signin_redirect():
    """Redirects to login page"""
    return RedirectResponse(url="/login")

@app.get("/signup", response_class=HTMLResponse)
async def signup_page():
    """Redirects to registration page"""
    return RedirectResponse(url="/register")

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Serves the login page"""
    # For now, redirect to home since we haven't created the login page yet
    return RedirectResponse(url="/")

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    """Serves the registration page"""
    # For now, redirect to home since we haven't created the registration page yet
    return RedirectResponse(url="/")

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