"""Privacy helpers: employee identifiers are pseudonymised before they are stored."""

from __future__ import annotations

import hashlib
import hmac


def pseudonymise(employee_ref: str, salt: str) -> str:
    """Stable, non-reversible identifier derived from an HR reference and a secret salt."""
    digest = hmac.new(salt.encode(), employee_ref.encode(), hashlib.sha256).hexdigest()
    return f"emp_{digest[:12]}"
