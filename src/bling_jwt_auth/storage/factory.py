"""Construct the configured token store from settings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from bling_jwt_auth.config import TokenStoreKind
from bling_jwt_auth.storage.file import FileTokenStore
from bling_jwt_auth.storage.sqlite import SQLiteTokenStore

if TYPE_CHECKING:
    from bling_jwt_auth.config import BlingAuthSettings


def create_token_store(settings: BlingAuthSettings) -> SQLiteTokenStore | FileTokenStore:
    """Create the token backend selected by ``settings.token_store``.

    ``TokenStoreKind.FILE`` returns :class:`FileTokenStore`; every other
    supported value currently returns :class:`SQLiteTokenStore`.
    """
    path = settings.token_store_path
    if settings.token_store is TokenStoreKind.FILE:
        return FileTokenStore(path)
    return SQLiteTokenStore(path)
