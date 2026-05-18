"""Shared fixtures."""

from __future__ import annotations

import pytest
from pydantic import SecretStr

from bling_jwt_auth.config import (
    DEFAULT_AUTHORIZE_HTTPS,
    DEFAULT_OAUTH_CREDENTIALS_HTTPS,
    DEFAULT_REVOKE_HTTPS,
    BlingAuthSettings,
)

from .url_utils import parsed_http_url


@pytest.fixture
def settings() -> BlingAuthSettings:
    """Minimal settings pointing OAuth traffic at the official host paths."""
    return BlingAuthSettings(
        client_id="test-client-id",
        client_secret=SecretStr("test-client-secret"),
        redirect_uri=parsed_http_url("https://example.org/oauth/callback"),
        authorize_url=DEFAULT_AUTHORIZE_HTTPS,
        token_url=DEFAULT_OAUTH_CREDENTIALS_HTTPS,
        revoke_url=DEFAULT_REVOKE_HTTPS,
        refresh_skew_seconds=60,
    )


@pytest.fixture
def long_jwt_like_token() -> str:
    """Simulated JWT-sized bearer string (Bling tokens are much longer than legacy opaque tokens)."""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." + "x" * 1200 + "." + "sig" * 200
