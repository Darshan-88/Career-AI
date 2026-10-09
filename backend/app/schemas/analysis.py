from pydantic import BaseModel


class ResumeAnalysisRequest(BaseModel):
    resume_text: str
    target_role: str | None = None


class ResumeAnalysisResponse(BaseModel):
    score: int
    matched_skills: list[str]
    missing_skills: list[str]
    recommendations: list[str]
