from fastapi import APIRouter, Depends

from backend.app.models.user import User
from backend.app.schemas.user import UserResponse
from backend.app.api.deps import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ============================================================
# GET CURRENT USER PROFILE
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Return the authenticated user's profile,
    including their role.
    """
    return current_user