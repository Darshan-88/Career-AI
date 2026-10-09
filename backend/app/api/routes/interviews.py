import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from sqlalchemy.orm import Session

from backend.app.ai.interview_generator import generate_questions

from backend.app.api.deps import get_current_user

from backend.app.database.connection import get_db

from backend.app.models.user import User
from backend.app.models.analysis import ResumeAnalysis

from backend.app.schemas.interview import (
    InterviewRequest,
    InterviewResponse,
)


router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"]
)


# ============================================================
# 1. MANUAL INTERVIEW GENERATION
# ============================================================

@router.post(
    "/generate",
    response_model=InterviewResponse
)
def generate(
    payload: InterviewRequest
):
    """
    Generate interview questions manually.

    The user provides:

    - Target role
    - Skills

    Example:

    {
        "role": "Python Developer",
        "skills": [
            "Python",
            "FastAPI",
            "SQL"
        ]
    }
    """

    # Validate role
    if not payload.role.strip():
        raise HTTPException(
            status_code=400,
            detail="Role cannot be empty."
        )

    # Generate questions
    questions = generate_questions(
        payload.role,
        payload.skills
    )

    return InterviewResponse(
        role=payload.role,
        questions=questions,
    )


# ============================================================
# 2. PERSONALIZED INTERVIEW GENERATION
# ============================================================

@router.get(
    "/personalized",
    response_model=InterviewResponse
)
def personalized_interview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate personalized interview questions
    automatically from the user's latest resume analysis.

    Flow:

    Logged-in User
          ↓
    Latest Resume Analysis
          ↓
    Target Role
          ↓
    Matched Skills
          ↓
    Interview Question Generator
          ↓
    Personalized Questions
    """

    # --------------------------------------------------------
    # STEP 1 — Find latest resume analysis
    # --------------------------------------------------------

    latest_analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.user_id == current_user.id
        )
        .order_by(
            ResumeAnalysis.id.desc()
        )
        .first()
    )

    # --------------------------------------------------------
    # STEP 2 — Make sure analysis exists
    # --------------------------------------------------------

    if not latest_analysis:
        raise HTTPException(
            status_code=404,
            detail=(
                "No resume analysis found. "
                "Please upload and analyze your resume first."
            )
        )

    # --------------------------------------------------------
    # STEP 3 — Get target role
    # --------------------------------------------------------

    role = (
        latest_analysis.target_role
        or "software engineer"
    ).strip()

    # --------------------------------------------------------
    # STEP 4 — Load matched skills
    # --------------------------------------------------------

    try:
        skills = json.loads(
            latest_analysis.matched_skills or "[]"
        )
    except (
        json.JSONDecodeError,
        TypeError
    ):
        skills = []

    # --------------------------------------------------------
    # STEP 5 — If no matched skills, use empty list
    # --------------------------------------------------------

    if not isinstance(skills, list):
        skills = []

    # --------------------------------------------------------
    # STEP 6 — Generate interview questions
    # --------------------------------------------------------

    questions = generate_questions(
        role,
        skills
    )

    # --------------------------------------------------------
    # STEP 7 — Return personalized interview
    # --------------------------------------------------------

    return InterviewResponse(
        role=role,
        questions=questions,
    )