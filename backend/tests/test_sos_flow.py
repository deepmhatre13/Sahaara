"""SOS fan-out: one event, N attempts, independent per-caregiver outcomes.

The provider is always a fake, so no real WhatsApp message is ever sent.
"""

from __future__ import annotations

import uuid

from app.models.emergency_event import EmergencyEvent
from app.models.notification import Notification
from app.schemas.caregiver import CaregiverCreate
from app.services import caregiver_service, emergency_service
from app.services.notification_service import notify_caregivers
from tests.conftest import FakeNotificationProvider


def _add_caregiver(db, elder, name, phone, **kwargs):
    return caregiver_service.create_caregiver(
        db, elder.id, CaregiverCreate(full_name=name, phone_number=phone, **kwargs)
    )


# --- zero caregivers ---------------------------------------------------------

def test_sos_without_caregivers_still_creates_the_event(db_session, elder, fake_provider):
    outcome = emergency_service.trigger_sos(
        db_session, elder.id, "sos_button", None, guardian_name=elder.full_name
    )

    assert outcome.event.id is not None
    assert outcome.event.status == "OPEN"
    assert outcome.event.source == "sos_button"
    assert outcome.caregiver_count == 0
    assert outcome.fanout.accepted == 0
    assert outcome.notified_any is False
    # Exactly one emergency event, and no notification rows to create.
    assert db_session.query(EmergencyEvent).count() == 1
    assert outcome.fanout.notifications_created == 0


# --- one caregiver -----------------------------------------------------------

def test_sos_with_one_caregiver_creates_one_notification(db_session, elder):
    _add_caregiver(db_session, elder, "Solo", "9892031558")
    provider = FakeNotificationProvider()

    outcome = emergency_service.trigger_sos(
        db_session, elder.id, "sos_button", None, guardian_name=elder.full_name
    )
    # Re-run the fan-out against the fake for a deterministic result set.
    report = notify_caregivers(
        db_session,
        user_id=elder.id,
        title="SAHAARA EMERGENCY ALERT",
        body="test",
        emergency_event_id=outcome.event.id,
        provider=provider,
    )

    assert report.caregivers_targeted == 1
    assert report.notifications_created == 1
    assert report.accepted == 1
    assert provider.sent[0]["to"] == "+919892031558"


# --- two caregivers ----------------------------------------------------------

def test_sos_with_two_caregivers_targets_both(db_session, elder):
    _add_caregiver(db_session, elder, "One", "9892031558", is_primary=True)
    _add_caregiver(db_session, elder, "Two", "8652721553")
    provider = FakeNotificationProvider()

    outcome = emergency_service.trigger_sos(
        db_session, elder.id, "sos_button", None, guardian_name=elder.full_name
    )
    report = notify_caregivers(
        db_session,
        user_id=elder.id,
        title="SAHAARA EMERGENCY ALERT",
        body="test",
        emergency_event_id=outcome.event.id,
        provider=provider,
    )

    assert report.caregivers_targeted == 2
    assert report.notifications_created == 2
    assert report.accepted == 2
    assert report.failed == 0
    # One SOS -> one emergency event, never one per caregiver.
    assert db_session.query(EmergencyEvent).count() == 1
    assert {call["to"] for call in provider.sent} == {"+919892031558", "+918652721553"}


def test_one_event_links_all_attempts(db_session, elder):
    _add_caregiver(db_session, elder, "One", "9892031558")
    _add_caregiver(db_session, elder, "Two", "8652721553")
    provider = FakeNotificationProvider()

    # trigger_sos performs the fan-out itself; pass the fake in via monkeypatch
    # so this test observes one real call path rather than fanning out twice.
    import app.services.notification_service as notification_service

    original_factory = notification_service.get_notification_provider
    notification_service.get_notification_provider = lambda: provider
    try:
        outcome = emergency_service.trigger_sos(
            db_session, elder.id, "sos_button", None, guardian_name=elder.full_name
        )
    finally:
        notification_service.get_notification_provider = original_factory

    linked = (
        db_session.query(Notification)
        .filter(Notification.emergency_event_id == outcome.event.id)
        .all()
    )
    # Exactly two attempts — one per caregiver — for the single event.
    assert len(linked) == 2
    assert outcome.fanout.caregivers_targeted == 2
    assert all(n.category == "sos" for n in linked)
    assert all(n.caregiver_id is not None for n in linked)
    assert all(n.status == "queued" for n in linked)
    assert all(n.provider_message_id for n in linked)
    # One event, two attempts — never two events.
    assert db_session.query(EmergencyEvent).count() == 1


