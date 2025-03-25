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
    
    ## API Usage
    
    Use the `/api/analyze` endpoint to analyze text content:
    
    ```
    POST /api/analyze
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
    # Read the simple.html file
    simple_html_path = Path(__file__).parent / "static" / "simple.html"
    if simple_html_path.exists():
        with open(simple_html_path, "r") as file:
            return file.read()
    else:
        # Fallback to embedded HTML
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ToxidAPI - Text Analysis with AI</title>
            <style>
                /* Embedded dark theme CSS */
                :root {
                    --primary-color: #9D4EDD;
                    --background-color: #121212;
                    --card-background: #1E1E1E;
                    --text-color: #FFFFFF;
                    --secondary-text: #B0B0B0;
                    --border-color: #333333;
                    --success-color: #4CAF50;
                    --error-color: #F44336;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                    background-color: var(--background-color);
                    color: var(--text-color);
                    margin: 0;
                    padding: 0;
                    line-height: 1.6;
                }
                
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid var(--border-color);
                    margin-bottom: 20px;
                }
                
                .logo {
                    font-size: 24px;
                    font-weight: 700;
                    color: var(--primary-color);
                    text-decoration: none;
                }
                
                nav a {
                    color: var(--secondary-text);
                    margin-left: 15px;
                    text-decoration: none;
                }
                
                nav a:hover {
                    color: var(--primary-color);
                }
                
                h1 {
                    color: var(--primary-color);
                    margin-bottom: 20px;
                }
                
                p {
                    color: var(--secondary-text);
                    margin-bottom: 20px;
                }
                
                .card {
                    background-color: var(--card-background);
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 20px;
                    border: 1px solid var(--border-color);
                }
                
                textarea {
                    width: 100%;
                    height: 120px;
                    padding: 12px;
                    border-radius: 4px;
                    background-color: #2A2A2A;
                    border: 1px solid var(--border-color);
                    color: var(--text-color);
                    resize: vertical;
                    font-family: inherit;
                    margin-bottom: 15px;
                    box-sizing: border-box;
                }
                
                button {
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: 500;
                    cursor: pointer;
                    border: none;
                    margin-right: 10px;
                }
                
                .button-primary {
                    background-color: var(--primary-color);
                    color: white;
                }
                
                .button-secondary {
                    background-color: transparent;
                    color: var(--text-color);
                    border: 1px solid var(--border-color);
                }
                
                .result {
                    display: none;
                }
                
                .sample {
                    background-color: #2A2A2A;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 4px;
                    cursor: pointer;
                }
                
                .toxic {
                    color: var(--error-color);
                    font-weight: 600;
                }
                
                .not-toxic {
                    color: var(--success-color);
                    font-weight: 600;
                }
                
                .error {
                    color: var(--error-color);
                    padding: 15px;
                    border: 1px solid var(--error-color);
                    border-radius: 4px;
                    margin-top: 15px;
                }
                
                .analyzing {
                    padding: 20px;
                    text-align: center;
                }
                
                footer {
                    text-align: center;
                    padding: 20px;
                    color: var(--secondary-text);
                    margin-top: 40px;
                    border-top: 1px solid var(--border-color);
                }
                
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }
                
                th, td {
                    text-align: left;
                    padding: 8px;
                    border-bottom: 1px solid var(--border-color);
                }
                
                th {
                    color: var(--secondary-text);
                }
            </style>
        </head>
        <body>
            <header>
                <a href="/" class="logo">ToxidAPI</a>
                <nav>
                    <a href="/api">API Docs</a>
                    <a href="/docs">ReDoc</a>
                    <a href="https://github.com/sanjanatg/toxidapi" target="_blank">GitHub</a>
                </nav>
            </header>

            <div class="container">
                <h1>ToxidAPI Demo</h1>
                <p>Test our AI-powered text analysis API that detects toxicity, sentiment, and identifies flagged content using Google's Gemini AI.</p>
                
                <div class="card">
                    <label for="text">Enter text to analyze:</label>
                    <textarea id="text" placeholder="Enter text to analyze..."></textarea>
                    <div>
                        <button id="analyze" class="button-primary">Analyze Text</button>
                        <button id="clear" class="button-secondary">Clear</button>
                    </div>
                </div>
                
                <div id="result" class="card result">
                    <!-- Results will be displayed here -->
                </div>
                
                <h3>Sample Texts:</h3>
                <div class="sample" onclick="document.getElementById('text').value=this.textContent;">I hate you, you're such a waste of space. Don't bother replying, I won't listen.</div>
                <div class="sample" onclick="document.getElementById('text').value=this.textContent;">This conversation was great, thank you for sharing your thoughts with me!</div>
                <div class="sample" onclick="document.getElementById('text').value=this.textContent;">F*** this sh1t, I'm done with these a$$holes.</div>
                <div class="sample" onclick="document.getElementById('text').value=this.textContent;">The rain is nice, but the sunshine is warm.</div>
                <div class="sample" onclick="document.getElementById('text').value=this.textContent;">This product sucks! Don't buy it, complete waste of money!!!</div>
            </div>

            <footer>
                <p>API Documentation: 
                    <a href="/api">Swagger UI</a> | 
                    <a href="/docs">ReDoc</a> | 
                    <a href="/static/api_docs.md">Markdown</a>
                </p>
                <p>© 2025 ToxidAPI. Powered by Google's Gemini AI.</p>
            </footer>
            
            <script>
                document.getElementById('analyze').addEventListener('click', async () => {
                    const text = document.getElementById('text').value;
                    if (!text) return;
                    
                    const resultDiv = document.getElementById('result');
                    resultDiv.style.display = 'block';
                    resultDiv.innerHTML = '<div class="analyzing">Analyzing text...</div>';
                    
                    try {
                        console.log('Current URL:', window.location.href);
                        const apiUrl = new URL('/api/analyze', window.location.href).href;
                        console.log('API URL:', apiUrl);
                        
                        const response = await fetch(apiUrl, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ text })
                        });
                        
                        if (!response.ok) {
                            let errorMessage = 'Failed to analyze text';
                            try {
                                const errorData = await response.json();
                                errorMessage = errorData.detail || errorMessage;
                            } catch (e) {
                                errorMessage = `Error ${response.status}: ${response.statusText}`;
                            }
                            throw new Error(errorMessage);
                        }
                        
                        const data = await response.json();
                        
                        // Display results
                        const toxicClass = data.toxicity.is_toxic ? 'toxic' : 'not-toxic';
                        const toxicText = data.toxicity.is_toxic ? 'Toxic' : 'Not Toxic';
                        
                        resultDiv.innerHTML = `
                            <h2>Analysis Results</h2>
                            
                            <div class="card">
                                <h3>Toxicity</h3>
                                <p>Score: ${data.toxicity.score.toFixed(4)}</p>
                                <p>Result: <span class="${toxicClass}">${toxicText}</span></p>
                                
                                <h3>Detailed Toxicity Scores</h3>
                                <table>
                                    <tr>
                                        <th>Category</th>
                                        <th>Score</th>
                                    </tr>
                                    ${Object.entries(data.toxicity.detailed_scores).map(([key, value]) => 
                                        `<tr>
                                            <td>${key}</td>
                                            <td>${value.toFixed(4)}</td>
                                        </tr>`
                                    ).join('')}
                                </table>
                            </div>
                            
                            <div class="card">
                                <h3>Sentiment</h3>
                                <p>Score: ${data.sentiment.score.toFixed(4)}</p>
                                <p>Label: ${data.sentiment.label}</p>
                            </div>
                            
                            <div class="card">
                                <h3>Flagged Words</h3>
                                <p>Count: ${data.flagged_words.count}</p>
                                <p>Words: ${data.flagged_words.words.join(', ') || 'None'}</p>
                                
                                <h4>Categories</h4>
                                <ul>
                                    ${Object.entries(data.flagged_words.categories || {}).map(([category, words]) => 
                                        `<li>${category}: ${words.join(', ')}</li>`
                                    ).join('') || '<li>None</li>'}
                                </ul>
                                
                                <p>Severity Score: ${data.flagged_words.severity_score.toFixed(4)}</p>
                                <p>Is Severe: ${data.flagged_words.is_severe ? 'Yes' : 'No'}</p>
                            </div>
                            
                            <div class="card">
                                <h3>Processing Information</h3>
                                <p>Processing Time: ${data.processing_time.toFixed(4)} seconds</p>
                                <p>Analyzed Text: "${text.substring(0, 100)}${text.length > 100 ? '...' : ''}"</p>
                            </div>
                        `;
                    } catch (error) {
                        console.error('Error:', error);
                        resultDiv.innerHTML = `
                            <div class="error">
                                <strong>Error:</strong> ${error.message}
                            </div>
                        `;
                    }
                });
                
                // Add clear button functionality
                document.getElementById('clear').addEventListener('click', () => {
                    document.getElementById('text').value = '';
                    document.getElementById('result').style.display = 'none';
                });
            </script>
        </body>
        </html>
        """

# Health check endpoint
@app.get("/health", summary="Health check endpoint", tags=["system"])
async def health_check():
    """
    Check if the API is operational.
    
    Returns information about the API status, version, and model being used.
    """
    return {
        "status": "ok",
        "version": "2.0.0",
        "model": "gemini-2.0-flash",
        "documentation": {
            "swagger": "/api",
            "redoc": "/docs",
            "markdown": "/static/api_docs.md"
        }
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