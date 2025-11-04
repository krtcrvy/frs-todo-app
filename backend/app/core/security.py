from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

# Initialize password hasher
password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against

    Returns:
        True if the password matches, False otherwise
    """
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain password using Argon2.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password string
    """
    return password_hash.hash(password)


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token (typically user ID and email)
        expires_delta: Optional custom expiration time. If None, uses settings default.

    Returns:
        The encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT token string to decode

    Returns:
        The decoded token payload

    Raises:
        jwt.ExpiredSignatureError: If the token has expired
        jwt.InvalidTokenError: If the token is invalid
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload
