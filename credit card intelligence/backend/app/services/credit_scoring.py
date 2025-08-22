import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import shap
import pickle
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from app.core.config import settings
from app.models.company import Company
from app.models.financial_data import FinancialData
from app.services.data_ingestion import DataIngestionService
from app.services.sentiment_analysis import SentimentAnalysisService

logger = logging.getLogger(__name__)


class CreditScoringService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.explainer = None
        self.feature_names = []
        self.model_version = "v1.0.0"
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and explainer"""
        try:
            model_path = settings.MODEL_PATH
            shap_path = settings.SHAP_MODEL_PATH
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                    self.feature_names = model_data['feature_names']
                
                if os.path.exists(shap_path):
                    with open(shap_path, 'rb') as f:
                        self.explainer = pickle.load(f)
                
                logger.info(f"Model loaded successfully: {model_path}")
            else:
                logger.warning("No trained model found. Training new model...")
                self._train_model()
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self._train_model()
    
    def _train_model(self):
        """Train a new credit scoring model"""
        try:
            # For demo purposes, we'll create a simple model
            # In production, this would use real historical data
            
            # Create synthetic training data
            np.random.seed(42)
            n_samples = 1000
            
            # Generate synthetic features
            debt_to_equity = np.random.normal(0.5, 0.3, n_samples)
            current_ratio = np.random.normal(1.5, 0.5, n_samples)
            roe = np.random.normal(0.15, 0.1, n_samples)
            market_cap = np.random.lognormal(10, 1, n_samples)
            sentiment_score = np.random.normal(0, 0.5, n_samples)
            
            # Create target variable (credit risk: 0=low, 1=medium, 2=high)
            risk_scores = (
                -0.3 * debt_to_equity +
                0.2 * current_ratio +
                -0.4 * roe +
                -0.1 * np.log(market_cap) +
                0.3 * sentiment_score +
                np.random.normal(0, 0.1, n_samples)
            )
            
            # Convert to risk levels
            risk_levels = np.where(risk_scores < -0.5, 0, np.where(risk_scores < 0.5, 1, 2))
            
            # Create feature matrix
            X = np.column_stack([debt_to_equity, current_ratio, roe, np.log(market_cap), sentiment_score])
            self.feature_names = ['debt_to_equity', 'current_ratio', 'roe', 'log_market_cap', 'sentiment_score']
            
            # Scale features
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model = RandomForestClassifier(n_estimators=100, random_state=42)
            self.model.fit(X_scaled, risk_levels)
            
            # Create SHAP explainer
            self.explainer = shap.TreeExplainer(self.model)
            
            # Save model
            self._save_model()
            
            logger.info("Model trained and saved successfully")
            
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise
    
    def _save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_names': self.feature_names,
                'version': self.model_version,
                'trained_at': datetime.utcnow()
            }
            
            with open(settings.MODEL_PATH, 'wb') as f:
                pickle.dump(model_data, f)
            
            with open(settings.SHAP_MODEL_PATH, 'wb') as f:
                pickle.dump(self.explainer, f)
                
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    async def calculate_score(self, company: Company, score_type: str, db) -> Dict[str, Any]:
        """Calculate credit score for a company"""
        try:
            # Get latest financial data
            financial_data = (
                db.query(FinancialData)
                .filter(FinancialData.company_id == company.id)
                .order_by(FinancialData.data_date.desc())
                .first()
            )
            
            if not financial_data:
                # Use company-level data if no financial data available
                features = self._extract_features_from_company(company)
            else:
                features = self._extract_features_from_financial_data(financial_data, company)
            
            # Get sentiment data
            sentiment_service = SentimentAnalysisService()
            sentiment_score = await sentiment_service.get_company_sentiment(company.ticker)
            features.append(sentiment_score)
            
            # Prepare features for prediction
            X = np.array(features).reshape(1, -1)
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            risk_probabilities = self.model.predict_proba(X_scaled)[0]
            risk_level = self.model.predict(X_scaled)[0]
            
            # Calculate score (0-100 scale)
            score = self._calculate_numeric_score(risk_probabilities, risk_level)
            
            # Generate SHAP explanations
            shap_values = self.explainer.shap_values(X_scaled)
            feature_contributions = self._generate_feature_contributions(shap_values[0], X_scaled[0])
            
            # Generate explanation
            explanation = self._generate_explanation(feature_contributions, risk_level)
            
            # Get key factors
            key_factors = self._get_key_factors(feature_contributions)
            
            return {
                "score": score,
                "confidence": self._calculate_confidence(risk_probabilities),
                "risk_level": self._get_risk_level_name(risk_level),
                "feature_contributions": feature_contributions,
                "explanation": explanation,
                "key_factors": key_factors,
                "model_version": self.model_version
            }
            
        except Exception as e:
            logger.error(f"Error calculating credit score: {e}")
            raise
    
    def _extract_features_from_company(self, company: Company) -> List[float]:
        """Extract features from company data"""
        return [
            company.debt_to_equity or 0.5,
            company.current_ratio or 1.5,
            company.roe or 0.15,
            np.log(company.market_cap or 1000000000)
        ]
    
    def _extract_features_from_financial_data(self, financial_data: FinancialData, company: Company) -> List[float]:
        """Extract features from financial data"""
        return [
            financial_data.debt_to_equity_ratio or 0.5,
            financial_data.current_ratio or 1.5,
            financial_data.roe or 0.15,
            np.log(financial_data.market_cap or 1000000000)
        ]
    
    def _calculate_numeric_score(self, probabilities: np.ndarray, risk_level: int) -> float:
        """Convert risk probabilities to numeric score (0-100)"""
        # Higher score = lower risk
        if risk_level == 0:  # Low risk
            return 85 + np.random.normal(0, 5)
        elif risk_level == 1:  # Medium risk
            return 60 + np.random.normal(0, 10)
        else:  # High risk
            return 30 + np.random.normal(0, 10)
    
    def _calculate_confidence(self, probabilities: np.ndarray) -> float:
        """Calculate confidence based on prediction probabilities"""
        return float(np.max(probabilities))
    
    def _get_risk_level_name(self, risk_level: int) -> str:
        """Convert numeric risk level to string"""
        risk_levels = {0: "low", 1: "medium", 2: "high"}
        return risk_levels.get(risk_level, "medium")
    
    def _generate_feature_contributions(self, shap_values: np.ndarray, features: np.ndarray) -> Dict[str, float]:
        """Generate feature contribution dictionary"""
        contributions = {}
        for i, feature_name in enumerate(self.feature_names):
            contributions[feature_name] = float(shap_values[i])
        return contributions
    
    def _generate_explanation(self, feature_contributions: Dict[str, float], risk_level: int) -> str:
        """Generate plain language explanation"""
        risk_level_name = self._get_risk_level_name(risk_level)
        
        # Get top contributing factors
        sorted_contributions = sorted(feature_contributions.items(), key=lambda x: abs(x[1]), reverse=True)
        top_factor = sorted_contributions[0]
        
        explanations = {
            "low": f"The company shows a low credit risk profile. The most significant factor is {top_factor[0]}.",
            "medium": f"The company shows a moderate credit risk profile. The most significant factor is {top_factor[0]}.",
            "high": f"The company shows a high credit risk profile. The most significant factor is {top_factor[0]}."
        }
        
        return explanations.get(risk_level_name, "Credit risk assessment completed.")
    
    def _get_key_factors(self, feature_contributions: Dict[str, float]) -> List[str]:
        """Get key factors affecting the score"""
        sorted_contributions = sorted(feature_contributions.items(), key=lambda x: abs(x[1]), reverse=True)
        return [factor for factor, _ in sorted_contributions[:3]] 