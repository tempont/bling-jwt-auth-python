"""URL helpers used by tests (strict :class:`~pydantic.HttpUrl` parsing)."""

from __future__ import annotations

from pydantic import HttpUrl, TypeAdapter

_http_url_adapter = TypeAdapter(HttpUrl)


def parsed_http_url(value: str) -> HttpUrl:
    """Parse strings into validated :class:`HttpUrl` values for settings constructors."""
    return _http_url_adapter.validate_python(value)
