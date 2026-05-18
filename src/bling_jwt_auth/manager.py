"""High-level helper that keeps a stored token fresh."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bling_jwt_auth.exceptions import TokenNotFoundError
from bling_jwt_auth.models.token import StoredToken

if TYPE_CHECKING:
    from bling_jwt_auth.config import BlingAuthSettings
    from bling_jwt_auth.oauth.client import OAuthClient
    from bling_jwt_auth.storage.base import TokenStore


class TokenManager:
    """Combine :class:`OAuthClient` with a :class:`TokenStore` for simple workflows."""

    def __init__(
        self,
        oauth: OAuthClient,
        store: TokenStore,
        settings: BlingAuthSettings,
    ) -> None:
        """Wire an OAuth client, persistent store, and shared settings."""
        self._oauth = oauth
        self._store = store
        self._settings = settings

    def save_from_code(self, code: str) -> StoredToken:
        """Exchange ``code`` and persist the resulting tokens."""
        token_response = self._oauth.exchange_code(code)
        stored = StoredToken.from_token_response(token_response)
        self._store.save(stored)
        return stored

    def get_access_token(self) -> str:
        """Return a usable access token, refreshing from disk when needed."""
        stored = self._store.load()
        if stored is None:
            msg = "No token in store; complete OAuth or call save_from_code first"
            raise TokenNotFoundError(msg)
        if stored.is_expired(skew_seconds=self._settings.refresh_skew_seconds):
            refreshed = self._oauth.refresh_token(stored.refresh_token)
            stored = StoredToken.from_token_response(refreshed)
            self._store.save(stored)
        return stored.access_token

    def load_stored(self) -> StoredToken | None:
        """Return the raw stored bundle without refreshing."""
        return self._store.load()

    def clear(self) -> None:
        """Remove persisted credentials."""
        self._store.clear()
