"""Tests for :func:`bling_jwt_auth.storage.factory.create_token_store`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import SecretStr, ValidationError

from bling_jwt_auth.config import BlingAuthSettings, TokenStoreKind
from bling_jwt_auth.storage.factory import create_token_store
from bling_jwt_auth.storage.file import FileTokenStore
from bling_jwt_auth.storage.sqlite import SQLiteTokenStore

from .url_utils import parsed_http_url

if TYPE_CHECKING:
    from pathlib import Path


def _minimal_settings(
    *,
    token_store: TokenStoreKind = TokenStoreKind.SQLITE,
    token_store_path: Path | None = None,
) -> BlingAuthSettings:
    return BlingAuthSettings(
        client_id="cid",
        client_secret=SecretStr("secret"),
        redirect_uri=parsed_http_url("https://example.org/callback"),
        token_store=token_store,
        token_store_path=token_store_path,
    )


def test_create_defaults_to_sqlite_with_builtin_path() -> None:
    """Default settings yield SQLite at the standard default path."""
    store = create_token_store(_minimal_settings())
    assert isinstance(store, SQLiteTokenStore)
    assert "tokens.db" in str(store.path)


def test_create_sqlite_with_custom_path(tmp_path: Path) -> None:
    """Custom ``token_store_path`` is passed through to SQLite."""
    db_path = tmp_path / "custom.db"
    store = create_token_store(_minimal_settings(token_store_path=db_path))
    assert isinstance(store, SQLiteTokenStore)
    assert store.path == db_path


def test_create_file_store(tmp_path: Path) -> None:
    """``TokenStoreKind.FILE`` builds a :class:`FileTokenStore` with the given path."""
    json_path = tmp_path / "tok.json"
    store = create_token_store(
        _minimal_settings(token_store=TokenStoreKind.FILE, token_store_path=json_path),
    )
    assert isinstance(store, FileTokenStore)
    assert store.path == json_path


def test_invalid_token_store_raises() -> None:
    """Unknown ``token_store`` string values fail validation."""
    with pytest.raises(ValidationError):
        BlingAuthSettings(
            client_id="cid",
            client_secret=SecretStr("secret"),
            redirect_uri=parsed_http_url("https://example.org/callback"),
            token_store="blob",  # type: ignore[arg-type]
        )
