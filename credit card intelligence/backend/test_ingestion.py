#!/usr/bin/env python3
"""
Test script for data ingestion
Run this to test and debug the ingestion process
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_news_api():
    """Test News API connection"""
    print("🔍 Testing News API...")
    try:
        from app.core.config import settings
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            url = f"{settings.NEWS_API_BASE_URL}/top-headlines"
            params = {
                'country': 'us',
                'category': 'business',
                'pageSize': 5,
                'apiKey': settings.NEWS_API_KEY
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ News API working! Found {data.get('totalResults', 0)} articles")
                    return True
                else:
                    print(f"❌ News API error: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ News API test failed: {e}")
        return False

async def test_yahoo_finance():
    """Test Yahoo Finance API"""
    print("🔍 Testing Yahoo Finance...")
    try:
        import yfinance as yf
        
        stock = yf.Ticker("AAPL")
        info = stock.info
        hist = stock.history(period="1d")
        
        if not hist.empty:
            print(f"✅ Yahoo Finance working! AAPL price: ${hist['Close'].iloc[-1]:.2f}")
            return True
        else:
            print("❌ Yahoo Finance returned empty data")
            return False
            
    except Exception as e:
        print(f"❌ Yahoo Finance test failed: {e}")
        return False

async def test_database_connections():
    """Test database connections"""
    print("🔍 Testing database connections...")
    
    # Test PostgreSQL
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine
        
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ PostgreSQL connection successful")
            postgres_ok = True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        postgres_ok = False
    
    # Test MongoDB
    try:
        from app.core.database import get_mongodb_sync
        
        mongodb = get_mongodb_sync()
        mongodb.admin.command('ping')
        print("✅ MongoDB connection successful")
        mongo_ok = True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        mongo_ok = False
    
    return postgres_ok and mongo_ok

async def test_ingestion_service():
    """Test the data ingestion service"""
    print("🔍 Testing data ingestion service...")
    try:
        from app.services.data_ingestion import DataIngestionService
        
        async with DataIngestionService() as service:
            # Test news fetching
            news_data = await service.fetch_news_data("Apple Inc.", "AAPL")
            print(f"✅ News fetching: {len(news_data)} articles")
            
            # Test financial data fetching
            financial_data = await service.fetch_yahoo_finance_data("AAPL")
            if financial_data:
                print(f"✅ Financial data fetching: ${financial_data.get('price', 0):.2f}")
            else:
                print("❌ Financial data fetching failed")
            
            return True
            
    except Exception as e:
        print(f"❌ Ingestion service test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Credit Intelligence Platform - Data Ingestion Test")
    print("=" * 60)
    
    tests = [
        ("News API", test_news_api),
        ("Yahoo Finance", test_yahoo_finance),
        ("Database Connections", test_database_connections),
        ("Ingestion Service", test_ingestion_service)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your ingestion service should work.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Common fixes:")
        print("- Ensure environment variables are set correctly")
        print("- Check database connections")
        print("- Verify API keys are valid")
        print("- Check network connectivity")

if __name__ == "__main__":
    asyncio.run(main()) 