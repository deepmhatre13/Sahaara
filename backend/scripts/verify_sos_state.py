"""End-to-end verification of the SOS fan-out against PostgreSQL.

Reads back exactly what the last SOS produced: the single emergency event, the
per-caregiver notification attempts, and whether each was accepted. Read-only.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text

from app.database.session import engine

with engine.connect() as c:
    print("=== CAREGIVERS ===")
    for row in c.execute(
        text(
            "select full_name, phone_number, whatsapp_number, is_primary, is_active, whatsapp_enabled "
            "from caregivers order by is_primary desc"
        )
    ):
        print("  ", row)
    print("count:", c.execute(text("select count(*) from caregivers")).scalar())

    print("\n=== LATEST EMERGENCY EVENT ===")
    for row in c.execute(
        text(
            "select id, source, status, resolved, created_at from emergency_events "
            "order by created_at desc limit 3"
        )
    ):
        print("  ", row)
    print("total events:", c.execute(text("select count(*) from emergency_events")).scalar())

    print("\n=== NOTIFICATION ATTEMPTS FOR LATEST EVENT ===")
    latest = c.execute(
        text("select id from emergency_events order by created_at desc limit 1")
    ).scalar()
    rows = c.execute(
        text(
            "select n.category, n.channel, n.status, n.delivered, "
            "       n.provider_message_id, left(coalesce(n.error_message,''), 90) as err, "
            "       c.full_name, n.emergency_event_id "
            "from notifications n left join caregivers c on c.id = n.caregiver_id "
            "where n.emergency_event_id = :eid order by c.full_name"
        ),
        {"eid": latest},
    ).all()
    print("linked to event", latest, "->", len(rows), "attempt(s)")
    for row in rows:
        print("  ", row)

    print("\n=== ONE EVENT -> N ATTEMPTS INVARIANT ===")
    grouped = c.execute(
        text(
            "select emergency_event_id, count(*) as attempts from notifications "
            "where emergency_event_id is not null group by emergency_event_id "
            "order by attempts desc"
        )
    ).all()
    for row in grouped:
        print("  event", row[0], "->", row[1], "attempt(s)")
