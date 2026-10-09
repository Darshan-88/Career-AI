from fastapi import APIRouter

from backend.app.api.routes import (
    auth,
    users,
    resumes,
    jobs,
    applications,
    analysis,
    interviews,
    dashboard,
    career,
)

api_router = APIRouter(prefix="/api")

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(resumes.router)
api_router.include_router(jobs.router)
api_router.include_router(applications.router)
api_router.include_router(analysis.router)
api_router.include_router(interviews.router)
api_router.include_router(dashboard.router)
api_router.include_router(career.router)