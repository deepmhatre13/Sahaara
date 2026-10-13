import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError

from app.core.config import get_settings

# bcrypt truncates (and historically wrapped) input at 72 bytes. passlib used to
# paper over this, but passlib 1.7.4 is unmaintained and crashes with
# `bcrypt >= 4.1` during its backend capability probe
#   ValueError: password cannot be longer than 72 bytes
# so we call the bcrypt library directly and handle the 72-byte limit ourselves.
_BCRYPT_MAX_BYTES = 72


def _prepare(password: str) -> bytes:
    """Encode a password to bytes, safely truncated to bcrypt's 72-byte limit."""
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_prepare(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(_prepare(plain_password), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        # Malformed / non-bcrypt stored hash — treat as a failed verification
        # rather than raising a 500.
        return False



def create_access_token(subject: uuid.UUID | str, expires_minutes: int | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload = {"sub": str(subject), "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
        return payload.get("sub")
    except JWTError:
        return None