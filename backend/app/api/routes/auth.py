from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth import SignupRequest, LoginRequest, GoogleLoginRequest, AuthResponse, MeResponse
from app.services import auth_service
from app.services.auth_service import AuthError
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    try:
        user, token = auth_service.signup_with_password(db, payload)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return AuthResponse(access_token=token, user=user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user, token = auth_service.login_with_password(db, payload)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return AuthResponse(access_token=token, user=user)


@router.post("/google", response_model=AuthResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        user, token = auth_service.login_or_signup_with_google(db, payload)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return AuthResponse(access_token=token, user=user)


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user