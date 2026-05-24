"""Call Bling with a plain ``httpx.Client`` and ``BlingAuth``.

Example:
    uv run python examples/oauth_flow.py
    uv run python examples/httpx_auth_request.py
"""

from __future__ import annotations

import json
import sys
from typing import Any, cast

import httpx

from bling_jwt_auth import BlingAuth, TokenNotFoundError

HOMOLOGACAO_PRODUTOS_URL = "https://api.bling.com.br/Api/v3/homologacao/produtos"


def _summarize_body(text: str, *, max_len: int = 800) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def main() -> None:
    """GET homologação produtos using only the httpx auth adapter."""
    try:
        with (
            BlingAuth.from_env() as auth,
            httpx.Client(auth=auth, timeout=30.0) as client,
        ):
            response = client.get(HOMOLOGACAO_PRODUTOS_URL)
    except TokenNotFoundError:
        msg = "No token found. Run `uv run python examples/oauth_flow.py` first."
        print(msg, file=sys.stderr)
        sys.exit(1)

    if not response.is_success:
        msg = f"Request failed: HTTP {response.status_code}\n{_summarize_body(response.text)}"
        print(msg, file=sys.stderr)
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


if __name__ == "__main__":
    main()
