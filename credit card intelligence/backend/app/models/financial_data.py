from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class FinancialData(Base):
    __tablename__ = "financial_data"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    
    # Financial metrics
    total_assets = Column(Float)
    total_liabilities = Column(Float)
    total_equity = Column(Float)
    current_assets = Column(Float)
    current_liabilities = Column(Float)
    long_term_debt = Column(Float)
    short_term_debt = Column(Float)
    cash_and_equivalents = Column(Float)
    net_income = Column(Float)
    ebitda = Column(Float)
    operating_cash_flow = Column(Float)
    free_cash_flow = Column(Float)
    
    # Ratios
    debt_to_equity_ratio = Column(Float)
    current_ratio = Column(Float)
    quick_ratio = Column(Float)
    cash_ratio = Column(Float)
    debt_to_ebitda = Column(Float)
    interest_coverage = Column(Float)
    roe = Column(Float)
    roa = Column(Float)
    roic = Column(Float)
    
    # Market data
    stock_price = Column(Float)
    market_cap = Column(Float)
    enterprise_value = Column(Float)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    ev_to_ebitda = Column(Float)
    
    # Metadata
    data_date = Column(DateTime, nullable=False)
    source = Column(String(100))  # 'yahoo_finance', 'sec', 'world_bank'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="financial_data")
    
    def __repr__(self):
        return f"<FinancialData(id={self.id}, company_id={self.company_id}, date={self.data_date})>" 