from textblob import TextBlob
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re

from app.core.database import get_mongodb_sync
from app.models.news_data import NewsData

logger = logging.getLogger(__name__)


class SentimentAnalysisService:
    def __init__(self):
        self.mongodb = get_mongodb_sync()
    
    async def get_company_sentiment(self, ticker: str, days: int = 7) -> float:
        """Get overall sentiment score for a company based on recent news"""
        try:
            # Get recent news articles for the company
            start_date = datetime.utcnow() - timedelta(days=days)
            
            news_collection = self.mongodb.news_data
            news_articles = list(news_collection.find({
                'company_ticker': ticker,
                'published_at': {'$gte': start_date}
            }).sort('published_at', -1).limit(50))
            
            if not news_articles:
                logger.warning(f"No news articles found for {ticker}")
                return 0.0
            
            # Calculate weighted sentiment score
            total_sentiment = 0.0
            total_weight = 0.0
            
            for article in news_articles:
                # Calculate article weight based on recency and source credibility
                days_old = (datetime.utcnow() - article['published_at']).days
                recency_weight = max(0.1, 1.0 - (days_old / days))
                
                # Source credibility weight
                source_weight = self._get_source_credibility(article.get('source', ''))
                
                # Combined weight
                weight = recency_weight * source_weight
                
                # Get sentiment score
                sentiment_score = article.get('sentiment_score', 0.0)
                
                total_sentiment += sentiment_score * weight
                total_weight += weight
            
            if total_weight > 0:
                return total_sentiment / total_weight
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Error calculating sentiment for {ticker}: {e}")
            return 0.0
    
    def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a given text"""
        try:
            # Clean text
            cleaned_text = self._clean_text(text)
            
            # Analyze with TextBlob
            blob = TextBlob(cleaned_text)
            
            # Get polarity (-1 to 1) and subjectivity (0 to 1)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Determine sentiment label
            if polarity > 0.1:
                sentiment_label = "positive"
            elif polarity < -0.1:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
            
            # Calculate confidence based on subjectivity
            confidence = 1.0 - subjectivity
            
            # Extract keywords
            keywords = self._extract_keywords(cleaned_text)
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(cleaned_text)
            
            return {
                'sentiment_score': polarity,
                'sentiment_label': sentiment_label,
                'confidence': confidence,
                'subjectivity': subjectivity,
                'keywords': keywords,
                'risk_factors': risk_factors
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {e}")
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'confidence': 0.0,
                'subjectivity': 0.5,
                'keywords': [],
                'risk_factors': []
            }
    
    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\-\:]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        try:
            blob = TextBlob(text.lower())
            
            # Get noun phrases and important words
            keywords = []
            
            # Add noun phrases
            keywords.extend([phrase.lower() for phrase in blob.noun_phrases])
            
            # Add important individual words (nouns, adjectives)
            for word, tag in blob.tags:
                if tag.startswith(('NN', 'JJ')) and len(word) > 3:
                    keywords.append(word.lower())
            
            # Remove duplicates and common words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            keywords = [word for word in set(keywords) if word not in stop_words]
            
            return keywords[:10]  # Return top 10 keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def _identify_risk_factors(self, text: str) -> List[str]:
        """Identify risk factors mentioned in text"""
        risk_keywords = {
            'debt': ['debt', 'loan', 'borrowing', 'credit', 'leverage'],
            'financial_stress': ['bankruptcy', 'default', 'insolvency', 'liquidation', 'restructuring'],
            'market_risk': ['volatility', 'market crash', 'bear market', 'recession'],
            'operational_risk': ['operational issues', 'supply chain', 'production problems'],
            'regulatory_risk': ['regulation', 'compliance', 'legal issues', 'lawsuit'],
            'competition': ['competition', 'market share loss', 'competitive pressure'],
            'economic_risk': ['inflation', 'interest rates', 'economic downturn', 'gdp'],
            'geopolitical_risk': ['trade war', 'sanctions', 'political instability']
        }
        
        text_lower = text.lower()
        identified_risks = []
        
        for risk_category, keywords in risk_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    identified_risks.append(risk_category)
                    break
        
        return list(set(identified_risks))
    
    def _get_source_credibility(self, source: str) -> float:
        """Get credibility weight for a news source"""
        high_credibility = {
            'reuters', 'bloomberg', 'wall street journal', 'financial times',
            'cnbc', 'marketwatch', 'yahoo finance', 'seeking alpha'
        }
        
        medium_credibility = {
            'cnn', 'bbc', 'forbes', 'fortune', 'business insider',
            'techcrunch', 'venturebeat'
        }
        
        source_lower = source.lower()
        
        if source_lower in high_credibility:
            return 1.0
        elif source_lower in medium_credibility:
            return 0.7
        else:
            return 0.5
    
    async def analyze_news_sentiment_batch(self, news_articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze sentiment for a batch of news articles"""
        analyzed_articles = []
        
        for article in news_articles:
            # Combine title and content for analysis
            text = f"{article.get('title', '')} {article.get('content', '')}"
            
            # Analyze sentiment
            sentiment_analysis = self.analyze_text_sentiment(text)
            
            # Add sentiment data to article
            article.update(sentiment_analysis)
            analyzed_articles.append(article)
        
        return analyzed_articles
    
    async def get_sector_sentiment(self, sector: str, days: int = 7) -> float:
        """Get overall sentiment for a sector"""
        try:
            # Get all companies in the sector
            from app.core.database import get_db
            db = next(get_db())
            
            from app.models.company import Company
            companies = db.query(Company).filter(Company.sector == sector).all()
            
            if not companies:
                return 0.0
            
            # Calculate average sentiment across companies in the sector
            total_sentiment = 0.0
            company_count = 0
            
            for company in companies:
                sentiment = await self.get_company_sentiment(company.ticker, days)
                total_sentiment += sentiment
                company_count += 1
            
            return total_sentiment / company_count if company_count > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating sector sentiment: {e}")
            return 0.0 