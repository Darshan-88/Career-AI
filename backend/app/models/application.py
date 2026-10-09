from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from backend.app.database.base import Base

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    status = Column(String(50), default="applied")
    created_at = Column(DateTime, default=datetime.utcnow)
