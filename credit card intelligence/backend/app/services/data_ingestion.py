import yfinance as yf
import requests
import pandas as pd
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp

from app.core.config import settings
from app.models.company import Company
from app.models.financial_data import FinancialData
from app.models.news_data import NewsData

logger = logging.getLogger(__name__)


class DataIngestionService:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_yahoo_finance_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch financial data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            
            # Get basic info
            info = stock.info
            hist = stock.history(period="1y")
            
            if hist.empty:
                logger.warning(f"No historical data found for {ticker}")
                return {}
            
            # Calculate key metrics
            latest_price = hist['Close'].iloc[-1]
            price_change = hist['Close'].iloc[-1] - hist['Close'].iloc[-2] if len(hist) > 1 else 0
            price_change_pct = (price_change / hist['Close'].iloc[-2]) * 100 if len(hist) > 1 else 0
            
            # Get financial ratios
            market_cap = info.get('marketCap', 0)
            pe_ratio = info.get('trailingPE', 0)
            debt_to_equity = info.get('debtToEquity', 0)
            current_ratio = info.get('currentRatio', 0)
            
            return {
                'ticker': ticker,
                'price': latest_price,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'market_cap': market_cap,
                'pe_ratio': pe_ratio,
                'debt_to_equity': debt_to_equity,
                'current_ratio': current_ratio,
                'volume': hist['Volume'].iloc[-1],
                'high_52w': hist['High'].max(),
                'low_52w': hist['Low'].min(),
                'data_date': datetime.now(),
                'source': 'yahoo_finance'
            }
            
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance data for {ticker}: {e}")
            return {}
    
    async def fetch_news_data(self, company_name: str, ticker: str) -> List[Dict[str, Any]]:
        """Fetch news data from News API"""
        try:
            if not settings.NEWS_API_KEY:
                logger.warning("News API key not configured")
                return []
            
            # First try to get company-specific news
            company_news = await self._fetch_company_news(company_name, ticker)
            
            # Then get general financial news that might affect the company
            general_news = await self._fetch_general_financial_news()
            
            # Combine and deduplicate
            all_news = company_news + general_news
            unique_news = self._deduplicate_news(all_news)
            
            logger.info(f"Fetched {len(unique_news)} news articles for {ticker}")
            return unique_news
            
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
            return []
    
    async def _fetch_company_news(self, company_name: str, ticker: str) -> List[Dict[str, Any]]:
        """Fetch company-specific news"""
        try:
            url = f"{settings.NEWS_API_BASE_URL}/everything"
            params = {
                'q': f'"{company_name}" OR "{ticker}"',
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 20,
                'apiKey': settings.NEWS_API_KEY
            }
            
            if self.session:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        
                        news_data = []
                        for article in articles:
                            news_item = {
                                'title': article.get('title', ''),
                                'content': article.get('content', ''),
                                'url': article.get('url', ''),
                                'source': article.get('source', {}).get('name', 'news_api'),
                                'published_at': datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')),
                                'company_name': company_name,
                                'company_ticker': ticker,
                                'news_type': 'company_specific'
                            }
                            news_data.append(news_item)
                        
                        return news_data
                    else:
                        logger.error(f"News API error: {response.status}")
                        return []
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching company news: {e}")
            return []
    
    async def _fetch_general_financial_news(self) -> List[Dict[str, Any]]:
        """Fetch general financial news that might affect credit markets"""
        try:
            url = f"{settings.NEWS_API_BASE_URL}/top-headlines"
            params = {
                'country': 'us',
                'category': 'business',
                'pageSize': 30,
                'apiKey': settings.NEWS_API_KEY
            }
            
            if self.session:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = data.get('articles', [])
                        
                        news_data = []
                        for article in articles:
                            # Check if article is relevant to credit/financial markets
                            if self._is_financial_relevant(article):
                                news_item = {
                                    'title': article.get('title', ''),
                                    'content': article.get('content', ''),
                                    'url': article.get('url', ''),
                                    'source': article.get('source', {}).get('name', 'news_api'),
                                    'published_at': datetime.fromisoformat(article.get('publishedAt', '').replace('Z', '+00:00')),
                                    'company_name': 'general',
                                    'company_ticker': 'MARKET',
                                    'news_type': 'general_financial'
                                }
                                news_data.append(news_item)
                        
                        return news_data
                    else:
                        logger.error(f"News API top-headlines error: {response.status}")
                        return []
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching general financial news: {e}")
            return []
    
    def _is_financial_relevant(self, article: Dict[str, Any]) -> bool:
        """Check if a news article is relevant to credit/financial markets"""
        relevant_keywords = [
            'credit', 'debt', 'bond', 'interest rate', 'federal reserve', 'fed',
            'inflation', 'recession', 'economic', 'financial', 'banking',
            'default', 'bankruptcy', 'restructuring', 'liquidity', 'risk',
            'market', 'trading', 'investment', 'portfolio', 'asset'
        ]
        
        title = article.get('title', '').lower()
        content = article.get('content', '').lower()
        
        for keyword in relevant_keywords:
            if keyword in title or keyword in content:
                return True
        
        return False
    
    def _deduplicate_news(self, news_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate news articles based on title similarity"""
        seen_titles = set()
        unique_news = []
        
        for news in news_list:
            # Simple deduplication based on title
            title_key = news['title'].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_news.append(news)
        
        return unique_news
    
    async def fetch_world_bank_data(self, country_code: str = "US") -> Dict[str, Any]:
        """Fetch economic indicators from World Bank API"""
        try:
            # World Bank API endpoints for key economic indicators
            indicators = {
                'GDP': 'NY.GDP.MKTP.CD',  # GDP (current US$)
                'INFLATION': 'FP.CPI.TOTL.ZG',  # Inflation, consumer prices (annual %)
                'INTEREST_RATE': 'FR.INR.RINR',  # Real interest rate (%)
                'UNEMPLOYMENT': 'SL.UEM.TOTL.ZS',  # Unemployment, total (% of total labor force)
                'DEBT': 'GC.DOD.TOTL.GD.ZS'  # Central government debt, total (% of GDP)
            }
            
            world_bank_data = {}
            
            for indicator_name, indicator_code in indicators.items():
                try:
                    url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/{indicator_code}"
                    params = {
                        'format': 'json',
                        'per_page': 1,
                        'date': datetime.now().year
                    }
                    
                    if self.session:
                        async with self.session.get(url, params=params) as response:
                            if response.status == 200:
                                data = await response.json()
                                if len(data) > 1 and data[1]:
                                    value = data[1][0].get('value')
                                    if value is not None:
                                        world_bank_data[indicator_name.lower()] = value
                    
                    # Small delay to avoid overwhelming the API
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Error fetching {indicator_name}: {e}")
                    continue
            
            return {
                'country_code': country_code,
                'data_date': datetime.now(),
                'indicators': world_bank_data,
                'source': 'world_bank'
            }
            
        except Exception as e:
            logger.error(f"Error fetching World Bank data: {e}")
            return {}
    
    async def ingest_company_data(self, ticker: str, db) -> Dict[str, Any]:
        """Ingest all data for a specific company"""
        try:
            # Get company info from database
            company = db.query(Company).filter(Company.ticker == ticker).first()
            if not company:
                raise ValueError(f"Company {ticker} not found in database")
            
            logger.info(f"Starting data ingestion for {ticker}")
            
            # Fetch financial data
            financial_data = await self.fetch_yahoo_finance_data(ticker)
            
            # Fetch news data
            news_data = await self.fetch_news_data(company.name, ticker)
            
            # Fetch economic indicators
            economic_data = await self.fetch_world_bank_data()
            
            # Save financial data to PostgreSQL
            if financial_data:
                financial_record = FinancialData(
                    company_id=company.id,
                    data_date=financial_data['data_date'],
                    price=financial_data['price'],
                    market_cap=financial_data['market_cap'],
                    pe_ratio=financial_data['pe_ratio'],
                    debt_to_equity=financial_data['debt_to_equity'],
                    current_ratio=financial_data['current_ratio'],
                    volume=financial_data['volume'],
                    source=financial_data['source']
                )
                db.add(financial_record)
                db.commit()
                logger.info(f"Saved financial data for {ticker}")
            
            # Save news data to MongoDB
            if news_data:
                from app.core.database import get_mongodb_sync
                mongodb = get_mongodb_sync()
                news_collection = mongodb.news_data
                
                for news_item in news_data:
                    # Add sentiment analysis
                    sentiment_score, sentiment_label = self._analyze_sentiment(news_item['title'] + ' ' + news_item['content'])
                    
                    news_record = {
                        'company_ticker': news_item['company_ticker'],
                        'company_name': news_item['company_name'],
                        'title': news_item['title'],
                        'content': news_item['content'],
                        'url': news_item['url'],
                        'source': news_item['source'],
                        'published_at': news_item['published_at'],
                        'news_type': news_item['news_type'],
                        'sentiment_score': sentiment_score,
                        'sentiment_label': sentiment_label,
                        'confidence': 0.8,
                        'collected_at': datetime.utcnow()
                    }
                    
                    news_collection.insert_one(news_record)
                
                logger.info(f"Saved {len(news_data)} news articles for {ticker}")
            
            return {
                'ticker': ticker,
                'financial_data': bool(financial_data),
                'news_data': len(news_data),
                'economic_data': bool(economic_data),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error ingesting data for {ticker}: {e}")
            return {
                'ticker': ticker,
                'status': 'error',
                'error': str(e)
            }
    
    async def batch_ingest_data(self, tickers: List[str], db) -> Dict[str, Any]:
        """Ingest data for multiple companies"""
        try:
            results = []
            for ticker in tickers:
                try:
                    result = await self.ingest_company_data(ticker, db)
                    results.append(result)
                    # Small delay between companies to avoid overwhelming APIs
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error(f"Error ingesting data for {ticker}: {e}")
                    results.append({
                        'ticker': ticker,
                        'status': 'error',
                        'error': str(e)
                    })
            
            return {
                'total_companies': len(tickers),
                'successful': len([r for r in results if r['status'] == 'success']),
                'failed': len([r for r in results if r['status'] == 'error']),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error in batch data ingestion: {e}")
            return {
                'total_companies': len(tickers),
                'successful': 0,
                'failed': len(tickers),
                'error': str(e)
            }
    
    def _analyze_sentiment(self, text: str) -> tuple[float, str]:
        """Simple sentiment analysis using TextBlob"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            sentiment_score = blob.sentiment.polarity
            
            if sentiment_score > 0.1:
                sentiment_label = 'positive'
            elif sentiment_score < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            return sentiment_score, sentiment_label
            
        except Exception as e:
            logger.warning(f"Error in sentiment analysis: {e}")
            return 0.0, 'neutral' 