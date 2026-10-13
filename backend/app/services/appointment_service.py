import uuid

from sqlalchemy.orm import Session

from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate


def create_appointment(db: Session, payload: AppointmentCreate) -> Appointment:
    appt = Appointment(**payload.model_dump())
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


def list_appointments(db: Session, user_id: uuid.UUID) -> list[Appointment]:
    return (
        db.query(Appointment)
        .filter(Appointment.user_id == user_id)
        .order_by(Appointment.scheduled_at.asc())
        .all()
    )


def delete_appointment(db: Session, appointment_id: uuid.UUID, user_id: uuid.UUID | None = None) -> bool:
    query = db.query(Appointment).filter(Appointment.id == appointment_id)
    if user_id is not None:
        query = query.filter(Appointment.user_id == user_id)
    appt = query.first()
    if not appt:
        return False
    db.delete(appt)
    db.commit()
    return True