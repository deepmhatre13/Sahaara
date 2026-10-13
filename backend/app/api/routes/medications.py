import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import ensure_self, get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.medication import MedicationCreate, MedicationOut
from app.services import medication_service

router = APIRouter(prefix="/medications", tags=["medications"])


@router.post("", response_model=MedicationOut, status_code=status.HTTP_201_CREATED)
def create(
    payload: MedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, payload.user_id)
    return medication_service.create_medication(db, payload)


@router.get("/{user_id}", response_model=list[MedicationOut])
def list_for_user(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return medication_service.list_medications(db, user_id)


@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate(
    medication_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    med = medication_service.deactivate_medication(db, medication_id, user_id=current_user.id)
    if not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medication not found")