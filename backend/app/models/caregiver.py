import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Caregiver(Base):
    """An emergency contact belonging to exactly one elder (``users``) row.

    Phone numbers are stored in E.164 (see ``app.core.phone.normalize_phone``)
    because that is the only format Twilio accepts.
    """

    __tablename__ = "caregivers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    elder_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    relationship_to_elder: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    whatsapp_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_primary: Mapped[bool] = mapped_column(default=False)
    # Deactivating keeps the record (and its notification history) but excludes
    # the caregiver from future SOS fan-out.
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true", default=True)
    # Independent of is_active: a caregiver can be reachable by call but have
    # opted out of WhatsApp.
    whatsapp_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true", default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    elder = relationship("User", back_populates="caregivers")
    notifications = relationship("Notification", back_populates="caregiver")

    @property
    def whatsapp_destination(self) -> str | None:
        """Number Twilio should target, in E.164, or None when unreachable.

        ``whatsapp_number`` wins when present; otherwise the number falls back to
        ``phone_number`` (most people's WhatsApp is their mobile).
        """
        if not self.whatsapp_enabled:
            return None
        return self.whatsapp_number or self.phone_number

    @property
    def is_whatsapp_reachable(self) -> bool:
        return self.whatsapp_destination is not None
