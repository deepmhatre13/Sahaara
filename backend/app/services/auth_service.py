import logging
import uuid

from sqlalchemy.orm import Session
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.core.config import get_settings
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import SignupRequest, LoginRequest, GoogleLoginRequest

logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Raised for any auth failure; routes translate this to HTTP 400/401."""


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def signup_with_password(db: Session, payload: SignupRequest) -> tuple[User, str]:
    if get_user_by_email(db, payload.email):
        raise AuthError("An account with this email already exists")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        auth_provider="password",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return user, token


def login_with_password(db: Session, payload: LoginRequest) -> tuple[User, str]:
    user = get_user_by_email(db, payload.email)
    if not user or user.auth_provider != "password" or not user.hashed_password:
        raise AuthError("Invalid email or password")
    if not verify_password(payload.password, user.hashed_password):
        raise AuthError("Invalid email or password")
    if not user.is_active:
        raise AuthError("Account is disabled")

    token = create_access_token(user.id)
    return user, token


def _verify_google_id_token(raw_token: str) -> dict:
    settings = get_settings()
    if not settings.google_client_id:
        raise AuthError("Google sign-in is not configured on the server")

    try:
        payload = google_id_token.verify_oauth2_token(
            raw_token, google_requests.Request(), settings.google_client_id
        )
    except ValueError as exc:
        logger.warning("Invalid Google ID token: %s", exc)
        raise AuthError("Invalid Google token") from exc

    if payload.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
        raise AuthError("Invalid token issuer")

    return payload


def login_or_signup_with_google(db: Session, payload: GoogleLoginRequest) -> tuple[User, str]:
    claims = _verify_google_id_token(payload.id_token)

    google_id = claims["sub"]
    email = claims.get("email")
    full_name = claims.get("name") or (email.split("@")[0] if email else "Google User")

    if not email:
        raise AuthError("Google account has no email")

    user = db.query(User).filter(User.google_id == google_id).first()
    if user is None:
        # Fall back to matching an existing password-based account with the same email,
        # so a person who signed up manually can also use "Sign in with Google" later.
        user = get_user_by_email(db, email)
        if user is None:
            user = User(
                full_name=full_name,
                email=email,
                auth_provider="google",
                google_id=google_id,
            )
            db.add(user)
        else:
            user.google_id = google_id
            if user.auth_provider == "password":
                # Keep existing password login working; just link the Google identity.
                pass
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise AuthError("Account is disabled")

    token = create_access_token(user.id)
    return user, token


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()