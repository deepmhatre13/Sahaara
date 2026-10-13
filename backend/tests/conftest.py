"""Shared pytest fixtures.

Tests run against a throwaway SQLite database so they never touch the developer's
PostgreSQL data, and the notification provider is always a fake so pytest can
never send a real WhatsApp message.
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

# The app reads DATABASE_URL at import time via a cached Settings object, so
# point it at an in-memory SQLite database *before* importing anything from app.
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["NOTIFICATION_PROVIDER"] = "console"

from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.database.base import Base  # noqa: E402
import app.models  # noqa: E402,F401 - registers every mapper on Base.metadata
from app.models.user import User  # noqa: E402
from app.notifications.base import (  # noqa: E402
    DeliveryResult,
    NotificationProvider,
    STATUS_QUEUED,
)


class FakeNotificationProvider(NotificationProvider):
    """Records every send attempt; returns a scripted result per recipient.

    ``fail_for`` holds the destinations that should come back as failures, which
    is how the partial-failure case is exercised without a network call.
    """

    name = "fake"

    def __init__(self, fail_for: set[str] | None = None, raises_for: set[str] | None = None):
        self.sent: list[dict] = []
        self.fail_for = fail_for or set()
        self.raises_for = raises_for or set()
        self._counter = 0

    def send(self, *, to: str | None, title: str, body: str) -> DeliveryResult:
        self.sent.append({"to": to, "title": title, "body": body})
        if to in self.raises_for:
            raise RuntimeError(f"simulated provider crash for {to}")
        if to in self.fail_for:
            return DeliveryResult.failure(
                error_code="63016",
                error_message="Recipient has not joined the WhatsApp sandbox",
            )
        self._counter += 1
        return DeliveryResult.success(
            status=STATUS_QUEUED, provider_message_id=f"SM_fake_{self._counter:04d}"
        )


@pytest.fixture()
def db_session():
    """A fresh schema per test, on a single shared in-memory connection."""
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def elder(db_session):
    """The authenticated elder the SOS flows act on."""
    user = User(
        id=uuid.uuid4(),
        full_name="DEEPAM MHATRE",
        email="mhatredeepam@gmail.com",
        auth_provider="password",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def other_elder(db_session):
    """A second account, used to prove caregiver isolation."""
    user = User(
        id=uuid.uuid4(),
        full_name="Other Person",
        email="other@example.com",
        auth_provider="password",
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def fake_provider():
    return FakeNotificationProvider()
