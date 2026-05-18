"""Tests for :class:`SQLiteTokenStore`."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from bling_jwt_auth.models.token import StoredToken
from bling_jwt_auth.storage.sqlite import SQLiteTokenStore

if TYPE_CHECKING:
    from pathlib import Path


def test_sqlite_round_trip(tmp_path: Path) -> None:
    """SQLite store persists JSON payload and reloads equivalently."""
    db = tmp_path / "tokens.db"
    store = SQLiteTokenStore(db)
    token = StoredToken(
        access_token="a",
        expires_in=120,
        refresh_token="r",
        obtained_at=datetime.now(UTC),
    )
    store.save(token)
    loaded = store.load()
    assert loaded == token


def test_sqlite_clear(tmp_path: Path) -> None:
    """``clear`` removes the lone credential row."""
    db = tmp_path / "tokens.db"
    store = SQLiteTokenStore(db)
    store.save(
        StoredToken(
            access_token="a",
            expires_in=60,
            refresh_token="r",
            obtained_at=datetime.now(UTC),
        ),
    )
    store.clear()
    assert store.load() is None
