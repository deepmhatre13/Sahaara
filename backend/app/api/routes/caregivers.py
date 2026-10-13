import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.caregiver import CaregiverCreate, CaregiverOut, CaregiverUpdate
from app.services import caregiver_service
from app.services.caregiver_service import CaregiverError

router = APIRouter(prefix="/caregivers", tags=["caregivers"])


@router.get("", response_model=list[CaregiverOut])
def list_caregivers(
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """The authenticated user's caregivers.

    Scope is always ``current_user.id`` — there is no path parameter to widen it,
    so one account can never enumerate another account's contacts.
    """
    return caregiver_service.list_caregivers(
        db, current_user.id, active_only=not include_inactive
    )


@router.post("", response_model=CaregiverOut, status_code=status.HTTP_201_CREATED)
def create_caregiver(
    payload: CaregiverCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return caregiver_service.create_caregiver(db, current_user.id, payload)
    except CaregiverError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.get("/{caregiver_id}", response_model=CaregiverOut)
def get_caregiver(
    caregiver_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    caregiver = caregiver_service.get_caregiver(db, current_user.id, caregiver_id)
    if not caregiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caregiver not found")
    return caregiver


@router.patch("/{caregiver_id}", response_model=CaregiverOut)
def update_caregiver(
    caregiver_id: uuid.UUID,
    payload: CaregiverUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        caregiver = caregiver_service.update_caregiver(db, current_user.id, caregiver_id, payload)
    except CaregiverError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    if not caregiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caregiver not found")
    return caregiver


@router.delete("/{caregiver_id}", response_model=CaregiverOut)
def deactivate_caregiver(
    caregiver_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Soft delete — keeps the record so notification history stays intact."""
    caregiver = caregiver_service.deactivate_caregiver(db, current_user.id, caregiver_id)
    if not caregiver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Caregiver not found")
    return caregiver
