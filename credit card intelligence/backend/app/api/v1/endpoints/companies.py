from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.company import Company
from app.schemas.company import CompanyResponse, CompanyCreate

router = APIRouter()


@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    sector: Optional[str] = Query(None, description="Filter by sector"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    country: Optional[str] = Query(None, description="Filter by country"),
    limit: int = Query(100, le=1000, description="Number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """Get companies with optional filtering"""
    query = db.query(Company)
    
    if sector:
        query = query.filter(Company.sector == sector)
    if industry:
        query = query.filter(Company.industry == industry)
    if country:
        query = query.filter(Company.country == country)
    
    companies = query.offset(offset).limit(limit).all()
    return companies


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific company by ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.get("/ticker/{ticker}", response_model=CompanyResponse)
async def get_company_by_ticker(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get a company by ticker symbol"""
    company = db.query(Company).filter(Company.ticker == ticker).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("/", response_model=CompanyResponse)
async def create_company(
    company: CompanyCreate,
    db: Session = Depends(get_db)
):
    """Create a new company"""
    # Check if company with same ticker already exists
    existing_company = db.query(Company).filter(Company.ticker == company.ticker).first()
    if existing_company:
        raise HTTPException(status_code=400, detail="Company with this ticker already exists")
    
    db_company = Company(**company.dict())
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


@router.get("/sectors/list")
async def get_sectors(db: Session = Depends(get_db)):
    """Get list of all sectors"""
    sectors = db.query(Company.sector).distinct().filter(Company.sector.isnot(None)).all()
    return [sector[0] for sector in sectors]


@router.get("/industries/list")
async def get_industries(db: Session = Depends(get_db)):
    """Get list of all industries"""
    industries = db.query(Company.industry).distinct().filter(Company.industry.isnot(None)).all()
    return [industry[0] for industry in industries] 