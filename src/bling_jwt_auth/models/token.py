"""OAuth token models."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Self

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from bling_jwt_auth.constants import OAUTH_BEARER_TYPE_LABEL


class TokenResponse(BaseModel):
    """Successful response from ``POST /oauth/token``."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True, str_strip_whitespace=True)

    access_token: str
    token_type: str = Field(default=OAUTH_BEARER_TYPE_LABEL)
    expires_in: int = Field(validation_alias=AliasChoices("expires_in", "token_validate"))
    refresh_token: str
    scope: str | None = None


class StoredToken(BaseModel):
    """Token bundle persisted by a :class:`~bling_jwt_auth.storage.base.TokenStore`."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    access_token: str
    token_type: str = Field(default=OAUTH_BEARER_TYPE_LABEL)
    expires_in: int
    refresh_token: str
    scope: str | None = None
    obtained_at: datetime

    @property
    def expires_at(self) -> datetime:
        """Absolute expiry in UTC (derived from ``obtained_at`` + ``expires_in``)."""
        return self.obtained_at + timedelta(seconds=self.expires_in)

    def is_expired(self, *, skew_seconds: int = 0) -> bool:
        """Return True when the token should be considered unusable (with skew)."""
        if skew_seconds < 0:
            msg = "skew_seconds must be >= 0"
            raise ValueError(msg)
        now = datetime.now(UTC)
        cutoff = self.expires_at - timedelta(seconds=skew_seconds)
        return now >= cutoff

    @classmethod
    def from_token_response(
        cls,
        response: TokenResponse,
        *,
        obtained_at: datetime | None = None,
    ) -> Self:
        """Build a stored token snapshot from a live OAuth response."""
        stamp = obtained_at if obtained_at is not None else datetime.now(UTC)
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=UTC)
        return cls(
            access_token=response.access_token,
            token_type=response.token_type,
            expires_in=response.expires_in,
            refresh_token=response.refresh_token,
            scope=response.scope,
            obtained_at=stamp,
        )
