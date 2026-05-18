# bling-jwt-auth-python

Repository: [github.com/tempont/bling-jwt-auth-python](https://github.com/tempont/bling-jwt-auth-python) · PyPI: [`bling-jwt-auth`](https://pypi.org/project/bling-jwt-auth/)

Python library for OAuth 2.0 authentication with the **Bling API v3**, including the JWT mode headers required by current Bling API endpoints.

Use this package when your application needs to obtain, persist, and refresh Bling OAuth tokens without reimplementing the flow. It covers the common integration path:

- build the authorization URL for the user to connect a Bling account;
- exchange the callback `code` for `access_token` and `refresh_token`;
- store tokens locally in SQLite or JSON;
- refresh the `access_token` before it expires;
- build the headers required for authenticated API v3 requests.

Primary Portuguese README: [../README.md](../README.md)

## Requirements

- Python 3.14 or newer
- An OAuth application registered in Bling
- The application's `client_id`, `client_secret`, and `redirect_uri`

## Installation

```bash
pip install bling-jwt-auth
```

Install directly from the repository:

```bash
pip install "git+https://github.com/tempont/bling-jwt-auth-python.git"
```

For local development:

```bash
uv sync --extra dev
```

## Configuration

Copy the example file and fill in your Bling app credentials:

```bash
cp .env.example .env
```

```env
BLING_CLIENT_ID=your_client_id
BLING_CLIENT_SECRET=your_client_secret
BLING_REDIRECT_URI=https://your-domain.com/oauth/callback
```

By default, tokens are stored in SQLite at `~/.config/bling_jwt_auth/tokens.db`.

To store tokens as JSON:

```env
BLING_TOKEN_STORE=file
BLING_TOKEN_STORE_PATH=./token.json
```

To store SQLite data at a custom path:

```env
BLING_TOKEN_STORE=sqlite
BLING_TOKEN_STORE_PATH=./bling-tokens.db
```

## OAuth Flow

### 1. Build the authorization URL

```python
from bling_jwt_auth import BlingAuthSettings, OAuthClient

settings = BlingAuthSettings.load()

with OAuthClient(settings) as oauth:
    url = oauth.build_authorization_url(state="secure-random-value")
    print(url)
```

Open the URL in a browser, authorize the application in Bling, then capture the `code` query parameter received by the callback configured in `BLING_REDIRECT_URI`.

### 2. Exchange the code for tokens and persist them

```python
from bling_jwt_auth import BlingAuthSettings, OAuthClient, TokenManager, create_token_store

settings = BlingAuthSettings.load()
store = create_token_store(settings)

with OAuthClient(settings) as oauth:
    manager = TokenManager(oauth, store, settings)
    manager.save_from_code("code-from-callback")
```

### 3. Use a valid access token

```python
import httpx

from bling_jwt_auth import (
    BlingAuthSettings,
    OAuthClient,
    TokenManager,
    bling_api_headers,
    create_token_store,
)

settings = BlingAuthSettings.load()
store = create_token_store(settings)

with OAuthClient(settings) as oauth:
    manager = TokenManager(oauth, store, settings)
    access_token = manager.get_access_token()

response = httpx.get(
    "https://api.bling.com.br/Api/v3/produtos",
    headers=bling_api_headers(access_token),
)
response.raise_for_status()
print(response.json())
```

`TokenManager.get_access_token()` reads the stored token, checks expiration using `BLING_REFRESH_SKEW_SECONDS`, and refreshes automatically when needed.

## Runnable Examples

Manual OAuth flow:

```bash
uv run python examples/oauth_flow.py
```

The script prints the authorization URL. After approving access in Bling, paste the callback `code` into the terminal.

To try opening the browser automatically:

```bash
uv run python examples/oauth_flow.py --open
```

Authenticated request test:

```bash
uv run python examples/authenticated_request.py
```

This example uses the same token saved by the OAuth flow, refreshes it if needed, and calls Bling's product homologation endpoint.

## Main API

| Object | Use |
| --- | --- |
| `BlingAuthSettings` | Loads configuration from `BLING_*` variables and `.env`. |
| `OAuthClient` | Synchronous client for authorization, code exchange, refresh, and revocation. |
| `TokenManager` | Coordinates `OAuthClient` + `TokenStore` to save and refresh tokens. |
| `create_token_store` | Creates the configured token backend (`sqlite` or `file`). |
| `SQLiteTokenStore` | Persists one token bundle in a local SQLite database. |
| `FileTokenStore` | Persists one token bundle in a local JSON file. |
| `bling_api_headers` | Builds `Authorization: Bearer ...` and `enable-jwt: 1`. |

## Environment Variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `BLING_CLIENT_ID` | Yes | - | OAuth client ID from Bling. |
| `BLING_CLIENT_SECRET` | Yes | - | OAuth client secret. |
| `BLING_REDIRECT_URI` | Yes | - | Callback registered in Bling. |
| `BLING_ENABLE_JWT` | No | `true` | Sends the `enable-jwt: 1` header to OAuth endpoints. |
| `BLING_AUTHORIZE_URL` | No | official endpoint | OAuth authorization URL. |
| `BLING_TOKEN_URL` | No | official endpoint | Token exchange and refresh URL. |
| `BLING_REVOKE_URL` | No | official endpoint | Token revocation URL. |
| `BLING_REFRESH_SKEW_SECONDS` | No | `60` | Seconds before real expiry to proactively refresh. |
| `BLING_TOKEN_STORE` | No | `sqlite` | Token backend: `sqlite` or `file`. |
| `BLING_TOKEN_STORE_PATH` | No | `~/.config/...` | Custom path for the SQLite DB or JSON file. |

## Error Handling

- `TokenNotFoundError`: no token has been saved yet. Run the OAuth flow or call `TokenManager.save_from_code()`.
- `OAuthRequestError`: Bling returned an HTTP error during exchange, refresh, or revocation. The exception keeps `status_code` and `response_body`.
- `ValueError`: required arguments such as `state`, `code`, or `refresh_token` were empty.

## Security

- Do not commit `.env`, `token.json`, or SQLite databases containing tokens.
- Use a random `state` and validate it in your OAuth callback.
- Configure `BLING_REDIRECT_URI` exactly as registered in Bling.
- In production, prefer environment variables or a secret manager for credentials.
- The JSON backend applies `0600` permissions on POSIX systems after writing.

## Development

Run lint, type checks, and tests:

```bash
make check
```

Or:

```bash
bash scripts/check.sh
```

Run tests only:

```bash
uv run --extra dev pytest
```

Build and validate local distribution artifacts:

```bash
uv run --extra dev python -m build
uv run --extra dev python -m twine check dist/*
```

## License

MIT. See [../LICENSE](../LICENSE).
