import random

from app.integrations.health_data.base import HealthDataProvider


class MockHealthDataProvider(HealthDataProvider):
    def get_current_readings(self) -> dict:
        return {
            "heart_rate": round(random.uniform(60, 95), 1),
            "steps": random.randint(500, 6000),
            "sleep_minutes": random.randint(300, 480),
            "spo2": round(random.uniform(94, 99), 1),
        }