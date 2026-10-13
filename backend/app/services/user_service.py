import hashlib
import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate


def _hash_password(password: str) -> str:
    # NOTE: placeholder hashing for Part 1 scaffolding. Swap for passlib/bcrypt
    # before any real deployment.
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(db: Session, payload: UserCreate) -> User:
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone_number=payload.phone_number,
        date_of_birth=payload.date_of_birth,
        hashed_password=_hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or user.hashed_password != _hash_password(password):
        return None
    return user


def list_users(db: Session) -> list[User]:
    return db.query(User).all()