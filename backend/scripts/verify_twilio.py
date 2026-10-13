"""Verify Twilio WhatsApp readiness without sending repeated real messages.

Reads the configured account and reports:

* which sender number is configured (sandbox vs. a WhatsApp Sender),
* whether the number is the Twilio WhatsApp Sandbox number,
* whether the account is a trial account,

and optionally performs ONE live send when explicitly requested with ``--send``.

Default behaviour is read-only so this can be run casually during development
without spraying real WhatsApp messages at caregivers.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.core.phone import mask_phone  # noqa: E402

# Twilio's shared WhatsApp Sandbox sender. If TWILIO_WHATSAPP_FROM points here,
# free-form messages work (once the recipient has joined the sandbox).
SANDBOX_FROM = "whatsapp:+14155238886"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Twilio WhatsApp configuration.")
    parser.add_argument(
        "--send",
        metavar="E164",
        help="Send ONE real test message to this number (e.g. +919892031558).",
    )
    args = parser.parse_args()

    settings = get_settings()
    provider = settings.notification_provider
    sender = settings.twilio_whatsapp_from or "<unset>"

    print("NOTIFICATION PROVIDER:", provider)
    print("TWILIO_WHATSAPP_FROM:", sender)
    print("  is sandbox sender :", sender == SANDBOX_FROM)
    print("TWILIO_WHATSAPP_TO  :", mask_phone(settings.twilio_whatsapp_to))
    print("ACCOUNT SID set     :", bool(settings.twilio_account_sid))
    print("AUTH TOKEN set      :", bool(settings.twilio_auth_token))
    print("SEND enabled        :", bool(settings.twilio_account_sid and settings.twilio_auth_token))

    if provider != "twilio":
        print("\nNOTE: provider is not 'twilio'. The dev console provider logs instead of sending.")
        print("      Set NOTIFICATION_PROVIDER=twilio in backend/.env to send for real.")

    if sender != SANDBOX_FROM:
        print(
            "\nNOTE: the configured sender is not the Twilio WhatsApp Sandbox number."
            "\n      A WhatsApp Sender that requires approved templates will reject"
            "\n      free-form 'Body' text with error 21654 (ContentSid Required)."
        )

    if not args.send:
        print("\n(read-only check complete; pass --send +91XXXXXXXXXX to attempt one live send)")
        return 0

    # Fetch account flags first — this is a read-only API call.
    try:
        from twilio.rest import Client
    except ImportError:
        print("\nERROR: the 'twilio' package is not installed in this environment.")
        return 1

    if not (settings.twilio_account_sid and settings.twilio_auth_token):
        print("\nERROR: Twilio credentials are not configured.")
        return 1

    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    try:
        account = client.api.accounts(settings.twilio_account_sid).fetch()
        print("\nACCOUNT TYPE:", "TRIAL" if account.type == "Trial" else account.type)
        print("ACCOUNT STATUS:", account.status)
    except Exception as exc:  # noqa: BLE001
        print(f"\nWARNING: could not read account info: {str(exc)[:200]}")

    # Report the numbers provisioned on this account, so it is obvious whether
    # the configured sender is a real WhatsApp number or the sandbox.
    try:
        numbers = client.incoming_phone_numbers.list(limit=20)
        print("\nINCOMING NUMBERS ON ACCOUNT:")
        if not numbers:
            print("  (none)")
        for n in numbers:
            caps = []
            if getattr(n, "capabilities", None):
                caps = [k for k, v in n.capabilities.items() if v]
            print(f"  - {n.phone_number}  caps={','.join(caps) or 'n/a'}")
    except Exception as exc:  # noqa: BLE001
        print(f"\nWARNING: could not list numbers: {str(exc)[:200]}")

    print(f"\nSending ONE test message to {mask_phone(args.send)} ...")
    from app.notifications.twilio_provider import TwilioNotificationProvider

    result = TwilioNotificationProvider().send(
        to=args.send,
        title="SAHAARA TEST",
        body="Test message from the Sahaara verification script. No action required.",
    )

    print("  ok:", result.ok)
    print("  status:", result.status)
    print("  provider_message_id:", result.provider_message_id)
    print("  error_code:", result.error_code)
    print("  error_message:", (result.error_message or "")[:300])
    return 0 if result.ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
