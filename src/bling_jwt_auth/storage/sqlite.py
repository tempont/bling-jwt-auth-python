"""SQLite-backed token storage (single row, single account)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from bling_jwt_auth.models.token import StoredToken


class SQLiteTokenStore:
    """Persist tokens in a local SQLite database."""

    _SCHEMA = """
    CREATE TABLE IF NOT EXISTS bling_tokens (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        payload TEXT NOT NULL
    );
    """

    def __init__(self, path: Path | None = None) -> None:
        """Use ``path`` or the default under ``~/.config/bling_jwt_auth/tokens.db``."""
        self._path = path or (Path.home() / ".config" / "bling_jwt_auth" / "tokens.db")

    @property
    def path(self) -> Path:
        """Database file path."""
        return self._path

    def _bootstrap(self, conn: sqlite3.Connection) -> None:
        """Apply pragmas and ensure the schema exists."""
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(self._SCHEMA)

    def load(self) -> StoredToken | None:
        """Return the persisted token, or ``None`` when the DB or row is absent."""
        if not self._path.is_file():
            return None
        conn = sqlite3.connect(self._path)
        try:
            self._bootstrap(conn)
            row = conn.execute(
                "SELECT payload FROM bling_tokens WHERE id = 1",
            ).fetchone()
        finally:
            conn.close()
        if row is None:
            return None
        payload = json.loads(row[0])
        return StoredToken.model_validate(payload)

    def save(self, token: StoredToken) -> None:
        """Upsert the single-row token snapshot and commit."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(token.model_dump(mode="json"), sort_keys=True)
        conn = sqlite3.connect(self._path)
        try:
            self._bootstrap(conn)
            conn.execute(
                """
                INSERT INTO bling_tokens (id, payload)
                VALUES (1, ?)
                ON CONFLICT (id) DO UPDATE SET payload = excluded.payload
                """,
                (data,),
            )
            conn.commit()
        finally:
            conn.close()

    def clear(self) -> None:
        """Remove the stored credential row."""
        if not self._path.is_file():
            return
        conn = sqlite3.connect(self._path)
        try:
            self._bootstrap(conn)
            conn.execute("DELETE FROM bling_tokens WHERE id = 1")
            conn.commit()
        finally:
            conn.close()
