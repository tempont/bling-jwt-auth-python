"""Bling API v3 OAuth helpers (JWT-ready)."""

from bling_jwt_auth.auth import BlingAuth
from bling_jwt_auth.client import BlingClient, connect
from bling_jwt_auth.config import BlingAuthSettings, TokenStoreKind
from bling_jwt_auth.exceptions import BlingAuthError, OAuthRequestError, TokenNotFoundError
from bling_jwt_auth.headers import bling_api_headers
from bling_jwt_auth.manager import TokenManager
from bling_jwt_auth.models.token import StoredToken, TokenResponse
from bling_jwt_auth.oauth.client import OAuthClient
from bling_jwt_auth.storage.base import TokenStore
from bling_jwt_auth.storage.factory import create_token_store
from bling_jwt_auth.storage.file import FileTokenStore
from bling_jwt_auth.storage.sqlite import SQLiteTokenStore

__all__ = [
    "BlingAuth",
    "BlingAuthError",
    "BlingAuthSettings",
    "BlingClient",
    "FileTokenStore",
    "OAuthClient",
    "OAuthRequestError",
    "SQLiteTokenStore",
    "StoredToken",
    "TokenManager",
    "TokenNotFoundError",
    "TokenResponse",
    "TokenStore",
    "TokenStoreKind",
    "bling_api_headers",
    "connect",
    "create_token_store",
]

__version__ = "0.3.0"
