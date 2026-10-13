import uuid
from datetime import datetime, time

from sqlalchemy import String, DateTime, Time, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Medication(Base):
    __tablename__ = "medications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    dosage: Mapped[str | None] = mapped_column(String(100), nullable=True)
    schedule_time: Mapped[time] = mapped_column(Time, nullable=False)
    frequency: Mapped[str] = mapped_column(String(50), default="daily")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="medications")