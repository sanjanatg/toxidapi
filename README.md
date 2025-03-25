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

## Prerequisites

Before getting started, ensure you have the following installed:

- [Python 3.9+](https://www.python.org/downloads/) - Used for the FastAPI backend
- [pip](https://pip.pypa.io/en/stable/installation/) - Python package installer
- [Git](https://git-scm.com/downloads) - For cloning the repository
- [Vercel CLI](https://vercel.com/docs/cli) (Optional) - For deployment to Vercel
- [Google Gemini API Key](https://aistudio.google.com/app/apikey) - Required for text analysis

## Installation and Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sanjanatg/toxidapi.git
   cd toxidapi
   ```

2. **Create a virtual environment**:
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   
   You can obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

5. **Run the development server**:
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the application**:
   - UI Demo: [http://localhost:8000](http://localhost:8000)
   - API Documentation: [http://localhost:8000/api](http://localhost:8000/api)
   - ReDoc: [http://localhost:8000/docs](http://localhost:8000/docs)

## API Documentation

- [Swagger UI](/api) - Interactive API documentation
- [ReDoc](/docs) - Alternative documentation viewer
- [Markdown](/static/api_docs.md) - Markdown documentation

## Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.9+)
- **AI Model**: [Google Gemini AI](https://ai.google.dev/)
- **Frontend**: Vanilla JavaScript with modern CSS
- **Deployment**: [Vercel](https://vercel.com/)
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
curl -X POST "https://gdg2025.vercel.app/api/analyze" \
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

## Deployment to Vercel

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Log in to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy to Vercel**:
   ```bash
   vercel
   ```

4. **Set environment variables**:
   
   After deployment, set up your `GEMINI_API_KEY` on the Vercel dashboard:
   - Go to your project on the [Vercel Dashboard](https://vercel.com/dashboard)
   - Navigate to Settings > Environment Variables
   - Add `GEMINI_API_KEY` with your Google Gemini API key

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

## Local Development

1. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Visit `http://localhost:8000` in your browser

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for the powerful text analysis capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the efficient API framework
- [Vercel](https://vercel.com/) for hosting and deployment
