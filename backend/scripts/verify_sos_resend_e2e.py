"""Live E2E test verifying the 4 SOS scenarios."""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8001/api"


def p(msg):
    print(msg, flush=True)


def call(method, path, body=None, token=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{BASE}{path}", data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode()[:400]


def main():
    from app.core.security import create_access_token
    from app.database.session import SessionLocal
    from app.models import User

    email = "mhatredeepam@gmail.com"
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print(f"ERROR: no user with email {email}")
            return 1
        token = create_access_token(user.id)
        user_id = user.id
        print(f"Authenticated as: {user.full_name} ({user_id})")
    finally:
        db.close()

    # Step 0: Clean up any existing OPEN events for clean baseline (resolve only first open event)
    status, events = call("GET", "/sos", token=token)
    if status == 200 and isinstance(events, list):
        for ev in events[:5]:
            if ev.get("status") == "OPEN":
                call("POST", f"/sos/{ev['id']}/resolve", {"resolution_note": "reset"}, token=token)
                break

    p("\n" + "=" * 50)
    p("TEST 1: Initial SOS (normal trigger)")
    p("=" * 50)
    status, sos1 = call("POST", "/sos", {"source": "sos_button", "force": False}, token=token)
    assert status in (200, 201), f"Unexpected status: {status}"
    assert sos1["created"] is True, "TEST 1 FAILED: expected created=True"
    event1_id = sos1["emergency_event"]["id"]
    p(f"Event 1 ID: {event1_id}")
    assert sos1["caregivers_targeted"] == 2
    assert sos1["notifications_created"] == 2
    p(f"Caregivers targeted: {sos1['caregivers_targeted']}, Notifications: {sos1['notifications_created']}")
    p(">>> TEST 1 PASS")

    p("\n" + "=" * 50)
    p("TEST 2: Rapid accidental duplicate (force=False)")
    p("=" * 50)
    status, sos2 = call("POST", "/sos", {"source": "sos_button", "force": False}, token=token)
    assert status in (200, 201), f"Unexpected status: {status}"
    assert sos2["created"] is False, "TEST 2 FAILED: expected duplicate suppression"
    assert sos2["emergency_event"]["id"] == event1_id
    assert sos2["notifications_created"] == 0
    p(f"Duplicate suppressed! Reused Event ID: {sos2['emergency_event']['id']}")
    p(">>> TEST 2 PASS")

    p("\n" + "=" * 50)
    p("TEST 3: Deliberate 'Send another alert' (force=True)")
    p("=" * 50)
    status, sos3 = call("POST", "/sos", {"source": "sos_button", "force": True}, token=token)
    assert status in (200, 201), f"Unexpected status: {status}"
    assert sos3["created"] is True
    assert sos3.get("is_resend") is True
    event2_id = sos3["emergency_event"]["id"]
    p(f"Event 2 ID: {event2_id}")
    assert event2_id != event1_id
    assert sos3["caregivers_targeted"] == 2
    assert sos3["notifications_created"] == 2
    assert len(sos3["delivery"]) == 2

    # Check both Event 1 and Event 2 exist in DB
    status, events = call("GET", "/sos", token=token)
    ids = [e["id"] for e in events]
    assert event1_id in ids and event2_id in ids
    p("Verified: Event 1 and Event 2 coexist in database without overwrite.")
    p(">>> TEST 3 PASS")

    p("\n" + "=" * 50)
    p("TEST 4: Resolve open event, then trigger SOS (force=False)")
    p("=" * 50)
    call("POST", f"/sos/{event1_id}/resolve", {"resolution_note": "Resolved 1"}, token=token)
    call("POST", f"/sos/{event2_id}/resolve", {"resolution_note": "Resolved 2"}, token=token)

    status, sos4 = call("POST", "/sos", {"source": "sos_button", "force": False}, token=token)
    assert status in (200, 201)
    assert sos4["created"] is True
    event4_id = sos4["emergency_event"]["id"]
    assert event4_id not in (event1_id, event2_id)
    assert sos4["caregivers_targeted"] == 2
    assert sos4["notifications_created"] == 2
    p(f"New Event 4 ID: {event4_id} created after resolution.")
    p(">>> TEST 4 PASS")

    p("\n" + "=" * 50)
    p("VERIFY NOTIFICATIONS AUDIT TRAIL")
    p("=" * 50)
    status, notifs = call("GET", "/notifications", token=token)
    assert status == 200 and isinstance(notifs, list)
    sos_notifs = [n for n in notifs if n.get("category") == "sos"]
    p(f"Total emergency notifications found in history: {len(sos_notifs)}")
    assert any(n.get("emergency_event_id") == event4_id for n in sos_notifs)
    p("Verified: Notifications linked to emergency events in DB.")
    p(">>> NOTIFICATIONS PASS")

    p("\n" + "=" * 50)
    p("ALL 4 LIVE E2E TESTS PASSED SUCCESSFULLY!")
    p("=" * 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
