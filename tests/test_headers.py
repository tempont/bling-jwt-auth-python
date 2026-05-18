"""Tests for :func:`bling_api_headers`."""

from bling_jwt_auth.constants import ENABLE_JWT_HEADER, ENABLE_JWT_VALUE
from bling_jwt_auth.headers import bling_api_headers


def test_bling_api_headers() -> None:
    """Output includes Bearer authorization and JWT compatibility header."""
    headers = bling_api_headers("my-token")
    assert headers["Authorization"] == "Bearer my-token"
    assert headers[ENABLE_JWT_HEADER] == ENABLE_JWT_VALUE
