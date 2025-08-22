#!/usr/bin/env python3
"""
Test script for News API integration
Run this to verify the News API is working correctly
"""
import asyncio
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_news_api():
    """Test the News API integration"""
    try:
        from app.services.data_ingestion import DataIngestionService
        from app.core.config import settings
        
        print("🔍 Testing News API Integration")
        print("=" * 50)
        
        # Check configuration
        print(f"News API Key: {'✅ Set' if settings.NEWS_API_KEY else '❌ Not set'}")
        print(f"News API Base URL: {settings.NEWS_API_BASE_URL}")
        
        if not settings.NEWS_API_KEY:
            print("❌ News API key not configured. Please set NEWS_API_KEY environment variable.")
            return
        
        # Test the service
        async with DataIngestionService() as service:
            print("\n📰 Testing Top Headlines...")
            try:
                headlines = await service._fetch_general_financial_news()
                print(f"✅ Successfully fetched {len(headlines)} financial news articles")
                
                if headlines:
                    print("\n📋 Sample Headlines:")
                    for i, article in enumerate(headlines[:3]):
                        print(f"{i+1}. {article['title'][:80]}...")
                        print(f"   Source: {article['source']}")
                        print(f"   Published: {article['published_at']}")
                        print()
                
            except Exception as e:
                print(f"❌ Error fetching headlines: {e}")
            
            print("\n🏢 Testing Company News...")
            try:
                company_news = await service._fetch_company_news("Apple Inc.", "AAPL")
                print(f"✅ Successfully fetched {len(company_news)} company news articles")
                
                if company_news:
                    print("\n📋 Sample Company News:")
                    for i, article in enumerate(company_news[:2]):
                        print(f"{i+1}. {article['title'][:80]}...")
                        print(f"   Source: {article['source']}")
                        print(f"   Type: {article['news_type']}")
                        print()
                        
            except Exception as e:
                print(f"❌ Error fetching company news: {e}")
        
        print("\n🎉 News API test completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the backend directory and dependencies are installed.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

async def test_direct_api_call():
    """Test direct API call to News API"""
    try:
        import aiohttp
        
        print("\n🔍 Testing Direct News API Call")
        print("=" * 40)
        
        api_key = "894690e075494683a4bbc7b7fc52456a"
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            'country': 'us',
            'category': 'business',
            'pageSize': 5,
            'apiKey': api_key
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    articles = data.get('articles', [])
                    
                    print(f"✅ Direct API call successful!")
                    print(f"Total results: {data.get('totalResults', 0)}")
                    print(f"Fetched articles: {len(articles)}")
                    
                    if articles:
                        print("\n📋 Direct API Results:")
                        for i, article in enumerate(articles[:3]):
                            print(f"{i+1}. {article.get('title', 'No title')}")
                            print(f"   Source: {article.get('source', {}).get('name', 'Unknown')}")
                            print(f"   Published: {article.get('publishedAt', 'Unknown')}")
                            print()
                else:
                    print(f"❌ Direct API call failed: {response.status}")
                    print(f"Response: {await response.text()}")
                    
    except Exception as e:
        print(f"❌ Direct API test failed: {e}")

async def main():
    """Main test function"""
    print("🚀 News API Integration Test")
    print("=" * 60)
    
    # Test direct API call first
    await test_direct_api_call()
    
    # Test service integration
    await test_news_api()
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(main()) 