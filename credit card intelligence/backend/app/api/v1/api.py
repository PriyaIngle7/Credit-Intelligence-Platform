from fastapi import APIRouter
from app.api.v1.endpoints import credit_scores, companies, data_ingestion, ml_models

api_router = APIRouter()

api_router.include_router(credit_scores.router, prefix="/credit-scores", tags=["credit-scores"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(data_ingestion.router, prefix="/data", tags=["data-ingestion"])
api_router.include_router(ml_models.router, prefix="/ml", tags=["ml-models"]) 