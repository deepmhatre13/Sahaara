import uuid

from sqlalchemy.orm import Session

from app.models.health_metric import HealthMetric
from app.integrations.health_data.base import HealthDataProvider
from app.integrations.health_data.fitbit_provider import build_health_data_provider
from app.schemas.health import HealthSummaryOut

#: Canonical unit per supported metric type.
_METRIC_UNITS = {
    "heart_rate": "bpm",
    "steps": "steps",
    "sleep_minutes": "minutes",
    "spo2": "%",
    "active_minutes": "minutes",
}

#: Metric types surfaced on the dashboard summary.
_SUMMARY_METRIC_TYPES = ["heart_rate", "steps", "sleep_minutes", "spo2"]


def sync_health_metrics(
    db: Session, user_id: uuid.UUID, provider: HealthDataProvider | None = None
) -> list[HealthMetric]:
    provider = provider or build_health_data_provider()
    readings = provider.get_current_readings()

    created: list[HealthMetric] = []
    for metric_type, value in readings.items():
        if value is None:
            continue
        metric = HealthMetric(
            user_id=user_id,
            metric_type=metric_type,
            value=value,
            unit=_METRIC_UNITS.get(metric_type, "unit"),
            # Persist the real provenance instead of a hardcoded "mock".
            source=provider.name,
        )
        db.add(metric)
        created.append(metric)

    db.commit()
    for metric in created:
        db.refresh(metric)
    return created


def get_latest_summary(db: Session, user_id: uuid.UUID) -> HealthSummaryOut:
    summary = HealthSummaryOut()
    for metric_type in _SUMMARY_METRIC_TYPES:
        latest = (
            db.query(HealthMetric)
            .filter(HealthMetric.user_id == user_id, HealthMetric.metric_type == metric_type)
            .order_by(HealthMetric.recorded_at.desc())
            .first()
        )
        if latest:
            setattr(summary, metric_type, latest.value)
            if summary.last_synced is None or latest.recorded_at > summary.last_synced:
                summary.last_synced = latest.recorded_at
    return summary


def list_metrics(db: Session, user_id: uuid.UUID, metric_type: str | None = None) -> list[HealthMetric]:
    query = db.query(HealthMetric).filter(HealthMetric.user_id == user_id)
    if metric_type:
        query = query.filter(HealthMetric.metric_type == metric_type)
    return query.order_by(HealthMetric.recorded_at.desc()).limit(100).all()