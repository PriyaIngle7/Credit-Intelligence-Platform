from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Credit Intelligence Platform"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "123")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "credit_intelligence")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # MongoDB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb+srv://priyaingle456:CLcRSTcllzOzrEpg@creditintelligence.hk0sndt.mongodb.net/")
    MONGODB_DB: str = os.getenv("MONGODB_DB", "credit_intelligence")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # External APIs
    YAHOO_FINANCE_API_KEY: Optional[str] = os.getenv("YAHOO_FINANCE_API_KEY")
    NEWS_API_KEY: Optional[str] = os.getenv("NEWS_API_KEY")
    WORLD_BANK_API_KEY: Optional[str] = os.getenv("WORLD_BANK_API_KEY")
    
    # ML Model
    MODEL_PATH: str = os.getenv("MODEL_PATH", "ml/models/credit_model.pkl")
    SHAP_MODEL_PATH: str = os.getenv("SHAP_MODEL_PATH", "ml/models/shap_explainer.pkl")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Data Refresh
    DATA_REFRESH_INTERVAL: int = 300  # 5 minutes
    MODEL_RETRAIN_INTERVAL: int = 86400  # 24 hours
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def MONGODB_DATABASE_URI(self) -> str:
        return f"{self.MONGODB_URL}/{self.MONGODB_DB}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 