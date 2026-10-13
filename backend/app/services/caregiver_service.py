"""Caregiver CRUD, always scoped to one elder.

Every read/write here filters on ``elder_id``. There is deliberately no
"fetch caregiver by id only" helper: an id-only lookup is exactly how one user
ends up able to read or edit another user's emergency contacts.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.phone import PhoneNumberError, normalize_phone
from app.models.caregiver import Caregiver
from app.schemas.caregiver import CaregiverCreate, CaregiverUpdate


class CaregiverError(ValueError):
    """Validation failure that the API layer turns into a 422/409."""


def _normalize_optional_phone(value: str | None, field: str) -> str | None:
    if value is None:
        return None
    if not str(value).strip():
        return None
    try:
        return normalize_phone(value)
    except PhoneNumberError as exc:
        raise CaregiverError(f"Invalid {field}: {exc}") from exc


def list_caregivers(db: Session, elder_id: uuid.UUID, *, active_only: bool = True) -> list[Caregiver]:
    """Caregivers belonging to ``elder_id``.

    Defaults to active-only, matching the API's ``include_inactive=False``
    default: a deactivated contact must not reappear in the normal listing.
    """
    query = db.query(Caregiver).filter(Caregiver.elder_id == elder_id)
    if active_only:
        query = query.filter(Caregiver.is_active.is_(True))
    return query.order_by(Caregiver.is_primary.desc(), Caregiver.created_at.asc()).all()


def get_caregiver(db: Session, elder_id: uuid.UUID, caregiver_id: uuid.UUID) -> Caregiver | None:
    """Fetch one caregiver, but only if it belongs to ``elder_id``."""
    return (
        db.query(Caregiver)
        .filter(Caregiver.id == caregiver_id, Caregiver.elder_id == elder_id)
        .first()
    )


def list_sos_recipients(db: Session, elder_id: uuid.UUID) -> list[Caregiver]:
    """Active caregivers reachable over WhatsApp — the SOS fan-out list.

    Ordered primary-first so the most important contact is attempted first; a
    failure on that one must not stop the others.
    """
    return [
        c
        for c in list_caregivers(db, elder_id, active_only=True)
        if c.is_whatsapp_reachable
    ]


def _clear_other_primaries(db: Session, elder_id: uuid.UUID, keep_id: uuid.UUID | None) -> None:
    """Enforce a single primary caregiver per elder.

    Not a DB constraint because a partial unique index would need a migration
    branch per backend; doing it here keeps the invariant where it is used.
    """
    query = db.query(Caregiver).filter(
        Caregiver.elder_id == elder_id,
        Caregiver.is_primary.is_(True),
    )
    if keep_id is not None:
        query = query.filter(Caregiver.id != keep_id)
    for other in query.all():
        other.is_primary = False


def create_caregiver(db: Session, elder_id: uuid.UUID, payload: CaregiverCreate) -> Caregiver:
    phone = _normalize_optional_phone(payload.phone_number, "phone_number")
    whatsapp = _normalize_optional_phone(payload.whatsapp_number, "whatsapp_number")

    if phone is None and whatsapp is None:
        raise CaregiverError("At least one of phone_number or whatsapp_number is required")

    caregiver = Caregiver(
        elder_id=elder_id,
        full_name=payload.full_name.strip(),
        relationship_to_elder=(payload.relationship_to_elder or None),
        phone_number=phone,
        whatsapp_number=whatsapp,
        email=(payload.email or None),
        is_primary=payload.is_primary,
        is_active=payload.is_active,
        whatsapp_enabled=payload.whatsapp_enabled,
    )
    db.add(caregiver)
    db.flush()  # assign caregiver.id before clearing siblings

    if caregiver.is_primary:
        _clear_other_primaries(db, elder_id, keep_id=caregiver.id)

    db.commit()
    db.refresh(caregiver)
    return caregiver


def update_caregiver(
    db: Session,
    elder_id: uuid.UUID,
    caregiver_id: uuid.UUID,
    payload: CaregiverUpdate,
) -> Caregiver | None:
    caregiver = get_caregiver(db, elder_id, caregiver_id)
    if caregiver is None:
        return None

    data = payload.model_dump(exclude_unset=True)

    if "full_name" in data and data["full_name"]:
        caregiver.full_name = data["full_name"].strip()
    if "relationship_to_elder" in data:
        caregiver.relationship_to_elder = data["relationship_to_elder"] or None
    if "phone_number" in data:
        caregiver.phone_number = _normalize_optional_phone(data["phone_number"], "phone_number")
    if "whatsapp_number" in data:
        caregiver.whatsapp_number = _normalize_optional_phone(data["whatsapp_number"], "whatsapp_number")
    if "email" in data:
        caregiver.email = data["email"] or None
    if "is_active" in data:
        caregiver.is_active = bool(data["is_active"])
    if "whatsapp_enabled" in data:
        caregiver.whatsapp_enabled = bool(data["whatsapp_enabled"])
    if "is_primary" in data:
        caregiver.is_primary = bool(data["is_primary"])

    if caregiver.phone_number is None and caregiver.whatsapp_number is None:
        raise CaregiverError("At least one of phone_number or whatsapp_number is required")

    if caregiver.is_primary:
        _clear_other_primaries(db, elder_id, keep_id=caregiver.id)

    db.commit()
    db.refresh(caregiver)
    return caregiver


def deactivate_caregiver(db: Session, elder_id: uuid.UUID, caregiver_id: uuid.UUID) -> Caregiver | None:
    """Soft-delete.

    Deleting outright would orphan notification history, so the record is kept
    and simply excluded from future SOS fan-out.
    """
    caregiver = get_caregiver(db, elder_id, caregiver_id)
    if caregiver is None:
        return None
    caregiver.is_active = False
    caregiver.is_primary = False
    db.commit()
    db.refresh(caregiver)
    return caregiver
