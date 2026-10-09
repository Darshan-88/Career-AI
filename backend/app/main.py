from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import APP_NAME, APP_VERSION
from backend.app.database.base import Base
from backend.app.database.connection import SessionLocal, engine
from backend.app.api.router import api_router
from backend.app.data_pipeline.job_seed import seed_jobs

# Import models so SQLAlchemy registers all tables
from backend.app.models.user import User
from backend.app.models.resume import Resume
from backend.app.models.analysis import ResumeAnalysis


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title=APP_NAME,
    description=(
        "AI-powered platform for resume analysis, "
        "job matching, skill gap analysis and career guidance."
    ),
    version=APP_VERSION,
)


# ============================================================
# CORS CONFIGURATION
# Allows the frontend running on port 3000
# to communicate with FastAPI running on port 8000.
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routes
app.include_router(api_router)


@app.on_event("startup")
def startup():
    db = SessionLocal()

    try:
        seed_jobs(db)
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": f"{APP_NAME} is running",
        "status": "success",
        "version": APP_VERSION,
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }