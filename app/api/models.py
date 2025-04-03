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

class EmotionScores(BaseModel):
    joy: float = Field(0.0, description="Joy emotion score")
    sadness: float = Field(0.0, description="Sadness emotion score")
    anger: float = Field(0.0, description="Anger emotion score")
    fear: float = Field(0.0, description="Fear emotion score")
    surprise: float = Field(0.0, description="Surprise emotion score")

class SentimentResponse(BaseModel):
    score: float = Field(..., description="Sentiment score (-1 to 1, negative to positive)")
    label: str = Field(..., description="Sentiment label (POSITIVE, NEGATIVE, NEUTRAL)")
    emotions: EmotionScores = Field(
        default_factory=EmotionScores,
        description="Detailed emotion scores"
    )

class ProfanityCategories(BaseModel):
    mild_profanity: float = Field(0.0, description="Mild profanity score")
    strong_profanity: float = Field(0.0, description="Strong profanity score")
    sexual_references: float = Field(0.0, description="Sexual references score")
    slurs: float = Field(0.0, description="Slurs score")

class ProfanityResponse(BaseModel):
    score: float = Field(0.0, description="Overall profanity score (0-1)")
    is_profane: bool = Field(False, description="Whether the content contains profanity")
    severity: str = Field("NONE", description="Profanity severity (NONE, LOW, MEDIUM, HIGH)")
    categories: ProfanityCategories = Field(
        default_factory=ProfanityCategories,
        description="Detailed profanity category scores"
    )

class SensitivityCategories(BaseModel):
    political: float = Field(0.0, description="Political sensitivity score")
    religious: float = Field(0.0, description="Religious sensitivity score")
    racial: float = Field(0.0, description="Racial sensitivity score")
    gender: float = Field(0.0, description="Gender sensitivity score")
    violence: float = Field(0.0, description="Violence sensitivity score")
    self_harm: float = Field(0.0, description="Self-harm sensitivity score")

class SensitivityResponse(BaseModel):
    score: float = Field(0.0, description="Overall sensitivity score (0-1)")
    is_sensitive: bool = Field(False, description="Whether the content contains sensitive material")
    categories: SensitivityCategories = Field(
        default_factory=SensitivityCategories,
        description="Detailed sensitivity category scores"
    )

class ReadabilityMetrics(BaseModel):
    avg_word_length: float = Field(5.0, description="Average word length")
    avg_sentence_length: float = Field(15.0, description="Average sentence length")
    complex_word_percentage: float = Field(0.3, description="Percentage of complex words")

class ReadabilityResponse(BaseModel):
    score: float = Field(0.5, description="Readability score (0-1, harder to easier)")
    grade_level: int = Field(8, description="Approximate grade level (1-12)")
    difficulty: str = Field("MEDIUM", description="Readability difficulty (EASY, MEDIUM, DIFFICULT)")
    metrics: ReadabilityMetrics = Field(
        default_factory=ReadabilityMetrics,
        description="Detailed readability metrics"
    )

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
    profanity: ProfanityResponse = Field(..., description="Profanity analysis results")
    sensitivity: SensitivityResponse = Field(..., description="Sensitivity analysis results")
    readability: ReadabilityResponse = Field(..., description="Readability analysis results")
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
                    "label": "NEGATIVE",
                    "emotions": {
                        "joy": 0.05,
                        "sadness": 0.68,
                        "anger": 0.82,
                        "fear": 0.12,
                        "surprise": 0.09
                    }
                },
                "profanity": {
                    "score": 0.82,
                    "is_profane": True,
                    "severity": "HIGH",
                    "categories": {
                        "mild_profanity": 0.2,
                        "strong_profanity": 0.85,
                        "sexual_references": 0.64,
                        "slurs": 0.18
                    }
                },
                "sensitivity": {
                    "score": 0.3,
                    "is_sensitive": False,
                    "categories": {
                        "political": 0.15,
                        "religious": 0.05,
                        "racial": 0.08,
                        "gender": 0.12,
                        "violence": 0.42,
                        "self_harm": 0.05
                    }
                },
                "readability": {
                    "score": 0.65,
                    "grade_level": 6,
                    "difficulty": "EASY",
                    "metrics": {
                        "avg_word_length": 4.2,
                        "avg_sentence_length": 8.7,
                        "complex_word_percentage": 0.15
                    }
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