from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# Request Models
class TextRequest(BaseModel):
    text: str = Field(..., description="The text to analyze for toxicity and sentiment.")

# Response Models
class DetailedToxicityScores(BaseModel):
    toxicity: float = Field(0.0, description="General toxicity score")
    severe_toxicity: float = Field(0.0, description="Severe toxicity score")
    obscene: float = Field(0.0, description="Obscenity score")
    threat: float = Field(0.0, description="Threatening content score")
    insult: float = Field(0.0, description="Insulting content score")
    identity_hate: float = Field(0.0, description="Identity-based hate score")

class ToxicityResponse(BaseModel):
    score: float = Field(..., description="Overall toxicity score (0-1)")
    is_toxic: bool = Field(..., description="Whether the content is considered toxic")
    detailed_scores: DetailedToxicityScores = Field(
        default_factory=DetailedToxicityScores,
        description="Detailed scores for different toxicity categories"
    )

class SentimentResponse(BaseModel):
    score: float = Field(..., description="Sentiment score (-1 to 1, negative to positive)")
    label: str = Field(..., description="Sentiment label (POSITIVE, NEGATIVE, NEUTRAL)")

class FlaggedWordsResponse(BaseModel):
    count: int = Field(..., description="Number of flagged words found")
    words: List[str] = Field(default_factory=list, description="List of flagged words")
    categories: Dict[str, List[str]] = Field(
        default_factory=dict, 
        description="Categorization of flagged words"
    )
    severity_score: float = Field(0.0, description="Severity score for flagged content (0-1)")
    is_severe: bool = Field(False, description="Whether the flagged content is considered severe")

class AnalysisResponse(BaseModel):
    toxicity: ToxicityResponse = Field(..., description="Toxicity analysis results")
    sentiment: SentimentResponse = Field(..., description="Sentiment analysis results")
    flagged_words: FlaggedWordsResponse = Field(..., description="Flagged words analysis")
    processing_time: float = Field(..., description="Processing time in seconds")
    text: str = Field(..., description="Original text that was analyzed")
    
    class Config:
        schema_extra = {
            "example": {
                "toxicity": {
                    "score": 0.92,
                    "is_toxic": True,
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
                    "is_severe": True
                },
                "processing_time": 0.437,
                "text": "This is f*cking sh*t!"
            }
        } 