"""JSON file token storage with atomic writes."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import suppress
from pathlib import Path

from bling_jwt_auth.models.token import StoredToken


class FileTokenStore:
    """JSON-file token store for a single Bling account.

    The store writes a complete token snapshot to disk using a temporary file
    followed by an atomic replace. On POSIX systems it attempts to restrict file
    permissions to ``0600`` after each save.
    """

    def __init__(self, path: Path | None = None) -> None:
        """Create a JSON token store.

        Args:
            path: Optional token file path. Defaults to
                ``~/.config/bling_jwt_auth/token.json``.
        """
        self._path = path or (Path.home() / ".config" / "bling_jwt_auth" / "token.json")

    @property
    def path(self) -> Path:
        """Filesystem path used by this store."""
        return self._path

    def load(self) -> StoredToken | None:
        """Load and validate a token file, or return ``None`` if missing."""
        if not self._path.is_file():
            return None
        raw = self._path.read_text(encoding="utf-8")
        payload = json.loads(raw)
        return StoredToken.model_validate(payload)

    def save(self, token: StoredToken) -> None:
        """Atomically write JSON (temp file + replace) and tighten permissions on Unix."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(token.model_dump(mode="json"), indent=2, sort_keys=True)
        directory = self._path.parent
        fd, tmppath = tempfile.mkstemp(prefix=".token.", suffix=".json", dir=directory)
        tmp = Path(tmppath)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            tmp.replace(self._path)
        except OSError:
            with suppress(OSError):
                tmp.unlink(missing_ok=True)
            raise
        self._restrict_permissions()

    def clear(self) -> None:
        """Delete the token file when it exists."""
        if self._path.is_file():
            self._path.unlink()

    def _restrict_permissions(self) -> None:
        if os.name != "posix":
            return
        with suppress(OSError):
            self._path.chmod(0o600)
