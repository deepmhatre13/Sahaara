import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import ensure_self, get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services import health_service, activity_service, emergency_service, notification_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{user_id}")
def get_dashboard(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return {
        "health_summary": health_service.get_latest_summary(db, user_id),
        "activity_status": activity_service.get_status(user_id),
        "open_emergencies": [
            e for e in emergency_service.list_events(db, user_id) if not e.resolved
        ],
        "recent_notifications": notification_service.list_notifications(db, user_id)[:10],
    }