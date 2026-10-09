from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.app.models.job import Job


def list_jobs(db: Session, keyword: str | None = None) -> list[Job]:
    query = db.query(Job)

    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Job.title.ilike(pattern),
                Job.company.ilike(pattern),
                Job.skills.ilike(pattern),
                Job.description.ilike(pattern),
            )
        )

    return query.order_by(Job.id.desc()).all()


def create_job(db: Session, **data) -> Job:
    job = Job(**data)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job
