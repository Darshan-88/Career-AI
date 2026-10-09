from sqlalchemy.orm import Session

from backend.app.models.job import Job


SAMPLE_JOBS = [
    {
        "title": "Python Backend Developer",
        "company": "Tech Solutions",
        "location": "Bengaluru",
        "description": "Build REST APIs and backend services using Python.",
        "skills": "python, fastapi, sql, git, rest api",
        "salary": "4-8 LPA",
    },
    {
        "title": "Data Analyst",
        "company": "Analytics Labs",
        "location": "Bengaluru",
        "description": "Analyze business data and create dashboards.",
        "skills": "python, sql, pandas, power bi, excel",
        "salary": "4-7 LPA",
    },
]


def seed_jobs(db: Session):
    if db.query(Job).count() > 0:
        return

    for item in SAMPLE_JOBS:
        db.add(Job(**item))

    db.commit()
