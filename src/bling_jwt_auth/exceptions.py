"""Error types for the Bling authentication helpers."""


class BlingAuthError(Exception):
    """Base exception for all errors raised directly by this package."""


class OAuthRequestError(BlingAuthError):
    """Raised when a Bling OAuth HTTP request fails.

    ``status_code`` and ``response_body`` are preserved when the error came from
    an HTTP response, making it possible to log or inspect Bling's returned
    error payload.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize the error with optional HTTP response details."""
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class TokenNotFoundError(BlingAuthError):
    """Raised when no stored credentials exist but an access token was required."""
