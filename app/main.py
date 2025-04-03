from fastapi import FastAPI, Request, Response, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import logging
import time
from pathlib import Path
import os

# Import the API routers
from app.api.routes import router as api_router
from app.api.auth_routes import router as auth_router
from app.api.rate_limiter import rate_limit_middleware, validate_api_key

# Database session dependency
from app.models.database import get_db

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
app.include_router(auth_router)

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

# Add a special error handler for the root route
@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serves the HTML demo interface for testing the API.
    """
    try:
        # Read the index.html file (demo UI)
        index_html_path = Path(__file__).parent / "static" / "index.html"
        logger.info(f"Attempting to read index.html from {index_html_path}")
        
        if index_html_path.exists():
            logger.info(f"index.html exists at {index_html_path}")
            try:
                with open(index_html_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    logger.info(f"Successfully read index.html ({len(content)} bytes)")
                    return content
            except Exception as e:
                logger.error(f"Error reading index.html: {str(e)}")
                # Continue to fallback
        else:
            logger.warning(f"index.html not found at {index_html_path}")
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
    
    # Fallback to embedded HTML
    logger.warning("Using fallback embedded HTML for root endpoint")
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ToxidAPI - Text Analysis with AI</title>
        <style>
            /* Dark theme CSS */
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
                box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            }
            h1, h2 { color: #9D4EDD; }
            a { color: #9D4EDD; }
            p { margin-bottom: 16px; }
            .status { 
                padding: 10px; 
                border-radius: 4px; 
                margin: 20px 0;
                background-color: rgba(255,53,71,0.1);
                border-left: 4px solid #ff3547;
            }
            .button {
                display: inline-block;
                background-color: #9D4EDD;
                color: white;
                padding: 10px 20px;
                border-radius: 4px;
                text-decoration: none;
                margin-top: 10px;
            }
            .navbar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem;
                border-bottom: 1px solid #333;
                margin-bottom: 2rem;
            }
            .nav-buttons {
                display: flex;
                gap: 1rem;
            }
            .btn {
                padding: 0.5rem 1rem;
                border-radius: 4px;
                text-decoration: none;
                color: white;
            }
            .btn-outline {
                border: 1px solid #444;
            }
            .btn-primary {
                background: #ff3547;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <nav class="navbar">
                <a href="/" style="font-size: 1.5rem; font-weight: bold; color: white; text-decoration: none;">ToxidAPI</a>
                <div class="nav-buttons">
                    <a href="/analyze" class="btn btn-outline">Analyze</a>
                    <a href="/docs" class="btn btn-outline">Docs</a>
                    <a href="/signin" class="btn btn-outline">Sign in</a>
                    <a href="/signup" class="btn btn-primary">Sign up</a>
                </div>
            </nav>
            
            <h1>ToxidAPI</h1>
            <p>AI-powered text analysis for toxicity, sentiment, and content moderation.</p>
            
            <div class="status">
                <h2>Server Status</h2>
                <p>Welcome to ToxidAPI! This is a fallback page - your static files may not be deployed correctly.</p>
            </div>
            
            <p>
                <a href="/analyze" class="button">Try Analysis Demo</a>
                <a href="/docs" class="button">API Documentation</a>
            </p>
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

@app.get("/login", response_class=HTMLResponse)
@app.get("/signin", response_class=HTMLResponse)
async def login_page():
    """Serves the login page"""
    logger.info("Login/signin page requested")
    try:
        login_html_path = Path(__file__).parent / "static" / "login.html"
        logger.info(f"Attempting to read login.html from {login_html_path}")
        
        if login_html_path.exists():
            logger.info(f"login.html exists at {login_html_path}")
            try:
                with open(login_html_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    logger.info(f"Successfully read login.html ({len(content)} bytes)")
                    return content
            except Exception as e:
                logger.error(f"Error reading login.html: {str(e)}")
        else:
            logger.warning(f"login.html not found at {login_html_path}")
    except Exception as e:
        logger.error(f"Error in login_page endpoint: {str(e)}")
    
    logger.warning("Redirecting to root due to login page error")
    return RedirectResponse(url="/")

@app.get("/register", response_class=HTMLResponse)
@app.get("/signup", response_class=HTMLResponse)
async def register_page():
    """Serves the registration page"""
    logger.info("Register/signup page requested")
    try:
        register_html_path = Path(__file__).parent / "static" / "register.html"
        logger.info(f"Attempting to read register.html from {register_html_path}")
        
        if register_html_path.exists():
            logger.info(f"register.html exists at {register_html_path}")
            try:
                with open(register_html_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    logger.info(f"Successfully read register.html ({len(content)} bytes)")
                    return content
            except Exception as e:
                logger.error(f"Error reading register.html: {str(e)}")
        else:
            logger.warning(f"register.html not found at {register_html_path}")
    except Exception as e:
        logger.error(f"Error in register_page endpoint: {str(e)}")
    
    logger.warning("Redirecting to root due to register page error")
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