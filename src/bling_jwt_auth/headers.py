"""HTTP header helpers for authenticated Bling API v3 calls."""

from __future__ import annotations

from bling_jwt_auth.constants import ENABLE_JWT_HEADER, ENABLE_JWT_VALUE


def bling_api_headers(access_token: str) -> dict[str, str]:
    """Build headers for authenticated Bling API v3 requests.

    Args:
        access_token: OAuth access token returned by Bling.

    Returns:
        Headers containing ``Authorization: Bearer <token>`` and Bling's
        ``enable-jwt: 1`` compatibility header.
    """
    return {
        "Authorization": f"Bearer {access_token}",
        ENABLE_JWT_HEADER: ENABLE_JWT_VALUE,
    }
