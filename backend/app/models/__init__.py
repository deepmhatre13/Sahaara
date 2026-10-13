"""Model package.

Importing this package registers every mapped class on ``Base.metadata``.

This matters because the models use string-based relationships
(``relationship("Notification")``). SQLAlchemy can only resolve those once the
referenced class has been imported, so any entry point that touches the ORM —
API routes, Celery tasks, Alembic, standalone scripts — must import this module
rather than individual model files.
"""

from app.models.user import User
from app.models.caregiver import Caregiver
from app.models.health_metric import HealthMetric
from app.models.activity_event import ActivityEvent
from app.models.emergency_event import EmergencyEvent
from app.models.medication import Medication
from app.models.appointment import Appointment
from app.models.notification import Notification
from app.models.chat import ChatSession, ChatMessage
from app.models.medical_document import MedicalDocument
from app.models.system_event import SystemEvent

__all__ = [
    "User",
    "Caregiver",
    "HealthMetric",
    "ActivityEvent",
    "EmergencyEvent",
    "Medication",
    "Appointment",
    "Notification",
    "ChatSession",
    "ChatMessage",
    "MedicalDocument",
    "SystemEvent",
]
