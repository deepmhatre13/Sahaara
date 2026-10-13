"""Smoke-test the database layer used by auth_service.

Verifies that the app's configured DATABASE_URL can connect and that the
`users` table is queryable via the same SQLAlchemy session factory the API uses.

Run from the backend directory:
    .\\venv\\Scripts\\python.exe scripts\\verify_db.py
"""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import get_settings  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402

# Import the full model set first so that every relationship() target
# (e.g. User.caregiver -> Caregiver) can be resolved by the mapper registry.
# Mirrors the imports in alembic/env.py.
from app.models import (  # noqa: E402,F401
    user,
    caregiver,
    health_metric,
    activity_event,
    emergency_event,
    medication,
    appointment,
    notification,
    chat,
    medical_document,
    system_event,
)
from app.models.user import User  # noqa: E402

settings = get_settings()
# Print the host/db without leaking the password.
safe_url = settings.database_url.split("@")[-1]
print(f"Connecting via DATABASE_URL -> ...@{safe_url}")

db = SessionLocal()
try:
    db.query(User).limit(1).all()
    total = db.query(User).count()
    print(f"OK: users table is queryable. rows={total}")
finally:
    db.close()

print("DB LAYER OK")
