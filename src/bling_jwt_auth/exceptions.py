"""Error types for the Bling authentication helpers."""


class BlingAuthError(Exception):
    """Base exception for this package."""


class OAuthRequestError(BlingAuthError):
    """Raised when the Bling OAuth HTTP endpoint returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize with a message and optional HTTP response details."""
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class TokenNotFoundError(BlingAuthError):
    """Raised when no stored credentials exist but a token was required."""
