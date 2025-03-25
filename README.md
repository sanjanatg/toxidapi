# ToxidAPI

A powerful AI-powered text analysis API that detects toxicity, sentiment, and identifies flagged content using Google's Gemini AI.

## Live Demo

Visit our live demo at: [ToxidAPI Demo](https://gdg2025.vercel.app/)

## Features

- **Toxicity Analysis**: Detect toxic content with detailed scores for multiple categories
- **Sentiment Analysis**: Determine positive, negative, or neutral sentiment with confidence scores
- **Content Moderation**: Identify and categorize flagged words with severity assessment
- **Modern Dark UI**: Clean, responsive interface with real-time analysis visualization
- **Interactive Demo**: Test the API with sample texts or your own content
- **Progress Bars**: Visual representation of toxicity and sentiment scores
- **Comprehensive Results**: Detailed breakdown of analysis including processing time

## API Documentation

- [Swagger UI](/api) - Interactive API documentation
- [ReDoc](/docs) - Alternative documentation viewer
- [Markdown](/static/api_docs.md) - Markdown documentation

## Tech Stack

- **Backend**: FastAPI (Python 3.8+)
- **AI Model**: Google Gemini AI
- **Frontend**: Vanilla JavaScript with modern CSS
- **Deployment**: Vercel
- **Documentation**: OpenAPI (Swagger) & ReDoc

## Project Structure

```
toxidapi/
├── app/
│   ├── api/
│   │   ├── routes.py      # API endpoints
│   │   └── rate_limiter.py # Rate limiting middleware
│   ├── static/
│   │   └── simple.html    # Frontend UI
│   └── main.py           # FastAPI application
├── vercel.json          # Vercel deployment config
└── requirements.txt     # Python dependencies
```

## API Usage

### Analyze Text

```bash
curl -X POST "https://your-deployment-url/api/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text here"}'
```

### Response Format

```json
{
    "toxicity": {
        "score": 0.8532,
        "is_toxic": true,
        "detailed_scores": {
            "toxicity": 0.8532,
            "severe_toxicity": 0.6231,
            "obscene": 0.7521,
            "threat": 0.1234,
            "insult": 0.8123,
            "identity_attack": 0.2341
        }
    },
    "sentiment": {
        "score": -0.7823,
        "label": "negative"
    },
    "flagged_words": {
        "count": 2,
        "words": ["word1", "word2"],
        "categories": {
            "profanity": ["word1"],
            "insult": ["word2"]
        },
        "severity_score": 0.7234,
        "is_severe": true
    },
    "processing_time": 0.1234
}
```

## Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/toxidapi.git
   cd toxidapi
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

5. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Visit `http://localhost:8000` in your browser

## Deployment

This project is configured for deployment on Vercel. Simply push to your repository and connect it to Vercel.

Make sure to set the following environment variables in your Vercel project:
- `GEMINI_API_KEY`: Your Google Gemini AI API key

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI for the powerful text analysis capabilities
- FastAPI for the efficient API framework
- Vercel for hosting and deployment
