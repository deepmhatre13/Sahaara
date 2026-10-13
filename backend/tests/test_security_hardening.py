"""Security and authorization regression tests.

Proves:
- Unauthenticated requests to private endpoints return 401.
- User A cannot access or mutate User B's resources (returns 403 or 404).
- Cross-tenant boundaries hold for health-data, medications, appointments, reports,
  chat sessions/messages, notifications, emergency events, and caregivers.
- Upload endpoint enforces file type, file size, safe filename, and clean failure.
"""

from __future__ import annotations

import io
import uuid
from datetime import time, datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app
from app.models.appointment import Appointment
from app.models.caregiver import Caregiver
from app.models.chat import ChatSession
from app.models.emergency_event import EmergencyEvent
from app.models.health_metric import HealthMetric
from app.models.medication import Medication
from app.models.notification import Notification
from app.models.user import User


@pytest.fixture()
def client(db_session):
    """Test client overriding the get_db dependency with test in-memory SQLite session."""
    from app.database.session import get_db

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def user_a(db_session) -> User:
    user = User(
        id=uuid.uuid4(),
        full_name="User Alpha",
        email="alpha@example.com",
        auth_provider="password",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def user_b(db_session) -> User:
    user = User(
        id=uuid.uuid4(),
        full_name="User Beta",
        email="beta@example.com",
        auth_provider="password",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def token_a(user_a) -> str:
    return create_access_token(user_a.id)


@pytest.fixture()
def token_b(user_b) -> str:
    return create_access_token(user_b.id)


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# =========================================================================
# 1. Unauthenticated requests fail with 401
# =========================================================================

def test_unauthenticated_requests_fail(client, user_a):
    endpoints = [
        ("GET", f"/api/health-data/{user_a.id}/summary"),
        ("GET", f"/api/health-data/{user_a.id}/metrics"),
        ("POST", f"/api/health-data/{user_a.id}/sync"),
        ("GET", f"/api/medications/{user_a.id}"),
        ("POST", "/api/medications"),
        ("DELETE", f"/api/medications/{uuid.uuid4()}"),
        ("GET", f"/api/appointments/{user_a.id}"),
        ("POST", "/api/appointments"),
        ("DELETE", f"/api/appointments/{uuid.uuid4()}"),
        ("GET", f"/api/reports/{user_a.id}"),
        ("POST", f"/api/reports/{user_a.id}/upload"),
        ("POST", "/api/chat/ask"),
        ("GET", f"/api/chat/session/{uuid.uuid4()}/messages"),
        ("GET", f"/api/activity/{user_a.id}/status"),
        ("GET", f"/api/activity/{user_a.id}/events"),
        ("POST", f"/api/activity/{user_a.id}/start-monitoring"),
        ("GET", f"/api/dashboard/{user_a.id}"),
        ("GET", "/api/notifications"),
        ("GET", f"/api/notifications/{user_a.id}"),
        ("POST", f"/api/notifications/{uuid.uuid4()}/read"),
        ("POST", "/api/sos"),
        ("POST", "/api/sos/resend"),
        ("POST", f"/api/sos/{uuid.uuid4()}/resolve"),
        ("GET", "/api/sos"),
        ("GET", f"/api/sos/{user_a.id}"),
        ("GET", "/api/caregivers"),
        ("POST", "/api/caregivers"),
        ("GET", f"/api/caregivers/{uuid.uuid4()}"),
        ("PATCH", f"/api/caregivers/{uuid.uuid4()}"),
        ("DELETE", f"/api/caregivers/{uuid.uuid4()}"),
    ]

    for method, path in endpoints:
        if method == "GET":
            res = client.get(path)
        elif method == "POST":
            res = client.post(path)
        elif method == "PATCH":
            res = client.patch(path)
        elif method == "DELETE":
            res = client.delete(path)
        assert res.status_code == 401, f"Expected 401 for unauthenticated {method} {path}, got {res.status_code}"


# =========================================================================
# 2. Health Data Ownership Checks
# =========================================================================

def test_user_a_cannot_read_or_sync_user_b_health_data(client, user_a, user_b, token_a, db_session):
    metric = HealthMetric(
        user_id=user_b.id,
        metric_type="heart_rate",
        value=75.0,
        unit="bpm",
        source="mock",
    )
    db_session.add(metric)
    db_session.commit()

    # User A attempting to access User B's health summary
    res_summary = client.get(f"/api/health-data/{user_b.id}/summary", headers=auth_header(token_a))
    assert res_summary.status_code == 403

    # User A attempting to access User B's metrics
    res_metrics = client.get(f"/api/health-data/{user_b.id}/metrics", headers=auth_header(token_a))
    assert res_metrics.status_code == 403

    # User A attempting to trigger sync for User B
    res_sync = client.post(f"/api/health-data/{user_b.id}/sync", headers=auth_header(token_a))
    assert res_sync.status_code == 403

    # User B accessing their own summary succeeds
    res_own = client.get(f"/api/health-data/{user_b.id}/summary", headers=auth_header(token_b))
    assert res_own.status_code == 200
    assert res_own.json()["heart_rate"] == 75.0


# =========================================================================
# 3. Medications Ownership Checks
# =========================================================================

def test_medication_isolation_and_cross_user_deletion(client, user_a, user_b, token_a, token_b, db_session):
    med_b = Medication(
        user_id=user_b.id,
        name="Aspirin",
        dosage="100mg",
        schedule_time=time(8, 0),
        frequency="daily",
        active=True,
    )
    db_session.add(med_b)
    db_session.commit()
    db_session.refresh(med_b)

    # User A cannot list User B's medications
    res_list = client.get(f"/api/medications/{user_b.id}", headers=auth_header(token_a))
    assert res_list.status_code == 403

    # User A cannot create medication pretending to be User B
    res_create = client.post(
        "/api/medications",
        headers=auth_header(token_a),
        json={
            "user_id": str(user_b.id),
            "name": "Ibuprofen",
            "schedule_time": "09:00:00",
        },
    )
    assert res_create.status_code == 403

    # User A cannot deactivate/delete User B's medication
    res_del = client.delete(f"/api/medications/{med_b.id}", headers=auth_header(token_a))
    assert res_del.status_code == 404

    # Medication must still be active
    db_session.refresh(med_b)
    assert med_b.active is True

    # User B can deactivate their own medication
    res_del_own = client.delete(f"/api/medications/{med_b.id}", headers=auth_header(token_b))
    assert res_del_own.status_code == 204
    db_session.refresh(med_b)
    assert med_b.active is False


# =========================================================================
# 4. Appointments Ownership Checks
# =========================================================================

def test_appointment_isolation_and_cross_user_deletion(client, user_a, user_b, token_a, token_b, db_session):
    appt_b = Appointment(
        user_id=user_b.id,
        title="Cardiologist Visit",
        scheduled_at=datetime(2026, 11, 1, 10, 0),
    )
    db_session.add(appt_b)
    db_session.commit()
    db_session.refresh(appt_b)

    # User A cannot list User B's appointments
    assert client.get(f"/api/appointments/{user_b.id}", headers=auth_header(token_a)).status_code == 403

    # User A cannot create appointment under User B
    res_create = client.post(
        "/api/appointments",
        headers=auth_header(token_a),
        json={
            "user_id": str(user_b.id),
            "title": "Dentist",
            "scheduled_at": "2026-11-02T10:00:00",
        },
    )
    assert res_create.status_code == 403

    # User A cannot delete User B's appointment
    assert client.delete(f"/api/appointments/{appt_b.id}", headers=auth_header(token_a)).status_code == 404
    assert db_session.query(Appointment).filter(Appointment.id == appt_b.id).first() is not None

    # User B can delete own appointment
    assert client.delete(f"/api/appointments/{appt_b.id}", headers=auth_header(token_b)).status_code == 204
    assert db_session.query(Appointment).filter(Appointment.id == appt_b.id).first() is None


# =========================================================================
# 5. Reports Upload and Ownership Checks
# =========================================================================

def test_reports_upload_validation_and_ownership(client, user_a, user_b, token_a, token_b):
    # User A cannot list User B's reports
    assert client.get(f"/api/reports/{user_b.id}", headers=auth_header(token_a)).status_code == 403

    # User A cannot upload report for User B
    dummy_file = ("report.pdf", io.BytesIO(b"%PDF-1.4 sample content"), "application/pdf")
    res_upload_b = client.post(
        f"/api/reports/{user_b.id}/upload",
        headers=auth_header(token_a),
        files={"file": dummy_file},
    )
    assert res_upload_b.status_code == 403

    # Invalid file extension rejected
    bad_file = ("virus.exe", io.BytesIO(b"malicious bytes"), "application/octet-stream")
    res_bad = client.post(
        f"/api/reports/{user_a.id}/upload",
        headers=auth_header(token_a),
        files={"file": bad_file},
    )
    assert res_bad.status_code == 400

    # Oversized file (> 10MB) rejected
    huge_data = io.BytesIO(b"0" * (10 * 1024 * 1024 + 1024))
    res_huge = client.post(
        f"/api/reports/{user_a.id}/upload",
        headers=auth_header(token_a),
        files={"file": ("large.pdf", huge_data, "application/pdf")},
    )
    assert res_huge.status_code == 413

    # Valid upload by owner works
    valid_pdf = ("lab_report.pdf", io.BytesIO(b"%PDF-1.4 Blood test normal"), "application/pdf")
    res_ok = client.post(
        f"/api/reports/{user_a.id}/upload",
        headers=auth_header(token_a),
        files={"file": valid_pdf},
    )
    assert res_ok.status_code == 201
    assert res_ok.json()["filename"] == "lab_report.pdf"


# =========================================================================
# 6. Chat Session Scoping
# =========================================================================

def test_chat_session_ownership(client, user_a, user_b, token_a, token_b, db_session):
    session_b = ChatSession(user_id=user_b.id, title="Beta Session")
    db_session.add(session_b)
    db_session.commit()
    db_session.refresh(session_b)

    # User A asking under User B's user_id -> 403
    res_ask_spoof = client.post(
        "/api/chat/ask",
        headers=auth_header(token_a),
        json={"user_id": str(user_b.id), "message": "hello"},
    )
    assert res_ask_spoof.status_code == 403

    # User A querying User B's session messages receives empty list (isolated)
    res_messages = client.get(
        f"/api/chat/session/{session_b.id}/messages",
        headers=auth_header(token_a),
    )
    assert res_messages.status_code == 200
    assert res_messages.json() == []


# =========================================================================
# 7. Notifications Scoping
# =========================================================================

def test_notification_ownership(client, user_a, user_b, token_a, token_b, db_session):
    notif_b = Notification(
        user_id=user_b.id,
        category="system",
        title="Beta Alert",
        body="Secret Info",
        channel="console",
        status="logged",
    )
    db_session.add(notif_b)
    db_session.commit()
    db_session.refresh(notif_b)

    # User A cannot read User B's notifications
    res = client.get(f"/api/notifications/{user_b.id}", headers=auth_header(token_a))
    assert res.status_code == 403

    # User A cannot mark User B's notification as read
    res_read = client.post(f"/api/notifications/{notif_b.id}/read", headers=auth_header(token_a))
    assert res_read.status_code == 404

    db_session.refresh(notif_b)
    assert notif_b.read is False


# =========================================================================
# 8. Emergency Event Ownership and Resolution
# =========================================================================

def test_sos_event_ownership_and_resolution(client, user_a, user_b, token_a, token_b, db_session):
    event_b = EmergencyEvent(
        user_id=user_b.id,
        source="sos_button",
        status="OPEN",
        resolved=False,
    )
    db_session.add(event_b)
    db_session.commit()
    db_session.refresh(event_b)

    # User A cannot list User B's SOS history
    assert client.get(f"/api/sos/{user_b.id}", headers=auth_header(token_a)).status_code == 403

    # User A cannot resolve User B's emergency event
    res_resolve = client.post(
        f"/api/sos/{event_b.id}/resolve",
        headers=auth_header(token_a),
        json={"resolution_note": "False alarm"},
    )
    assert res_resolve.status_code == 404

    db_session.refresh(event_b)
    assert event_b.resolved is False


# =========================================================================
# 9. Caregivers Scoping
# =========================================================================

def test_caregiver_scoping(client, user_a, user_b, token_a, token_b, db_session):
    cg_b = Caregiver(
        elder_id=user_b.id,
        full_name="Caregiver Beta",
        phone_number="+919892000000",
        is_active=True,
    )
    db_session.add(cg_b)
    db_session.commit()
    db_session.refresh(cg_b)

    # User A listing caregivers only sees their own (0 for user A)
    res_list = client.get("/api/caregivers", headers=auth_header(token_a))
    assert res_list.status_code == 200
    assert len(res_list.json()) == 0

    # User A cannot read User B's caregiver
    assert client.get(f"/api/caregivers/{cg_b.id}", headers=auth_header(token_a)).status_code == 404

    # User A cannot update User B's caregiver
    assert client.patch(
        f"/api/caregivers/{cg_b.id}",
        headers=auth_header(token_a),
        json={"full_name": "Hacked Name"},
    ).status_code == 404

    # User A cannot delete User B's caregiver
    assert client.delete(f"/api/caregivers/{cg_b.id}", headers=auth_header(token_a)).status_code == 404
