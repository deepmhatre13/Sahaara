"""Idempotent development seed for the SOS caregiver contacts.

Running this repeatedly must be safe: it upserts by (elder, phone number) so a
second run updates the existing rows instead of creating duplicates.

Usage (from ``backend/``):

    venv\\Scripts\\python.exe scripts\\seed_caregivers.py
    venv\\Scripts\\python.exe scripts\\seed_caregivers.py --email other@example.com

The numbers live here rather than in the frontend because the database is the
single source of truth for who receives an SOS.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.phone import mask_phone, normalize_phone  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
# Import the package so every mapped class is registered before mappers
# configure (the models use string-based relationships).
from app.models import Caregiver, User  # noqa: E402

DEFAULT_ELDER_EMAIL = "mhatredeepam@gmail.com"

# The two intended emergency contacts. Stored in E.164.
SEED_CAREGIVERS = [
    {
        "full_name": "Caregiver One",
        "relationship_to_elder": "Primary Contact",
        "phone_number": "+919892031558",
        "whatsapp_number": "+919892031558",
        "is_primary": True,
        "whatsapp_enabled": True,
    },
    {
        "full_name": "Caregiver Two",
        "relationship_to_elder": "Family Contact",
        "phone_number": "+918652721553",
        "whatsapp_number": "+918652721553",
        "is_primary": False,
        "whatsapp_enabled": True,
    },
]


def seed(elder_email: str) -> int:
    db = SessionLocal()
    created = 0
    updated = 0
    try:
        elder = db.query(User).filter(User.email == elder_email).first()
        if elder is None:
            print(f"ERROR: no user with email {elder_email!r}. Create the account first.")
            return 1

        print(f"Seeding caregivers for {elder.full_name} <{elder.email}> ({elder.id})")

        for spec in SEED_CAREGIVERS:
            phone = normalize_phone(spec["phone_number"])

            # Match on either number so re-running cannot duplicate a contact
            # that was previously stored under the other column.
            existing = (
                db.query(Caregiver)
                .filter(
                    Caregiver.elder_id == elder.id,
                    (Caregiver.phone_number == phone) | (Caregiver.whatsapp_number == phone),
                )
                .first()
            )

            if existing is None:
                db.add(
                    Caregiver(
                        elder_id=elder.id,
                        full_name=spec["full_name"],
                        relationship_to_elder=spec["relationship_to_elder"],
                        phone_number=phone,
                        whatsapp_number=spec["whatsapp_number"],
                        is_primary=spec["is_primary"],
                        is_active=True,
                        whatsapp_enabled=spec["whatsapp_enabled"],
                    )
                )
                created += 1
                print(f"  + created  {spec['full_name']:<16} {mask_phone(phone)}")
            else:
                existing.full_name = spec["full_name"]
                existing.relationship_to_elder = spec["relationship_to_elder"]
                existing.phone_number = phone
                existing.whatsapp_number = spec["whatsapp_number"]
                existing.is_active = True
                existing.whatsapp_enabled = spec["whatsapp_enabled"]
                updated += 1
                print(f"  ~ updated  {spec['full_name']:<16} {mask_phone(phone)}")

        # Exactly one primary per elder, enforced after all rows are staged.
        db.flush()
        primaries = (
            db.query(Caregiver)
            .filter(Caregiver.elder_id == elder.id, Caregiver.is_active.is_(True))
            .order_by(Caregiver.created_at.asc())
            .all()
        )
        if primaries and not any(c.is_primary for c in primaries):
            primaries[0].is_primary = True

        db.commit()

        active = (
            db.query(Caregiver)
            .filter(Caregiver.elder_id == elder.id, Caregiver.is_active.is_(True))
            .all()
        )
        print(f"\nDone. created={created} updated={updated} active_caregivers={len(active)}")
        for c in active:
            dest = c.whatsapp_destination
            print(
                f"  - {c.full_name:<16} {mask_phone(dest)} "
                f"primary={c.is_primary} whatsapp_enabled={c.whatsapp_enabled}"
            )
        return 0
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed SOS caregiver contacts (idempotent).")
    parser.add_argument(
        "--email",
        default=DEFAULT_ELDER_EMAIL,
        help=f"Elder account email to attach caregivers to (default: {DEFAULT_ELDER_EMAIL})",
    )
    args = parser.parse_args()
    return seed(args.email)


if __name__ == "__main__":
    raise SystemExit(main())