# --- partial failure ---------------------------------------------------------

def test_one_success_one_failure_is_reported_per_caregiver(db_session, elder):
    _add_caregiver(db_session, elder, "Good", "9892031558")
    _add_caregiver(db_session, elder, "Bad", "8652721553")
    # Second caregiver is rejected by the "provider" (e.g. sandbox not joined).
    provider = FakeNotificationProvider(fail_for={"+918652721553"})

    report = notify_caregivers(
        db_session,
        user_id=elder.id,
        title="SAHAARA EMERGENCY ALERT",
        body="test",
        provider=provider,
    )

    assert report.caregivers_targeted == 2
    assert report.notifications_created == 2
    assert report.accepted == 1
    assert report.failed == 1
    # Both recipients were attempted — the failure did not abort the loop.
    assert len(provider.sent) == 2

    by_name = {d.caregiver_name: d for d in report.delivery}
    assert by_name["Good"].accepted is True
    assert by_name["Good"].provider_message_id is not None
    assert by_name["Bad"].accepted is False
    assert by_name["Bad"].error_code == "63016"


def test_failed_attempt_is_persisted_with_the_provider_error(db_session, elder):
    _add_caregiver(db_session, elder, "Bad", "8652721553")
    provider = FakeNotificationProvider(fail_for={"+918652721553"})

    notify_caregivers(
        db_session,
        user_id=elder.id,
        title="SAHAARA EMERGENCY ALERT",
        body="test",
        provider=provider,
    )

    record = db_session.query(Notification).one()
    assert record.status == "failed"
    assert record.delivered is False
    assert record.error_message == "Recipient has not joined the WhatsApp sandbox"
    assert record.caregiver_id is not None


def test_provider_exception_does_not_abort_the_fan_out(db_session, elder):
    _add_caregiver(db_session, elder, "Crasher", "9892031558")
    _add_caregiver(db_session, elder, "Survivor", "8652721553")
    provider = FakeNotificationProvider(raises_for={"+919892031558"})

    report = notify_caregivers(
        db_session,
        user_id=elder.id,
        title="SAHAARA EMERGENCY ALERT",
        body="test",
        provider=provider,
    )

    assert report.caregivers_targeted == 2
    assert report.accepted == 1
    assert report.failed == 1
    by_name = {d.caregiver_name: d for d in report.delivery}
    assert by_name["Crasher"].error_code == "provider_exception"
    assert by_name["Survivor"].accepted is True


# --- complete failure --------------------------------------------------------

def test_all_caregivers_failing_still_reports_the_event(db_session, elder):
    _add_caregiver(db_session, elder, "One", "9892031558")
    _add_caregiver(db_session, elder, "Two", "8652721553")
    provider = FakeNotificationProvider(fail_for={"+919892031558", "+918652721553"})

    outcome = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)
    report = notify_caregivers(
        db_session,
        user_id=elder.id,
        title="SAHAARA EMERGENCY ALERT",
        body="test",
        emergency_event_id=outcome.event.id,
        provider=provider,
    )

    assert report.accepted == 0
    assert report.failed == 2
    assert report.any_accepted is False
    # The emergency event exists and stands regardless of delivery.
    assert db_session.query(EmergencyEvent).count() == 1


def test_simulated_provider_is_flagged(db_session, elder):
    """The console provider must be distinguishable from a real send."""
    _add_caregiver(db_session, elder, "One", "9892031558")
    from app.notifications.console_provider import ConsoleNotificationProvider

    report = notify_caregivers(
        db_session,
        user_id=elder.id,
        title="SAHAARA EMERGENCY ALERT",
        body="test",
        provider=ConsoleNotificationProvider(),
    )

    assert report.simulated is True
    assert report.accepted == 1
    assert report.delivery[0].status == "logged"


# --- duplicate protection ----------------------------------------------------

def test_duplicate_sos_inside_the_window_reuses_the_event(db_session, elder):
    first = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)
    second = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)

    assert second.duplicate is True
    assert second.event.id == first.event.id
    assert second.fanout is None
    assert db_session.query(EmergencyEvent).count() == 1


