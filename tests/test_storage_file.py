"""Tests for :class:`FileTokenStore`."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from bling_jwt_auth.models.token import StoredToken
from bling_jwt_auth.storage.file import FileTokenStore

if TYPE_CHECKING:
    from pathlib import Path


def test_file_store_round_trip(tmp_path: Path) -> None:
    """Saved JSON round-trips to an equivalent :class:`StoredToken`."""
    path = tmp_path / "token.json"
    store = FileTokenStore(path)
    token = StoredToken(
        access_token="a",
        expires_in=60,
        refresh_token="r",
        obtained_at=datetime.now(UTC),
        scope="x",
    )
    store.save(token)
    loaded = store.load()
    assert loaded == token


def test_file_store_clear(tmp_path: Path) -> None:
    """``clear`` removes the backing file."""
    path = tmp_path / "token.json"
    store = FileTokenStore(path)
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
    assert not path.is_file()


def test_file_store_load_missing_returns_none(tmp_path: Path) -> None:
    """Missing path yields ``None`` without creating a file."""
    store = FileTokenStore(tmp_path / "nope.json")
    assert store.load() is None
