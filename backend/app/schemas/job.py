from pydantic import BaseModel


class JobCreate(BaseModel):
    title: str
    company: str
    location: str | None = None
    description: str
    skills: str
    salary: str | None = None


class JobResponse(JobCreate):
    id: int

    class Config:
        from_attributes = True
