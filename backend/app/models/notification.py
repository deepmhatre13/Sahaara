import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Notification(Base):
    """One *delivery attempt* to one recipient, plus the resulting channel state.

    ``status`` holds the finest-grained truth the provider gave us:

        queued    — accepted by the provider, no delivery receipt yet
        sent      — provider accepted the request (Twilio ``queued``/``sent``)
        delivered — provider confirmed handset delivery (WhatsApp receipts)
        failed    — provider rejected it, or the provider raised
        skipped   — not attempted (no reachable number / WhatsApp disabled)
        logged    — console provider (development), nothing was actually sent

    ``delivered`` is kept as a coarse boolean for the existing Notifications UI.
    """

    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    # Optional links: a notification may be entirely user-scoped (e.g. a reminder
    # shown in-app) rather than tied to a caregiver or an emergency.
    caregiver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("caregivers.id", ondelete="SET NULL"), nullable=True
    )
    emergency_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("emergency_events.id", ondelete="SET NULL"), nullable=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # sos, medication, appointment, inactivity, system
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(String(1000), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), default="console")  # console, whatsapp, twilio
    status: Mapped[str] = mapped_column(String(30), nullable=False, server_default="pending")
    delivered: Mapped[bool] = mapped_column(Boolean, default=False)
    # Provider-side identifier (Twilio Message SID) — required for delivery
    # reconciliation via Twilio's status callback later.
    provider_message_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Sanitised provider error (Twilio code + short message). Never contains secrets.
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="notifications")
    caregiver = relationship("Caregiver", back_populates="notifications")
