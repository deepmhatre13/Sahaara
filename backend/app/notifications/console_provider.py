import logging

from app.notifications.base import (
    DeliveryResult,
    NotificationProvider,
    STATUS_LOGGED,
)
from app.core.phone import mask_phone

logger = logging.getLogger(__name__)


class ConsoleNotificationProvider(NotificationProvider):
    """Development-safe provider: logs the notification instead of sending it.

    Reports ``status="logged"`` and ``simulated=True`` so callers can tell the
    difference between "Twilio accepted this" and "we printed it to the console"
    — the SOS UI must never claim a real delivery on the strength of this.
    """

    name = "console"

    def send(self, *, to: str | None, title: str, body: str) -> DeliveryResult:
        logger.info("[NOTIFICATION -> %s] %s :: %s", mask_phone(to) if to else "unknown", title, body)
        return DeliveryResult.success(status=STATUS_LOGGED, simulated=True)
