import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.emergency_event import EmergencyEvent
from app.services import caregiver_service
from app.services.notification_service import FanoutReport, notify_caregivers

logger = logging.getLogger(__name__)

#: A second SOS from the same user inside this window is treated as an
#: accidental duplicate (double-click / network retry) and reuses the event that
#: is already open rather than fanning out again. Kept small so a genuine
#: second emergency a minute later still works.
DUPLICATE_WINDOW_SECONDS = 30


@dataclass(slots=True)
class SosOutcome:
    """Everything the SOS endpoint needs to answer honestly."""

    event: EmergencyEvent
    fanout: FanoutReport | None
    duplicate: bool
    caregiver_count: int
    is_resend: bool = False

    #: True when the alert reached at least one caregiver.
    @property
    def notified_any(self) -> bool:
        return bool(self.fanout and self.fanout.any_accepted)


def _find_recent_open_event(
    db: Session, user_id: uuid.UUID, source: str
) -> EmergencyEvent | None:
    """An OPEN event of the same source created within the duplicate window."""
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        seconds=DUPLICATE_WINDOW_SECONDS
    )
    return (
        db.query(EmergencyEvent)
        .filter(
            EmergencyEvent.user_id == user_id,
            EmergencyEvent.source == source,
            EmergencyEvent.status == "OPEN",
            EmergencyEvent.created_at >= cutoff,
        )
        .order_by(EmergencyEvent.created_at.desc())
        .first()
    )


def trigger_sos(
    db: Session,
    user_id: uuid.UUID,
    source: str,
    message: str | None,
    *,
    guardian_name: str | None = None,
    force: bool = False,
) -> SosOutcome:
    """Create one emergency event and fan an alert out to every caregiver.

    Exactly one ``emergency_events`` row is created per genuine SOS; the
    per-caregiver attempts live in ``notifications`` and are linked back to it.

    If ``force`` is False, an OPEN event with the same source within the duplicate
    window (30s) is reused to prevent rapid double-clicks or retries from spamming.
    If ``force`` is True (deliberate user action "Send another alert"), duplicate
    suppression is bypassed, creating a new emergency event and notifying caregivers again.
    """
    existing = _find_recent_open_event(db, user_id, source)
    if existing is not None:
        if not force:
            logger.info(
                "Existing SOS detected: event_id=%s created_at=%s. Duplicate blocked for user_id=%s (window=%ss)",
                existing.id,
                existing.created_at,
                user_id,
                DUPLICATE_WINDOW_SECONDS,
            )
            return SosOutcome(
                event=existing,
                fanout=None,
                duplicate=True,
                caregiver_count=len(caregiver_service.list_sos_recipients(db, user_id)),
                is_resend=False,
            )
        logger.info(
            "Existing SOS detected: event_id=%s, but deliberate resend requested (force=True). Bypassing duplicate suppression for user_id=%s.",
            existing.id,
            user_id,
        )

    event = EmergencyEvent(
        user_id=user_id,
        source=source,
        status="OPEN",
        message=message or "SOS triggered. Immediate attention required.",
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    recipients = caregiver_service.list_sos_recipients(db, user_id)

    logger.info(
        "New SOS created: user_id=%s emergency_event_id=%s source=%s is_resend=%s",
        user_id,
        event.id,
        source,
        force,
    )
    logger.info(
        "Caregivers found: count=%d for user_id=%s emergency_event_id=%s",
        len(recipients),
        user_id,
        event.id,
    )

    fanout = notify_caregivers(
        db,
        user_id=user_id,
        title="SAHAARA EMERGENCY ALERT",
        body=build_emergency_message(guardian_name=guardian_name, event=event),
        category="sos",
        emergency_event_id=event.id,
        caregivers=recipients,
    )

    return SosOutcome(
        event=event,
        fanout=fanout,
        duplicate=False,
        caregiver_count=len(recipients),
        is_resend=force,
    )


def build_emergency_message(*, guardian_name: str | None, event: EmergencyEvent) -> str:
    """Compose the factual WhatsApp body.

    Deliberately avoids any diagnosis or claim beyond "an SOS was triggered".
    Location is omitted rather than fabricated when unavailable — the platform
    does not currently capture it for SOS events.
    """
    who = guardian_name or "a Sahaara user"
    triggered_at = event.created_at or datetime.now(timezone.utc).replace(tzinfo=None)
    if isinstance(triggered_at, datetime):
        timestamp = triggered_at.strftime("%d %b %Y, %I:%M %p UTC").replace(" 0", " ")
    else:
        timestamp = str(triggered_at)

    lines = [
        "SAHAARA EMERGENCY ALERT",
        "",
        f"An SOS alert has been triggered by {who}.",
        "",
        "Please check on them immediately.",
        "",
        f"Time: {timestamp}",
        "",
        "Location information is currently unavailable.",
        "",
        "-- Sahaara ElderCare",
    ]
    return "\n".join(lines)


def resolve_event(db: Session, user_id: uuid.UUID, event_id: uuid.UUID, note: str | None) -> EmergencyEvent | None:
    """Resolve an event, but only if it belongs to ``user_id``."""
    event = (
        db.query(EmergencyEvent)
        .filter(EmergencyEvent.id == event_id, EmergencyEvent.user_id == user_id)
        .first()
    )
    if not event:
        return None
    event.status = "RESOLVED"
    event.resolved = True
    event.resolved_at = datetime.now(timezone.utc).replace(tzinfo=None)
    if note:
        event.message = f"{event.message}\nResolution: {note}"
    db.commit()
    db.refresh(event)
    return event


def list_events(db: Session, user_id: uuid.UUID) -> list[EmergencyEvent]:
    return (
        db.query(EmergencyEvent)
        .filter(EmergencyEvent.user_id == user_id)
        .order_by(EmergencyEvent.created_at.desc())
        .all()
    )
