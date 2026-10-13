import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    caregiver_id: uuid.UUID | None = None
    emergency_event_id: uuid.UUID | None = None
    category: str
    title: str
    body: str
    channel: str
    status: str
    delivered: bool
    provider_message_id: str | None = None
    error_message: str | None = None
    read: bool
    created_at: datetime
