"""Tests for :class:`BlingAuth`."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import httpx
import pytest

from bling_jwt_auth.auth import BlingAuth
from bling_jwt_auth.constants import ENABLE_JWT_HEADER, ENABLE_JWT_VALUE
from bling_jwt_auth.manager import TokenManager
from bling_jwt_auth.models.token import StoredToken
from bling_jwt_auth.oauth.client import OAuthClient
from bling_jwt_auth.storage.file import FileTokenStore

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_httpx import HTTPXMock

    from bling_jwt_auth.config import BlingAuthSettings

pytest.importorskip("pytest_httpx")


def test_bling_auth_adds_bearer_headers(
    httpx_mock: HTTPXMock,
    settings: BlingAuthSettings,
    tmp_path: Path,
) -> None:
    """Httpx requests receive the bearer and JWT compatibility headers."""
    store = FileTokenStore(tmp_path / "tok.json")
    store.save(
        StoredToken(
            access_token="stored-access",
            expires_in=3600,
            refresh_token="stored-refresh",
            obtained_at=datetime.now(UTC),
        ),
    )
    httpx_mock.add_response(
        url="https://api.bling.com.br/Api/v3/homologacao/produtos",
        method="GET",
        json={"data": []},
    )

    with OAuthClient(settings) as oauth:
        manager = TokenManager(oauth, store, settings)
        auth = BlingAuth(manager)
        with httpx.Client(auth=auth) as client:
            response = client.get("https://api.bling.com.br/Api/v3/homologacao/produtos")

    assert response.json() == {"data": []}
    sent = httpx_mock.get_request(url="https://api.bling.com.br/Api/v3/homologacao/produtos")
    assert sent is not None
    assert sent.headers["Authorization"] == "Bearer stored-access"
    assert sent.headers[ENABLE_JWT_HEADER] == ENABLE_JWT_VALUE


def test_bling_auth_from_settings_uses_configured_store(
    httpx_mock: HTTPXMock,
    settings: BlingAuthSettings,
    tmp_path: Path,
) -> None:
    """The factory wires settings, store, OAuth client, and token manager."""
    store = FileTokenStore(tmp_path / "tok.json")
    store.save(
        StoredToken(
            access_token="factory-access",
            expires_in=3600,
            refresh_token="factory-refresh",
            obtained_at=datetime.now(UTC),
        ),
    )
    httpx_mock.add_response(
        url="https://api.bling.com.br/Api/v3/homologacao/produtos",
        method="GET",
        json={"data": []},
    )

    with (
        BlingAuth.from_settings(settings, store=store) as auth,
        httpx.Client(auth=auth) as client,
    ):
        response = client.get("https://api.bling.com.br/Api/v3/homologacao/produtos")

    assert response.status_code == 200
    sent = httpx_mock.get_request(url="https://api.bling.com.br/Api/v3/homologacao/produtos")
    assert sent is not None
    assert sent.headers["Authorization"] == "Bearer factory-access"
