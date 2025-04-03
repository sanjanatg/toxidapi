import google.generativeai as genai
import logging
from typing import Dict, Any
import json
import re

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """
    Unified text analyzer using Google's Gemini API for toxicity, sentiment, and content analysis.
    """
    def __init__(self, api_key: str):
        """
        Initialize the Gemini analyzer.
        
        Args:
            api_key: Google Gemini API key
        """
        logger.info("Initializing GeminiAnalyzer...")
        genai.configure(api_key=api_key)
        
        # Initialize model with safety settings turned off since we're doing content moderation
        self.model = genai.GenerativeModel('gemini-2.0-flash',
            generation_config={
                "temperature": 0,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE",
                },
            ]
        )
        
        # Define the prompt template for analysis
        self.prompt_template = """You are a comprehensive content analysis AI. Analyze the following text for toxicity, sentiment, readability, profanity, and sensitivity. You must detect ALL forms of problematic content, including obfuscated words.

Text to analyze: "{text}"

Return a JSON object with this exact structure:
{{
    "toxicity": {{
        "score": <0.0-1.0>,
        "is_toxic": <true/false>,
        "detailed_scores": {{
            "toxicity": <0.0-1.0>,
            "severe_toxicity": <0.0-1.0>,
            "obscene": <0.0-1.0>,
            "threat": <0.0-1.0>,
            "insult": <0.0-1.0>,
            "identity_hate": <0.0-1.0>
        }}
    }},
    "sentiment": {{
        "score": <-1.0 to 1.0>,
        "label": <"POSITIVE"/"NEGATIVE"/"NEUTRAL">,
        "emotions": {{
            "joy": <0.0-1.0>,
            "sadness": <0.0-1.0>,
            "anger": <0.0-1.0>,
            "fear": <0.0-1.0>,
            "surprise": <0.0-1.0>
        }}
    }},
    "profanity": {{
        "score": <0.0-1.0>,
        "is_profane": <true/false>,
        "severity": <"NONE"/"LOW"/"MEDIUM"/"HIGH">,
        "categories": {{
            "mild_profanity": <0.0-1.0>,
            "strong_profanity": <0.0-1.0>,
            "sexual_references": <0.0-1.0>,
            "slurs": <0.0-1.0>
        }}
    }},
    "sensitivity": {{
        "score": <0.0-1.0>,
        "is_sensitive": <true/false>,
        "categories": {{
            "political": <0.0-1.0>,
            "religious": <0.0-1.0>,
            "racial": <0.0-1.0>,
            "gender": <0.0-1.0>,
            "violence": <0.0-1.0>,
            "self_harm": <0.0-1.0>
        }}
    }},
    "readability": {{
        "score": <0.0-1.0>,
        "grade_level": <1-12>,
        "difficulty": <"EASY"/"MEDIUM"/"DIFFICULT">,
        "metrics": {{
            "avg_word_length": <number>,
            "avg_sentence_length": <number>,
            "complex_word_percentage": <0.0-1.0>
        }}
    }},
    "flagged_words": {{
        "count": <number>,
        "words": [<word1>, <word2>, ...],
        "categories": {{
            "profanity": [<words>],
            "insults": [<words>],
            "slurs": [<words>],
            "other": [<words>]
        }},
        "severity_score": <0.0-1.0>,
        "is_severe": <true/false>
    }}
}}

Important rules:
1. Detect ALL profanity including obfuscated forms (f*ck, sh!t, a$$, etc.)
2. Score toxicity high for profanity and aggressive language
3. Consider ALL-CAPS and multiple punctuation (!!!) as anger indicators
4. Include original obfuscated forms in flagged_words
5. Set high severity for multiple profanities or aggressive context
6. Carefully analyze for sensitive topics like politics, religion, race
7. Evaluate readability using standard metrics (word/sentence length, complexity)
8. For sentiment, identify underlying emotions beyond positive/negative

Return ONLY valid JSON, no other text or explanation."""
        
        self.api_key = api_key
        
        logger.info("GeminiAnalyzer initialized successfully")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze the text using Gemini API.
        
        Args:
            text: The text to analyze
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Format the prompt with the input text
            prompt = self.prompt_template.format(text=text)
            
            # Get response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the JSON response
            try:
                # Get the response text
                response_text = response.text
                
                # Try to find JSON in the response
                try:
                    # First try direct JSON parsing
                    result = json.loads(response_text)
                except:
                    # If that fails, try to extract JSON from markdown blocks
                    if "```json" in response_text:
                        json_str = response_text.split("```json")[1].split("```")[0]
                    elif "```" in response_text:
                        json_str = response_text.split("```")[1].split("```")[0]
                    else:
                        # Try to find JSON-like structure
                        match = re.search(r'({[\s\S]*})', response_text)
                        json_str = match.group(1) if match else response_text
                    
                    # Clean up the JSON string
                    json_str = re.sub(r'<[^>]+>', '', json_str)  # Remove angle brackets
                    json_str = json_str.strip()
                    result = json.loads(json_str)
                
                # Validate and normalize scores
                self._normalize_scores(result)
                
                # Ensure non-zero scores for toxic content
                if result["flagged_words"]["count"] > 0 and result["toxicity"]["score"] == 0:
                    result["toxicity"]["score"] = max(0.7, result["flagged_words"]["severity_score"])
                    result["toxicity"]["is_toxic"] = True
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing Gemini response: {str(e)}")
                logger.error(f"Raw response: {response_text}")
                return self._get_default_response()
            
        except Exception as e:
            logger.error(f"Error analyzing text with Gemini: {str(e)}")
            return self._get_default_response()
    
    def _normalize_scores(self, result: Dict[str, Any]) -> None:
        """Normalize and validate all scores in the result."""
        # Ensure toxicity scores exist and are normalized
        result.setdefault("toxicity", {})
        toxicity = result["toxicity"]
        toxicity.setdefault("score", 0.0)
        toxicity.setdefault("is_toxic", False)
        toxicity.setdefault("detailed_scores", {})
        
        # Normalize detailed scores
        for key in ["toxicity", "severe_toxicity", "obscene", "threat", "insult", "identity_hate"]:
            toxicity["detailed_scores"].setdefault(key, 0.0)
            toxicity["detailed_scores"][key] = min(1.0, max(0.0, float(toxicity["detailed_scores"][key])))
        
        # Update is_toxic based on score
        if toxicity["score"] > 0.5 or any(score > 0.5 for score in toxicity["detailed_scores"].values()):
            toxicity["is_toxic"] = True
        
        # Normalize sentiment
        result.setdefault("sentiment", {})
        sentiment = result["sentiment"]
        sentiment.setdefault("score", 0.0)
        sentiment.setdefault("label", "NEUTRAL")
        sentiment.setdefault("emotions", {})
        
        # Add emotions if not present
        for emotion in ["joy", "sadness", "anger", "fear", "surprise"]:
            sentiment["emotions"].setdefault(emotion, 0.0)
        
        # Normalize profanity
        result.setdefault("profanity", {})
        profanity = result["profanity"]
        profanity.setdefault("score", 0.0)
        profanity.setdefault("is_profane", False)
        profanity.setdefault("severity", "NONE")
        profanity.setdefault("categories", {})
        
        # Add profanity categories if not present
        for category in ["mild_profanity", "strong_profanity", "sexual_references", "slurs"]:
            profanity["categories"].setdefault(category, 0.0)
        
        # Update is_profane based on score
        if profanity["score"] > 0.3:
            profanity["is_profane"] = True
            if profanity["score"] > 0.7:
                profanity["severity"] = "HIGH"
            elif profanity["score"] > 0.4:
                profanity["severity"] = "MEDIUM"
            else:
                profanity["severity"] = "LOW"
        
        # Normalize sensitivity
        result.setdefault("sensitivity", {})
        sensitivity = result["sensitivity"]
        sensitivity.setdefault("score", 0.0)
        sensitivity.setdefault("is_sensitive", False)
        sensitivity.setdefault("categories", {})
        
        # Add sensitivity categories if not present
        for category in ["political", "religious", "racial", "gender", "violence", "self_harm"]:
            sensitivity["categories"].setdefault(category, 0.0)
            
        # Update is_sensitive based on score
        if sensitivity["score"] > 0.5 or any(score > 0.6 for score in sensitivity["categories"].values()):
            sensitivity["is_sensitive"] = True
        
        # Normalize readability
        result.setdefault("readability", {})
        readability = result["readability"]
        readability.setdefault("score", 0.5)
        readability.setdefault("grade_level", 8)
        readability.setdefault("difficulty", "MEDIUM")
        readability.setdefault("metrics", {})
        
        # Add readability metrics if not present
        readability["metrics"].setdefault("avg_word_length", 5.0)
        readability["metrics"].setdefault("avg_sentence_length", 15.0)
        readability["metrics"].setdefault("complex_word_percentage", 0.3)
        
        # Normalize flagged words
        result.setdefault("flagged_words", {})
        flagged = result["flagged_words"]
        flagged.setdefault("count", 0)
        flagged.setdefault("words", [])
        flagged.setdefault("categories", {})
        flagged.setdefault("severity_score", 0.0)
        flagged.setdefault("is_severe", False)
        
        # Update severity based on content
        if flagged["count"] > 0:
            if not flagged["severity_score"]:
                flagged["severity_score"] = max(profanity["score"], toxicity["score"])
            flagged["is_severe"] = flagged["severity_score"] > 0.5
    
    def _get_default_response(self) -> Dict[str, Any]:
        """Get default response structure when analysis fails."""
        return {
            "toxicity": {
                "score": 0.0,
                "is_toxic": False,
                "detailed_scores": {
                    "toxicity": 0.0,
                    "severe_toxicity": 0.0,
                    "obscene": 0.0,
                    "threat": 0.0,
                    "insult": 0.0,
                    "identity_hate": 0.0
                }
            },
            "sentiment": {
                "score": 0.0,
                "label": "NEUTRAL",
                "emotions": {
                    "joy": 0.0,
                    "sadness": 0.0,
                    "anger": 0.0,
                    "fear": 0.0,
                    "surprise": 0.0
                }
            },
            "profanity": {
                "score": 0.0,
                "is_profane": False,
                "severity": "NONE",
                "categories": {
                    "mild_profanity": 0.0,
                    "strong_profanity": 0.0,
                    "sexual_references": 0.0,
                    "slurs": 0.0
                }
            },
            "sensitivity": {
                "score": 0.0,
                "is_sensitive": False,
                "categories": {
                    "political": 0.0,
                    "religious": 0.0,
                    "racial": 0.0,
                    "gender": 0.0,
                    "violence": 0.0,
                    "self_harm": 0.0
                }
            },
            "readability": {
                "score": 0.5,
                "grade_level": 8,
                "difficulty": "MEDIUM",
                "metrics": {
                    "avg_word_length": 5.0,
                    "avg_sentence_length": 15.0,
                    "complex_word_percentage": 0.3
                }
            },
            "flagged_words": {
                "count": 0,
                "words": [],
                "categories": {},
                "severity_score": 0.0,
                "is_severe": False
            }
        } 