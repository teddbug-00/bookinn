from starlette import status

from src.exceptions import AppError


class IncorrectEmailOrPasswordException(AppError):
    """ Raised when authentication fails either because of a wrong password or email. """
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        message = "Incorrect email or password"
        super().__init__(message)


class CredentialsException(AppError):
    """Raised when JWT verification fails due to an invalid token or missing user."""
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        message = "Could not validate credentials."
        super().__init__(message)


class TokenExpiredException(AppError):
    """ Raised when a token has expired. """
    status_code = status.HTTP_401_UNAUTHORIZED

    def __init__(self):
        message = "Token has expired"
        super().__init__(message)


class NotEnoughPermissionsException(AppError):
    """ Raised when a user is not authorized to perform an action. """
    status_code = status.HTTP_403_FORBIDDEN

    def __init__(self):
        message = "Not enough permissions"
        super().__init__(message)
