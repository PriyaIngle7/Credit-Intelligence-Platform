# Deploying Backend on Replit

This guide will help you deploy your Credit Intelligence Platform backend on Replit.

## Prerequisites

1. A Replit account (free at [replit.com](https://replit.com))
2. Your project code (already prepared)

## Step-by-Step Deployment

### 1. Create a New Repl

1. Go to [replit.com](https://replit.com) and sign in
2. Click "Create Repl"
3. Choose "Import from GitHub" 
4. Enter your repository URL: `https://github.com/yourusername/credit-card-intelligence`
5. Select "Python" as the language
6. Click "Import from GitHub"

### 2. Configure the Environment

Once your repl is created, you'll need to set up environment variables:

1. In your repl, click on the "Tools" icon in the left sidebar
2. Select "Secrets"
3. Add the following environment variables with your actual values:

```
# PostgreSQL Configuration
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=credit_intelligence
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123

# MongoDB Configuration
MONGODB_URL=mongodb+srv://priyaingle456:CLcRSTcllzOzrEpg@creditintelligence.hk0sndt.mongodb.net/
MONGODB_DB=credit_intelligence

# Redis Configuration (for Celery)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS
ALLOWED_HOSTS=["*"]

# Environment
ENVIRONMENT=production
DEBUG=false

# Logging
LOG_LEVEL=INFO

# ML Model Paths
MODEL_PATH=ml/models/credit_model.pkl
SHAP_MODEL_PATH=ml/models/shap_explainer.pkl

# Data Refresh Intervals
DATA_REFRESH_INTERVAL=300
MODEL_RETRAIN_INTERVAL=86400
```

**Important Notes:**
- Replace `your-secret-key-here` with a strong, random secret key
- Your MongoDB connection is already configured with Atlas
- For PostgreSQL, you'll need to set up a database service (see Database Setup section)

### 3. Install Dependencies

1. In the Replit shell, run:
```bash
cd backend
pip install -r requirements.txt
```

### 4. Run the Application

1. Click the "Run" button in Replit
2. The application will start and show a URL like: `https://your-repl-name.your-username.repl.co`

### 5. Access Your API

- **Main API**: `https://your-repl-name.your-username.repl.co/`
- **API Documentation**: `https://your-repl-name.your-username.repl.co/docs`
- **Health Check**: `https://your-repl-name.your-username.repl.co/health`

## Configuration Files

The following files have been created for Replit deployment:

- `.replit` - Main Replit configuration
- `backend/.replit` - Backend-specific configuration  
- `backend/pyproject.toml` - Python project configuration
- `backend/run.py` - Entry point script
- `backend/env.example` - Environment variables template (updated with your config)

## Database Setup

### PostgreSQL Options:

**Option 1: Use Replit's Built-in Database**
- Replit provides a built-in SQLite database
- Update your config to use SQLite instead of PostgreSQL

**Option 2: External PostgreSQL Services (Recommended)**
- [Neon](https://neon.tech) - Free tier with 3GB storage
- [Supabase](https://supabase.com) - Free tier with 500MB storage
- [Railway](https://railway.app) - Free tier with $5 credit

**Option 3: Local PostgreSQL (Development Only)**
- Use your local PostgreSQL instance (localhost:5432)

### MongoDB:
- Your MongoDB Atlas connection is already configured
- The connection string is: `mongodb+srv://priyaingle456:CLcRSTcllzOzrEpg@creditintelligence.hk0sndt.mongodb.net/`

### Redis:
- For Celery background tasks
- Consider using [Redis Cloud](https://redis.com/try-free/) free tier

## Environment Variables for Replit

Copy these exact values to your Replit Secrets:

```
POSTGRES_SERVER=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_DB=credit_intelligence
POSTGRES_USER=your-postgres-user
POSTGRES_PASSWORD=your-postgres-password
MONGODB_URL=mongodb+srv://priyaingle456:CLcRSTcllzOzrEpg@creditintelligence.hk0sndt.mongodb.net/
MONGODB_DB=credit_intelligence
LOG_LEVEL=INFO
SECRET_KEY=generate-a-strong-secret-key
```

## Troubleshooting

### Common Issues:

1. **Port Issues**: Replit automatically assigns ports, so the app will use the `PORT` environment variable
2. **Dependencies**: Make sure all packages in `requirements.txt` are compatible
3. **Database Connection**: Ensure your database URLs are correct and accessible from Replit
4. **CORS**: The app is configured to allow all origins (`["*"]`) for development
5. **MongoDB Connection**: Your Atlas connection should work from Replit

### Debug Mode:

To enable debug mode, set `DEBUG=true` in your environment variables.

## Monitoring

- Check the Replit console for logs
- Use the built-in monitoring tools in Replit
- Set up health checks at `/health` endpoint
- Monitor database connections in the logs

## Next Steps

1. Test your API endpoints
2. Set up your frontend to connect to the Replit backend
3. Configure your PostgreSQL database connection
4. Test the MongoDB connection
5. Set up CI/CD if needed

## Support

If you encounter issues:
1. Check the Replit console for error messages
2. Verify your environment variables
3. Test locally first to ensure the code works
4. Check the FastAPI documentation for API-specific issues
5. Verify database connectivity from Replit

Your backend should now be successfully deployed on Replit! 🚀 