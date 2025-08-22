from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.credit_score import CreditScore
from app.models.company import Company
from app.schemas.credit_score import CreditScoreResponse, CreditScoreCreate
from app.services.credit_scoring import CreditScoringService

router = APIRouter()


@router.get("/", response_model=List[CreditScoreResponse])
async def get_credit_scores(
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    score_type: Optional[str] = Query(None, description="Filter by score type (issuer/asset_class)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level"),
    limit: int = Query(100, le=1000, description="Number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get credit scores with optional filtering"""
    query = db.query(CreditScore)
    
    if company_id:
        query = query.filter(CreditScore.company_id == company_id)
    if score_type:
        query = query.filter(CreditScore.score_type == score_type)
    if risk_level:
        query = query.filter(CreditScore.risk_level == risk_level)
    
    credit_scores = query.offset(offset).limit(limit).all()
    return credit_scores


@router.get("/{score_id}", response_model=CreditScoreResponse)
async def get_credit_score(
    score_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific credit score by ID"""
    credit_score = db.query(CreditScore).filter(CreditScore.id == score_id).first()
    if not credit_score:
        raise HTTPException(status_code=404, detail="Credit score not found")
    return credit_score


@router.get("/company/{company_ticker}/latest", response_model=CreditScoreResponse)
async def get_latest_credit_score(
    company_ticker: str,
    score_type: str = Query("issuer", description="Score type (issuer/asset_class)"),
    db: Session = Depends(get_db)
):
    """Get the latest credit score for a company"""
    company = db.query(Company).filter(Company.ticker == company_ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    credit_score = (
        db.query(CreditScore)
        .filter(CreditScore.company_id == company.id)
        .filter(CreditScore.score_type == score_type)
        .order_by(CreditScore.created_at.desc())
        .first()
    )
    
    if not credit_score:
        raise HTTPException(status_code=404, detail="Credit score not found")
    
    return credit_score


@router.get("/company/{company_ticker}/history", response_model=List[CreditScoreResponse])
async def get_credit_score_history(
    company_ticker: str,
    days: int = Query(30, description="Number of days of history to retrieve"),
    score_type: str = Query("issuer", description="Score type (issuer/asset_class)"),
    db: Session = Depends(get_db)
):
    """Get credit score history for a company"""
    company = db.query(Company).filter(Company.ticker == company_ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    credit_scores = (
        db.query(CreditScore)
        .filter(CreditScore.company_id == company.id)
        .filter(CreditScore.score_type == score_type)
        .filter(CreditScore.created_at >= start_date)
        .order_by(CreditScore.created_at.desc())
        .all()
    )
    
    return credit_scores


@router.post("/calculate/{company_ticker}", response_model=CreditScoreResponse)
async def calculate_credit_score(
    company_ticker: str,
    score_type: str = Query("issuer", description="Score type (issuer/asset_class)"),
    db: Session = Depends(get_db)
):
    """Calculate a new credit score for a company"""
    company = db.query(Company).filter(Company.ticker == company_ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Use the credit scoring service to calculate the score
    scoring_service = CreditScoringService()
    credit_score_data = await scoring_service.calculate_score(company, score_type, db)
    
    # Create new credit score record
    credit_score = CreditScore(
        company_id=company.id,
        score=credit_score_data["score"],
        score_type=score_type,
        confidence=credit_score_data["confidence"],
        risk_level=credit_score_data["risk_level"],
        feature_contributions=credit_score_data["feature_contributions"],
        explanation=credit_score_data["explanation"],
        key_factors=credit_score_data["key_factors"],
        model_version=credit_score_data["model_version"]
    )
    
    db.add(credit_score)
    db.commit()
    db.refresh(credit_score)
    
    return credit_score


@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Get summary statistics for the dashboard"""
    total_companies = db.query(Company).count()
    total_scores = db.query(CreditScore).count()
    
    # Risk level distribution
    risk_distribution = (
        db.query(CreditScore.risk_level, db.func.count(CreditScore.id))
        .group_by(CreditScore.risk_level)
        .all()
    )
    
    # Recent scores (last 24 hours)
    recent_scores = (
        db.query(CreditScore)
        .filter(CreditScore.created_at >= datetime.utcnow() - timedelta(days=1))
        .count()
    )
    
    return {
        "total_companies": total_companies,
        "total_scores": total_scores,
        "recent_scores": recent_scores,
        "risk_distribution": dict(risk_distribution)
    } 