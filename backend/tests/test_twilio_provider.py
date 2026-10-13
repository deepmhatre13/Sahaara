"""Unit tests for the Twilio WhatsApp notification provider.

Every test injects a fake Twilio client, so no real WhatsApp message is ever
sent. The suite covers the Content Template (``content_sid``) contract that
Twilio enforces for WhatsApp sends, including the 21654 / 21655 error mapping,
and asserts that ``content_variables`` is never sent for this Trial template.
"""

from __future__ import annotations

from types import SimpleNamespace

from app.core.config import Settings
from app.notifications.base import STATUS_FAILED, STATUS_QUEUED, STATUS_SENT
from app.notifications.twilio_provider import TwilioNotificationProvider


CONTENT_SID = "HX00000000000000000000000000000000"


class FakeTwilioError(Exception):
    """Mimics ``twilio.base.exceptions.TwilioRestException``'s useful fields."""

    def __init__(self, status: int, code: int | None, msg: str):
        super().__init__(msg)
        self.status = status
        self.code = code


class FakeMessages:
    """Records ``create`` calls and returns a scripted outcome."""

    def __init__(self, outcome=None, error: Exception | None = None):
        self.calls: list[dict] = []
        self._outcome = outcome
        self._error = error

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        return self._outcome


def _provider(
    content_sid: str | None = CONTENT_SID, messages: FakeMessages | None = None
) -> TwilioNotificationProvider:
    provider = TwilioNotificationProvider()
    # Override settings without touching the real .env / cached Settings.
    provider._settings = SimpleNamespace(
        twilio_account_sid="AC_test",
        twilio_auth_token="token_test",
        twilio_whatsapp_from="whatsapp:+15005550006",
        twilio_whatsapp_to="whatsapp:+919892031558",
        twilio_whatsapp_content_sid=content_sid,
    )
    provider._client = SimpleNamespace(messages=messages or FakeMessages())
    return provider


def _queued_message(sid: str = "SM_queued_1"):
    return SimpleNamespace(sid=sid, status="queued", error_code=None, error_message=None)


