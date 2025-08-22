from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class ModelPerformance(Base):
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model information
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50))  # 'logistic_regression', 'decision_tree', etc.
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    auc_roc = Column(Float)
    
    # Explainability metrics
    shap_consistency = Column(Float)  # Consistency of SHAP explanations
    feature_importance_stability = Column(Float)  # Stability of feature importance
    
    # Training information
    training_date = Column(DateTime, nullable=False)
    training_samples = Column(Integer)
    validation_samples = Column(Integer)
    
    # Model parameters
    hyperparameters = Column(JSON)
    feature_names = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    
    def __repr__(self):
        return f"<ModelPerformance(id={self.id}, version='{self.model_version}', accuracy={self.accuracy})>" 