def test_a_resolved_event_does_not_block_a_new_sos(db_session, elder):
    first = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)
    emergency_service.resolve_event(db_session, elder.id, first.event.id, "fine now")

    second = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)
    assert second.duplicate is False
    assert second.event.id != first.event.id
    assert db_session.query(EmergencyEvent).count() == 2


def test_force_sos_bypasses_duplicate_suppression_and_creates_new_event(db_session, elder):
    _add_caregiver(db_session, elder, "Primary", "9892031558")
    provider = FakeNotificationProvider()

    import app.services.notification_service as notification_service

    original_factory = notification_service.get_notification_provider
    notification_service.get_notification_provider = lambda: provider
    try:
        first = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)
        assert first.duplicate is False
        assert first.is_resend is False
        assert db_session.query(EmergencyEvent).count() == 1
        assert len(provider.sent) == 1

        # Deliberate "Send another alert" inside the 30s window
        second = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None, force=True)
        assert second.duplicate is False
        assert second.is_resend is True
        assert second.event.id != first.event.id
        # Both events remain OPEN and intact
        assert first.event.status == "OPEN"
        assert second.event.status == "OPEN"
        assert db_session.query(EmergencyEvent).count() == 2
        # Caregivers were targeted again
        assert len(provider.sent) == 2
        assert second.fanout is not None
        assert second.fanout.notifications_created == 1
    finally:
        notification_service.get_notification_provider = original_factory


def test_rapid_accidental_click_suppressed_then_force_resend_succeeds(db_session, elder):
    _add_caregiver(db_session, elder, "Caregiver", "9892031558")
    provider = FakeNotificationProvider()

    import app.services.notification_service as notification_service

    original_factory = notification_service.get_notification_provider
    notification_service.get_notification_provider = lambda: provider
    try:
        # 1. Normal SOS
        first = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)
        assert first.duplicate is False
        assert len(provider.sent) == 1

        # 2. Rapid accidental click
        accidental = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)
        assert accidental.duplicate is True
        assert accidental.event.id == first.event.id
        assert accidental.fanout is None
        assert len(provider.sent) == 1  # No duplicate alert sent

        # 3. Deliberate "Send another alert"
        resend = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None, force=True)
        assert resend.duplicate is False
        assert resend.is_resend is True
        assert resend.event.id != first.event.id
        assert len(provider.sent) == 2  # New alert sent
        assert db_session.query(EmergencyEvent).count() == 2
    finally:
        notification_service.get_notification_provider = original_factory


# --- message content ---------------------------------------------------------

def test_emergency_message_is_factual_and_omits_location(db_session, elder):
    outcome = emergency_service.trigger_sos(
        db_session, elder.id, "sos_button", None, guardian_name=elder.full_name
    )
    body = emergency_service.build_emergency_message(
        guardian_name=elder.full_name, event=outcome.event
    )

    assert "SAHAARA EMERGENCY ALERT" in body
    assert "DEEPAM MHATRE" in body
    assert "An SOS alert has been triggered" in body
    assert "Location information is currently unavailable." in body
    # No invented diagnosis or unverifiable claim.
    assert "diagnos" not in body.lower()


def test_emergency_message_falls_back_when_name_unknown(db_session, elder):
    outcome = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)
    body = emergency_service.build_emergency_message(guardian_name=None, event=outcome.event)
    assert "a Sahaara user" in body


# --- authorization -----------------------------------------------------------

def test_resolve_refuses_another_users_event(db_session, elder, other_elder):
    outcome = emergency_service.trigger_sos(db_session, elder.id, "sos_button", None)

    assert (
        emergency_service.resolve_event(db_session, other_elder.id, outcome.event.id, "nope")
        is None
    )
    db_session.refresh(outcome.event)
    assert outcome.event.status == "OPEN"


def test_caregivers_of_one_user_are_never_targeted_for_another(db_session, elder, other_elder):
    _add_caregiver(db_session, elder, "Mine", "9892031558")
    _add_caregiver(db_session, other_elder, "Theirs", "8652721553")
    provider = FakeNotificationProvider()

    report = notify_caregivers(
        db_session,
        user_id=elder.id,
        title="SAHAARA EMERGENCY ALERT",
        body="test",
        provider=provider,
    )

    assert report.caregivers_targeted == 1
    assert [call["to"] for call in provider.sent] == ["+919892031558"]
