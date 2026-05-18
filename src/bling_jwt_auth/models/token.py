"""OAuth token models."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Self

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from bling_jwt_auth.constants import OAUTH_BEARER_TYPE_LABEL


class TokenResponse(BaseModel):
    """Validated response returned by Bling's OAuth token endpoint.

    Bling may return token lifetime as ``expires_in`` or ``token_validate``.
    Both names are accepted and normalized to ``expires_in``.
    """

    model_config = ConfigDict(extra="ignore", populate_by_name=True, str_strip_whitespace=True)

    access_token: str
    """Bearer token used in authenticated API requests."""

    token_type: str = Field(default=OAUTH_BEARER_TYPE_LABEL)
    """OAuth token type, usually ``Bearer``."""

    expires_in: int = Field(validation_alias=AliasChoices("expires_in", "token_validate"))
    """Token lifetime in seconds."""

    refresh_token: str
    """Token used to obtain a new access token after expiry."""

    scope: str | None = None
    """Optional scope string returned by Bling."""


class StoredToken(BaseModel):
    """Token bundle persisted by a :class:`~bling_jwt_auth.storage.base.TokenStore`.

    ``StoredToken`` adds ``obtained_at`` to the live OAuth response so expiry can
    be evaluated later without decoding the access token.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    access_token: str
    token_type: str = Field(default=OAUTH_BEARER_TYPE_LABEL)
    expires_in: int
    refresh_token: str
    scope: str | None = None
    obtained_at: datetime
    """UTC timestamp when this token bundle was obtained from Bling."""

    @property
    def expires_at(self) -> datetime:
        """Absolute expiry timestamp derived from ``obtained_at`` and ``expires_in``."""
        return self.obtained_at + timedelta(seconds=self.expires_in)

    def is_expired(self, *, skew_seconds: int = 0) -> bool:
        """Return whether the token should be refreshed.

        Args:
            skew_seconds: Optional proactive refresh margin. A value of ``60``
                treats the token as expired during the last minute of validity.

        Raises:
            ValueError: If ``skew_seconds`` is negative.
        """
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
        """Build a persisted token snapshot from a live OAuth response."""
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
