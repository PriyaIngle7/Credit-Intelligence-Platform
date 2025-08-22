from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class CreditScoreBase(BaseModel):
    score: float
    score_type: str
    confidence: float
    risk_level: str
    feature_contributions: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    key_factors: Optional[List[str]] = None
    model_version: Optional[str] = None


class CreditScoreCreate(CreditScoreBase):
    company_id: int


class CreditScoreUpdate(BaseModel):
    score: Optional[float] = None
    confidence: Optional[float] = None
    risk_level: Optional[str] = None
    feature_contributions: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    key_factors: Optional[List[str]] = None


class CreditScoreResponse(CreditScoreBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CreditScoreWithCompany(CreditScoreResponse):
    company_name: str
    company_ticker: str
    company_sector: Optional[str] = None


class CreditScoreTrend(BaseModel):
    date: datetime
    score: float
    risk_level: str
    change: Optional[float] = None  # Score change from previous period


class CreditScoreComparison(BaseModel):
    company_ticker: str
    company_name: str
    current_score: float
    previous_score: Optional[float] = None
    score_change: Optional[float] = None
    risk_level: str
    confidence: float
    key_factors: List[str] 