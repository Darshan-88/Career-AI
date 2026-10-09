from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db

from backend.app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse
)

from backend.app.services.auth_service import (
    register_user,
    login_user
)

from backend.app.core.security import (
    create_access_token
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db)
):

    try:

        user = register_user(
            db=db,
            name=payload.name,
            email=payload.email,
            password=payload.password
        )

        return user

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ============================================================
# LOGIN
# ============================================================

@router.post("/login")
def login(
    payload: UserLogin,
    db: Session = Depends(get_db)
):

    try:

        user = login_user(
            db=db,
            email=payload.email,
            password=payload.password
        )

    except ValueError as error:

        raise HTTPException(
            status_code=401,
            detail=str(error)
        )

    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email
        }
    )

    return {
        "message": "Login successful",
        "token": access_token,
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }