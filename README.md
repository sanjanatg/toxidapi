# ToxidAPI

A professional API for analyzing text toxicity, sentiment, and content moderation using Google's Gemini AI.

![image](https://github.com/user-attachments/assets/3af2f980-9843-48a2-a628-162e4a17f10b)

## Features

- **Toxicity Analysis**: Detect toxic content with detailed category scores
- **Sentiment Analysis**: Determine text sentiment (positive, negative, neutral)
- **Content Moderation**: Identify and categorize flagged words
- **API Key Authentication**: Secure access with custom API keys
- **Rate Limiting**: Prevent abuse with tiered usage limits
- **Interactive UI**: Test the API directly in your browser
- **Comprehensive Documentation**: Easy-to-follow integration guides

## Getting Started

### 1. Create an Account

1. Visit [ToxidAPI Registration](https://toxidapi.vercel.app/register)
2. Sign up with your email and password
3. Log in to your account

### 2. Generate API Keys

1. Navigate to the [API Keys](https://toxidapi.vercel.app/keys) page
2. Click "Create New Key" and give it a name (e.g., "Development", "Production")
3. Copy and securely store your API key
4. Use this key in all your API requests

### 3. Make API Requests

Include your API key in the `X-API-Key` header with every request:

```python
import requests

API_KEY = "your_api_key_here"  # Replace with your actual API key

response = requests.post(
    "https://toxidapi.vercel.app/api/v2/analyze",
    headers={
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    },
    json={"text": "Text to analyze"}
)

if response.status_code == 200:
    result = response.json()
    print(f"Toxicity score: {result['toxicity']['score']}")
    print(f"Sentiment: {result['sentiment']['label']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

## API Response Format

ToxidAPI returns analysis results in JSON format:

```json
{
  "toxicity": {
    "score": 0.03,          // 0-1 scale
    "is_toxic": false,      // boolean
    "detailed_scores": {
      "toxicity": 0.03,
      "severe_toxicity": 0.01,
      "obscene": 0.02,
      "threat": 0.01,
      "insult": 0.02,
      "identity_hate": 0.01
    }
  },
  "sentiment": {
    "score": 0.72,          // -1 to 1 scale
    "label": "POSITIVE"     // POSITIVE, NEGATIVE, or NEUTRAL
  },
  "flagged_words": {
    "count": 0,
    "words": [],
    "categories": {}
  },
  "processing_time": 0.254,
  "text": "Text to analyze"
}
```

## Integration Examples

### JavaScript/Node.js

```javascript
// Browser or Node.js with fetch
async function analyzeText(text, apiKey) {
    try {
        const response = await fetch("https://toxidapi.vercel.app/api/v2/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-API-Key": apiKey
            },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error("Error analyzing text:", error);
        return null;
    }
}

// Example usage
analyzeText("This is a sample text.", "your_api_key_here")
    .then(result => {
        if (result) {
            console.log(`Toxicity: ${result.toxicity.score}`);
            console.log(`Sentiment: ${result.sentiment.label}`);
        }
    });
```

### Python

```python
import requests

def analyze_text(text, api_key):
    response = requests.post(
        "https://toxidapi.vercel.app/api/v2/analyze",
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key
        },
        json={"text": text}
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# Example usage
result = analyze_text("This is a sample text.", "your_api_key_here")
if result:
    print(f"Toxicity: {result['toxicity']['score']}")
    print(f"Sentiment: {result['sentiment']['label']}")
```

## Security Best Practices

### Protect Your API Key

1. **Never expose your API key in client-side code** (JavaScript running in browsers)
2. **Store keys in environment variables**, not hardcoded in your application
3. **Use a backend proxy** when integrating with frontend applications

### Example Backend Proxy

```javascript
// server.js - Secure Node.js proxy for frontend applications
require('dotenv').config(); // Load API_KEY from .env file
const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

// Endpoint clients can use without exposing your API key
app.post('/analyze', async (req, res) => {
    try {
        const { text } = req.body;
        
        // Make request to ToxidAPI with your protected API key
        const response = await axios.post(
            'https://toxidapi.vercel.app/api/v2/analyze',
            { text },
            {
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': process.env.TOXIDAPI_KEY // Secured in environment variables
                }
            }
        );
        
        // Return the analysis to your client
        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json({
            error: error.response?.data?.detail || 'An error occurred'
        });
    }
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

## Use Cases

- **Content Moderation**: Filter user-generated content automatically
- **Brand Protection**: Ensure content aligns with your brand values
- **User Safety**: Detect cyberbullying, harassment, or harmful language
- **Sentiment Analysis**: Categorize feedback or comments by sentiment
- **Social Listening**: Monitor sentiment across social media
- **Online Communities**: Create safer spaces with automated moderation

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v2/analyze` | POST | Analyze a single text |
| `/api/v2/analyze/batch` | POST | Analyze multiple texts at once (max 10) |
| `/health` | GET | API health check |

## Rate Limits

- **Standard tier**: 100 requests/hour
- **Pro tier**: 1000 requests/hour

When you exceed your rate limit, requests will return a 429 status code.

## Error Handling

Always implement proper error handling:

```javascript
try {
    const result = await analyzeText("Text to analyze", apiKey);
    // Process result
} catch (error) {
    if (error.status === 401 || error.status === 403) {
        console.error("Authentication failed. Check your API key.");
    } else if (error.status === 429) {
        console.error("Rate limit exceeded. Retry later.");
    } else {
        console.error("An error occurred:", error.message);
    }
}
```

## Additional Resources

- [Integration Guide](https://toxidapi.vercel.app/integration)
- [API Documentation](https://toxidapi.vercel.app/docs)
- [GitHub Repository](https://github.com/sanjanatg/toxidapi)

## Support

If you have any questions or need help, please contact us:
- Email: [sanjanatg2126@gmail.com](mailto:sanjanatg2126@gmail.com)
- [GitHub Issues](https://github.com/sanjanatg/toxidapi/issues)
