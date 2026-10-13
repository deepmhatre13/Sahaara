import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EmergencyTrigger(BaseModel):
    """SOS request body.

    ``user_id`` is deliberately NOT accepted: the subject always comes from the
    authenticated token, otherwise any caller could raise an alarm against
    another account's caregivers.

    ``force`` allows a deliberate "Send another alert" action to bypass the
    short-window duplicate suppression guard.
    """

    source: str = "sos_button"
    message: str | None = None
    force: bool = False


class EmergencyEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    user_id: uuid.UUID
    source: str
    status: str
    message: str | None
    resolved: bool
    created_at: datetime
    resolved_at: datetime | None


class CaregiverDeliveryOut(BaseModel):
    """Per-caregiver notification outcome."""

    caregiver_id: uuid.UUID
    caregiver_name: str
    notification_id: uuid.UUID | None = None
    status: str
    channel: str
    accepted: bool
    provider_message_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None


class SosResponse(BaseModel):
    """Structured SOS result.

    ``notified_caregivers`` is the only field the UI may use to claim that
    caregivers were notified — it counts provider-accepted sends, not attempts.
    """

    success: bool = True
    emergency_event: EmergencyEventOut
    #: False when this call was recognised as a duplicate of a very recent SOS.
    created: bool = True
    caregivers_targeted: int = 0
    caregivers_skipped: int = 0
    notifications_created: int = 0
    notified_caregivers: int = 0
    failed_caregivers: int = 0
    #: True when the active provider only logged the message (dev console).
    simulated: bool = False
    #: True when this SOS was triggered with force=True (deliberate resend).
    is_resend: bool = False
    delivery: list[CaregiverDeliveryOut] = Field(default_factory=list)

    @property
    def any_notified(self) -> bool:
        return self.notified_caregivers > 0


class EmergencyResolve(BaseModel):
    resolution_note: str | None = None
