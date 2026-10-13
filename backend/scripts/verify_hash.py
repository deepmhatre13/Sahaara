"""Verify the bcrypt password helpers in app.core.security."""

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.security import hash_password, verify_password  # noqa: E402

h = hash_password("password123")
print("hash prefix:", h[:7], "len:", len(h))
assert h.startswith("$2"), "expected a bcrypt hash"
assert verify_password("password123", h) is True, "correct password must verify"
assert verify_password("wrong-password", h) is False, "wrong password must fail"
# Long passwords must not raise (the original passlib failure mode).
long_h = hash_password("x" * 200)
assert verify_password("x" * 200, long_h) is True
# A malformed stored hash must return False, not explode.
assert verify_password("password123", "not-a-bcrypt-hash") is False

print("HASH LAYER OK")
