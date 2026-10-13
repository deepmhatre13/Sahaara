"""Phone-number normalisation to E.164.

Twilio (and every serious SMS/WhatsApp gateway) requires E.164:
    +[country code][national number]   e.g. +919892031558

Caregiver numbers are personal data and are typed by humans in many shapes
("9892031558", "+91 98920 31558", "098920 31558", "0091-98920-31558"), so we
normalise once at the API boundary and store only the canonical form.

The default region is India (this deployment's user base), but the function is
region-parameterised rather than India-only, so a future deployment can pass a
different ``default_country_code`` without touching callers.
"""

from __future__ import annotations

import re

# E.164 allows up to 15 digits total, including the country code.
E164_MAX_DIGITS = 15
E164_MIN_DIGITS = 8

# Region hint -> international dialling prefix. Deliberately tiny: this maps the
# *default region* a bare national number should be interpreted in.
_REGION_CALLING_CODES: dict[str, str] = {
    "IN": "91",
    "US": "1",
    "CA": "1",
    "GB": "44",
    "AU": "61",
    "AE": "971",
    "SG": "65",
}

DEFAULT_REGION = "IN"

_DIGITS_ONLY = re.compile(r"\D")


class PhoneNumberError(ValueError):
    """Raised when a value cannot be converted into a valid E.164 number."""


def normalize_phone(raw: str | None, *, default_region: str = DEFAULT_REGION) -> str:
    """Return ``raw`` as an E.164 string, or raise :class:`PhoneNumberError`.

    Accepted inputs (region ``IN``, calling code ``91``):
        +919892031558      -> +919892031558
        +91 98920 31558    -> +919892031558
        9892031558         -> +919892031558   (bare national number)
        09892031558        -> +919892031558   (national trunk prefix "0")
        0091-98920-31558   -> +919892031558   (international "00" prefix)

    A value that already starts with ``+`` is treated as authoritative and only
    validated, never re-prefixed — this keeps the function safe for numbers from
    a region other than ``default_region``.
    """
    if raw is None:
        raise PhoneNumberError("Phone number is required")

    candidate = str(raw).strip()
    if not candidate:
        raise PhoneNumberError("Phone number is required")

    # Reject anything with letters — catches pasted emails/names.
    if re.search(r"[A-Za-z]", candidate):
        raise PhoneNumberError("Phone number must contain digits only")

    had_plus = candidate.startswith("+")
    digits = _DIGITS_ONLY.sub("", candidate)

    if not digits:
        raise PhoneNumberError("Phone number must contain digits")

    if had_plus:
        # Already international; keep the country code exactly as supplied.
        normalized = f"+{digits}"
    elif digits.startswith("00"):
        # International "00" escape prefix.
        normalized = f"+{digits[2:]}"
    else:
        calling_code = _REGION_CALLING_CODES.get(default_region.upper())
        if not calling_code:
            raise PhoneNumberError(f"Unsupported default region: {default_region}")

        if digits.startswith(calling_code) and len(digits) > len(calling_code) + 4:
            # Caller already typed the country code without a "+" (e.g. 919892031558).
            normalized = f"+{digits}"
        else:
            # Bare national number, optionally with the trunk prefix "0".
            national = digits[1:] if digits.startswith("0") else digits
            normalized = f"+{calling_code}{national}"

    _validate_e164(normalized)
    return normalized


def _validate_e164(value: str) -> None:
    if not value.startswith("+"):
        raise PhoneNumberError("E.164 numbers must start with '+'")

    digits = value[1:]
    if not digits.isdigit():
        raise PhoneNumberError("E.164 numbers must contain digits only after '+'")

    if not (E164_MIN_DIGITS <= len(digits) <= E164_MAX_DIGITS):
        raise PhoneNumberError(
            f"Phone number must contain between {E164_MIN_DIGITS} and "
            f"{E164_MAX_DIGITS} digits, got {len(digits)}"
        )

    if digits.startswith("0"):
        # A country code never starts with 0 in E.164.
        raise PhoneNumberError("Invalid country code in phone number")


def try_normalize_phone(raw: str | None, *, default_region: str = DEFAULT_REGION) -> str | None:
    """Best-effort variant used when reading legacy rows.

    Returns ``None`` instead of raising so a single malformed historical record
    cannot break an entire caregiver listing.
    """
    try:
        return normalize_phone(raw, default_region=default_region)
    except PhoneNumberError:
        return None


def mask_phone(value: str | None) -> str:
    """Mask a phone number for logs: ``+919892031558`` -> ``+9198****1558``.

    Caregiver numbers are personal data, so logs must never carry them in full.
    """
    if not value:
        return "<none>"
    if len(value) <= 6:
        return "*" * len(value)
    return f"{value[:5]}{'*' * (len(value) - 9)}{value[-4:]}"
