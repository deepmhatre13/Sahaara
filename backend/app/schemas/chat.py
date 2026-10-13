import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ChatAsk(BaseModel):
    user_id: uuid.UUID
    session_id: uuid.UUID | None = None
    message: str


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    role: str
    content: str
    sources: str | None
    created_at: datetime


class ChatAskResponse(BaseModel):
    session_id: uuid.UUID
    response: str
    sources: list[str] = []