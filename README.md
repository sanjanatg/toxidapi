# ToxidAPI

A professional API for analyzing text toxicity, sentiment, and content moderation using Google's Gemini AI.

## Features

- **Toxicity Analysis**: Detect toxic content with detailed category scores
- **Sentiment Analysis**: Determine text sentiment (positive, negative, neutral)
- **Content Moderation**: Identify and categorize flagged words
- **API Versioning**: Supports v1 (deprecated) and v2 endpoints
- **Rate Limiting**: Per-API key rate limiting with Redis
- **API Key Authentication**: Secure access control
- **Usage Tracking**: Monitor API usage and performance
- **OpenAPI Documentation**: Interactive API documentation

## Tech Stack

- **Backend**: FastAPI (Python 3.9+)
- **AI Model**: Google Gemini AI
- **Database**: Redis for rate limiting and caching
- **Authentication**: API key-based authentication
- **Documentation**: OpenAPI (Swagger) & ReDoc
- **Deployment**: Vercel

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/toxidapi.git
   cd toxidapi
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` to add your own API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   REDIS_URL=your_redis_url
   API_KEY_REQUIRED=true
   RATE_LIMIT=100
   PRO_RATE_LIMIT=1000
   RATE_WINDOW=3600
   ```
   
   > ⚠️ **SECURITY NOTE**: Never commit your `.env` file with real API keys to Git. The `.gitignore` file is configured to exclude it.
   
   You can obtain:
   - Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Redis URL from [Redis Cloud](https://redis.com/cloud/overview/) or local Redis instance

5. **Run the development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the application**:
   - UI Demo: [http://localhost:8000](http://localhost:8000)
   - API Documentation: [http://localhost:8000/api](http://localhost:8000/api)
   - ReDoc: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Documentation

### Authentication

All API requests require an API key. Include your API key in the `X-API-Key` header:

```bash
curl -X POST "https://api.toxidapi.com/api/v2/analyze" \
     -H "X-API-Key: your_api_key" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text here"}'
```

### Rate Limiting

Rate limits are applied per API key:
- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour

Rate limit headers are included in all responses:
- `X-Rate-Limit-Limit`: Maximum requests per window
- `X-Rate-Limit-Remaining`: Remaining requests in current window
- `X-Rate-Limit-Reset`: Seconds until rate limit resets

### Endpoints

#### Analyze Text (v2)

```bash
POST /api/v2/analyze
```

Request body:
```json
{
    "text": "Your text here"
}
```

Response:
```json
{
    "toxicity": {
        "is_toxic": false,
        "score": 0.1234,
        "detailed_scores": {
            "hate": 0.1,
            "threat": 0.05,
            "obscene": 0.2,
            "insult": 0.15,
            "severe_toxic": 0.05
        }
    },
    "sentiment": {
        "label": "positive",
        "score": 0.85
    },
    "flagged_words": {
        "count": 0,
        "words": [],
        "categories": {},
        "severity_score": 0.0,
        "is_severe": false
    },
    "processing_time": 0.1234
}
```

#### Batch Analysis (v2)

```bash
POST /api/v2/analyze/batch
```

Request body:
```json
{
    "texts": ["Text 1", "Text 2", "Text 3"]
}
```

#### Health Check

```bash
GET /health
```

### Error Responses

All errors follow this format:
```json
{
    "error": "error_type",
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
        // Additional error details if available
    }
}
```

Common error codes:
- `API_KEY_MISSING`: Missing API key
- `INVALID_API_KEY`: Invalid API key
- `RATE_LIMIT_EXCEEDED`: Rate limit exceeded
- `INVALID_REQUEST`: Invalid request parameters
- `INTERNAL_ERROR`: Server error

## Deployment

### Vercel Deployment

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy to Vercel**:
   ```bash
   vercel
   ```

3. **Set environment variables in Vercel dashboard**:
   - `GEMINI_API_KEY`
   - `REDIS_URL`
   - `API_KEY_REQUIRED`
   - `RATE_LIMIT`
   - `PRO_RATE_LIMIT`
   - `RATE_WINDOW`

### Custom Domain

1. Add your domain in the Vercel dashboard
2. Configure DNS settings as per Vercel instructions
3. Enable HTTPS (automatic with Vercel)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
