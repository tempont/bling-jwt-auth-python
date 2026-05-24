"""Tests for :class:`BlingClient` and :func:`connect`."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from bling_jwt_auth.client import BlingClient, connect
from bling_jwt_auth.constants import ENABLE_JWT_HEADER, ENABLE_JWT_VALUE
from bling_jwt_auth.models.token import StoredToken
from bling_jwt_auth.storage.file import FileTokenStore

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_httpx import HTTPXMock

    from bling_jwt_auth.config import BlingAuthSettings

pytest.importorskip("pytest_httpx")


def _store_fresh_token(tmp_path: Path, access_token: str) -> FileTokenStore:
    store = FileTokenStore(tmp_path / "tok.json")
    store.save(
        StoredToken(
            access_token=access_token,
            expires_in=3600,
            refresh_token="refresh",
            obtained_at=datetime.now(UTC),
        ),
    )
    return store


def test_bling_client_sends_authenticated_relative_request(
    httpx_mock: HTTPXMock,
    settings: BlingAuthSettings,
    tmp_path: Path,
) -> None:
    """SDK client applies base_url and auth headers for relative API paths."""
    store = _store_fresh_token(tmp_path, "client-access")
    httpx_mock.add_response(
        url="https://api.bling.com.br/Api/v3/homologacao/produtos",
        method="GET",
        json={"data": [{"id": 1}]},
    )

    with BlingClient.from_settings(settings, store=store) as bling:
        response = bling.get("/Api/v3/homologacao/produtos")

    assert response.json() == {"data": [{"id": 1}]}
    sent = httpx_mock.get_request(url="https://api.bling.com.br/Api/v3/homologacao/produtos")
    assert sent is not None
    assert sent.headers["Authorization"] == "Bearer client-access"
    assert sent.headers[ENABLE_JWT_HEADER] == ENABLE_JWT_VALUE


def test_connect_uses_explicit_settings_and_store(
    httpx_mock: HTTPXMock,
    settings: BlingAuthSettings,
    tmp_path: Path,
) -> None:
    """``connect`` is the short factory for an authenticated client."""
    store = _store_fresh_token(tmp_path, "connect-access")
    httpx_mock.add_response(
        url="https://api.bling.com.br/Api/v3/homologacao/produtos",
        method="GET",
        json={"data": []},
    )

    with connect(settings=settings, store=store) as bling:
        response = bling.request("GET", "/Api/v3/homologacao/produtos")

    assert response.status_code == 200
    sent = httpx_mock.get_request(url="https://api.bling.com.br/Api/v3/homologacao/produtos")
    assert sent is not None
    assert sent.headers["Authorization"] == "Bearer connect-access"
