from sqlalchemy.orm import Session

from backend.app.models.resume import Resume


def create_resume(
    db: Session,
    user_id: int,
    filename: str | None,
    content: str
) -> Resume:

    resume = Resume(
        user_id=user_id,
        filename=filename,
        content=content
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume


def get_user_resumes(
    db: Session,
    user_id: int
) -> list[Resume]:

    return (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.id.desc())
        .all()
    )