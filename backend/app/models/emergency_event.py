import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class EmergencyEvent(Base):
    __tablename__ = "emergency_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    source: Mapped[str] = mapped_column(String(50), default="sos_button")  # sos_button, inactivity, manual
    status: Mapped[str] = mapped_column(String(30), default="OPEN")  # OPEN, ACKNOWLEDGED, RESOLVED
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="emergency_events")