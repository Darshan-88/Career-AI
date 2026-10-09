from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from backend.app.database.base import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    resume_id = Column(
        Integer,
        ForeignKey("resumes.id"),
        nullable=True,
        index=True
    )

    target_role = Column(
        Text,
        nullable=False
    )

    score = Column(
        Integer,
        nullable=False
    )

    matched_skills = Column(
        Text,
        nullable=True
    )

    missing_skills = Column(
        Text,
        nullable=True
    )

    recommendations = Column(
        Text,
        nullable=True
    )

    user = relationship(
        "User",
        backref="resume_analyses"
    )

    resume = relationship(
        "Resume",
        backref="analyses"
    )