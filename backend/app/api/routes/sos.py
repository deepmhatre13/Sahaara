import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.emergency import (
    CaregiverDeliveryOut,
    EmergencyEventOut,
    EmergencyResolve,
    EmergencyTrigger,
    SosResponse,
)
from app.services import emergency_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sos", tags=["sos"])


def _to_response(outcome: emergency_service.SosOutcome) -> SosResponse:
    fanout = outcome.fanout
    return SosResponse(
        success=True,
        emergency_event=EmergencyEventOut.model_validate(outcome.event),
        created=not outcome.duplicate,
        caregivers_targeted=fanout.caregivers_targeted if fanout else outcome.caregiver_count,
        caregivers_skipped=fanout.caregivers_skipped if fanout else 0,
        notifications_created=fanout.notifications_created if fanout else 0,
        notified_caregivers=fanout.accepted if fanout else 0,
        failed_caregivers=fanout.failed if fanout else 0,
        simulated=fanout.simulated if fanout else False,
        is_resend=outcome.is_resend,
        delivery=[
            CaregiverDeliveryOut(
                caregiver_id=d.caregiver_id,
                caregiver_name=d.caregiver_name,
                notification_id=d.notification_id,
                status=d.status,
                channel=d.channel,
                accepted=d.accepted,
                provider_message_id=d.provider_message_id,
                error_code=d.error_code,
                error_message=d.error_message,
            )
            for d in (fanout.delivery if fanout else [])
        ],
    )


@router.post("", response_model=SosResponse, status_code=status.HTTP_201_CREATED)
def trigger_sos(
    payload: EmergencyTrigger,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Raise an SOS for the authenticated user and alert their caregivers.

    Always returns 201 with a structured report. A caregiver-side delivery
    failure does not make the request fail — the emergency event is the source
    of truth and the per-caregiver statuses carry the delivery truth.

    Supports ``force=True`` to deliberately bypass duplicate suppression and
    issue another alert.
    """
    logger.info(
        "SOS received: user_id=%s source=%s force=%s",
        current_user.id,
        payload.source,
        payload.force,
    )
    outcome = emergency_service.trigger_sos(
        db,
        user_id=current_user.id,
        source=payload.source,
        message=payload.message,
        guardian_name=current_user.full_name,
        force=payload.force,
    )
    return _to_response(outcome)


@router.post("/resend", response_model=SosResponse, status_code=status.HTTP_201_CREATED)
def resend_sos(
    payload: EmergencyTrigger | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dedicated endpoint to deliberately resend an emergency alert."""
    source = payload.source if payload else "sos_button"
    message = payload.message if payload else None
    logger.info("SOS resend received: user_id=%s source=%s", current_user.id, source)
    outcome = emergency_service.trigger_sos(
        db,
        user_id=current_user.id,
        source=source,
        message=message,
        guardian_name=current_user.full_name,
        force=True,
    )
    return _to_response(outcome)


@router.post("/{event_id}/resolve", response_model=EmergencyEventOut)
def resolve_sos(
    event_id: uuid.UUID,
    payload: EmergencyResolve,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = emergency_service.resolve_event(db, current_user.id, event_id, payload.resolution_note)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency event not found")
    return event


@router.get("", response_model=list[EmergencyEventOut])
def list_my_sos(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """The authenticated user's own emergency history."""
    return emergency_service.list_events(db, current_user.id)


@router.get("/{user_id}", response_model=list[EmergencyEventOut])
def list_sos(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Kept for backward compatibility; only your own history is returned."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized for this user",
        )
    return emergency_service.list_events(db, user_id)
