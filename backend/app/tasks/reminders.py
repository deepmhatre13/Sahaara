"""Periodic reminder tasks (medications + appointments).

Both tasks are written to be safe to run repeatedly: the appointment task flips a
``reminded`` flag so a reminder is only ever sent once, and the medication task
uses a ±1 minute window so a beat/worker drift cannot cause a double send within
the same minute.

Timezone note: ``Medication.schedule_time`` is a naive time-of-day column and
``Appointment.scheduled_at`` is a naive datetime column, so reminder windows are
evaluated in UTC. For a real deployment where elders live in one non-UTC region,
either switch these columns to timezone-aware types or add a per-user timezone
and convert here — this is a deliberate Part 1 simplification.
"""
import logging
from datetime import datetime, timedelta, timezone

from app.core.celery_app import celery_app
from app.database.session import SessionLocal
from app.models.appointment import Appointment
from app.models.medication import Medication
from app.services import notification_service

logger = logging.getLogger(__name__)

#: How close "now" must be to a scheduled time-of-day to fire a medication reminder.
_MEDICATION_WINDOW_MINUTES = 1

#: How far ahead of an appointment to send a heads-up reminder.
_APPOINTMENT_LEAD_MINUTES = 60


@celery_app.task(name="app.tasks.reminders.check_medication_reminders")
def check_medication_reminders() -> int:
    """Fire once per active medication whose ``schedule_time`` matches this minute.

    Returns the number of reminders sent.
    """
    db = SessionLocal()
    sent = 0
    try:
        now = datetime.now(timezone.utc)
        current_time = now.time().replace(second=0, microsecond=0)
        midnight = datetime.combine(now.date(), datetime.min.time())

        medications = db.query(Medication).filter(Medication.active.is_(True)).all()
        for med in medications:
            if med.schedule_time is None:
                continue

            scheduled = med.schedule_time.replace(second=0, microsecond=0)
            # Compare as datetimes on a shared date so the midnight wrap cannot
            # produce a spurious ~24h difference.
            diff_minutes = abs(
                (midnight + current_time - (midnight + scheduled)).total_seconds()
            ) / 60
            if diff_minutes > _MEDICATION_WINDOW_MINUTES:
                continue

            dosage = f" ({med.dosage})" if med.dosage else ""
            notification_service.notify(
                db,
                user_id=med.user_id,
                category=notification_service.CATEGORY_MEDICATION,
                title="Medication Reminder",
                body=f"It's time to take {med.name}{dosage}.",
            )
            sent += 1
    except Exception as exc:  # noqa: BLE001 - a bad row must not stop the schedule
        logger.error("check_medication_reminders failed: %s", exc)
        db.rollback()
    finally:
        db.close()
    return sent


@celery_app.task(name="app.tasks.reminders.check_appointment_reminders")
def check_appointment_reminders() -> int:
    """Send a one-time reminder for appointments starting within the lead window.

    Returns the number of reminders sent.
    """
    db = SessionLocal()
    sent = 0
    try:
        now = datetime.now(timezone.utc)
        # ``scheduled_at`` is stored naive/UTC, so strip tzinfo for the comparison.
        now_naive = now.replace(tzinfo=None)
        window_end = now_naive + timedelta(minutes=_APPOINTMENT_LEAD_MINUTES)

        appointments = (
            db.query(Appointment)
            .filter(
                Appointment.reminded.is_(False),
                Appointment.scheduled_at >= now_naive,
                Appointment.scheduled_at <= window_end,
            )
            .all()
        )

        for appt in appointments:
            location = f", {appt.location}" if appt.location else ""
            notification_service.notify(
                db,
                user_id=appt.user_id,
                category=notification_service.CATEGORY_APPOINTMENT,
                title="Upcoming Appointment",
                body=(
                    f"Reminder: '{appt.title}' at "
                    f"{appt.scheduled_at.strftime('%H:%M')}{location}."
                ),
            )
            appt.reminded = True
            sent += 1

        if appointments:
            db.commit()
    except Exception as exc:  # noqa: BLE001
        logger.error("check_appointment_reminders failed: %s", exc)
        db.rollback()
    finally:
        db.close()
    return sent
