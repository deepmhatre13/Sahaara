"""Caregiver CRUD, E.164 normalisation and per-user isolation."""

from __future__ import annotations

import pytest

from app.core.phone import PhoneNumberError, normalize_phone
from app.models.caregiver import Caregiver
from app.schemas.caregiver import CaregiverCreate, CaregiverUpdate
from app.services import caregiver_service
from app.services.caregiver_service import CaregiverError


# --- phone normalisation -----------------------------------------------------

@pytest.mark.parametrize(
    "raw,expected",
    [
        ("+919892031558", "+919892031558"),
        ("+91 98920 31558", "+919892031558"),
        ("9892031558", "+919892031558"),
        ("09892031558", "+919892031558"),
        ("0091-98920-31558", "+919892031558"),
        ("919892031558", "+919892031558"),
        ("+918652721553", "+918652721553"),
        ("8652721553", "+918652721553"),
        # A number from another region must survive untouched.
        ("+14155552671", "+14155552671"),
    ],
)
def test_normalize_phone(raw, expected):
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", None, "abc", "+", "12", "1234567890123456789"])
def test_normalize_phone_rejects_invalid(raw):
    with pytest.raises(PhoneNumberError):
        normalize_phone(raw)


# --- listing -----------------------------------------------------------------

def test_list_caregivers_is_scoped_to_the_elder(db_session, elder, other_elder):
    caregiver_service.create_caregiver(
        db_session, elder.id, CaregiverCreate(full_name="Mine", phone_number="9892031558")
    )
    caregiver_service.create_caregiver(
        db_session, other_elder.id, CaregiverCreate(full_name="Theirs", phone_number="8652721553")
    )

    mine = caregiver_service.list_caregivers(db_session, elder.id)
    assert [c.full_name for c in mine] == ["Mine"]


def test_get_caregiver_refuses_another_users_record(db_session, elder, other_elder):
    theirs = caregiver_service.create_caregiver(
        db_session, other_elder.id, CaregiverCreate(full_name="Theirs", phone_number="8652721553")
    )
    assert caregiver_service.get_caregiver(db_session, elder.id, theirs.id) is None


# --- creation ----------------------------------------------------------------

def test_create_caregiver_normalizes_to_e164(db_session, elder):
    caregiver = caregiver_service.create_caregiver(
        db_session,
        elder.id,
        CaregiverCreate(
            full_name="Priya Sharma",
            phone_number="98765 43210",
            relationship_to_elder="Daughter",
        ),
    )
    assert caregiver.phone_number == "+919876543210"
    assert caregiver.is_active is True
    assert caregiver.whatsapp_enabled is True


def test_create_caregiver_requires_a_number(db_session, elder):
    with pytest.raises(CaregiverError):
        caregiver_service.create_caregiver(
            db_session, elder.id, CaregiverCreate(full_name="No Number")
        )


def test_create_caregiver_rejects_bad_number(db_session, elder):
    with pytest.raises(CaregiverError):
        caregiver_service.create_caregiver(
            db_session, elder.id, CaregiverCreate(full_name="Bad", phone_number="nonsense")
        )


def test_only_one_primary_caregiver_per_elder(db_session, elder):
    first = caregiver_service.create_caregiver(
        db_session,
        elder.id,
        CaregiverCreate(full_name="First", phone_number="9892031558", is_primary=True),
    )
    second = caregiver_service.create_caregiver(
        db_session,
        elder.id,
        CaregiverCreate(full_name="Second", phone_number="8652721553", is_primary=True),
    )

    db_session.refresh(first)
    assert first.is_primary is False
    assert second.is_primary is True
    assert db_session.query(Caregiver).filter(Caregiver.is_primary.is_(True)).count() == 1


# --- recipients (SOS eligibility) --------------------------------------------

def test_sos_recipients_exclude_inactive_and_whatsapp_disabled(db_session, elder):
    caregiver_service.create_caregiver(
        db_session, elder.id, CaregiverCreate(full_name="Active", phone_number="9892031558")
    )
    inactive = caregiver_service.create_caregiver(
        db_session, elder.id, CaregiverCreate(full_name="Inactive", phone_number="+919000000001")
    )
    no_whatsapp = caregiver_service.create_caregiver(
        db_session, elder.id, CaregiverCreate(full_name="NoWA", phone_number="+919000000002")
    )
    caregiver_service.deactivate_caregiver(db_session, elder.id, inactive.id)
    caregiver_service.update_caregiver(
        db_session, elder.id, no_whatsapp.id, CaregiverUpdate(whatsapp_enabled=False)
    )

    recipients = caregiver_service.list_sos_recipients(db_session, elder.id)
    assert [c.full_name for c in recipients] == ["Active"]


def test_whatsapp_number_takes_precedence_over_phone(db_session, elder):
    caregiver = caregiver_service.create_caregiver(
        db_session,
        elder.id,
        CaregiverCreate(
            full_name="Both",
            phone_number="9892031558",
            whatsapp_number="+919999888877",
        ),
    )
    assert caregiver.whatsapp_destination == "+919999888877"


def test_whatsapp_destination_falls_back_to_phone(db_session, elder):
    caregiver = caregiver_service.create_caregiver(
        db_session, elder.id, CaregiverCreate(full_name="PhoneOnly", phone_number="9892031558")
    )
    assert caregiver.whatsapp_destination == "+919892031558"


# --- update / deactivate -----------------------------------------------------

def test_update_caregiver_only_touches_supplied_fields(db_session, elder):
    caregiver = caregiver_service.create_caregiver(
        db_session,
        elder.id,
        CaregiverCreate(full_name="Original", phone_number="9892031558", relationship_to_elder="Son"),
    )
    updated = caregiver_service.update_caregiver(
        db_session, elder.id, caregiver.id, CaregiverUpdate(relationship_to_elder="Daughter")
    )
    assert updated.full_name == "Original"
    assert updated.phone_number == "+919892031558"
    assert updated.relationship_to_elder == "Daughter"


def test_deactivate_is_a_soft_delete(db_session, elder):
    caregiver = caregiver_service.create_caregiver(
        db_session,
        elder.id,
        CaregiverCreate(full_name="Temp", phone_number="9892031558", is_primary=True),
    )
    result = caregiver_service.deactivate_caregiver(db_session, elder.id, caregiver.id)
    assert result.is_active is False
    assert result.is_primary is False
    # The row survives, so notification history stays attributable.
    assert db_session.query(Caregiver).filter(Caregiver.id == caregiver.id).first() is not None
    assert caregiver_service.list_caregivers(db_session, elder.id) == []


def test_update_refuses_another_users_caregiver(db_session, elder, other_elder):
    theirs = caregiver_service.create_caregiver(
        db_session, other_elder.id, CaregiverCreate(full_name="Theirs", phone_number="8652721553")
    )
    assert (
        caregiver_service.update_caregiver(
            db_session, elder.id, theirs.id, CaregiverUpdate(full_name="Hacked")
        )
        is None
    )
    db_session.refresh(theirs)
    assert theirs.full_name == "Theirs"


def test_deactivate_refuses_another_users_caregiver(db_session, elder, other_elder):
    theirs = caregiver_service.create_caregiver(
        db_session, other_elder.id, CaregiverCreate(full_name="Theirs", phone_number="8652721553")
    )
    assert caregiver_service.deactivate_caregiver(db_session, elder.id, theirs.id) is None
    db_session.refresh(theirs)
    assert theirs.is_active is True
