import logging

from app.notifications.base import (
    DeliveryResult,
    NotificationProvider,
    STATUS_FAILED,
    STATUS_QUEUED,
    STATUS_SENT,
)
from app.core.config import Settings, get_settings
from app.core.phone import mask_phone

logger = logging.getLogger(__name__)

# Twilio rejects a WhatsApp send that carries no Content Template with 21654
# ("ContentSid Required"); an unknown or mis-copied template SID comes back as
# 21655 ("The ContentSid is Invalid"). Both are configuration problems rather
# than transient failures, so they are mapped to actionable messages instead
# of surfacing Twilio's raw text.
_FRIENDLY_CODES = {
    21654: (
        "Twilio rejected the WhatsApp send: ContentSid Required (21654). "
        "Set TWILIO_WHATSAPP_CONTENT_SID to a valid WhatsApp Content Template "
        "SID (HX...)."
    ),
    21655: (
        "Twilio rejected the WhatsApp send: invalid ContentSid (21655). "
        "TWILIO_WHATSAPP_CONTENT_SID does not match a Content Template on "
        "this account."
    ),
}


class TwilioNotificationProvider(NotificationProvider):
    """Sends a WhatsApp message via Twilio.

    Reuses the single lazily-constructed Twilio REST client so credentials are
    read once and missing credentials never crash the app at import time.

    Twilio requires a Content Template (``content_sid``) for every WhatsApp
    outbound message. When ``TWILIO_WHATSAPP_CONTENT_SID`` is configured the
    template is sent as ``content_sid`` alongside ``from_``; when it is missing
    the send is refused up front with a clear configuration error rather than
    letting Twilio answer 21654 at request time.

    Note: this Trial template is static, so no ``content_variables`` are sent —
    Twilio's generated successful request did not include them.
    """

    name = "twilio"

    def __init__(self, settings: Settings | None = None) -> None:
        self._client = None
        self._settings = settings if settings is not None else get_settings()

    def _get_client(self):
        if self._client is None:
            from twilio.rest import Client  # imported lazily

            if not (self._settings.twilio_account_sid and self._settings.twilio_auth_token):
                raise RuntimeError("Twilio credentials are not configured")
            self._client = Client(self._settings.twilio_account_sid, self._settings.twilio_auth_token)
        return self._client

    def _whatsapp_address(self, number: str | None) -> str | None:
        """Prefix a bare E.164 number with the ``whatsapp:`` channel marker.

        Twilio expects ``whatsapp:+919892031558``. Numbers already carrying the
        prefix are passed through so callers may store either form.
        """
        if not number:
            return None
        value = number.strip()
        if not value:
            return None
        return value if value.startswith("whatsapp:") else f"whatsapp:{value}"

    @staticmethod
    def _friendly_error(code, detail: str) -> str:
        """Map a Twilio numeric error code to an actionable message.

        Unrecognised codes keep Twilio's own text (truncated) so nothing is
        silently swallowed.
        """
        try:
            numeric = int(code) if code is not None else None
        except (TypeError, ValueError):
            numeric = None
        if numeric in _FRIENDLY_CODES:
            return _FRIENDLY_CODES[numeric]
        return detail[:400] if detail else "Twilio rejected the WhatsApp send"

    def send(self, *, to: str | None, title: str, body: str) -> DeliveryResult:
        destination_raw = to or self._settings.twilio_whatsapp_to
        destination = self._whatsapp_address(destination_raw)

        if not destination:
            logger.error("Twilio destination missing; notification not sent")
            return DeliveryResult.failure(
                error_code="no_destination",
                error_message="No caregiver WhatsApp number available and TWILIO_WHATSAPP_TO is unset",
            )

        if not self._settings.twilio_whatsapp_from:
            logger.error("Twilio sender (TWILIO_WHATSAPP_FROM) missing; notification not sent")
            return DeliveryResult.failure(
                error_code="no_sender",
                error_message="TWILIO_WHATSAPP_FROM is not configured",
            )

        content_sid = (self._settings.twilio_whatsapp_content_sid or "").strip()
        if not content_sid:
            # Fail fast with a configuration error: Twilio would reject this
            # request with 21654 anyway, and we can say something useful.
            logger.error(
                "Twilio WhatsApp ContentSid (TWILIO_WHATSAPP_CONTENT_SID) missing; "
                "notification not sent"
            )
            return DeliveryResult.failure(
                error_code="no_content_sid",
                error_message=(
                    "Twilio WhatsApp ContentSid is not configured. Set "
                    "TWILIO_WHATSAPP_CONTENT_SID to a WhatsApp Content Template "
                    "SID (HX...)."
                ),
            )

        try:
            client = self._get_client()
        except Exception as exc:  # noqa: BLE001 - misconfiguration must not abort SOS
            logger.error("Twilio client unavailable: %s", exc)
            return DeliveryResult.failure(
                error_code="client_unavailable",
                error_message=str(exc),
            )

        # Twilio's generated successful request for this Trial template does not
        # include content_variables, so the static template is sent as-is.
        try:
            logger.info(
                "Twilio provider call: sending WhatsApp to=%s from=%s content_sid=%s",
                mask_phone(destination_raw),
                self._settings.twilio_whatsapp_from,
                content_sid,
            )
            message = client.messages.create(
                from_=self._settings.twilio_whatsapp_from,
                to=destination,
                content_sid=content_sid,
            )
        except Exception as exc:  # noqa: BLE001 - provider errors are data, not crashes
            # Twilio's exception carries .code (numeric) and .status (HTTP).
            code = getattr(exc, "code", None)
            http_status = getattr(exc, "status", None)
            # Keep the message but strip the number we already know about.
            detail = str(exc)
            friendly = self._friendly_error(code, detail)
            logger.error(
                "Twilio send FAILED to=%s code=%s http=%s detail=%s",
                mask_phone(destination_raw),
                code,
                http_status,
                detail,
            )
            return DeliveryResult.failure(
                error_code=str(code) if code is not None else (str(http_status) if http_status else "unknown"),
                error_message=friendly,
            )

        # Twilio returns a Message with a SID and an initial status
        # ("queued" on create, or "failed" for an async rejection).
        twilio_status = (getattr(message, "status", None) or "").lower()
        sid = getattr(message, "sid", None)

        if twilio_status == STATUS_FAILED:
            error_code = getattr(message, "error_code", None)
            error_message = getattr(message, "error_message", None)
            friendly = self._friendly_error(error_code, error_message or "")
            logger.error(
                "Twilio rejected message sid=%s code=%s msg=%s",
                sid,
                error_code,
                error_message,
            )
            return DeliveryResult(
                ok=False,
                status=STATUS_FAILED,
                provider_message_id=sid,
                error_code=str(error_code) if error_code is not None else None,
                error_message=friendly,
            )

        status = STATUS_SENT if twilio_status in {"sent", "delivered"} else STATUS_QUEUED
        logger.info(
            "Twilio WhatsApp accepted to=%s sid=%s status=%s",
            mask_phone(destination_raw),
            sid,
            status,
        )
        return DeliveryResult.success(status=status, provider_message_id=sid)
