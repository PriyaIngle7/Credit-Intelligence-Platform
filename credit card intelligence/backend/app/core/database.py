from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# PostgreSQL
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# MongoDB
mongodb_client: AsyncIOMotorClient = None
mongodb_sync_client: MongoClient = None


async def init_db():
    """Initialize database connections"""
    global mongodb_client, mongodb_sync_client
    
    try:
        # MongoDB connection options for better SSL handling
        mongo_options = {
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 10000,
            "socketTimeoutMS": 10000,
            "maxPoolSize": 10,
            "retryWrites": True,
            "retryReads": True,
            "ssl": True,
            "ssl_cert_reqs": "CERT_NONE"  # For development - use proper certs in production
        }
        
        # Initialize MongoDB async client
        mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL, **mongo_options)
        await mongodb_client.admin.command('ping')
        logger.info("MongoDB async connection established")
        
        # Initialize MongoDB sync client
        mongodb_sync_client = MongoClient(settings.MONGODB_URL, **mongo_options)
        mongodb_sync_client.admin.command('ping')
        logger.info("MongoDB sync connection established")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Don't raise the exception - allow the app to start without MongoDB
        logger.warning("Continuing without MongoDB connection")
        mongodb_client = None
        mongodb_sync_client = None


def get_db():
    """Get PostgreSQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongodb():
    """Get MongoDB database"""
    if mongodb_client is None:
        raise Exception("MongoDB connection not available")
    return mongodb_client[settings.MONGODB_DB]


def get_mongodb_sync():
    """Get MongoDB sync database"""
    if mongodb_sync_client is None:
        raise Exception("MongoDB connection not available")
    return mongodb_sync_client[settings.MONGODB_DB]


async def close_db():
    """Close database connections"""
    global mongodb_client, mongodb_sync_client
    
    if mongodb_client:
        mongodb_client.close()
        logger.info("MongoDB async connection closed")
    
    if mongodb_sync_client:
        mongodb_sync_client.close()
        logger.info("MongoDB sync connection closed") 