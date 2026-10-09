from pydantic import BaseModel


class InterviewRequest(BaseModel):
    role: str
    skills: list[str] = []


class InterviewResponse(BaseModel):
    role: str
    questions: list[str]