def test_settings_load_twilio_credentials_and_initialize_client(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            (
                "NOTIFICATION_PROVIDER=twilio",
                "TWILIO_ACCOUNT_SID=AC_test_settings",
                "TWILIO_AUTH_TOKEN=test_auth_token",
                "TWILIO_WHATSAPP_FROM=whatsapp:+15005550006",
                "TWILIO_WHATSAPP_CONTENT_SID=HX00000000000000000000000000000000",
            )
        ),
        encoding="utf-8",
    )
    for name in (
        "NOTIFICATION_PROVIDER",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_FROM",
        "TWILIO_WHATSAPP_CONTENT_SID",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings(_env_file=env_file)
    assert settings.twilio_account_sid == "AC_test_settings"
    assert settings.twilio_auth_token == "test_auth_token"
    assert settings.twilio_whatsapp_from == "whatsapp:+15005550006"
    assert settings.twilio_whatsapp_content_sid == "HX00000000000000000000000000000000"

    client = object()
    client_arguments = []

    def create_client(account_sid, auth_token):
        client_arguments.append((account_sid, auth_token))
        return client

    monkeypatch.setattr("twilio.rest.Client", create_client)
    provider = TwilioNotificationProvider(settings=settings)

    assert provider._settings is settings
    assert provider._get_client() is client
    assert client_arguments == [("AC_test_settings", "test_auth_token")]

    monkeypatch.setattr("app.notifications.factory.get_settings", lambda: settings)
    from app.notifications.factory import get_notification_provider

    factory_provider = get_notification_provider()
    assert isinstance(factory_provider, TwilioNotificationProvider)
    assert factory_provider._settings is settings


# --- content_sid present -----------------------------------------------------

def test_sends_content_sid_and_from_without_legacy_body():
    messages = FakeMessages(outcome=_queued_message())
    provider = _provider(messages=messages)

    result = provider.send(to="9892031558", title="SAHAARA EMERGENCY ALERT", body="An SOS was triggered.")

    assert result.ok is True
    assert result.status == STATUS_QUEUED
    assert result.provider_message_id == "SM_queued_1"

    call = messages.calls[0]
    assert call["content_sid"] == CONTENT_SID
    # No legacy free-form body: WhatsApp template sends must not carry one.
    assert "body" not in call
    assert call["from_"] == "whatsapp:+15005550006"


def test_content_variables_is_never_sent_for_trial_template():
    messages = FakeMessages(outcome=_queued_message())
    provider = _provider(messages=messages)

    provider.send(to="+919892031558", title="t", body="b")

    call = messages.calls[0]
    assert "content_variables" not in call
    assert "ContentVariables" not in call
    assert "contentvariables" not in {k.lower() for k in call}


# --- error mapping -----------------------------------------------------------

def test_21654_exception_is_mapped_to_friendly_message():
    error = FakeTwilioError(status=400, code=21654, msg="Unable to create record: ContentSid Required")
    messages = FakeMessages(error=error)
    provider = _provider(messages=messages)

    result = provider.send(to="+919892031558", title="t", body="b")

    assert result.ok is False
    assert result.status == STATUS_FAILED
    assert result.error_code == "21654"
    assert "ContentSid Required" in (result.error_message or "")
    assert "TWILIO_WHATSAPP_CONTENT_SID" in (result.error_message or "")


def test_21655_invalid_content_sid_is_mapped_to_friendly_message():
    error = FakeTwilioError(status=400, code=21655, msg="The ContentSid is Invalid")
    provider = _provider(messages=FakeMessages(error=error))

    result = provider.send(to="+919892031558", title="t", body="b")

    assert result.ok is False
    assert result.error_code == "21655"
    assert "invalid ContentSid" in (result.error_message or "")


def test_unknown_error_code_keeps_twilio_detail():
    error = FakeTwilioError(status=400, code=63016, msg="Account not active or something")
    provider = _provider(messages=FakeMessages(error=error))

    result = provider.send(to="+919892031558", title="t", body="b")

    assert result.ok is False
    assert result.error_code == "63016"
    assert "Account not active" in (result.error_message or "")


def test_async_failed_message_status_is_reported_as_failure():
    message = SimpleNamespace(
        sid="SM_fail", status="failed", error_code=21654, error_message="ContentSid Required"
    )
    provider = _provider(messages=FakeMessages(outcome=message))

    result = provider.send(to="+919892031558", title="t", body="b")

    assert result.ok is False
    assert result.status == STATUS_FAILED
    assert result.error_code == "21654"
    assert "ContentSid Required" in (result.error_message or "")


def test_sent_status_maps_to_sent():
    message = SimpleNamespace(sid="SM_sent", status="sent", error_code=None, error_message=None)
    provider = _provider(messages=FakeMessages(outcome=message))

    result = provider.send(to="+919892031558", title="t", body="b")

    assert result.ok is True
    assert result.status == STATUS_SENT
    assert result.provider_message_id == "SM_sent"


# --- destination handling ----------------------------------------------------

def test_missing_destination_fails_without_calling_twilio():
    messages = FakeMessages(outcome=_queued_message())
    provider = _provider(messages=messages)
    provider._settings.twilio_whatsapp_to = None

    result = provider.send(to=None, title="t", body="b")

    assert result.ok is False
    assert result.error_code == "no_destination"
    assert messages.calls == []


def test_existing_whatsapp_prefix_is_not_doubled():
    messages = FakeMessages(outcome=_queued_message())
    provider = _provider(messages=messages)

    provider.send(to="whatsapp:+919892031558", title="t", body="b")

    assert messages.calls[0]["to"] == "whatsapp:+919892031558"


def test_credential_failure_returns_config_error():
    provider = _provider(messages=FakeMessages())
    provider._client = None
    provider._settings.twilio_account_sid = None
    provider._settings.twilio_auth_token = None

    result = provider.send(to="+919892031558", title="t", body="b")

    assert result.ok is False
    assert result.error_code == "client_unavailable"



# --- content_sid missing -----------------------------------------------------

def test_missing_content_sid_fails_gracefully_without_calling_twilio():
    messages = FakeMessages(outcome=_queued_message())
    provider = _provider(content_sid=None, messages=messages)

    result = provider.send(to="+919892031558", title="t", body="b")

    assert result.ok is False
    assert result.status == STATUS_FAILED
    assert result.error_code == "no_content_sid"
    assert "ContentSid is not configured" in (result.error_message or "")
    assert messages.calls == []  # never hit the network


def test_blank_content_sid_is_treated_as_missing():
    provider = _provider(content_sid="   ", messages=FakeMessages())
    result = provider.send(to="+919892031558", title="t", body="b")
    assert result.ok is False
    assert result.error_code == "no_content_sid"
