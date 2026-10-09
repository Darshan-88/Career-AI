import json
from collections import Counter

from sqlalchemy.orm import Session

from backend.app.models.application import Application
from backend.app.models.job import Job
from backend.app.models.resume import Resume
from backend.app.models.analysis import ResumeAnalysis


def _load_json_list(value):
    """
    Convert JSON text stored in the database
    back into a Python list.
    """

    if not value:
        return []

    try:
        result = json.loads(value)

        if isinstance(result, list):
            return result

        return []

    except (json.JSONDecodeError, TypeError):
        return []


def get_dashboard(db: Session, user_id: int) -> dict:
    """
    Generate dashboard statistics for a user.
    """

    # ========================================================
    # BASIC COUNTS
    # ========================================================

    resume_count = (
        db.query(Resume)
        .filter(
            Resume.user_id == user_id
        )
        .count()
    )

    application_count = (
        db.query(Application)
        .filter(
            Application.user_id == user_id
        )
        .count()
    )

    available_jobs = (
        db.query(Job)
        .count()
    )

    # ========================================================
    # APPLICATION STATUS COUNTS
    # ========================================================

    applications = (
        db.query(Application)
        .filter(
            Application.user_id == user_id
        )
        .all()
    )

    application_status_counts = {
        "applied": 0,
        "shortlisted": 0,
        "interview": 0,
        "selected": 0,
        "rejected": 0,
    }

    for application in applications:

        status = (
            application.status
            or "applied"
        ).lower().strip()

        if status in application_status_counts:
            application_status_counts[status] += 1

    # ========================================================
    # USER'S ANALYSES
    # ========================================================

    analyses = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.user_id == user_id
        )
        .order_by(
            ResumeAnalysis.id.desc()
        )
        .all()
    )

    analysis_count = len(analyses)

    # ========================================================
    # DEFAULT DASHBOARD VALUES
    # ========================================================

    latest_score = None
    average_score = 0
    latest_target_role = None

    total_matched_skills = 0
    total_missing_skills = 0

    most_common_missing_skills = []

    # ========================================================
    # ANALYSIS CALCULATIONS
    # ========================================================

    if analyses:

        # Latest analysis
        latest_analysis = analyses[0]

        latest_score = latest_analysis.score

        latest_target_role = (
            latest_analysis.target_role
        )

        # Average score
        scores = [
            analysis.score
            for analysis in analyses
            if analysis.score is not None
        ]

        if scores:
            average_score = round(
                sum(scores) / len(scores)
            )

        # Skill counters
        missing_skill_counter = Counter()

        for analysis in analyses:

            matched_skills = _load_json_list(
                analysis.matched_skills
            )

            missing_skills = _load_json_list(
                analysis.missing_skills
            )

            total_matched_skills += len(
                matched_skills
            )

            total_missing_skills += len(
                missing_skills
            )

            missing_skill_counter.update(
                skill.lower().strip()
                for skill in missing_skills
                if skill
            )

        # Top missing skills
        most_common_missing_skills = [
            {
                "skill": skill,
                "count": count
            }
            for skill, count
            in missing_skill_counter.most_common(5)
        ]

    # ========================================================
    # RETURN DASHBOARD DATA
    # ========================================================

    return {
        # Basic statistics
        "resume_count": resume_count,

        "application_count": application_count,

        "available_jobs": available_jobs,

        # Application tracking
        "application_status": {
            "applied": application_status_counts["applied"],
            "shortlisted": application_status_counts["shortlisted"],
            "interview": application_status_counts["interview"],
            "selected": application_status_counts["selected"],
            "rejected": application_status_counts["rejected"],
        },

        # Resume analysis
        "analysis_count": analysis_count,

        "latest_score": latest_score,

        "average_score": average_score,

        "latest_target_role": latest_target_role,

        "total_matched_skills": total_matched_skills,

        "total_missing_skills": total_missing_skills,

        "most_common_missing_skills": (
            most_common_missing_skills
        ),
    }