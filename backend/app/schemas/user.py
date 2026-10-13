import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str | None = None
    date_of_birth: datetime | None = None


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    is_active: bool
    auth_provider: str
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"