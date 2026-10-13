"""Verify the pluggable provider factories resolve for every configured backend.

Regression coverage for the NameError bugs where a factory returned a
provider class that was never imported (MockHealthDataProvider /
MockOCRProvider), and for the missing `provider.name` attribute used as
HealthMetric.source.
"""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.integrations.health_data.base import HealthDataProvider  # noqa: E402
from app.integrations.health_data.fitbit_provider import build_health_data_provider  # noqa: E402
from app.integrations.health_data.mock_provider import MockHealthDataProvider  # noqa: E402
from app.integrations.ocr.base import OCRProvider  # noqa: E402
from app.integrations.ocr.mistral_provider import build_ocr_provider  # noqa: E402
from app.vision.motion_monitor import build_motion_provider  # noqa: E402

# --- health data ------------------------------------------------------------
hp = build_health_data_provider()
assert isinstance(hp, HealthDataProvider), f"unexpected provider: {hp!r}"
assert hp.name, "provider.name must be non-empty (persisted as HealthMetric.source)"
assert len(hp.name) <= 50, "provider.name must fit HealthMetric.source String(50)"
readings = hp.get_current_readings()
assert set(readings) == {"heart_rate", "steps", "sleep_minutes", "spo2"}, readings
print(f"health_data provider OK  -> {type(hp).__name__} name={hp.name!r}")

# Exact regression: the mock class must be importable from the factory module.
assert MockHealthDataProvider().name == "mock"
print("MockHealthDataProvider importable from factory module OK")

# --- OCR --------------------------------------------------------------------
ocr = build_ocr_provider()
assert isinstance(ocr, OCRProvider), f"unexpected provider: {ocr!r}"
print(f"ocr provider OK          -> {type(ocr).__name__}")

# --- motion -----------------------------------------------------------------
motion = build_motion_provider()
assert hasattr(motion, "poll"), "motion provider must expose poll()"
print(f"motion provider OK       -> {type(motion).__name__}")

print("ALL PROVIDER FACTORIES OK")
