import uuid
from pydantic import BaseModel, EmailStr

from app.schemas.user import UserOut


class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str  # ID token obtained client-side via Google Identity Services


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class MeResponse(UserOut):
    auth_provider: str