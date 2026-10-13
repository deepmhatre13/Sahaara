import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AppointmentCreate(BaseModel):
    user_id: uuid.UUID
    title: str
    description: str | None = None
    location: str | None = None
    scheduled_at: datetime


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    location: str | None
    scheduled_at: datetime
    reminded: bool
    created_at: datetime