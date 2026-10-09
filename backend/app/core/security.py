
import os
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash


# ============================================================
# JWT CONFIGURATION
# ============================================================

# Set SECRET_KEY in your hosting provider's environment variables.
# This fallback is only for local development.
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "local-development-only-change-this-secret"
)

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ============================================================
# PASSWORD HASHING
# ============================================================

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """Verify a plain password against its stored hash."""
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# ============================================================
# CREATE ACCESS TOKEN
# ============================================================

def create_access_token(
    data: dict,
    expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    """Create a JWT access token."""
    payload = data.copy()

    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_minutes)

    payload.update({
        "iat": now,
        "exp": expire
    })

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


# ============================================================
# DECODE ACCESS TOKEN
# ============================================================

def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    return payload


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def decode_session_token(token: str) -> dict:
    """Compatibility function for older authentication code."""
    return decode_access_token(token)
