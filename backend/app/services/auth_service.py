from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.core.security import (
    hash_password,
    verify_password
)


# ============================================================
# REGISTER USER
# ============================================================

def register_user(
    db: Session,
    name: str,
    email: str,
    password: str
) -> User:

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise ValueError(
            "Email already registered"
        )

    hashed_password = hash_password(password)

    new_user = User(
        name=name,
        email=email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ============================================================
# LOGIN USER
# ============================================================

def login_user(
    db: Session,
    email: str,
    password: str
) -> User:

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError(
            "Invalid email or password"
        )

    password_valid = verify_password(
        password,
        user.password
    )

    if not password_valid:
        raise ValueError(
            "Invalid email or password"
        )

    return user