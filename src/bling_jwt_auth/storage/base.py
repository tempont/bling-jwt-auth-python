"""Token persistence interfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from bling_jwt_auth.models.token import StoredToken


@runtime_checkable
class TokenStore(Protocol):
    """Load and persist a single Bling token bundle."""

    def load(self) -> StoredToken | None:
        """Return the stored token, or ``None`` if nothing is saved."""

    def save(self, token: StoredToken) -> None:
        """Persist (or overwrite) the stored token."""

    def clear(self) -> None:
        """Remove any stored token."""
