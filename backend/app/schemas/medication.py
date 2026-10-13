import uuid
from datetime import datetime, time
from pydantic import BaseModel, ConfigDict


class MedicationCreate(BaseModel):
    user_id: uuid.UUID
    name: str
    dosage: str | None = None
    schedule_time: time
    frequency: str = "daily"
    notes: str | None = None


class MedicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    dosage: str | None
    schedule_time: time
    frequency: str
    active: bool
    notes: str | None
    created_at: datetime