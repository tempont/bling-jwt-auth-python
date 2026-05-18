"""Application settings loaded from environment variables."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path  # noqa: TC003
from typing import ClassVar, Self

from pydantic import Field, HttpUrl, SecretStr, TypeAdapter
from pydantic_settings import BaseSettings, SettingsConfigDict

from bling_jwt_auth.constants import (
    DEFAULT_AUTHORIZE_URL,
    DEFAULT_OAUTH_CREDENTIALS_URL,
    DEFAULT_REVOKE_URL,
)

_HttpUrl = TypeAdapter(HttpUrl)
DEFAULT_AUTHORIZE_HTTPS: HttpUrl = _HttpUrl.validate_python(DEFAULT_AUTHORIZE_URL)
DEFAULT_OAUTH_CREDENTIALS_HTTPS: HttpUrl = _HttpUrl.validate_python(DEFAULT_OAUTH_CREDENTIALS_URL)
DEFAULT_REVOKE_HTTPS: HttpUrl = _HttpUrl.validate_python(DEFAULT_REVOKE_URL)


class TokenStoreKind(StrEnum):
    """Supported persistence backends for the local OAuth token snapshot.

    The package stores one Bling account token bundle at a time. Use ``sqlite``
    for the default local database backend or ``file`` for a plain JSON file.
    """

    SQLITE = "sqlite"
    FILE = "file"


class BlingAuthSettings(BaseSettings):
    """Runtime configuration loaded from ``BLING_*`` environment variables.

    Required fields are ``BLING_CLIENT_ID``, ``BLING_CLIENT_SECRET``, and
    ``BLING_REDIRECT_URI``. Optional fields let applications override Bling
    endpoint URLs, disable the JWT compatibility header, choose the token
    storage backend, and tune the proactive refresh margin.
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="BLING_",
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=".env",
    )

    client_id: str = Field(min_length=1)
    """OAuth client ID from the application registered in Bling."""

    client_secret: SecretStr
    """OAuth client secret from Bling.

    The value is represented as a Pydantic ``SecretStr`` to avoid accidental
    disclosure in repr/log output.
    """

    redirect_uri: HttpUrl
    """Callback URI registered in Bling for the OAuth application."""

    enable_jwt: bool = True
    """Whether OAuth requests should include Bling's ``enable-jwt: 1`` header."""

    authorize_url: HttpUrl = Field(default=DEFAULT_AUTHORIZE_HTTPS)
    """OAuth authorization endpoint used to build the browser redirect URL."""

    token_url: HttpUrl = Field(default=DEFAULT_OAUTH_CREDENTIALS_HTTPS)
    """OAuth token endpoint used for authorization-code and refresh grants."""

    revoke_url: HttpUrl = Field(default=DEFAULT_REVOKE_HTTPS)
    """OAuth revocation endpoint used by :meth:`OAuthClient.revoke_token`."""

    refresh_skew_seconds: int = Field(default=60, ge=0)
    """Seconds before actual expiry when a stored access token should refresh."""

    token_store: TokenStoreKind = TokenStoreKind.SQLITE
    """Token persistence backend selected by ``BLING_TOKEN_STORE``."""

    token_store_path: Path | None = None
    """Optional custom path for the SQLite database or JSON token file."""

    @classmethod
    def load(cls) -> Self:
        """Create settings from environment variables and the optional ``.env`` file."""
        return cls()  # pyright: ignore[reportCallIssue]
