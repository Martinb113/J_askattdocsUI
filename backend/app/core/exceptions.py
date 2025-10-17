"""
Custom exception classes for the application.
"""
from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Raised when authentication fails."""
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedError(HTTPException):
    """Raised when user lacks permission for an action."""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class ResourceNotFoundError(HTTPException):
    """Raised when a requested resource is not found."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ValidationError(HTTPException):
    """Raised when request validation fails."""
    def __init__(self, detail: str = "Invalid request data"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
