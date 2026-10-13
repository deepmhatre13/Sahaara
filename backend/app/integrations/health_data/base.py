from abc import ABC, abstractmethod


class HealthDataProvider(ABC):
    @abstractmethod
    def get_current_readings(self) -> dict:
        """Return a dict with keys: heart_rate, steps, sleep_minutes, spo2."""
        raise NotImplementedError