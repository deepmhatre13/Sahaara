import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MedicalDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    filename: str
    extracted_text: str | None
    explanation: str | None
    created_at: datetime