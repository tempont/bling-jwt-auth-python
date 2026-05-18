"""Minimal manual OAuth walkthrough.

Loads secrets from `./.env` (see `env_file` on `BlingAuthSettings`) and/or exported
`BLING_*` environment variables — run from the repo root next to `.env`.

Example:
    uv sync
    uv run python examples/oauth_flow.py
"""

from __future__ import annotations

import os
import sys
import webbrowser

from bling_jwt_auth import BlingAuthSettings, OAuthClient, TokenManager, create_token_store


def main() -> None:
    """Prompt for OAuth code interactively after printing the authorize URL."""
    settings = BlingAuthSettings.load()
    store = create_token_store(settings)
    with OAuthClient(settings) as oauth:
        manager = TokenManager(oauth, store, settings)

        auth_url = oauth.build_authorization_url(state=os.urandom(16).hex())
        print("Open this URL in a browser, approve access, then copy the `code` query param:")
        print(auth_url)
        if "--open" in sys.argv:
            webbrowser.open(auth_url)

        code = input("Paste authorization code: ").strip()
        manager.save_from_code(code)
        token = manager.get_access_token()
        print("Access token acquired (truncated):", token[:24], "...")
        print("Use HTTP headers:")
        print("  Authorization: Bearer", "<token>")
        print("  enable-jwt: 1")


if __name__ == "__main__":
    main()
