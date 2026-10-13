"""Apply all Alembic migrations up to head.

Used because invoking the `alembic` console script from PowerShell can abort on
stderr output (PowerShell surfaces native stderr as a terminating error).

Run from the backend directory:
    .\\venv\\Scripts\\python.exe scripts\\migrate.py
"""

import sys
from pathlib import Path

# Ensure the backend root (which contains the `app` package and alembic.ini)
# is importable regardless of the current working directory.
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from alembic import command  # noqa: E402
from alembic.config import Config  # noqa: E402

cfg = Config(str(BACKEND_ROOT / "alembic.ini"))
cfg.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))

print("Applying migrations to head ...")
command.upgrade(cfg, "head")
print("MIGRATIONS APPLIED OK")
