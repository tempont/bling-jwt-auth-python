"""Call the Bling homologation endpoint to verify OAuth + stored tokens.

Loads secrets from `./.env` (see `env_file` on `BlingAuthSettings`) and/or exported
`BLING_*` environment variables — run from the repo root next to `.env`.

Uses the same token store as `oauth_flow.py` (see `BLING_TOKEN_STORE` and
`BLING_TOKEN_STORE_PATH`).

Example:
    uv sync
    uv run python examples/oauth_flow.py
    uv run python examples/authenticated_request.py
"""

from __future__ import annotations

import json
import sys
from typing import Any, cast

import httpx

from bling_jwt_auth import (
    BlingAuthSettings,
    OAuthClient,
    TokenManager,
    TokenNotFoundError,
    bling_api_headers,
    create_token_store,
)

HOMOLOGACAO_PRODUTOS_URL = "https://api.bling.com.br/Api/v3/homologacao/produtos"


def _summarize_body(text: str, *, max_len: int = 800) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def main() -> None:
    """GET homologação produtos using the access token from the configured store."""
    settings = BlingAuthSettings.load()
    store = create_token_store(settings)
    print(f"Token store: {settings.token_store.value} at {store.path}")

    with OAuthClient(settings) as oauth:
        manager = TokenManager(oauth, store, settings)
        try:
            access_token = manager.get_access_token()
        except TokenNotFoundError:
            print(
                "No token found. Run `uv run python examples/oauth_flow.py` first "
                f"using the same BLING_TOKEN_STORE ({settings.token_store.value}).",
                file=sys.stderr,
            )
            sys.exit(1)

    headers = bling_api_headers(access_token)
    with httpx.Client(timeout=30.0) as client:
        response = client.get(HOMOLOGACAO_PRODUTOS_URL, headers=headers)

    if not response.is_success:
        print(
            f"Request failed: HTTP {response.status_code}\n"
            f"{_summarize_body(response.text)}",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        parsed: Any = response.json()
    except json.JSONDecodeError:
        print("Unexpected response: not JSON", file=sys.stderr)
        print(_summarize_body(response.text), file=sys.stderr)
        sys.exit(1)

    if not isinstance(parsed, dict):
        print("Unexpected response: JSON must be an object", file=sys.stderr)
        sys.exit(1)
    body: dict[str, Any] = cast("dict[str, Any]", parsed)
    data: Any | None = body.get("data")
    preview_payload: Any = body if data is None else data
    preview = json.dumps(preview_payload, indent=2, ensure_ascii=False)
    print(f"HTTP {response.status_code} OK")
    print(preview)
    print("Token from store is valid for the Bling API (homologação GET).")


if __name__ == "__main__":
    main()
