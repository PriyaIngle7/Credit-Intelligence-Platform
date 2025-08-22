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
            
            # Get financial statements
            balance_sheet = stock.balance_sheet
            income_stmt = stock.income_stmt
            cash_flow = stock.cashflow
            
            # Get latest data
            latest_balance = balance_sheet.iloc[:, 0] if not balance_sheet.empty else pd.Series()
            latest_income = income_stmt.iloc[:, 0] if not income_stmt.empty else pd.Series()
            latest_cashflow = cash_flow.iloc[:, 0] if not cash_flow.empty else pd.Series()
            
            # Calculate ratios
            total_assets = latest_balance.get('Total Assets', 0)
            total_liabilities = latest_balance.get('Total Liabilities Net Minority Interest', 0)
            total_equity = latest_balance.get('Total Equity Gross Minority Interest', 0)
            current_assets = latest_balance.get('Current Assets', 0)
            current_liabilities = latest_balance.get('Current Liabilities', 0)
            long_term_debt = latest_balance.get('Long Term Debt', 0)
            short_term_debt = latest_balance.get('Short Term Debt', 0)
            cash = latest_balance.get('Cash and Cash Equivalents', 0)
            
            net_income = latest_income.get('Net Income', 0)
            ebitda = latest_income.get('EBITDA', 0)
            operating_cash_flow = latest_cashflow.get('Operating Cash Flow', 0)
            
            # Calculate ratios
            debt_to_equity = (long_term_debt + short_term_debt) / total_equity if total_equity else 0
            current_ratio = current_assets / current_liabilities if current_liabilities else 0
            quick_ratio = (current_assets - latest_balance.get('Inventory', 0)) / current_liabilities if current_liabilities else 0
            cash_ratio = cash / current_liabilities if current_liabilities else 0
            debt_to_ebitda = (long_term_debt + short_term_debt) / ebitda if ebitda else 0
            roe = net_income / total_equity if total_equity else 0
            roa = net_income / total_assets if total_assets else 0
            
            return {
                'total_assets': float(total_assets),
                'total_liabilities': float(total_liabilities),
                'total_equity': float(total_equity),
                'current_assets': float(current_assets),
                'current_liabilities': float(current_liabilities),
                'long_term_debt': float(long_term_debt),
                'short_term_debt': float(short_term_debt),
                'cash_and_equivalents': float(cash),
                'net_income': float(net_income),
                'ebitda': float(ebitda),
                'operating_cash_flow': float(operating_cash_flow),
                'debt_to_equity_ratio': float(debt_to_equity),
                'current_ratio': float(current_ratio),
                'quick_ratio': float(quick_ratio),
                'cash_ratio': float(cash_ratio),
                'debt_to_ebitda': float(debt_to_ebitda),
                'roe': float(roe),
                'roa': float(roa),
                'stock_price': float(info.get('currentPrice', 0)),
                'market_cap': float(info.get('marketCap', 0)),
                'enterprise_value': float(info.get('enterpriseValue', 0)),
                'pe_ratio': float(info.get('trailingPE', 0)),
                'pb_ratio': float(info.get('priceToBook', 0)),
                'ev_to_ebitda': float(info.get('enterpriseToEbitda', 0)),
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
            
            url = "https://newsapi.org/v2/everything"
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
                                'company_ticker': ticker
                            }
                            news_data.append(news_item)
                        
                        return news_data
                    else:
                        logger.error(f"News API error: {response.status}")
                        return []
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching news data: {e}")
            return []
    
    async def fetch_world_bank_data(self, country_code: str = "US") -> Dict[str, Any]:
        """Fetch economic indicators from World Bank API"""
        try:
            # World Bank API endpoint for GDP growth
            url = f"http://api.worldbank.org/v2/country/{country_code}/indicator/NY.GDP.MKTP.KD.ZG"
            params = {
                'format': 'json',
                'per_page': 5
            }
            
            if self.session:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if len(data) > 1 and data[1]:
                            latest_data = data[1][0]
                            return {
                                'gdp_growth': float(latest_data.get('value', 0)),
                                'year': int(latest_data.get('date', 2023)),
                                'country_code': country_code
                            }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching World Bank data: {e}")
            return {}
    
    async def ingest_company_data(self, ticker: str, db) -> bool:
        """Ingest all data for a company"""
        try:
            # Check if company exists
            company = db.query(Company).filter(Company.ticker == ticker).first()
            if not company:
                logger.error(f"Company {ticker} not found in database")
                return False
            
            # Fetch financial data
            financial_data = await self.fetch_yahoo_finance_data(ticker)
            if financial_data:
                # Save financial data
                db_financial = FinancialData(
                    company_id=company.id,
                    **financial_data
                )
                db.add(db_financial)
                db.commit()
                logger.info(f"Financial data ingested for {ticker}")
            
            # Fetch news data
            news_data = await self.fetch_news_data(company.name, ticker)
            if news_data:
                # Save news data to MongoDB
                from app.core.database import get_mongodb_sync
                mongodb = get_mongodb_sync()
                news_collection = mongodb.news_data
                
                for news_item in news_data:
                    news_doc = NewsData(**news_item)
                    news_collection.insert_one(news_doc.dict())
                
                logger.info(f"News data ingested for {ticker}: {len(news_data)} articles")
            
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting data for {ticker}: {e}")
            return False
    
    async def batch_ingest_data(self, tickers: List[str], db) -> Dict[str, bool]:
        """Ingest data for multiple companies"""
        results = {}
        
        async with self:
            tasks = [self.ingest_company_data(ticker, db) for ticker in tickers]
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            for ticker, result in zip(tickers, results_list):
                if isinstance(result, Exception):
                    logger.error(f"Error ingesting data for {ticker}: {result}")
                    results[ticker] = False
                else:
                    results[ticker] = result
        
        return results 