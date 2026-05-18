"""OAuth2 client for Bling API v3 token endpoints."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self
from urllib.parse import urlencode

import httpx

from bling_jwt_auth.constants import (
    ACCEPT_HEADER_VALUE,
    ENABLE_JWT_HEADER,
    ENABLE_JWT_VALUE,
)
from bling_jwt_auth.exceptions import OAuthRequestError
from bling_jwt_auth.models.token import TokenResponse

if TYPE_CHECKING:
    from bling_jwt_auth.config import BlingAuthSettings


class OAuthClient:
    """Thin synchronous wrapper around Bling's OAuth endpoints."""

    def __init__(
        self,
        settings: BlingAuthSettings,
        *,
        client: httpx.Client | None = None,
        timeout: float = 30.0,
    ) -> None:
        """Create a client; owns and closes ``httpx.Client`` unless one is injected."""
        self._settings = settings
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)

    @property
    def settings(self) -> BlingAuthSettings:
        """Settings used by this client."""
        return self._settings

    def close(self) -> None:
        """Close the underlying HTTP client when this instance created it."""
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> Self:
        """Begin a context-managed session (no-op besides returning ``self``)."""
        return self

    def __exit__(self, *_exc: object) -> None:
        """Ensure the underlying client is closed when exiting the context."""
        self.close()

    def build_authorization_url(self, state: str) -> str:
        """Return the Bling ``/oauth/authorize`` URL for redirecting the resource owner."""
        if not state:
            msg = "state must be a non-empty string"
            raise ValueError(msg)
        params = {
            "response_type": "code",
            "client_id": self._settings.client_id,
            "state": state,
            "redirect_uri": str(self._settings.redirect_uri),
        }
        return f"{self._settings.authorize_url}?{urlencode(params)}"

    def exchange_code(self, code: str) -> TokenResponse:
        """Exchange an authorization code for tokens."""
        if not code:
            msg = "code must be a non-empty string"
            raise ValueError(msg)
        data = {
            "grant_type": "authorization_code",
            "code": code,
        }
        return self._post_token(data)

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Obtain new tokens using a refresh token."""
        if not refresh_token:
            msg = "refresh_token must be a non-empty string"
            raise ValueError(msg)
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        return self._post_token(data)

    def revoke_token(
        self,
        token: str,
        *,
        token_type_hint: str | None = None,
    ) -> None:
        """Revoke an access or refresh token."""
        if not token:
            msg = "token must be a non-empty string"
            raise ValueError(msg)
        data: dict[str, str] = {"token": token}
        if token_type_hint is not None:
            data["token_type_hint"] = token_type_hint
        response = self._client.post(
            str(self._settings.revoke_url),
            data=data,
            headers=self._oauth_headers(),
            auth=httpx.BasicAuth(
                self._settings.client_id,
                self._settings.client_secret.get_secret_value(),
            ),
        )
        self._raise_for_status(response)

    def _oauth_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": ACCEPT_HEADER_VALUE,
        }
        if self._settings.enable_jwt:
            headers[ENABLE_JWT_HEADER] = ENABLE_JWT_VALUE
        return headers

    def _post_token(self, data: dict[str, str]) -> TokenResponse:
        response = self._client.post(
            str(self._settings.token_url),
            data=data,
            headers=self._oauth_headers(),
            auth=httpx.BasicAuth(
                self._settings.client_id,
                self._settings.client_secret.get_secret_value(),
            ),
        )
        self._raise_for_status(response)
        payload = response.json()
        if not isinstance(payload, dict):
            msg = "Unexpected token response: JSON object expected"
            raise OAuthRequestError(msg, status_code=response.status_code, response_body=response.text)
        return TokenResponse.model_validate(payload)

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.is_success:
            return
        msg = f"OAuth request failed with HTTP {response.status_code}"
        raise OAuthRequestError(
            msg,
            status_code=response.status_code,
            response_body=response.text,
        )
