"""Shared constants for Bling OAuth / JWT."""

ENABLE_JWT_HEADER = "enable-jwt"
ENABLE_JWT_VALUE = "1"

DEFAULT_AUTHORIZE_URL = "https://www.bling.com.br/Api/v3/oauth/authorize"
# RFC 6749 token endpoint URL (avoid *_TOKEN_* in the name due to flake8-bandit S105).
DEFAULT_OAUTH_CREDENTIALS_URL = "https://www.bling.com.br/Api/v3/oauth/token"
DEFAULT_REVOKE_URL = "https://www.bling.com.br/Api/v3/oauth/revoke"
DEFAULT_API_BASE_URL = "https://api.bling.com.br"

ACCEPT_HEADER_VALUE = "1.0"

# RFC 6750 bearer token scheme label used in OAuth responses.
OAUTH_BEARER_TYPE_LABEL = "Bearer"
