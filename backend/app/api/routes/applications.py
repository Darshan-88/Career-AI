from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.database.connection import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User

from backend.app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
)

from backend.app.services.application_service import (
    apply_to_job,
    get_applications,
    update_application_status,
)


router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)


# ============================================================
# APPLICATION STATUS REQUEST
# ============================================================

class ApplicationStatusUpdate(BaseModel):
    status: str


# ============================================================
# APPLY TO JOB
# ============================================================

@router.post(
    "/",
    response_model=ApplicationResponse,
    status_code=201
)
def apply(
    payload: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return apply_to_job(
        db,
        current_user.id,
        payload.job_id
    )


# ============================================================
# GET USER APPLICATIONS
# ============================================================

@router.get(
    "/",
    response_model=list[ApplicationResponse]
)
def applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_applications(
        db,
        current_user.id
    )


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

@router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse
)
def update_status(
    application_id: int,
    payload: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        application = update_application_status(
            db=db,
            user_id=current_user.id,
            application_id=application_id,
            new_status=payload.status,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    if not application:
        raise HTTPException(
            status_code=404,
            detail="Application not found."
        )

    return application