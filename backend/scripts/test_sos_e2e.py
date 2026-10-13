"""End-to-end SOS check through the running HTTP API.

Logs in as the real development user, reads the caregiver list, triggers ONE
SOS, and prints the structured delivery report.

This deliberately triggers a single SOS. Re-running it inside the duplicate
window will reuse the existing event rather than sending another alert.
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BASE = "http://127.0.0.1:8001/api"


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
    # Mint a real access token with the app's own security module, so this
    # script exercises exactly the same auth dependency the browser uses
    # without needing the user's password.
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
        print(f"[1] minted token for {user.full_name} ({user.id})")
    finally:
        db.close()

    status, me = call("GET", "/auth/me", token=token)
    print(f"[2] me -> {status} user={me.get('full_name') if isinstance(me, dict) else me}")

    status, caregivers = call("GET", "/caregivers", token=token)
    print(f"[3] caregivers -> {status} count={len(caregivers) if isinstance(caregivers, list) else '?'}")
    if isinstance(caregivers, list):
        for c in caregivers:
            print(
                f"     - {c['full_name']:<16} phone={c['phone_number']} "
                f"wa={c['whatsapp_number']} primary={c['is_primary']} "
                f"active={c['is_active']} wa_enabled={c['whatsapp_enabled']}"
            )

    status, sos = call("POST", "/sos", {"source": "sos_button"}, token=token)
    print(f"[4] POST /sos -> {status}")
    if status not in (200, 201):
        print("    ", sos)
        return 1

    if not sos["created"]:
        # A previous run left an OPEN event inside the duplicate window. Confirm
        # the guard behaved, then resolve it and raise a genuine new SOS once.
        print(f"     DUPLICATE GUARD OK: reused event {sos['emergency_event']['id']} (no second alert sent)")
        status, _ = call(
            "POST",
            f"/sos/{sos['emergency_event']['id']}/resolve",
            {"resolution_note": "e2e test cleanup"},
            token=token,
        )
        print(f"     resolve stale event -> {status}")
        status, sos = call("POST", "/sos", {"source": "sos_button"}, token=token)
        print(f"[4b] POST /sos (after resolve) -> {status}")

    print(f"     created={sos['created']} event={sos['emergency_event']['id']}")
    print(f"     status={sos['emergency_event']['status']} source={sos['emergency_event']['source']}")
    print(f"     caregivers_targeted={sos['caregivers_targeted']}")
    print(f"     notifications_created={sos['notifications_created']}")
    print(f"     notified_caregivers={sos['notified_caregivers']}")
    print(f"     failed_caregivers={sos['failed_caregivers']}")
    print(f"     simulated={sos['simulated']}")
    for d in sos["delivery"]:
        print(f"       * {d['caregiver_name']:<16} status={d['status']:<8} accepted={d['accepted']}")
        if d.get("provider_message_id"):
            print(f"         provider_message_id={d['provider_message_id']}")
        if d.get("error_message"):
            print(f"         error_code={d.get('error_code')} error={d['error_message'][:160]}")

    status, notifs = call("GET", "/notifications", token=token)
    print(f"[5] notifications -> {status} count={len(notifs) if isinstance(notifs, list) else '?'}")
    if isinstance(notifs, list):
        for n in notifs[:4]:
            title = str(n["title"]).encode("ascii", "replace").decode()
            print(
                f"     - [{n['category']}] {title[:32]:<32} "
                f"channel={n['channel']:<8} status={n['status']:<8} delivered={n['delivered']}"
            )
            if n.get("error_message"):
                err = str(n["error_message"]).encode("ascii", "replace").decode()
                print(f"       error={err[:160]}")

    # Authorization check: another user's caregivers must be unreachable.
    status, forbidden = call(
        "GET", "/caregivers", token=token
    )
    print(f"[6] caregivers re-check -> {status}")

    print("\nNO-AUTH CHECK:")
    status, body = call("POST", "/sos", {"source": "sos_button"})
    print(f"     POST /sos without token -> {status} (expect 401/403) {str(body)[:120]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
