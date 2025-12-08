# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime


class TextAnalysisRequest(BaseModel):
    """Request model for text analysis"""
    text: str = Field(..., min_length=50, description="Text to analyze (minimum 50 characters)")
    api_key: str = Field(..., description="Your API key")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "In today's digital age, it is important to note that artificial intelligence has revolutionized content creation...",
                "api_key": "your_api_key_here"
            }
        }


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis"""
    texts: list[str] = Field(..., max_length=10, description="List of texts to analyze (max 10)")
    api_key: str = Field(..., description="Your API key")

    class Config:
        json_schema_extra = {
            "example": {
                "texts": [
                    "First text to analyze...",
                    "Second text to analyze..."
                ],
                "api_key": "your_api_key_here"
            }
        }


class AnalysisMetrics(BaseModel):
    """Metrics from the analysis"""
    ai_phrases_detected: int
    sentence_uniformity_score: float
    repetition_score: float


class AnalysisResult(BaseModel):
    """Result of AI content detection"""
    ai_probability: float = Field(..., ge=0, le=100, description="Probability that text is AI-generated (0-100)")
    is_likely_ai: bool = Field(..., description="Whether text is likely AI-generated")
    confidence: str = Field(..., description="Confidence level (Low/Medium/High/Very High)")
    metrics: AnalysisMetrics


class TextAnalysisResponse(BaseModel):
    """Response model for text analysis"""
    status: str
    request_id: str
    timestamp: str
    analysis: AnalysisResult
    text_length: int
    word_count: int


class BatchAnalysisResponse(BaseModel):
    """Response model for batch analysis"""
    status: str
    timestamp: str
    total_analyzed: int
    results: list[Dict]


class ErrorResponse(BaseModel):
    """Error response model"""
    status: str = "error"
    message: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str
    timestamp: str


class PricingTier(BaseModel):
    """Pricing tier information"""
    requests_per_month: int | str
    price: float | str
    features: list[str]


class PricingResponse(BaseModel):
    """Pricing information response"""
    status: str
    pricing_tiers: Dict[str, PricingTier]
