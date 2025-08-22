from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio

from app.core.database import get_db
from app.models.company import Company
from app.services.data_ingestion import DataIngestionService
from app.services.sentiment_analysis import SentimentAnalysisService

router = APIRouter()


@router.post("/ingest/{ticker}")
async def ingest_company_data(
    ticker: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger data ingestion for a specific company"""
    try:
        # Check if company exists
        company = db.query(Company).filter(Company.ticker == ticker).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Add to background tasks
        background_tasks.add_task(ingest_company_data_task, ticker, db)
        
        return {
            "message": f"Data ingestion started for {ticker}",
            "ticker": ticker,
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/batch")
async def batch_ingest_data(
    tickers: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger data ingestion for multiple companies"""
    try:
        # Validate tickers
        valid_tickers = []
        for ticker in tickers:
            company = db.query(Company).filter(Company.ticker == ticker).first()
            if company:
                valid_tickers.append(ticker)
            else:
                raise HTTPException(status_code=404, detail=f"Company {ticker} not found")
        
        # Add to background tasks
        background_tasks.add_task(batch_ingest_data_task, valid_tickers, db)
        
        return {
            "message": f"Batch data ingestion started for {len(valid_tickers)} companies",
            "tickers": valid_tickers,
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/all")
async def ingest_all_companies_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger data ingestion for all companies"""
    try:
        # Get all companies
        companies = db.query(Company).all()
        tickers = [company.ticker for company in companies]
        
        if not tickers:
            raise HTTPException(status_code=404, detail="No companies found")
        
        # Add to background tasks
        background_tasks.add_task(batch_ingest_data_task, tickers, db)
        
        return {
            "message": f"Data ingestion started for all {len(tickers)} companies",
            "total_companies": len(tickers),
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{ticker}")
async def get_ingestion_status(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get data ingestion status for a company"""
    try:
        company = db.query(Company).filter(Company.ticker == ticker).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Check latest financial data
        from app.models.financial_data import FinancialData
        latest_financial = (
            db.query(FinancialData)
            .filter(FinancialData.company_id == company.id)
            .order_by(FinancialData.data_date.desc())
            .first()
        )
        
        # Check latest news data
        from app.core.database import get_mongodb_sync
        mongodb = get_mongodb_sync()
        news_collection = mongodb.news_data
        
        latest_news = news_collection.find_one(
            {'company_ticker': ticker},
            sort=[('published_at', -1)]
        )
        
        return {
            "ticker": ticker,
            "company_name": company.name,
            "latest_financial_data": latest_financial.data_date if latest_financial else None,
            "latest_news_data": latest_news['published_at'] if latest_news else None,
            "data_freshness": "current" if latest_financial else "stale"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def ingest_company_data_task(ticker: str, db: Session):
    """Background task for ingesting company data"""
    try:
        ingestion_service = DataIngestionService()
        async with ingestion_service:
            await ingestion_service.ingest_company_data(ticker, db)
    except Exception as e:
        print(f"Error ingesting data for {ticker}: {e}")


async def batch_ingest_data_task(tickers: List[str], db: Session):
    """Background task for batch data ingestion"""
    try:
        ingestion_service = DataIngestionService()
        async with ingestion_service:
            await ingestion_service.batch_ingest_data(tickers, db)
    except Exception as e:
        print(f"Error in batch data ingestion: {e}") 