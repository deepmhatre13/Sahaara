from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# Canonical delivery states. Providers report the finest granularity they know;
# callers persist it verbatim so the UI never has to guess.
STATUS_QUEUED = "queued"
STATUS_SENT = "sent"
STATUS_DELIVERED = "delivered"
STATUS_FAILED = "failed"
STATUS_SKIPPED = "skipped"
STATUS_LOGGED = "logged"

# States that mean "the provider accepted the request". Used to decide whether
# the UI is allowed to say "caregivers have been notified".
ACCEPTED_STATUSES = frozenset({STATUS_QUEUED, STATUS_SENT, STATUS_DELIVERED, STATUS_LOGGED})


@dataclass(slots=True)
class DeliveryResult:
    """Outcome of a single send attempt.

    Replaces the earlier bare ``bool`` return. A bool could not distinguish
    "Twilio accepted it" from "Twilio rejected the recipient" nor carry the
    Message SID / error code we must persist for reconciliation.
    """

    ok: bool
    status: str
    provider_message_id: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    # True when the provider did not actually transmit anything (dev console
    # provider, or a recipient we deliberately skipped).
    simulated: bool = field(default=False)

    @classmethod
    def success(
        cls,
        status: str = STATUS_SENT,
        *,
        provider_message_id: str | None = None,
        simulated: bool = False,
    ) -> "DeliveryResult":
        return cls(
            ok=True,
            status=status,
            provider_message_id=provider_message_id,
            simulated=simulated,
        )

    @classmethod
    def failure(
        cls,
        *,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> "DeliveryResult":
        return cls(
            ok=False,
            status=STATUS_FAILED,
            error_code=error_code,
            error_message=error_message,
        )

    @classmethod
    def skipped(cls, reason: str) -> "DeliveryResult":
        return cls(ok=False, status=STATUS_SKIPPED, error_message=reason)

    @property
    def was_accepted(self) -> bool:
        return self.status in ACCEPTED_STATUSES


class NotificationProvider(ABC):
    """Abstract channel used to deliver a notification to a caregiver/user."""

    #: Short identifier persisted as ``Notification.channel``.
    name: str = "unknown"

    @abstractmethod
    def send(self, *, to: str | None, title: str, body: str) -> DeliveryResult:
        """Attempt to deliver a notification.

        Implementations must not raise for expected provider failures — return
        :meth:`DeliveryResult.failure` instead so the caller can record the
        attempt and continue with the remaining recipients.
        """
        raise NotImplementedError
