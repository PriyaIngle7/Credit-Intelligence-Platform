from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
from datetime import datetime

from app.core.database import get_db
from app.models.model_performance import ModelPerformance
from app.services.credit_scoring import CreditScoringService

router = APIRouter()


@router.post("/retrain")
async def retrain_model(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Trigger model retraining"""
    try:
        # Add to background tasks
        background_tasks.add_task(retrain_model_task, db)
        
        return {
            "message": "Model retraining started",
            "status": "started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance", response_model=List[Dict[str, Any]])
async def get_model_performance(
    limit: int = Query(10, le=100, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """Get model performance history"""
    try:
        performances = (
            db.query(ModelPerformance)
            .order_by(ModelPerformance.training_date.desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                "id": perf.id,
                "model_version": perf.model_version,
                "model_type": perf.model_type,
                "accuracy": perf.accuracy,
                "precision": perf.precision,
                "recall": perf.recall,
                "f1_score": perf.f1_score,
                "auc_roc": perf.auc_roc,
                "training_date": perf.training_date,
                "training_samples": perf.training_samples,
                "validation_samples": perf.validation_samples
            }
            for perf in performances
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/performance/latest")
async def get_latest_model_performance(db: Session = Depends(get_db)):
    """Get latest model performance metrics"""
    try:
        latest_performance = (
            db.query(ModelPerformance)
            .order_by(ModelPerformance.training_date.desc())
            .first()
        )
        
        if not latest_performance:
            raise HTTPException(status_code=404, detail="No model performance data found")
        
        return {
            "model_version": latest_performance.model_version,
            "model_type": latest_performance.model_type,
            "accuracy": latest_performance.accuracy,
            "precision": latest_performance.precision,
            "recall": latest_performance.recall,
            "f1_score": latest_performance.f1_score,
            "auc_roc": latest_performance.auc_roc,
            "training_date": latest_performance.training_date,
            "training_samples": latest_performance.training_samples,
            "validation_samples": latest_performance.validation_samples,
            "shap_consistency": latest_performance.shap_consistency,
            "feature_importance_stability": latest_performance.feature_importance_stability
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def get_model_info():
    """Get current model information"""
    try:
        scoring_service = CreditScoringService()
        
        return {
            "model_version": scoring_service.model_version,
            "feature_names": scoring_service.feature_names,
            "model_loaded": scoring_service.model is not None,
            "explainer_loaded": scoring_service.explainer is not None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate/{ticker}")
async def evaluate_model_on_company(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Evaluate model performance on a specific company"""
    try:
        from app.models.company import Company
        company = db.query(Company).filter(Company.ticker == ticker).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Get historical credit scores for evaluation
        from app.models.credit_score import CreditScore
        credit_scores = (
            db.query(CreditScore)
            .filter(CreditScore.company_id == company.id)
            .order_by(CreditScore.created_at.desc())
            .limit(10)
            .all()
        )
        
        if not credit_scores:
            raise HTTPException(status_code=404, detail="No credit scores found for company")
        
        # Calculate evaluation metrics
        scores = [score.score for score in credit_scores]
        avg_score = sum(scores) / len(scores)
        score_variance = sum((score - avg_score) ** 2 for score in scores) / len(scores)
        
        return {
            "ticker": ticker,
            "company_name": company.name,
            "evaluation_metrics": {
                "average_score": avg_score,
                "score_variance": score_variance,
                "score_count": len(scores),
                "latest_score": scores[0] if scores else None,
                "score_trend": "stable" if score_variance < 100 else "volatile"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def retrain_model_task(db: Session):
    """Background task for model retraining"""
    try:
        scoring_service = CreditScoringService()
        scoring_service._train_model()
        
        # Save performance metrics
        # In a real implementation, you would calculate actual performance metrics
        performance = ModelPerformance(
            model_version=scoring_service.model_version,
            model_type="RandomForest",
            accuracy=0.85,  # Placeholder
            precision=0.83,  # Placeholder
            recall=0.87,     # Placeholder
            f1_score=0.85,   # Placeholder
            auc_roc=0.89,    # Placeholder
            training_date=datetime.utcnow(),
            training_samples=1000,  # Placeholder
            validation_samples=200,  # Placeholder
            hyperparameters={"n_estimators": 100, "random_state": 42},
            feature_names=scoring_service.feature_names,
            shap_consistency=0.92,  # Placeholder
            feature_importance_stability=0.88  # Placeholder
        )
        
        db.add(performance)
        db.commit()
        
        print("Model retraining completed successfully")
        
    except Exception as e:
        print(f"Error in model retraining: {e}") 