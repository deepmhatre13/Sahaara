import logging
import threading
import time
import uuid
from datetime import datetime, timezone

from app.core.config import get_settings
from app.vision.base import MotionProvider
from app.vision.mock_provider import MockMotionProvider
from app.vision.opencv_provider import OpenCVMotionProvider

logger = logging.getLogger(__name__)


def build_motion_provider() -> MotionProvider:
    settings = get_settings()
    if settings.motion_provider == "opencv":
        return OpenCVMotionProvider()
    return MockMotionProvider()


class MotionMonitor:
    """Per-user in-memory motion state machine. Runs a background thread that
    polls a MotionProvider and raises ActivityEvents via the callback."""

    def __init__(
        self,
        user_id: uuid.UUID,
        on_event: callable,
        provider: MotionProvider | None = None,
    ) -> None:
        self.user_id = user_id
        self.on_event = on_event
        self.provider = provider or build_motion_provider()
        settings = get_settings()
        self.inactivity_threshold = settings.inactivity_threshold_seconds
        self.poll_interval = settings.motion_poll_interval_seconds

        self._lock = threading.Lock()
        self._last_motion_at = datetime.now(timezone.utc)
        self._current_status = "NO_MOTION"
        self._threshold_breached = False
        self._running = False
        self._thread: threading.Thread | None = None

    def get_status(self) -> dict:
        with self._lock:
            seconds_since = (datetime.now(timezone.utc) - self._last_motion_at).total_seconds()
            return {
                "current_status": self._current_status,
                "last_motion_at": self._last_motion_at,
                "seconds_since_motion": seconds_since,
                "inactivity_threshold_seconds": self.inactivity_threshold,
            }

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False

    def _run_loop(self) -> None:
        while self._running:
            try:
                motion_detected = self.provider.poll()
                now = datetime.now(timezone.utc)

                with self._lock:
                    if motion_detected:
                        self._current_status = "MOTION_DETECTED"
                        self._last_motion_at = now
                        self._threshold_breached = False
                        self.on_event(self.user_id, "MOTION_DETECTED", None)
                    else:
                        seconds_since = (now - self._last_motion_at).total_seconds()
                        if seconds_since > self.inactivity_threshold:
                            self._current_status = "INACTIVITY_THRESHOLD_EXCEEDED"
                            if not self._threshold_breached:
                                self._threshold_breached = True
                                self.on_event(
                                    self.user_id,
                                    "INACTIVITY_THRESHOLD_EXCEEDED",
                                    f"No motion for {int(seconds_since)}s",
                                )
                        else:
                            self._current_status = "NO_MOTION"
            except Exception as exc:  # noqa: BLE001
                logger.error("Motion monitor error for user %s: %s", self.user_id, exc)

            time.sleep(self.poll_interval)


class MotionMonitorRegistry:
    """Keeps one MotionMonitor per user alive for the app's lifetime."""

    def __init__(self) -> None:
        self._monitors: dict[uuid.UUID, MotionMonitor] = {}
        self._lock = threading.Lock()

    def get_or_create(self, user_id: uuid.UUID, on_event: callable) -> MotionMonitor:
        with self._lock:
            monitor = self._monitors.get(user_id)
            if monitor is None:
                monitor = MotionMonitor(user_id=user_id, on_event=on_event)
                monitor.start()
                self._monitors[user_id] = monitor
            return monitor

    def get(self, user_id: uuid.UUID) -> MotionMonitor | None:
        return self._monitors.get(user_id)


motion_registry = MotionMonitorRegistry()