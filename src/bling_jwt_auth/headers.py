"""HTTP header helpers for authenticated Bling API v3 calls."""

from __future__ import annotations

from bling_jwt_auth.constants import ENABLE_JWT_HEADER, ENABLE_JWT_VALUE


def bling_api_headers(access_token: str) -> dict[str, str]:
    """Headers required for authenticated Bling API requests when using JWT mode."""
    return {
        "Authorization": f"Bearer {access_token}",
        ENABLE_JWT_HEADER: ENABLE_JWT_VALUE,
    }
