import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import ensure_self, get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Admin/manual user creation. Left unauthenticated in dev; gate this behind
    an admin role before any real deployment."""
    if user_service.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return user_service.create_user(db, payload)


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Fetch one profile. A user may always read their own; anything else is
    refused until caregiver-role authorization exists."""
    ensure_self(current_user, user_id)
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Directory listing — effectively an admin endpoint.

    It stays authenticated-only for Part 1 (rather than returning every account
    to anonymous callers, which would leak the whole user table). Replace the body
    with a real admin check when roles land.
    """
    return user_service.list_users(db)
