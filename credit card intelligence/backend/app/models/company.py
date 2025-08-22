from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    ticker = Column(String(20), unique=True, index=True)
    sector = Column(String(100))
    industry = Column(String(100))
    country = Column(String(100))
    
    # Financial metrics
    market_cap = Column(Float)
    revenue = Column(Float)
    debt_to_equity = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    roe = Column(Float)  # Return on Equity
    roa = Column(Float)  # Return on Assets
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    credit_scores = relationship("CreditScore", back_populates="company")
    financial_data = relationship("FinancialData", back_populates="company")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', ticker='{self.ticker}')>" 