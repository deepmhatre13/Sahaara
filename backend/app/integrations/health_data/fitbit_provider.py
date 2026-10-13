import logging

from app.core.config import get_settings
from app.integrations.health_data.base import HealthDataProvider

logger = logging.getLogger(__name__)


class FitbitHealthDataProvider(HealthDataProvider):
    """Placeholder for a real Fitbit Web API integration (OAuth2 + REST).
    Structured so it can be dropped in without changing calling code."""

    def __init__(self) -> None:
        self.settings = get_settings()

    def get_current_readings(self) -> dict:
        if not (self.settings.fitbit_client_id and self.settings.fitbit_client_secret):
            logger.warning("Fitbit credentials not configured; returning empty readings")
            return {"heart_rate": None, "steps": None, "sleep_minutes": None, "spo2": None}
        # TODO: implement OAuth2 token exchange + calls to
        # https://api.fitbit.com/1/user/-/activities/date/today.json etc.
        raise NotImplementedError("Fitbit integration not yet implemented")


def build_health_data_provider() -> HealthDataProvider:
    settings = get_settings()
    if settings.health_data_provider == "fitbit":
        return FitbitHealthDataProvider()
    return MockHealthDataProvider()