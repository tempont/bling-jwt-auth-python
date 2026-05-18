"""Tests for :class:`TokenManager`."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import pytest
from pydantic import SecretStr

from bling_jwt_auth.config import BlingAuthSettings
from bling_jwt_auth.exceptions import TokenNotFoundError
from bling_jwt_auth.manager import TokenManager
from bling_jwt_auth.models.token import StoredToken
from bling_jwt_auth.oauth.client import OAuthClient
from bling_jwt_auth.storage.file import FileTokenStore

from .url_utils import parsed_http_url

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_httpx import HTTPXMock

pytest.importorskip("pytest_httpx")


def test_get_access_token_refreshes_when_expired(
    httpx_mock: HTTPXMock,
    tmp_path: Path,
) -> None:
    """Expired stored token triggers refresh POST and persists new credentials."""
    settings = BlingAuthSettings(
        client_id="c",
        client_secret=SecretStr("s"),
        redirect_uri=parsed_http_url("https://example.org/cb"),
        refresh_skew_seconds=60,
    )
    store = FileTokenStore(tmp_path / "tok.json")
    old = StoredToken(
        access_token="old-access",
        expires_in=60,
        refresh_token="rt-old",
        obtained_at=datetime.now(UTC) - timedelta(hours=2),
    )
    store.save(old)

    httpx_mock.add_response(
        url=str(settings.token_url),
        method="POST",
        json={
            "access_token": "new-access",
            "expires_in": 3600,
            "refresh_token": "rt-new",
        },
    )

    with OAuthClient(settings) as oauth:
        manager = TokenManager(oauth, store, settings)
        assert manager.get_access_token() == "new-access"

    loaded = store.load()
    assert loaded is not None
    assert loaded.access_token == "new-access"
    assert loaded.refresh_token == "rt-new"


def test_get_access_token_skips_network_when_fresh(httpx_mock: HTTPXMock, tmp_path: Path) -> None:
    """Valid stored token avoids any outbound HTTP."""
    settings = BlingAuthSettings(
        client_id="c",
        client_secret=SecretStr("s"),
        redirect_uri=parsed_http_url("https://example.org/cb"),
    )
    store = FileTokenStore(tmp_path / "tok.json")
    fresh = StoredToken(
        access_token="still-good",
        expires_in=3600,
        refresh_token="rt",
        obtained_at=datetime.now(UTC),
    )
    store.save(fresh)

    with OAuthClient(settings) as oauth:
        manager = TokenManager(oauth, store, settings)
        assert manager.get_access_token() == "still-good"

    assert not httpx_mock.get_requests()


def test_get_access_token_missing_raises(tmp_path: Path) -> None:
    """Empty store raises :class:`TokenNotFoundError`."""
    settings = BlingAuthSettings(
        client_id="c",
        client_secret=SecretStr("s"),
        redirect_uri=parsed_http_url("https://example.org/cb"),
    )
    store = FileTokenStore(tmp_path / "missing.json")
    with (
        OAuthClient(settings) as oauth,
        pytest.raises(TokenNotFoundError),
    ):
        TokenManager(oauth, store, settings).get_access_token()


def test_save_from_code_persists(httpx_mock: HTTPXMock, tmp_path: Path) -> None:
    """Authorization-code exchange persists through the configured store."""
    settings = BlingAuthSettings(
        client_id="c",
        client_secret=SecretStr("s"),
        redirect_uri=parsed_http_url("https://example.org/cb"),
    )
    httpx_mock.add_response(
        url=str(settings.token_url),
        method="POST",
        json={
            "access_token": "from-code",
            "token_validate": 120,
            "refresh_token": "rt",
        },
    )
    store = FileTokenStore(tmp_path / "tok.json")
    with OAuthClient(settings) as oauth:
        manager = TokenManager(oauth, store, settings)
        stored = manager.save_from_code("auth-code")

    assert stored.access_token == "from-code"
    loaded = store.load()
    assert loaded is not None
    assert loaded.access_token == "from-code"
