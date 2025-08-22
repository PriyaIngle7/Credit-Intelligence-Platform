# 🔧 Data Ingestion Troubleshooting Guide

## Common Issues and Solutions

### 1. "Failed to Start Ingestion" Error

#### **Problem**: Ingestion fails to start or crashes immediately

#### **Solutions**:

**Check Environment Variables:**
```bash
# Ensure these are set in Replit Secrets
POSTGRES_SERVER=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_DB=credit_intelligence
POSTGRES_USER=your-postgres-user
POSTGRES_PASSWORD=your-postgres-password
MONGODB_URL=mongodb+srv://priyaingle456:CLcRSTcllzOzrEpg@creditintelligence.hk0sndt.mongodb.net/
MONGODB_DB=credit_intelligence
NEWS_API_KEY=894690e075494683a4bbc7b7fc52456a
```

**Test Database Connections:**
```bash
cd backend
python test_ingestion.py
```

**Check Logs:**
- Look at the Replit console for error messages
- Check if databases are accessible

### 2. Database Connection Issues

#### **PostgreSQL Problems:**
- **Error**: "Connection refused" or "Authentication failed"
- **Solution**: 
  - Verify database credentials
  - Check if database allows external connections
  - Use free services like Neon or Supabase

#### **MongoDB Problems:**
- **Error**: "Connection timeout" or "Authentication failed"
- **Solution**:
  - Verify your Atlas connection string
  - Check IP whitelist (allow all IPs: 0.0.0.0/0)
  - Ensure username/password are correct

### 3. API Connection Issues

#### **News API Problems:**
- **Error**: "401 Unauthorized" or "403 Forbidden"
- **Solution**:
  - Verify API key: `894690e075494683a4bbc7b7fc52456a`
  - Check if you've exceeded rate limits
  - Ensure the API key is active

#### **Yahoo Finance Problems:**
- **Error**: "No data found" or connection timeout
- **Solution**:
  - Check internet connectivity
  - Verify ticker symbols are valid
  - Try different tickers (AAPL, MSFT, GOOGL)

### 4. Missing Dependencies

#### **Installation Issues:**
```bash
cd backend
pip install -r requirements.txt
```

**Common Missing Packages:**
- `yfinance` - for stock data
- `aiohttp` - for async HTTP requests
- `textblob` - for sentiment analysis
- `motor` - for MongoDB async operations

### 5. Step-by-Step Debugging

#### **Step 1: Run the Test Script**
```bash
cd backend
python test_ingestion.py
```

#### **Step 2: Check Individual Components**
```bash
# Test News API directly
curl "https://newsapi.org/v2/top-headlines?country=us&apiKey=894690e075494683a4bbc7b7fc52456a"

# Test database connections
python -c "
from app.core.database import get_mongodb_sync
mongodb = get_mongodb_sync()
mongodb.admin.command('ping')
print('MongoDB OK')
"
```

#### **Step 3: Check Environment**
```bash
# Verify environment variables
python -c "
from app.core.config import settings
print(f'News API Key: {settings.NEWS_API_KEY[:10]}...')
print(f'MongoDB URL: {settings.MONGODB_URL[:30]}...')
print(f'PostgreSQL: {settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}')
"
```

### 6. Quick Fixes for Common Scenarios

#### **Scenario A: Fresh Replit Setup**
1. Set all environment variables in Secrets
2. Install dependencies: `pip install -r requirements.txt`
3. Run test: `python test_ingestion.py`
4. Start the app: `python run.py`

#### **Scenario B: Database Connection Issues**
1. Use free database services:
   - **PostgreSQL**: [Neon](https://neon.tech) (free 3GB)
   - **MongoDB**: Already configured with Atlas
2. Update environment variables
3. Test connections again

#### **Scenario C: API Rate Limits**
1. Check News API usage at [newsapi.org](https://newsapi.org)
2. Reduce request frequency
3. Implement caching if needed

### 7. Testing Your Setup

#### **Test Individual Endpoints:**
```bash
# Test news endpoint
curl "https://your-repl-url.repl.co/api/v1/news/top-headlines"

# Test company news
curl "https://your-repl-url.repl.co/api/v1/news/company/AAPL"

# Test data ingestion
curl -X POST "https://your-repl-url.repl.co/api/v1/data/ingest/AAPL"
```

#### **Monitor Logs:**
- Watch the Replit console for real-time logs
- Check for specific error messages
- Verify successful operations

### 8. Still Having Issues?

#### **Check These:**
1. **Network**: Can Replit access external APIs?
2. **Dependencies**: Are all packages installed correctly?
3. **Environment**: Are all variables set?
4. **Database**: Are connections working?
5. **API Keys**: Are they valid and active?

#### **Get Help:**
1. Run `python test_ingestion.py` and share the output
2. Check the Replit console for specific error messages
3. Verify your environment variables are set correctly
4. Test database connectivity separately

## 🎯 Quick Success Checklist

- [ ] Environment variables set in Replit Secrets
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test script runs successfully (`python test_ingestion.py`)
- [ ] Database connections working
- [ ] API keys valid and active
- [ ] App starts without errors (`python run.py`)

If you check all these boxes, your ingestion should work! 🚀 