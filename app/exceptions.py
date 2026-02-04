class ServiceError(Exception):
    """Base class for service-layer errors."""


class PermissionDeniedError(ServiceError):
    """Raised when a user lacks required permissions."""


class InactiveUserError(ServiceError):
    """Raised when a user is inactive."""

class InvalidCredentialsError(ServiceError):
    """Raised when an invalid credentials are given."""
