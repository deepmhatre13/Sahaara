import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ActivityEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    event_type: str
    details: str | None
    created_at: datetime


class ActivityStatusOut(BaseModel):
    user_id: uuid.UUID
    current_status: str
    last_motion_at: datetime | None
    seconds_since_motion: float | None
    inactivity_threshold_seconds: int