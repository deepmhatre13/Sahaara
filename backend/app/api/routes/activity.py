import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import ensure_self, get_current_user
from app.database.session import get_db
from app.database.session import SessionLocal
from app.models.user import User
from app.schemas.activity import ActivityEventOut, ActivityStatusOut
from app.services import activity_service

router = APIRouter(prefix="/activity", tags=["activity"])


@router.post("/{user_id}/start-monitoring", status_code=202)
def start_monitoring(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    activity_service.ensure_monitor_running(user_id, SessionLocal)
    return {"status": "monitoring_started"}


@router.get("/{user_id}/status", response_model=ActivityStatusOut | None)
def status(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    status = activity_service.get_status(user_id)
    if status is None:
        return None
    return {"user_id": user_id, **status}


@router.get("/{user_id}/events", response_model=list[ActivityEventOut])
def events(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return activity_service.list_events(db, user_id)