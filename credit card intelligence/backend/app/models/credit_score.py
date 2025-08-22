from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CreditScore(Base):
    __tablename__ = "credit_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    score = Column(Float, nullable=False)
    score_type = Column(String(50), nullable=False)  # 'issuer', 'asset_class'
    confidence = Column(Float, default=0.0)
    risk_level = Column(String(20), nullable=False)  # 'low', 'medium', 'high'
    
    # Explainability features
    feature_contributions = Column(JSON)  # SHAP values
    explanation = Column(Text)  # Plain language explanation
    key_factors = Column(JSON)  # Top contributing factors
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    model_version = Column(String(50))
    
    # Relationships
    company = relationship("Company", back_populates="credit_scores")
    
    def __repr__(self):
        return f"<CreditScore(id={self.id}, company_id={self.company_id}, score={self.score})>" 