"""Application-wide exception hierarchy.

Every custom exception carries a ``status_code`` and ``detail`` string so the
FastAPI exception handler can render consistent JSON error responses.
"""


class AppError(Exception):
    """Base class for all application errors."""

    status_code: int = 400
    detail: str = "Bad request"

    def __init__(self, message: str | None = None) -> None:
        """Store the message as ``detail`` (and in ``args``) for handlers.

        This lets ``AppError("friendly text")`` surface text in both the REST
        ``detail`` JSON field and the GraphQL ``errors[].message``.
        """
        super().__init__(message or self.detail)
        if message is not None:
            self.detail = message


class DuplicateEmailError(AppError):
    status_code = 409
    detail = "An account with this email already exists"


class InvalidCredentialsError(AppError):
    status_code = 401
    detail = "Invalid credentials"


class InvalidTokenError(AppError):
    status_code = 401
    detail = "Invalid or malformed token"


class ExpiredTokenError(AppError):
    status_code = 401
    detail = "Token has expired"


class InactiveUserError(AppError):
    status_code = 403
    detail = "Account is not active"


class PermissionDeniedError(AppError):
    status_code = 403
    detail = "You do not have permission to perform this action"


class GoogleAuthError(AppError):
    status_code = 401
    detail = "Google authentication failed"


class NotFoundError(AppError):
    status_code = 404
    detail = "Resource not found"


class ValidationError(AppError):
    status_code = 422
    detail = "Validation failed"


class DuplicateResourceError(AppError):
    status_code = 409
    detail = "Resource already exists"
