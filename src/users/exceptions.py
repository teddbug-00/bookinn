from starlette import status

from src.exceptions.base import AppError


class UserNotFoundException(AppError):
    """Custom exception raised when a user is not found."""
    status_code: int = status.HTTP_404_NOT_FOUND

    def __init__(self):
        message = "User not found"
        super().__init__(message)


class UserAlreadyExistsException(AppError):
    """Custom exception raised when an email is already being used"""
    status_code: int = status.HTTP_409_CONFLICT

    def __init__(self):
        message = "Email already exists"
        super().__init__(message)
