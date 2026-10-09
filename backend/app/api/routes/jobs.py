
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.api.deps import get_current_user, get_current_admin

from backend.app.models.user import User
from backend.app.models.analysis import ResumeAnalysis
from backend.app.models.resume import Resume

from backend.app.schemas.job import JobCreate, JobResponse

from backend.app.services.job_service import create_job, list_jobs

from backend.app.ai.job_matcher import get_top_matches
from backend.app.ai.job_analyzer import extract_skills


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# ============================================================
# JOB MATCH REQUEST
# ============================================================

class JobMatchRequest(BaseModel):
    resume_skills: list[str]
    limit: int = 10


# ============================================================
# 1. GET ALL JOBS
# Public endpoint: anyone can browse available jobs
# ============================================================

@router.get(
    "/",
    response_model=list[JobResponse]
)
def get_jobs(
    keyword: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Get all available jobs.

    An optional keyword can be used to search jobs.
    """
    return list_jobs(db, keyword)


# ============================================================
# 2. CREATE JOB — ADMIN ONLY
# Only authenticated administrators can publish jobs
# ============================================================

@router.post(
    "/",
    response_model=JobResponse,
    status_code=201
)
def add_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """
    Create a new job.
    Administrator access is required.
    """
    return create_job(
        db,
        **payload.model_dump()
    )


# ============================================================
# 3. MANUAL JOB MATCHING
# ============================================================

@router.post("/match")
def match_jobs(
    payload: JobMatchRequest,
    db: Session = Depends(get_db),
):
    """
    Match manually provided resume skills
    against all available jobs.
    """
    jobs = list_jobs(db)

    matches = get_top_matches(
        resume_skills=payload.resume_skills,
        jobs=jobs,
        limit=payload.limit
    )

    return {
        "resume_skills": payload.resume_skills,
        "total_jobs_checked": len(jobs),
        "matches": matches
    }


# ============================================================
# 4. AUTOMATIC JOB RECOMMENDATIONS
# ============================================================

@router.get("/recommendations")
def get_job_recommendations(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate personalized job recommendations using
    the logged-in user's latest resume analysis.
    """

    # STEP 1 — Validate limit
    if limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Limit must be at least 1."
        )

    limit = min(limit, 50)

    # STEP 2 — Find the user's latest resume analysis
    latest_analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.user_id == current_user.id
        )
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )

    if not latest_analysis:
        raise HTTPException(
            status_code=404,
            detail=(
                "No resume analysis found. "
                "Please upload and analyze a resume first."
            )
        )

    # STEP 3 — Find the resume linked to that analysis
    resume = None

    if latest_analysis.resume_id:
        resume = (
            db.query(Resume)
            .filter(
                Resume.id == latest_analysis.resume_id,
                Resume.user_id == current_user.id,
            )
            .first()
        )

    if not resume:
        raise HTTPException(
            status_code=404,
            detail=(
                "The resume linked to the latest "
                "analysis could not be found."
            )
        )

    # STEP 4 — Extract skills from the resume
    resume_skills = extract_skills(resume.content)

    if not resume_skills:
        try:
            saved_skills = json.loads(
                latest_analysis.matched_skills or "[]"
            )

            if isinstance(saved_skills, list):
                resume_skills = [
                    skill for skill in saved_skills
                    if isinstance(skill, str)
                ]
        except (json.JSONDecodeError, TypeError):
            resume_skills = []

    if not resume_skills:
        raise HTTPException(
            status_code=400,
            detail="No recognizable skills were found in your resume."
        )

    # STEP 5 — Get available jobs
    jobs = list_jobs(db)

    if not jobs:
        return {
            "message": "No jobs are currently available.",
            "user_id": current_user.id,
            "resume_id": resume.id,
            "analysis_id": latest_analysis.id,
            "resume_skills": resume_skills,
            "total_jobs_checked": 0,
            "recommendations": [],
        }

    # STEP 6 — Calculate job matches
    matches = get_top_matches(
        resume_skills=resume_skills,
        jobs=jobs,
        limit=limit,
    )

    # STEP 7 — Return recommendations
    return {
        "message": "Job recommendations generated successfully.",
        "user_id": current_user.id,
        "resume_id": resume.id,
        "analysis_id": latest_analysis.id,
        "target_role": latest_analysis.target_role,
        "resume_skills": resume_skills,
        "total_jobs_checked": len(jobs),
        "recommendations": matches,
    }
