from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio

from app.core.database import get_db
from app.services.data_ingestion import DataIngestionService
from app.services.sentiment_analysis import SentimentAnalysisService

router = APIRouter()


@router.get("/top-headlines")
async def get_top_headlines(
    country: str = Query("us", description="Country code for headlines"),
    category: Optional[str] = Query("business", description="News category"),
    page_size: int = Query(20, ge=1, le=100, description="Number of articles to return")
):
    """Get top headlines from News API"""
    try:
        async with DataIngestionService() as ingestion_service:
            # Fetch top headlines
            url = f"{ingestion_service.settings.NEWS_API_BASE_URL}/top-headlines"
            params = {
                'country': country,
                'category': category,
                'pageSize': page_size,
                'apiKey': ingestion_service.settings.NEWS_API_KEY
            }
            
            async with ingestion_service.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    
                    # Process articles
                    processed_articles = []
                    for article in articles:
                        processed_article = {
                            'title': article.get('title', ''),
                            'description': article.get('description', ''),
                            'url': article.get('url', ''),
                            'urlToImage': article.get('urlToImage', ''),
                            'source': article.get('source', {}).get('name', ''),
                            'publishedAt': article.get('publishedAt', ''),
                            'content': article.get('content', ''),
                            'relevance_score': _calculate_relevance_score(article)
                        }
                        processed_articles.append(processed_article)
                    
                    return {
                        'status': 'ok',
                        'totalResults': data.get('totalResults', 0),
                        'articles': processed_articles,
                        'fetched_at': datetime.utcnow().isoformat()
                    }
                else:
                    raise HTTPException(status_code=response.status, detail="Failed to fetch headlines")
                    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching headlines: {str(e)}")


@router.get("/company/{ticker}")
async def get_company_news(
    ticker: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of articles")
):
    """Get news articles for a specific company"""
    try:
        from app.core.database import get_mongodb_sync
        mongodb = get_mongodb_sync()
        news_collection = mongodb.news_data
        
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Query MongoDB for company news
        news_articles = list(news_collection.find({
            'company_ticker': ticker.upper(),
            'published_at': {'$gte': start_date}
        }).sort('published_at', -1).limit(limit))
        
        # Process articles
        processed_articles = []
        for article in news_articles:
            processed_article = {
                'title': article.get('title', ''),
                'content': article.get('content', ''),
                'url': article.get('url', ''),
                'source': article.get('source', ''),
                'published_at': article.get('published_at', ''),
                'sentiment_score': article.get('sentiment_score', 0),
                'sentiment_label': article.get('sentiment_label', 'neutral'),
                'news_type': article.get('news_type', 'unknown')
            }
            processed_articles.append(processed_article)
        
        return {
            'ticker': ticker.upper(),
            'total_articles': len(processed_articles),
            'date_range_days': days,
            'articles': processed_articles
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company news: {str(e)}")


@router.get("/financial-markets")
async def get_financial_market_news(
    limit: int = Query(30, ge=1, le=100, description="Maximum number of articles")
):
    """Get financial market news that could affect credit markets"""
    try:
        from app.core.database import get_mongodb_sync
        mongodb = get_mongodb_sync()
        news_collection = mongodb.news_data
        
        # Get recent financial market news
        start_date = datetime.utcnow() - timedelta(days=3)
        
        news_articles = list(news_collection.find({
            'news_type': 'general_financial',
            'published_at': {'$gte': start_date}
        }).sort('published_at', -1).limit(limit))
        
        # Process articles
        processed_articles = []
        for article in news_articles:
            processed_article = {
                'title': article.get('title', ''),
                'content': article.get('content', ''),
                'url': article.get('url', ''),
                'source': article.get('source', ''),
                'published_at': article.get('published_at', ''),
                'sentiment_score': article.get('sentiment_score', 0),
                'sentiment_label': article.get('sentiment_label', 'neutral')
            }
            processed_articles.append(processed_article)
        
        return {
            'total_articles': len(processed_articles),
            'date_range_days': 3,
            'articles': processed_articles
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching financial market news: {str(e)}")


@router.get("/sentiment-summary")
async def get_news_sentiment_summary(
    ticker: Optional[str] = Query(None, description="Company ticker for specific analysis"),
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze")
):
    """Get sentiment analysis summary for news"""
    try:
        sentiment_service = SentimentAnalysisService()
        
        if ticker:
            # Company-specific sentiment
            sentiment_score = await sentiment_service.get_company_sentiment(ticker, days)
            return {
                'ticker': ticker.upper(),
                'sentiment_score': sentiment_score,
                'sentiment_label': _get_sentiment_label(sentiment_score),
                'analysis_period_days': days,
                'analysis_type': 'company_specific'
            }
        else:
            # Market-wide sentiment
            market_sentiment = await sentiment_service.get_market_sentiment(days)
            return {
                'sentiment_score': market_sentiment,
                'sentiment_label': _get_sentiment_label(market_sentiment),
                'analysis_period_days': days,
                'analysis_type': 'market_wide'
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")


@router.post("/refresh/{ticker}")
async def refresh_company_news(
    ticker: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Refresh news data for a specific company"""
    try:
        # Check if company exists
        from app.models.company import Company
        company = db.query(Company).filter(Company.ticker == ticker.upper()).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Add to background tasks
        background_tasks.add_task(_refresh_news_task, ticker, company.name)
        
        return {
            "message": f"News refresh started for {ticker}",
            "ticker": ticker,
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _calculate_relevance_score(article: Dict[str, Any]) -> float:
    """Calculate relevance score for a news article"""
    financial_keywords = [
        'credit', 'debt', 'bond', 'interest rate', 'federal reserve', 'fed',
        'inflation', 'recession', 'economic', 'financial', 'banking',
        'default', 'bankruptcy', 'restructuring', 'liquidity', 'risk',
        'market', 'trading', 'investment', 'portfolio', 'asset'
    ]
    
    title = article.get('title', '').lower()
    content = article.get('content', '').lower()
    
    score = 0.0
    for keyword in financial_keywords:
        if keyword in title:
            score += 0.3  # Title matches are more important
        if keyword in content:
            score += 0.1  # Content matches add to relevance
    
    return min(score, 1.0)  # Cap at 1.0


def _get_sentiment_label(score: float) -> str:
    """Convert sentiment score to label"""
    if score > 0.1:
        return 'positive'
    elif score < -0.1:
        return 'negative'
    else:
        return 'neutral'


async def _refresh_news_task(ticker: str, company_name: str):
    """Background task to refresh news data"""
    try:
        async with DataIngestionService() as ingestion_service:
            news_data = await ingestion_service.fetch_news_data(company_name, ticker)
            print(f"Refreshed {len(news_data)} news articles for {ticker}")
    except Exception as e:
        print(f"Error refreshing news for {ticker}: {e}") 