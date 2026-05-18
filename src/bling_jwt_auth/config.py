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
    """Where persisted OAuth tokens are stored."""

    SQLITE = "sqlite"
    FILE = "file"


class BlingAuthSettings(BaseSettings):
    """Configuration for OAuth clients and token refresh behaviour."""

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="BLING_",
        env_file_encoding="utf-8",
        extra="ignore",
        env_file=".env",
    )

    client_id: str = Field(min_length=1)
    client_secret: SecretStr
    redirect_uri: HttpUrl

    enable_jwt: bool = True

    authorize_url: HttpUrl = Field(default=DEFAULT_AUTHORIZE_HTTPS)
    token_url: HttpUrl = Field(default=DEFAULT_OAUTH_CREDENTIALS_HTTPS)
    revoke_url: HttpUrl = Field(default=DEFAULT_REVOKE_HTTPS)

    refresh_skew_seconds: int = Field(default=60, ge=0)

    token_store: TokenStoreKind = TokenStoreKind.SQLITE
    token_store_path: Path | None = None

    @classmethod
    def load(cls) -> Self:
        """Load from ``BLING_*`` environment variables and optional ``.env``."""
        return cls()  # pyright: ignore[reportCallIssue]
