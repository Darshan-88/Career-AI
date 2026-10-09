import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.ai.career_advisor import career_advice
from backend.app.api.deps import get_current_user
from backend.app.database.connection import get_db
from backend.app.models.user import User
from backend.app.models.analysis import ResumeAnalysis


router = APIRouter(
    prefix="/career",
    tags=["Career Advisor"]
)


# ============================================================
# PERSONALIZED CAREER ADVICE
# ============================================================

@router.get("/advice")
def get_career_advice(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate personalized career advice
    using the user's latest resume analysis.
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
    # STEP 2 — Check whether analysis exists
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

    target_role = (
        latest_analysis.target_role
        or "software engineer"
    ).strip()

    # --------------------------------------------------------
    # STEP 4 — Load matched skills
    # --------------------------------------------------------

    try:
        matched_skills = json.loads(
            latest_analysis.matched_skills or "[]"
        )
    except (
        json.JSONDecodeError,
        TypeError
    ):
        matched_skills = []

    if not isinstance(matched_skills, list):
        matched_skills = []

    # --------------------------------------------------------
    # STEP 5 — Load missing skills
    # --------------------------------------------------------

    try:
        missing_skills = json.loads(
            latest_analysis.missing_skills or "[]"
        )
    except (
        json.JSONDecodeError,
        TypeError
    ):
        missing_skills = []

    if not isinstance(missing_skills, list):
        missing_skills = []

    # --------------------------------------------------------
    # STEP 6 — Generate career advice
    # --------------------------------------------------------

    advice = career_advice(
        matched_skills,
        target_role
    )

    # --------------------------------------------------------
    # STEP 7 — Return career intelligence
    # --------------------------------------------------------

    return {
        "message": (
            "Career advice generated successfully."
        ),

        "user_id": current_user.id,

        "analysis_id": latest_analysis.id,

        "target_role": target_role,

        "score": latest_analysis.score,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "career_advice": advice,
    }