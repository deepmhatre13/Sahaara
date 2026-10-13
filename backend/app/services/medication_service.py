import uuid

from sqlalchemy.orm import Session

from app.models.medication import Medication
from app.schemas.medication import MedicationCreate


def create_medication(db: Session, payload: MedicationCreate) -> Medication:
    med = Medication(**payload.model_dump())
    db.add(med)
    db.commit()
    db.refresh(med)
    return med


def list_medications(db: Session, user_id: uuid.UUID) -> list[Medication]:
    return (
        db.query(Medication)
        .filter(Medication.user_id == user_id, Medication.active.is_(True))
        .all()
    )


def deactivate_medication(db: Session, medication_id: uuid.UUID, user_id: uuid.UUID | None = None) -> Medication | None:
    query = db.query(Medication).filter(Medication.id == medication_id)
    if user_id is not None:
        query = query.filter(Medication.user_id == user_id)
    med = query.first()
    if not med:
        return None
    med.active = False
    db.commit()
    db.refresh(med)
    return med