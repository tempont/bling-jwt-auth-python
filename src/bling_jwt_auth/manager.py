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
    """High-level token workflow for one Bling account.

    ``TokenManager`` combines an :class:`~bling_jwt_auth.oauth.client.OAuthClient`
    with a :class:`~bling_jwt_auth.storage.base.TokenStore`. It is the easiest
    entry point for applications that want to save tokens after OAuth and later
    ask for a valid access token without manually checking expiry.
    """

    def __init__(
        self,
        oauth: OAuthClient,
        store: TokenStore,
        settings: BlingAuthSettings,
    ) -> None:
        """Create a manager using an OAuth client, token store, and settings."""
        self._oauth = oauth
        self._store = store
        self._settings = settings

    def save_from_code(self, code: str) -> StoredToken:
        """Exchange an OAuth callback code and persist the resulting token bundle.

        Args:
            code: Authorization code received by the configured redirect URI.

        Returns:
            The token snapshot written to the configured store.
        """
        token_response = self._oauth.exchange_code(code)
        stored = StoredToken.from_token_response(token_response)
        self._store.save(stored)
        return stored

    def get_access_token(self) -> str:
        """Return a valid access token, refreshing and saving when needed.

        Raises:
            TokenNotFoundError: If no token has been saved yet.
            OAuthRequestError: If a refresh request fails.
        """
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
        """Return the stored token snapshot without checking expiry or refreshing."""
        return self._store.load()

    def clear(self) -> None:
        """Delete persisted credentials from the configured store."""
        self._store.clear()
