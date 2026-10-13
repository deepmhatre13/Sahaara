import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class HealthMetricCreate(BaseModel):
    metric_type: str
    value: float
    unit: str
    source: str = "mock"


class HealthMetricOut(HealthMetricCreate):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    recorded_at: datetime


class HealthSummaryOut(BaseModel):
    heart_rate: float | None = None
    steps: float | None = None
    sleep_minutes: float | None = None
    spo2: float | None = None
    last_synced: datetime | None = None