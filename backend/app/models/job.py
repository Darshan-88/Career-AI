from sqlalchemy import Column, Integer, String, Text

from backend.app.database.base import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False)
    location = Column(String(200), nullable=True)
    description = Column(Text, nullable=False)
    skills = Column(Text, nullable=False, default="")
    salary = Column(String(100), nullable=True)
