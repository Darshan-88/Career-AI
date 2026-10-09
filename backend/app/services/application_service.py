from sqlalchemy.orm import Session

from backend.app.models.application import Application


# ============================================================
# ALLOWED APPLICATION STATUSES
# ============================================================

ALLOWED_STATUSES = {
    "applied",
    "shortlisted",
    "interview",
    "selected",
    "rejected",
}


# ============================================================
# APPLY TO JOB
# ============================================================

def apply_to_job(
    db: Session,
    user_id: int,
    job_id: int
) -> Application:

    existing = (
        db.query(Application)
        .filter(
            Application.user_id == user_id,
            Application.job_id == job_id,
        )
        .first()
    )

    # Prevent duplicate applications
    if existing:
        return existing

    application = Application(
        user_id=user_id,
        job_id=job_id,
        status="applied",
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


# ============================================================
# GET USER APPLICATIONS
# ============================================================

def get_applications(
    db: Session,
    user_id: int
) -> list[Application]:

    return (
        db.query(Application)
        .filter(
            Application.user_id == user_id
        )
        .order_by(
            Application.id.desc()
        )
        .all()
    )


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

def update_application_status(
    db: Session,
    user_id: int,
    application_id: int,
    new_status: str,
) -> Application | None:

    # Normalize status
    new_status = (
        new_status
        .lower()
        .strip()
    )

    # Validate status
    if new_status not in ALLOWED_STATUSES:
        raise ValueError(
            "Invalid application status. "
            "Allowed statuses: "
            "applied, shortlisted, interview, "
            "selected, rejected."
        )

    # Find application belonging to this user
    application = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == user_id,
        )
        .first()
    )

    if not application:
        return None

    # Update status
    application.status = new_status

    db.commit()
    db.refresh(application)

    return application