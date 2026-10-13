import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.notification import NotificationOut
from app.services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
def list_mine(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """The authenticated user's own notifications."""
    return notification_service.list_notifications(db, current_user.id)


@router.get("/{user_id}", response_model=list[NotificationOut])
def list_for_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Kept for backward compatibility; only your own notifications are returned."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this user",
        )
    return notification_service.list_notifications(db, user_id)


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = notification_service.mark_read(db, current_user.id, notification_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return record
