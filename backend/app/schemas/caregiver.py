import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CaregiverBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    relationship_to_elder: str | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(default=None, max_length=32)
    whatsapp_number: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    is_primary: bool = False
    is_active: bool = True
    whatsapp_enabled: bool = True


class CaregiverCreate(CaregiverBase):
    """Payload for creating a caregiver.

    ``elder_id`` is intentionally absent: the owner always comes from the
    authenticated user, never from the request body.
    """


class CaregiverUpdate(BaseModel):
    """Partial update — only supplied fields are changed."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    relationship_to_elder: str | None = Field(default=None, max_length=100)
    phone_number: str | None = Field(default=None, max_length=32)
    whatsapp_number: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=255)
    is_primary: bool | None = None
    is_active: bool | None = None
    whatsapp_enabled: bool | None = None


class CaregiverOut(CaregiverBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    elder_id: uuid.UUID
    created_at: datetime
