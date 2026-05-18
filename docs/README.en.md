# bling-jwt-auth-python

A small Python library for authenticating with the **Bling API v3** using OAuth 2.0 and JWT tokens.

It helps you:

- build the Bling authorization URL;
- exchange the received `code` for tokens;
- store tokens in a file or SQLite;
- refresh the access token automatically when needed;
- build the correct headers for Bling API requests.

Primary Portuguese README: [../README.md](../README.md)

## Requirements

- Python 3.14 or newer
- An OAuth application registered in Bling

## Installation

Install with `pip`:

```bash
pip install bling-jwt-auth-python
```

Or install directly from GitHub:

```bash
pip install "git+https://github.com/mercanatu/bling-jwt-auth-python.git"
```

For local development in this repository, use:

```bash
uv sync --extra dev
```

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your Bling app credentials:

```env
BLING_CLIENT_ID=your_client_id
BLING_CLIENT_SECRET=your_client_secret
BLING_REDIRECT_URI=https://your-domain.com/oauth/callback
```

By default, tokens are stored in SQLite. To store them as JSON instead:

```env
BLING_TOKEN_STORE=file
BLING_TOKEN_STORE_PATH=./token.json
```

## Usage

### 1. Authorize the Bling account

Run the OAuth example:

```bash
uv run python examples/oauth_flow.py
```

The script will print a URL. Open it in your browser, approve access in Bling, then paste the `code` received in the callback back into the terminal.

To let the script try to open the browser automatically:

```bash
uv run python examples/oauth_flow.py --open
```

### 2. Test an authenticated request

After saving the token, run:

```bash
uv run python examples/authenticated_request.py
```

This example uses the saved token, refreshes it if needed, and calls a Bling homologation endpoint.

### 3. Use it in your code

```python
import httpx
from bling_jwt_auth import (
    BlingAuthSettings,
    OAuthClient,
    TokenManager,
    bling_api_headers,
    create_token_store,
)

settings = BlingAuthSettings()
store = create_token_store(settings)

with OAuthClient(settings) as oauth:
    manager = TokenManager(oauth, store, settings)
    access_token = manager.get_access_token()

headers = bling_api_headers(access_token)

response = httpx.get(
    "https://api.bling.com.br/Api/v3/produtos",
    headers=headers,
)
response.raise_for_status()
print(response.json())
```

## Useful Development Commands

Run lint, type checks, and tests:

```bash
make check
```

Or:

```bash
bash scripts/check.sh
```

Run only the tests:

```bash
uv run --extra dev pytest
```

## License

MIT. See [../LICENSE](../LICENSE).
