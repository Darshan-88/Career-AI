from pydantic import BaseModel, EmailStr, ConfigDict


# ============================================================
# USER REGISTRATION
# ============================================================

class UserCreate(BaseModel):

    name: str
    email: EmailStr
    password: str


# ============================================================
# USER LOGIN
# ============================================================

class UserLogin(BaseModel):

    email: EmailStr
    password: str


# ============================================================
# USER RESPONSE
# ============================================================

class UserResponse(BaseModel):

    id: int
    name: str
    email: EmailStr
    role: str="user"

    model_config = ConfigDict(
        from_attributes=True
    )


# ============================================================
# TOKEN RESPONSE
# ============================================================

class TokenResponse(BaseModel):

    access_token: str
    token_type: str


# ============================================================
# CURRENT USER RESPONSE
# ============================================================

class CurrentUserResponse(BaseModel):

    id: int
    name: str
    email: EmailStr

    model_config = ConfigDict(
        from_attributes=True
    )