from pydantic import BaseModel, ConfigDict


class ResumeCreate(BaseModel):
    filename: str | None = None
    content: str


class ResumeResponse(BaseModel):
    id: int
    filename: str | None
    content: str

    model_config = ConfigDict(
        from_attributes=True
    )