import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import ensure_self, get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentOut
from app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, payload.user_id)
    return appointment_service.create_appointment(db, payload)


@router.get("/{user_id}", response_model=list[AppointmentOut])
def list_for_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return appointment_service.list_appointments(db, user_id)


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    appointment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not appointment_service.delete_appointment(db, appointment_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")