from starlette import status

from src.exceptions.base import AppError


class ListingNotAvailableException(AppError):
    """Raised when a listing is not available for the requested dates."""
    status_code = status.HTTP_409_CONFLICT

    def __init__(self):
        message = "The selected dates are not available for this listing."
        super().__init__(message)


class InvalidLeasePeriodException(AppError):
    """Raised when the booking duration is less than the minimum required."""
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, min_months: int):
        message = f"The minimum lease period for this listing is {min_months} months."
        super().__init__(message)
