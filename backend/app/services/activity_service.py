import uuid
import logging

from sqlalchemy.orm import Session

from app.models.activity_event import ActivityEvent
from app.services.notification_service import notify
from app.vision.motion_monitor import motion_registry

logger = logging.getLogger(__name__)


def _persist_event_factory(db_factory):
    """Returns an on_event callback bound to a fresh DB session per call,
    since the motion monitor runs on a background thread."""

    def _on_event(user_id: uuid.UUID, event_type: str, details: str | None) -> None:
        db = db_factory()
        try:
            event = ActivityEvent(user_id=user_id, event_type=event_type, details=details)
            db.add(event)
            db.commit()

            if event_type == "INACTIVITY_THRESHOLD_EXCEEDED":
                notify(
                    db,
                    user_id=user_id,
                    category="inactivity",
                    title="Inactivity Alert",
                    body=details or "No motion detected for an extended period.",
                )
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to persist activity event: %s", exc)
        finally:
            db.close()

    return _on_event


def ensure_monitor_running(user_id: uuid.UUID, db_factory) -> None:
    motion_registry.get_or_create(user_id, _persist_event_factory(db_factory))


def get_status(user_id: uuid.UUID) -> dict | None:
    monitor = motion_registry.get(user_id)
    if monitor is None:
        return None
    return monitor.get_status()


def list_events(db: Session, user_id: uuid.UUID) -> list[ActivityEvent]:
    return (
        db.query(ActivityEvent)
        .filter(ActivityEvent.user_id == user_id)
        .order_by(ActivityEvent.created_at.desc())
        .limit(100)
        .all()
    )