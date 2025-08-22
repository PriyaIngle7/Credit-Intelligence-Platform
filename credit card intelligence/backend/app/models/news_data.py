from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class NewsData(BaseModel):
    """News data model for MongoDB"""
    
    id: Optional[str] = Field(None, alias="_id")
    company_ticker: str
    company_name: str
    
    # News content
    title: str
    content: str
    summary: Optional[str] = None
    url: str
    source: str  # 'news_api', 'twitter', 'reddit', etc.
    
    # Sentiment analysis
    sentiment_score: float  # -1 to 1
    sentiment_label: str  # 'positive', 'negative', 'neutral'
    confidence: float
    
    # Keywords and entities
    keywords: List[str] = []
    entities: List[Dict[str, Any]] = []
    
    # Metadata
    published_at: datetime
    collected_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Impact assessment
    impact_score: Optional[float] = None  # How much this news affects credit risk
    risk_factors: List[str] = []  # Identified risk factors
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "company_ticker": "AAPL",
                "company_name": "Apple Inc.",
                "title": "Apple Announces Debt Restructuring",
                "content": "Apple Inc. has announced a major debt restructuring...",
                "sentiment_score": -0.7,
                "sentiment_label": "negative",
                "confidence": 0.85,
                "impact_score": 0.3,
                "risk_factors": ["debt_restructuring", "financial_stress"]
            }
        } 