from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.resume import ResumeCreate, ResumeResponse
from backend.app.services.resume_service import (
    create_resume,
    get_user_resumes
)

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)


@router.post(
    "/",
    response_model=ResumeResponse,
    status_code=201
)
def add_resume(
    payload: ResumeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return create_resume(
        db=db,
        user_id=current_user.id,
        filename=payload.filename,
        content=payload.content
    )


@router.get(
    "/",
    response_model=list[ResumeResponse]
)
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_resumes(
        db=db,
        user_id=current_user.id
    )