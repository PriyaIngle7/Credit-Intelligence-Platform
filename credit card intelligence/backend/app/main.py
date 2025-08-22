from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import init_db, engine
from app.models import *  # noqa
from app.core.database import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Create tables (only if PostgreSQL is available)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create PostgreSQL tables: {e}")
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Credit Intelligence Platform",
    description="Real-Time Explainable Credit Intelligence Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Credit Intelligence Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "credit-intelligence-api"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 