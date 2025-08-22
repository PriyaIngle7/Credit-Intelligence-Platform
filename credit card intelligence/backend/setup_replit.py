#!/usr/bin/env python3
"""
Setup script for Replit deployment
This script helps configure the environment and test database connections
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        from app.core.config import settings
        from motor.motor_asyncio import AsyncIOMotorClient
        
        print("🔍 Testing MongoDB connection...")
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        from app.core.config import settings
        from sqlalchemy import create_engine
        
        print("🔍 Testing PostgreSQL connection...")
        engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ PostgreSQL connection successful!")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'POSTGRES_SERVER', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 
        'POSTGRES_DB', 'POSTGRES_PORT', 'MONGODB_URL', 'MONGODB_DB'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in Replit Secrets")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def install_dependencies():
    """Install required dependencies"""
    print("🔍 Installing dependencies...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

async def main():
    """Main setup function"""
    print("🚀 Credit Intelligence Platform - Replit Setup")
    print("=" * 50)
    
    # Check environment
    env_ok = check_environment()
    if not env_ok:
        print("\n📝 Please configure your environment variables in Replit Secrets first")
        return
    
    # Install dependencies
    deps_ok = install_dependencies()
    if not deps_ok:
        print("\n❌ Failed to install dependencies")
        return
    
    # Test database connections
    print("\n🔍 Testing database connections...")
    
    mongo_ok = await test_mongodb_connection()
    postgres_ok = test_postgres_connection()
    
    if mongo_ok and postgres_ok:
        print("\n🎉 Setup completed successfully!")
        print("You can now run your FastAPI application")
        print("\nTo start the app, run: python run.py")
    else:
        print("\n⚠️  Some database connections failed")
        print("Please check your database configuration")
        
        if not mongo_ok:
            print("- MongoDB: Check your MONGODB_URL and network access")
        if not postgres_ok:
            print("- PostgreSQL: Check your database credentials and network access")

if __name__ == "__main__":
    asyncio.run(main()) 