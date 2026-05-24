"""High-level synchronous client for authenticated Bling API calls."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

import httpx

from bling_jwt_auth.auth import BlingAuth
from bling_jwt_auth.config import BlingAuthSettings
from bling_jwt_auth.constants import DEFAULT_API_BASE_URL

if TYPE_CHECKING:
    from bling_jwt_auth.oauth.client import OAuthClient
    from bling_jwt_auth.storage.base import TokenStore


class BlingClient:
    """Small SDK-style client that sends authenticated Bling API requests."""

    def __init__(
        self,
        *,
        auth: BlingAuth,
        base_url: str = DEFAULT_API_BASE_URL,
        client: httpx.Client | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Create a client using a Bling auth adapter.

        Args:
            auth: Auth adapter responsible for token loading and refresh.
            base_url: Base URL for Bling API calls.
            client: Optional preconfigured ``httpx.Client``. When omitted, a
                new client is created and owned by this instance.
            timeout: Timeout used only when this instance creates the HTTP
                client internally.
        """
        self.auth = auth
        self.base_url = base_url
        self._owns_client = client is None
        self._client = client or httpx.Client(auth=auth, base_url=base_url, timeout=timeout)

    @classmethod
    def from_env(
        cls,
        *,
        base_url: str = DEFAULT_API_BASE_URL,
        timeout: float = 30.0,
    ) -> Self:
        """Create a client from ``BLING_*`` environment settings."""
        return cls.from_settings(BlingAuthSettings.load(), base_url=base_url, timeout=timeout)

    @classmethod
    def from_settings(  # noqa: PLR0913
        cls,
        settings: BlingAuthSettings,
        *,
        store: TokenStore | None = None,
        oauth: OAuthClient | None = None,
        base_url: str = DEFAULT_API_BASE_URL,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
    ) -> Self:
        """Create a client from explicit settings and optional dependencies."""
        auth = BlingAuth.from_settings(settings, store=store, oauth=oauth)
        return cls(auth=auth, base_url=base_url, client=client, timeout=timeout)

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,  # noqa: ANN401
    ) -> httpx.Response:
        """Send an authenticated request through the underlying ``httpx.Client``."""
        return self._client.request(method, url, **kwargs)

    def get(self, url: str, **kwargs: Any) -> httpx.Response:  # noqa: ANN401
        """Send an authenticated ``GET`` request."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> httpx.Response:  # noqa: ANN401
        """Send an authenticated ``POST`` request."""
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: Any) -> httpx.Response:  # noqa: ANN401
        """Send an authenticated ``PUT`` request."""
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs: Any) -> httpx.Response:  # noqa: ANN401
        """Send an authenticated ``PATCH`` request."""
        return self.request("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> httpx.Response:  # noqa: ANN401
        """Send an authenticated ``DELETE`` request."""
        return self.request("DELETE", url, **kwargs)

    def close(self) -> None:
        """Close HTTP resources owned by this SDK client."""
        if self._owns_client:
            self._client.close()
        self.auth.close()

    def __enter__(self) -> Self:
        """Return the context-managed client."""
        return self

    def __exit__(self, *_exc: object) -> None:
        """Close owned resources when leaving a ``with`` block."""
        self.close()


def connect(  # noqa: PLR0913
    *,
    settings: BlingAuthSettings | None = None,
    store: TokenStore | None = None,
    oauth: OAuthClient | None = None,
    base_url: str = DEFAULT_API_BASE_URL,
    timeout: float = 30.0,
    client: httpx.Client | None = None,
) -> BlingClient:
    """Create the default authenticated Bling client.

    Without arguments, configuration is loaded from ``BLING_*`` environment
    variables and the configured token store is used.
    """
    resolved_settings = settings or BlingAuthSettings.load()
    return BlingClient.from_settings(
        resolved_settings,
        store=store,
        oauth=oauth,
        base_url=base_url,
        timeout=timeout,
        client=client,
    )
