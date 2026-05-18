"""Tests for :class:`OAuthClient`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx
import pytest

from bling_jwt_auth.constants import (
    ACCEPT_HEADER_VALUE,
    ENABLE_JWT_HEADER,
    ENABLE_JWT_VALUE,
    OAUTH_BEARER_TYPE_LABEL,
)
from bling_jwt_auth.exceptions import OAuthRequestError
from bling_jwt_auth.oauth.client import OAuthClient

if TYPE_CHECKING:
    from pytest_httpx import HTTPXMock

    from bling_jwt_auth.config import BlingAuthSettings

pytest.importorskip("pytest_httpx")


def test_build_authorization_url(settings: BlingAuthSettings) -> None:
    """Authorization URL contains OAuth query parameters and encoded redirect_uri."""
    with httpx.Client() as http:
        client = OAuthClient(settings, client=http)
        url = client.build_authorization_url("random-state-value")
    assert url.startswith(str(settings.authorize_url))
    assert "response_type=code" in url
    assert "client_id=test-client-id" in url
    assert "state=random-state-value" in url
    assert "redirect_uri=https%3A%2F%2Fexample.org%2Foauth%2Fcallback" in url


def test_build_authorization_url_rejects_empty_state(settings: BlingAuthSettings) -> None:
    """Empty ``state`` is rejected before building a URL."""
    with httpx.Client() as http:
        client = OAuthClient(settings, client=http)
        with pytest.raises(ValueError, match="state"):
            client.build_authorization_url("")


def test_exchange_code_sets_headers_and_parses_body(
    settings: BlingAuthSettings,
    httpx_mock: HTTPXMock,
    long_jwt_like_token: str,
) -> None:
    """Token exchange POST uses JWT/header/Basic settings and parses ``token_validate``."""
    httpx_mock.add_response(
        url=str(settings.token_url),
        method="POST",
        json={
            "access_token": long_jwt_like_token,
            "token_type": OAUTH_BEARER_TYPE_LABEL,
            "token_validate": 3600,
            "refresh_token": "refresh-1",
            "scope": "contacts",
        },
    )
    with OAuthClient(settings) as client:
        result = client.exchange_code("auth-code-xyz")

    assert result.access_token == long_jwt_like_token
    assert result.expires_in == 3600
    assert result.refresh_token == "refresh-1"

    sent = httpx_mock.get_request(url=str(settings.token_url))
    assert sent is not None
    assert sent.headers[ENABLE_JWT_HEADER] == ENABLE_JWT_VALUE
    assert sent.headers["Accept"] == ACCEPT_HEADER_VALUE
    assert sent.headers["Content-Type"] == "application/x-www-form-urlencoded"
    auth_header = sent.headers.get("Authorization", "")
    assert auth_header.startswith("Basic ")


def test_refresh_token_request(httpx_mock: HTTPXMock, settings: BlingAuthSettings) -> None:
    """Refresh grant posts ``refresh_token`` in the URL-encoded body."""
    httpx_mock.add_response(
        url=str(settings.token_url),
        method="POST",
        json={
            "access_token": "new-access",
            "expires_in": 1800,
            "refresh_token": "new-refresh",
        },
    )
    with OAuthClient(settings) as client:
        token = client.refresh_token("old-refresh")

    assert token.access_token == "new-access"
    assert token.refresh_token == "new-refresh"
    sent = httpx_mock.get_request(url=str(settings.token_url))
    assert sent is not None
    body = sent.content.decode()
    assert "grant_type=refresh_token" in body
    assert "refresh_token=old-refresh" in body


def test_revoke_posts_form(httpx_mock: HTTPXMock, settings: BlingAuthSettings) -> None:
    """Revocation sends token and optional type hint as form fields."""
    httpx_mock.add_response(url=str(settings.revoke_url), method="POST", text="")
    with OAuthClient(settings) as client:
        client.revoke_token("token-value", token_type_hint="access_token")

    sent = httpx_mock.get_request(url=str(settings.revoke_url))
    assert sent is not None
    body = sent.content.decode()
    assert "token=token-value" in body
    assert "token_type_hint=access_token" in body


def test_exchange_code_http_error(httpx_mock: HTTPXMock, settings: BlingAuthSettings) -> None:
    """Non-success HTTP statuses become :class:`OAuthRequestError`."""
    httpx_mock.add_response(
        url=str(settings.token_url),
        method="POST",
        status_code=400,
        text="invalid_grant",
    )
    with (
        OAuthClient(settings) as client,
        pytest.raises(OAuthRequestError) as excinfo,
    ):
        client.exchange_code("bad")

    assert excinfo.value.status_code == 400
    assert excinfo.value.response_body == "invalid_grant"


def test_enable_jwt_can_be_disabled(httpx_mock: HTTPXMock, settings: BlingAuthSettings) -> None:
    """When JWT mode is disabled, ``enable-jwt`` is omitted from token POSTs."""
    settings = settings.model_copy(update={"enable_jwt": False})
    httpx_mock.add_response(
        url=str(settings.token_url),
        method="POST",
        json={
            "access_token": "at",
            "expires_in": 60,
            "refresh_token": "rt",
        },
    )
    with OAuthClient(settings) as client:
        client.exchange_code("c")

    sent = httpx_mock.get_request(url=str(settings.token_url))
    assert sent is not None
    assert ENABLE_JWT_HEADER not in sent.headers
