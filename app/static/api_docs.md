# ToxidAPI Documentation

## Overview

ToxidAPI is a powerful text analysis API powered by Google's Gemini AI. It provides comprehensive analysis for:

- Toxicity detection
- Sentiment analysis
- Content moderation
- Flagged words identification

## Authentication

API key authentication can be enabled by setting environment variables. When enabled, all requests must include the `X-API-Key` header.

Example:
```
X-API-Key: your_api_key_here
```

## Rate Limiting

Rate limiting may be applied based on your API key or IP address to ensure fair usage.

## Endpoints

### Analyze Text

Analyze text for toxicity, sentiment, and content moderation.

**URL**: `/api/analyze`  
**Method**: `POST`  
**Auth required**: Depends on configuration  

#### Request Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| text | string | Yes | The text to analyze |

Example request:
```json
{
  "text": "This is a sample text to analyze."
}
```

#### Response

| Field | Type | Description |
|-------|------|-------------|
| toxicity | object | Toxicity analysis results |
| toxicity.score | float | Overall toxicity score (0-1) |
| toxicity.is_toxic | boolean | Whether the content is considered toxic |
| toxicity.detailed_scores | object | Detailed scores for different toxicity categories |
| sentiment | object | Sentiment analysis results |
| sentiment.score | float | Sentiment score (-1 to 1) |
| sentiment.label | string | Sentiment label (POSITIVE, NEGATIVE, NEUTRAL) |
| flagged_words | object | Flagged words analysis |
| flagged_words.count | integer | Number of flagged words found |
| flagged_words.words | array | List of flagged words |
| flagged_words.categories | object | Categorization of flagged words |
| flagged_words.severity_score | float | Severity score for flagged content (0-1) |
| flagged_words.is_severe | boolean | Whether the flagged content is considered severe |
| processing_time | float | Processing time in seconds |
| text | string | The original text that was analyzed |

Example response:
```json
{
  "toxicity": {
    "score": 0.92,
    "is_toxic": true,
    "detailed_scores": {
      "toxicity": 0.92,
      "severe_toxicity": 0.71,
      "obscene": 0.88,
      "threat": 0.12,
      "insult": 0.76,
      "identity_hate": 0.21
    }
  },
  "sentiment": {
    "score": -0.85,
    "label": "NEGATIVE"
  },
  "flagged_words": {
    "count": 2,
    "words": ["f*ck", "sh*t"],
    "categories": {
      "profanity": ["f*ck", "sh*t"]
    },
    "severity_score": 0.75,
    "is_severe": true
  },
  "processing_time": 0.437,
  "text": "This is f*cking sh*t!"
}
```

#### Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input parameters |
| 401 | Unauthorized - API key missing |
| 403 | Forbidden - Invalid API key |
| 500 | Internal Server Error - Analysis failed |

### API Statistics

Get statistics about API usage.

**URL**: `/api/stats`  
**Method**: `GET`  
**Auth required**: Depends on configuration  

#### Response

Example response:
```json
{
  "cache_size": 10,
  "cache_max_size": 100,
  "analyzer_type": "gemini-2.0-flash"
}
```

### Flush Cache

Flush the result cache.

**URL**: `/api/cache/flush`  
**Method**: `POST`  
**Auth required**: Yes (Admin API key)  

#### Response

Example response:
```json
{
  "status": "success",
  "message": "Cache flushed successfully. 10 entries removed."
}
```

### Health Check

Check if the API is operational.

**URL**: `/health`  
**Method**: `GET`  
**Auth required**: No  

#### Response

Example response:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "model": "gemini-2.0-flash"
}
```

## Error Handling

The API returns standard HTTP error codes along with a JSON response that includes details about the error.

Example error response:
```json
{
  "detail": "Error during text analysis: API key not valid"
}
```

## Rate Limiting

If rate limiting is enabled, the following headers will be included in the response:

- `X-Rate-Limit-Limit`: Number of requests allowed per time window
- `X-Rate-Limit-Remaining`: Number of requests remaining in the current time window
- `X-Rate-Limit-Reset`: Time (in seconds) until the rate limit resets

## SDKs and Client Libraries

### Python

```python
import requests

API_URL = "https://your-deployment-url.com/api/analyze"
API_KEY = "your_api_key"  # Optional if API key authentication is enabled

def analyze_text(text):
    headers = {"Content-Type": "application/json"}
    
    # Add API key if authentication is enabled
    if API_KEY:
        headers["X-API-Key"] = API_KEY
        
    response = requests.post(
        API_URL,
        headers=headers,
        json={"text": text}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Example usage
result = analyze_text("This is a test message.")
print(result)
```

### JavaScript

```javascript
async function analyzeText(text, apiKey = null) {
    const apiUrl = 'https://your-deployment-url.com/api/analyze';
    
    const headers = {
        'Content-Type': 'application/json'
    };
    
    // Add API key if provided
    if (apiKey) {
        headers['X-API-Key'] = apiKey;
    }
    
    try {
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to analyze text');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error analyzing text:', error);
        throw error;
    }
}

// Example usage
analyzeText('This is a test message.')
    .then(result => console.log(result))
    .catch(error => console.error(error));
``` 