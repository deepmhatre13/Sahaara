import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import ensure_self, get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.health import HealthMetricOut, HealthSummaryOut
from app.services import health_service

router = APIRouter(prefix="/health-data", tags=["health-data"])


@router.post("/{user_id}/sync", response_model=list[HealthMetricOut])
def sync(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return health_service.sync_health_metrics(db, user_id)


@router.get("/{user_id}/summary", response_model=HealthSummaryOut)
def summary(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return health_service.get_latest_summary(db, user_id)


@router.get("/{user_id}/metrics", response_model=list[HealthMetricOut])
def metrics(
    user_id: uuid.UUID,
    metric_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ensure_self(current_user, user_id)
    return health_service.list_metrics(db, user_id, metric_type)