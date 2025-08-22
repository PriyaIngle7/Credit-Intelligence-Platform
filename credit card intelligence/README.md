# 🏆 Real-Time Explainable Credit Intelligence Platform

A comprehensive web-based credit intelligence system that continuously gathers structured and unstructured data, generates real-time creditworthiness scores, provides explanations, and displays everything in an interactive dashboard.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Data Sources  │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (APIs)        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Tailwind CSS  │    │   ML Pipeline   │    │   PostgreSQL    │
│   + Charts      │    │   + SHAP        │    │   (Structured)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   MongoDB       │    │   Deployment    │
                       │   (Unstructured)│    │   (Render/Vercel) 
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Features

### 1. Data Ingestion & Processing
- **Structured Sources**: Yahoo Finance API, World Bank API, SEC filings
- **Unstructured Sources**: Financial news headlines, social media sentiment
- Real-time data pipeline with automated updates
- Data cleaning and normalization

### 2. Scoring Engine
- Interpretable ML models (Logistic Regression, Decision Trees)
- Incremental retraining support
- Issuer-level and asset-class level scoring
- Real-time score updates

### 3. Explainability Layer
- SHAP integration for feature contributions
- Short-term vs long-term trend indicators
- Plain-language explanations and event reasoning

### 4. Interactive Dashboard
- Score trends visualization
- Feature importance & explanations
- Event highlights and alerts
- Company/sector filtering
- Model performance view

## 🛠️ Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: React + Tailwind CSS + Recharts
- **Database**: PostgreSQL (structured) + MongoDB (unstructured)
- **ML**: Scikit-learn + SHAP
- **Deployment**: Render (backend) + Vercel (frontend)
- **APIs**: Yahoo Finance, World Bank, News APIs

## 📦 Project Structure

```
credit-card-intelligence/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── services/
│   │   └── utils/
│   ├── data/
│   ├── ml/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── utils/
│   ├── public/
│   └── package.json
├── vercel.json
└── README.md
```

## 🚀 Quick Start (Local Dev, no Docker)

### Prerequisites
- Python 3.9+
- Node.js 16+
- Local PostgreSQL and MongoDB (or remote URIs)

### Backend (Windows PowerShell)
```powershell
cd "backend"
python -m venv venv
./venv/Scripts/Activate.ps1
pip install -r requirements.txt
# Environment (edit to your values)
$env:POSTGRES_SERVER="localhost"
$env:POSTGRES_USER="postgres"
$env:POSTGRES_PASSWORD="password"
$env:POSTGRES_DB="credit_intelligence"
$env:POSTGRES_PORT="5432"
$env:MONGODB_URL="mongodb://localhost:27017"
$env:MONGODB_DB="credit_intelligence"
$env:LOG_LEVEL="INFO"
uvicorn app.main:app --reload
```

### Frontend (Windows PowerShell)
```powershell
cd "frontend"
npm install
npm start
```
- UI: http://localhost:3000
- API docs: http://localhost:8000/docs

## 🌐 Deployment (Render + Vercel)

### Backend on Render
- Create a new Web Service from this repo
- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Environment variables:
  - `POSTGRES_SERVER`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_PORT`
  - `MONGODB_URL`, `MONGODB_DB` (use MongoDB Atlas free tier)
  - `NEWS_API_KEY` (optional)
  - `LOG_LEVEL=INFO`
- CORS: In `backend/app/core/config.py`, ensure `ALLOWED_HOSTS` includes your Vercel domain, e.g., `https://your-app.vercel.app`

### Frontend on Vercel
- This repo includes `vercel.json`:
```
{
  "rewrites": [
    { "source": "/api/(.*)", "destination": "https://RENDER_BACKEND_URL/api/$1" }
  ]
}
```
- Replace `RENDER_BACKEND_URL` with your actual Render backend base domain (no trailing slash), e.g., `your-service.onrender.com`
- Framework preset: Create React App
- Build command: `npm run build`
- Output directory: `build`

Alternative (without rewrites): set `REACT_APP_API_BASE` env in Vercel and point Axios to it.

## 🔧 Useful Endpoints
- Health: `GET /health`
- Dashboard summary: `GET /api/v1/credit-scores/dashboard/summary`
- Latest score: `GET /api/v1/credit-scores/company/{ticker}/latest`
- Ingestion: `POST /api/v1/data/ingest/{ticker}`
- Retrain model: `POST /api/v1/ml/retrain`
- Latest model performance: `GET /api/v1/ml/performance/latest`

## 📊 Explainability Strategy
- SHAP for feature contribution breakdowns per score
- Plain-language explanations summarizing key factors
- Trend indicators via score history endpoints

## 🎯 Use Cases
- Debt restructuring headline → score decrease with explanation
- Commodity price shock → risk adjustment for exposed firms
- Negative sentiment → risk signal in dashboard

## 🔄 Data Pipeline
1. Collection: Yahoo Finance, News API, World Bank
2. Processing: cleaning, normalization, feature engineering
3. Scoring: interpretable model with SHAP
4. Explainability: per-issuer explanations + key factors
5. Dashboard: real-time widgets and charts

## 📈 Ops Notes
- Tables auto-create on backend startup (SQLAlchemy)
- Outbound internet required for APIs (Render supports)
- For sentiment, TextBlob is used; can be swapped for VADER if desired

## 🆘 Support
Open an issue or contact the maintainers.

---

Built with ❤️ for the Hackathon

