from starlette import status


class AppError(Exception):
    """Base class for all application errors."""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "An unexpected application error occurred."):
        super().__init__(message)
