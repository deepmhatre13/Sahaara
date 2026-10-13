"""Notification persistence and delivery.

Two entry points:

``notify_caregivers`` — fan-out used by SOS (and, later, by inactivity alerts).
    Attempts every eligible caregiver independently, so one provider rejection
    never blocks the rest, and returns a per-recipient report.

``notify`` — single-recipient helper kept for the non-emergency callers
    (medication reminders, inactivity notices) that already used it.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import asdict, dataclass, field

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.phone import mask_phone
from app.models.caregiver import Caregiver
from app.models.notification import Notification
from app.notifications.base import DeliveryResult, NotificationProvider
from app.notifications.factory import get_notification_provider
from app.services import caregiver_service

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CaregiverDelivery:
    """One caregiver's attempt result, as returned to the API layer."""

    caregiver_id: uuid.UUID
    caregiver_name: str
    status: str
    channel: str
    accepted: bool
    notification_id: uuid.UUID | None = None
    provider_message_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None


@dataclass(slots=True)
class FanoutReport:
    """Aggregate outcome of one fan-out, plus the per-caregiver detail."""

    caregivers_targeted: int = 0
    caregivers_skipped: int = 0
    notifications_created: int = 0
    accepted: int = 0
    failed: int = 0
    simulated: bool = False
    delivery: list[CaregiverDelivery] = field(default_factory=list)

    @property
    def any_accepted(self) -> bool:
        return self.accepted > 0

    def to_dict(self) -> dict:
        return {
            "caregivers_targeted": self.caregivers_targeted,
            "caregivers_skipped": self.caregivers_skipped,
            "notifications_created": self.notifications_created,
            "accepted": self.accepted,
            "failed": self.failed,
            "simulated": self.simulated,
            "delivery": [asdict(d) for d in self.delivery],
        }


def _record_attempt(
    db: Session,
    *,
    user_id: uuid.UUID,
    title: str,
    body: str,
    channel: str,
    result: DeliveryResult,
    category: str,
    caregiver_id: uuid.UUID | None,
    emergency_event_id: uuid.UUID | None,
) -> Notification:
    """Persist a single delivery attempt (staged; caller commits)."""
    record = Notification(
        user_id=user_id,
        caregiver_id=caregiver_id,
        emergency_event_id=emergency_event_id,
        category=category,
        title=title[:255],
        body=body[:1000],
        channel=channel,
        status=result.status,
        delivered=result.was_accepted,
        provider_message_id=result.provider_message_id,
        error_message=result.error_message,
    )
    db.add(record)
    return record


def notify_caregivers(
    db: Session,
    *,
    user_id: uuid.UUID,
    title: str,
    body: str,
    category: str = "sos",
    emergency_event_id: uuid.UUID | None = None,
    caregivers: list[Caregiver] | None = None,
    provider: NotificationProvider | None = None,
) -> FanoutReport:
    """Send ``title``/``body`` to every active WhatsApp-reachable caregiver.

    Each caregiver is attempted inside its own guard. A failure is recorded
    against that caregiver and the loop continues — one bad number must not
    suppress the alert to everyone else, and the emergency event stands either
    way.

    ``provider`` is injectable so tests can supply a fake without touching
    Twilio or the module-level factory.
    """
    settings = get_settings()
    provider = provider or get_notification_provider()
    channel = getattr(provider, "name", None) or settings.notification_provider

    if caregivers is None:
        caregivers = caregiver_service.list_sos_recipients(db, user_id)

    report = FanoutReport(caregivers_targeted=len(caregivers))
    logger.info(
        "Caregiver fan-out: user_id=%s event_id=%s channel=%s caregiver_count=%d",
        user_id,
        emergency_event_id,
        channel,
        len(caregivers),
    )

    for caregiver in caregivers:
        destination = caregiver.whatsapp_destination
        logger.info(
            "Notification attempt: channel=%s caregiver_id=%s name=%s to=%s emergency_event_id=%s",
            channel,
            caregiver.id,
            caregiver.full_name,
            mask_phone(destination),
            emergency_event_id,
        )

        if not destination:
            report.caregivers_skipped += 1
            result = DeliveryResult.skipped("Caregiver has no WhatsApp-reachable number")
        else:
            try:
                result = provider.send(to=destination, title=title, body=body)
            except Exception as exc:  # noqa: BLE001 - a raise must not abort the fan-out
                logger.exception("Provider raised for caregiver_id=%s", caregiver.id)
                result = DeliveryResult.failure(
                    error_code="provider_exception",
                    error_message=str(exc)[:400],
                )

        record = _record_attempt(
            db,
            user_id=user_id,
            caregiver_id=caregiver.id,
            emergency_event_id=emergency_event_id,
            category=category,
            title=title,
            body=body,
            channel=channel,
            result=result,
        )

        if result.simulated:
            report.simulated = True
        if result.was_accepted:
            report.accepted += 1
            logger.info(
                "Notification success: channel=%s caregiver_id=%s to=%s provider_message_id=%s status=%s",
                channel,
                caregiver.id,
                mask_phone(destination),
                result.provider_message_id,
                result.status,
            )
        else:
            report.failed += 1
            logger.warning(
                "Notification failure: channel=%s caregiver_id=%s to=%s status=%s error_code=%s error=%s",
                channel,
                caregiver.id,
                mask_phone(destination),
                result.status,
                result.error_code,
                result.error_message,
            )

        # Flush per record so the row gets its primary key and any integrity
        # error is attributed to this caregiver, not to the whole batch.
        db.flush()
        report.delivery.append(
            CaregiverDelivery(
                caregiver_id=caregiver.id,
                caregiver_name=caregiver.full_name,
                notification_id=record.id,
                status=result.status,
                channel=channel,
                accepted=result.was_accepted,
                provider_message_id=result.provider_message_id,
                error_code=result.error_code,
                error_message=result.error_message,
            )
        )
        report.notifications_created += 1

    db.commit()
    return report


def notify(db: Session, *, user_id: uuid.UUID, category: str, title: str, body: str) -> Notification:
    settings = get_settings()
    provider = get_notification_provider()

    destination = None
    caregiver = (
        db.query(Caregiver)
        .filter(Caregiver.elder_id == user_id, Caregiver.is_primary.is_(True))
        .first()
    )
    if caregiver:
        destination = caregiver.whatsapp_number or caregiver.phone_number

    result = provider.send(to=destination, title=title, body=body)

    record = Notification(
        user_id=user_id,
        category=category,
        title=title,
        body=body,
        channel=getattr(provider, "name", None) or settings.notification_provider,
        status=result.status,
        delivered=result.was_accepted,
        provider_message_id=result.provider_message_id,
        error_message=result.error_message,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_notifications(db: Session, user_id: uuid.UUID) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(100)
        .all()
    )


def mark_read(db: Session, user_id: uuid.UUID, notification_id: uuid.UUID) -> Notification | None:
    """Mark read, but only for the owning user (prevents cross-account writes)."""
    record = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == user_id)
        .first()
    )
    if not record:
        return None
    record.read = True
    db.commit()
    db.refresh(record)
    return record
