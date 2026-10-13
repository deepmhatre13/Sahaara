from app.core.config import get_settings
from app.notifications.base import NotificationProvider
from app.notifications.console_provider import ConsoleNotificationProvider
from app.notifications.twilio_provider import TwilioNotificationProvider


def get_notification_provider() -> NotificationProvider:
    settings = get_settings()
    if settings.notification_provider == "twilio":
        return TwilioNotificationProvider(settings=settings)
    return ConsoleNotificationProvider()