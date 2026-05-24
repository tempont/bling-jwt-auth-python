"""httpx authentication adapter for Bling API requests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

import httpx

from bling_jwt_auth.config import BlingAuthSettings
from bling_jwt_auth.headers import bling_api_headers
from bling_jwt_auth.manager import TokenManager
from bling_jwt_auth.oauth.client import OAuthClient
from bling_jwt_auth.storage.factory import create_token_store

if TYPE_CHECKING:
    from collections.abc import Generator

    from bling_jwt_auth.storage.base import TokenStore


class BlingAuth(httpx.Auth):
    """httpx ``Auth`` implementation backed by a refreshing ``TokenManager``."""

    def __init__(
        self,
        manager: TokenManager,
        *,
        oauth: OAuthClient | None = None,
    ) -> None:
        """Create an auth adapter using an existing token manager.

        Args:
            manager: Token manager that returns a valid access token.
            oauth: Optional OAuth client owned by this adapter and closed by
                :meth:`close`. This is used by the factory constructors.
        """
        self._manager = manager
        self._oauth = oauth

    @classmethod
    def from_env(cls) -> Self:
        """Create an auth adapter from ``BLING_*`` environment settings."""
        return cls.from_settings(BlingAuthSettings.load())

    @classmethod
    def from_settings(
        cls,
        settings: BlingAuthSettings,
        *,
        store: TokenStore | None = None,
        oauth: OAuthClient | None = None,
    ) -> Self:
        """Create an auth adapter from explicit settings.

        Args:
            settings: Bling OAuth configuration.
            store: Optional token store. When omitted, the configured store is
                created with :func:`create_token_store`.
            oauth: Optional OAuth client. When omitted, this adapter creates and
                owns one for refresh requests.
        """
        token_store = store or create_token_store(settings)
        oauth_client = oauth or OAuthClient(settings)
        manager = TokenManager(oauth_client, token_store, settings)
        owned_oauth = oauth_client if oauth is None else None
        return cls(manager, oauth=owned_oauth)

    @property
    def manager(self) -> TokenManager:
        """Token manager used to obtain and refresh access tokens."""
        return self._manager

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:
        """Attach Bling bearer/JWT headers before the request is sent."""
        request.headers.update(bling_api_headers(self._manager.get_access_token()))
        yield request

    def close(self) -> None:
        """Close the internally-created OAuth client, when this adapter owns one."""
        if self._oauth is not None:
            self._oauth.close()

    def __enter__(self) -> Self:
        """Return the context-managed auth adapter."""
        return self

    def __exit__(self, *_exc: object) -> None:
        """Close owned resources when leaving a ``with`` block."""
        self.close()
